import os
import re
import json
import numpy as np
from functools import lru_cache
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer

# ---------------------------
# Model (load once)
# ---------------------------
_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------
# PDPA loading & category extraction
# ---------------------------

@lru_cache(maxsize=1)
def _load_pdpa_json(path: str) -> Dict[str, Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=1)
def _get_category_embeddings(pdpa_path: str) -> Tuple[Tuple[str, ...], np.ndarray]:
    """
    Get category names and their embeddings for vector matching
    """
    pdpa_tree = _load_pdpa_json(pdpa_path)
    category_names = tuple(pdpa_tree.keys())  # Convert to tuple (hashable)
    
    # Create embeddings for category names
    embs = _model.encode(list(category_names), convert_to_numpy=True, normalize_embeddings=True)
    return category_names, embs


# ---------------------------
# FIRST CHECK - Category Matching
# ---------------------------

def first_check(
    key_terms: List[str],
    pdpa_path: str = "pdpa.json",
    similarity_threshold: float = 0.3,
    max_matches: int = 3,
) -> List[Tuple[str, str, List[Tuple[str, str]]]]:
    """
    Compare key_terms against PDPA category names using vector matching.
    Returns list of (category_name, context, section_matches) for each matched category.
    """
    if not key_terms:
        return []

    # Load PDPA data and get category embeddings
    pdpa_tree = _load_pdpa_json(os.path.abspath(pdpa_path))
    category_names, category_embeddings = _get_category_embeddings(os.path.abspath(pdpa_path))

    # Clean and deduplicate terms - convert to tuple for hashing
    terms_list = [t.strip().lower() for t in key_terms if isinstance(t, str) and t.strip()]
    terms = tuple(dict.fromkeys(terms_list))  # Remove duplicates, keep as tuple
    
    if not terms:
        return []

    # Create embeddings for key terms
    term_embeddings = _model.encode(list(terms), convert_to_numpy=True, normalize_embeddings=True)
    
    # Calculate similarity matrix
    sim_matrix = term_embeddings @ category_embeddings.T  # (M terms x N categories)
    
    # Find best matches per category
    matched_categories = {}
    for i in range(sim_matrix.shape[1]):  # For each category
        max_score = float(np.max(sim_matrix[:, i]))
        if max_score >= similarity_threshold:
            category_name = category_names[i]
            matched_categories[category_name] = max_score
    
    # Sort by score and take top matches
    sorted_matches = sorted(matched_categories.items(), key=lambda x: x[1], reverse=True)[:max_matches]
    
    # Create contexts for each matched category
    results = []
    for category_name, score in sorted_matches:
        # Get all sections in this category
        sections = pdpa_tree.get(category_name, {})
        
        # Create context with all sections in the category
        context_parts = []
        section_matches = []
        
        for section_title, section_content in sections.items():
            context_parts.append(f"### {section_title}\n{section_content}")
            section_matches.append((section_title, section_content))
        
        context = "\n\n---\n\n".join(context_parts)
        results.append((category_name, context, section_matches))
    
    return results


# ---------------------------
# SECOND CHECK - Interpretation Terms
# ---------------------------

