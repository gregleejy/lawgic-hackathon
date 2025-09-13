import os
import re
import json
from functools import lru_cache
from typing import Dict, List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------
# Model (load once)
# ---------------------------
_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------
# PDPA loading & flattening
# Expected pdpa.json format:
# {
#   "category_name": {
#     "section_number section_name": "content_with_subsection_markers"
#   },
#   "category_name_2": {
#     "section_number section_name": "content_with_subsection_markers"
#   }
# }
# ---------------------------

@lru_cache(maxsize=1)
def _load_pdpa_json(path: str) -> Dict[str, Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _flatten_pdpa(pdpa_tree: Dict[str, Dict[str, str]]) -> Tuple[List[str], Dict[str, str]]:
    """
    Flattens the nested PDPA dict-of-dicts into:
      - document_keys: List[str] of "section_number section_name"
      - document_json: Dict[str, str] mapping section_title -> content
    """
    document_json: Dict[str, str] = {}
    for _category, section_map in pdpa_tree.items():
        if not isinstance(section_map, dict):
            continue
        for section_title, content in section_map.items():
            if isinstance(section_title, str) and isinstance(content, str):
                document_json[section_title] = content
    document_keys = list(document_json.keys())
    return document_keys, document_json

@lru_cache(maxsize=1)
def _pdpa_keys_and_embs(pdpa_path: str) -> Tuple[Tuple[str, ...], np.ndarray, Dict[str, str]]:
    """
    Loads + flattens PDPA, returns:
      - document_keys (tuple for cache hashing)
      - document_embeddings (np.ndarray normalized)
      - document_json (dict mapping section_title -> content)
    """
    pdpa_tree = _load_pdpa_json(os.path.abspath(pdpa_path))
    document_keys, document_json = _flatten_pdpa(pdpa_tree)
    embs = _model.encode(document_keys, convert_to_numpy=True, normalize_embeddings=True)
    return tuple(document_keys), embs, document_json


# ---------------------------
# FIRST CHECK
# ---------------------------

def first_check(
    context: str,
    key_terms: List[str],
    pdpa_path: str = "pdpa.json",
    similarity_threshold: float = 0.45,
    max_matches: int = 5,
) -> Tuple[str, List[Tuple[str, float]]]:
    """
    Compare key_terms against PDPA section titles (flattened from pdpa.json).
    - Uses vector similarity to find up to max_matches relevant sections.
    - Appends matched section contents to context, separated for readability.
    Returns:
      (updated_context, [(section_title, score), ...])
    """
    if not key_terms:
        return context, []

    # Load PDPA keys + embeddings + text
    document_keys, document_embeddings, document_json = _pdpa_keys_and_embs(os.path.abspath(pdpa_path))

    # Deduplicate & clean terms
    terms = list(dict.fromkeys(t.strip().lower() for t in key_terms if isinstance(t, str) and t.strip()))
    if not terms:
        return context, []

    term_embeddings = _model.encode(terms, convert_to_numpy=True, normalize_embeddings=True)

    # Cosine similarity via dot product (normalized vectors)
    sim_matrix = term_embeddings @ document_embeddings.T  # (M terms x N sections)

    matched: Dict[str, float] = {}
    # Best per-term to encourage diversity
    for i in range(sim_matrix.shape[0]):
        j = int(np.argmax(sim_matrix[i]))
        score = float(sim_matrix[i, j])
        if score >= similarity_threshold:
            key = document_keys[j]
            matched[key] = max(matched.get(key, 0.0), score)

    # Backfill via centroid if needed
    if len(matched) < max_matches:
        centroid = np.mean(term_embeddings, axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid /= norm
            centroid_sims = centroid @ document_embeddings.T  # (N,)
            for idx in np.argsort(-centroid_sims):
                key = document_keys[idx]
                score = float(centroid_sims[idx])
                if score < similarity_threshold:
                    break
                if key not in matched:
                    matched[key] = score
                if len(matched) >= max_matches:
                    break

    matches_sorted = sorted(matched.items(), key=lambda x: x[1], reverse=True)[:max_matches]

    # Append matched contents to context
    additions = []
    for section_title, _score in matches_sorted:
        content = document_json.get(section_title)
        if content:
            # Include the section title as a heading for clarity
            additions.append(f"### {section_title}\n{content}")

    if additions:
        context += ("\n\n---\n\n" if context.strip() else "") + "\n\n---\n\n".join(additions)

    return context, matches_sorted


# ---------------------------
# SECOND CHECK
# ---------------------------

def second_check(
    context: str,
    interpretation_keys: List[str],
    interpretation_json: Dict[str, str],
) -> str:
    """
    Scan context for mentions of any interpretation_keys (case-insensitive).
    If mentioned, append the corresponding interpretation content (once per key).
    """
    if not context.strip() or not interpretation_keys or not interpretation_json:
        return context

    lowered_context = context.lower()
    matched_keys = [
        key for key in interpretation_keys
        if isinstance(key, str) and key.lower() in lowered_context
    ]
    # Deduplicate preserving order
    matched_keys = list(dict.fromkeys(matched_keys))

    additions = [interpretation_json[k] for k in matched_keys if k in interpretation_json]
    if additions:
        context += "\n\n---\n\n" + "\n\n---\n\n".join(additions)

    return context


# ---------------------------
# THIRD CHECK
# ---------------------------

def third_check(
    context: str,
    schedule_lookup: Dict[str, str],
) -> str:
    """
    If 'schedule' appears, capture the word immediately before it (e.g., 'First Schedule').
    If that preceding word exists in schedule_lookup (case-insensitive keys), append the content.
    """
    if not context.strip() or not schedule_lookup:
        return context

    matches = re.findall(r"\b(\w+)\s+schedule\b", context, flags=re.IGNORECASE)
    if not matches:
        return context

    # Normalize extracted words and schedule_lookup keys to lowercase
    schedule_keys = list(dict.fromkeys(m.lower() for m in matches))
    normalized_lookup = {k.lower(): v for k, v in schedule_lookup.items()}

    additions = [normalized_lookup[k] for k in schedule_keys if k in normalized_lookup]
    if additions:
        context += "\n\n---\n\n" + "\n\n---\n\n".join(additions)

    return context


# ---------------------------
# FOURTH CHECK (subsidiary)
# ---------------------------

@lru_cache(maxsize=1)
def _load_subsidiary_json(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fourth_check(
    context: str,
    sub_id: str,
    path: str = "subsidiary.json",
) -> str:
    """
    Given an ID, look up corresponding content in subsidiary.json and append it.
    Supports either {"<id>": "text"} or {"<id>": {"content": "text"}} structures.
    """
    if not sub_id:
        return context

    try:
        data = _load_subsidiary_json(os.path.abspath(path))
    except (FileNotFoundError, json.JSONDecodeError):
        return context

    entry = data.get(sub_id) or data.get(str(sub_id))
    if entry is None:
        return context

    content = entry.get("content") if isinstance(entry, dict) else (entry if isinstance(entry, str) else None)
    if not content:
        return context

    context += ("\n\n---\n\n" if context.strip() else "") + content
    return context