@lru_cache(maxsize=1)
def _load_interpretation_json(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def second_check(
    context: str,
    interpretation_path: str = "interpretation.json",
) -> str:
    """
    Check if any interpretation terms appear in context and append their definitions.
    """
    if not context.strip():
        return context

    try:
        interpretation_json = _load_interpretation_json(os.path.abspath(interpretation_path))
    except (FileNotFoundError, json.JSONDecodeError):
        return context

    lowered_context = context.lower()
    matched_keys = []
    
    # Check each interpretation key
    for key in interpretation_json.keys():
        if re.search(r'\b' + re.escape(key.lower()) + r'\b', lowered_context):
            matched_keys.append(key)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keys = []
    for key in matched_keys:
        if key not in seen:
            seen.add(key)
            unique_keys.append(key)
    
    # Append definitions
    additions = []
    for key in unique_keys:
        definition = interpretation_json[key]
        additions.append(f"### Definition: {key}\n{definition}")

    if additions:
        context += "\n\n---\n\n" + "\n\n---\n\n".join(additions)

    return context


# ---------------------------
# THIRD CHECK - Schedule References
# ---------------------------

@lru_cache(maxsize=1)
def _load_schedule_json(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def third_check(
    context: str,
    schedule_path: str = "schedule.json",
) -> str:
    """
    Check if 'schedule' appears and find preceding words (first, second, etc.).
    Append corresponding schedule content.
    """
    if not context.strip():
        return context

    try:
        schedule_lookup = _load_schedule_json(os.path.abspath(schedule_path))
    except (FileNotFoundError, json.JSONDecodeError):
        return context

    # Find patterns like "first schedule", "second schedule", etc.
    schedule_pattern = r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh)\s+schedule\b'
    matches = re.findall(schedule_pattern, context, flags=re.IGNORECASE)
    
    if not matches:
        return context

    # Remove duplicates while preserving order
    seen = set()
    unique_keys = []
    for match in matches:
        key = match.lower()
        if key not in seen:
            seen.add(key)
            unique_keys.append(key)
    
    # Append schedule content
    additions = []
    for key in unique_keys:
        if key in schedule_lookup:
            schedule_title = f"{key.title()} Schedule"
            additions.append(f"### {schedule_title}\n{schedule_lookup[key]}")

    if additions:
        context += "\n\n---\n\n" + "\n\n---\n\n".join(additions)

    return context


# ---------------------------
# FINAL CHECK - Subsidiary Legislation
# ---------------------------

@lru_cache(maxsize=1)
def _load_subsidiary_json(path: str) -> str:
    """Load subsidiary JSON and return as string to make it hashable"""
    with open(path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f))

def _parse_subsidiary_data(json_string: str) -> Dict:
    """Parse the JSON string back to dict"""
    return json.loads(json_string)

def final_check(
    context: str,
    section_matches_str: str,  # Pass as string instead of list
    subsidiary_path: str = "subsidiary.json",
) -> str:
    """
    Extract section numbers from section matches and find corresponding subsidiary legislation.
    """
    if not context.strip() or not section_matches_str:
        return context

    # Parse section matches from string
    try:
        section_matches = json.loads(section_matches_str)
    except json.JSONDecodeError:
        return context

    try:
        subsidiary_json = _load_subsidiary_json(os.path.abspath(subsidiary_path))
        subsidiary_data = _parse_subsidiary_data(subsidiary_json)
        subsidiary_mapping = subsidiary_data.get("subsidiary_legislation_mapping", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return context

    additions = []
    
    for section_title, section_content in section_matches:
        # Extract section number from title like "21 notification of purpose"
        section_match = re.match(r'^(\d+[a-z]?)\s+', section_title)
        if section_match:
            section_number = section_match.group(1)
            
            # Look for this section in subsidiary legislation
            for reg_name, reg_sections in subsidiary_mapping.items():
                if section_number in reg_sections:
                    reg_info = reg_sections[section_number]
                    
                    if isinstance(reg_info, dict):
                        description = reg_info.get("description", "")
                        
                        if description:
                            reg_text = f"### Subsidiary Legislation - Section {section_number}\n"
                            reg_text += f"**Regulation:** {reg_name}\n"
                            reg_text += f"**Description:** {description}\n"
                            
                            additions.append(reg_text)
                            break

    if additions:
        context += "\n\n---\n\n" + "\n\n---\n\n".join(additions)

    return context


# ---------------------------
# MAIN PROCESSING FUNCTION
# ---------------------------

def process_context(
    key_terms: List[str],
    pdpa_path: str = "pdpa.json",
    interpretation_path: str = "interpretation.json",
    schedule_path: str = "schedule.json",
    subsidiary_path: str = "subsidiary.json"
) -> str:
    """
    Main function to process context through all checks.
    """
    # First check - get category matches
    category_matches = first_check(key_terms, pdpa_path)
    
    if not category_matches:
        return "No relevant categories found in PDPA."
    
    # Process each category match
    final_contexts = []
    
    for category_name, context, section_matches in category_matches:
        # Second check - add interpretation terms
        context = second_check(context, interpretation_path)
        
        # Third check - add schedule references
        context = third_check(context, schedule_path)
        
        # Final check - add subsidiary legislation
        # Convert section_matches to JSON string to make it hashable
        section_matches_str = json.dumps(section_matches)
        context = final_check(context, section_matches_str, subsidiary_path)
        
        # Add category header
        final_context = f"## {category_name.title()}\n\n{context}"
        final_contexts.append(final_context)
    
    # Combine all contexts
    return "\n\n" + "="*50 + "\n\n".join(final_contexts)
