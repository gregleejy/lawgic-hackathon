# terms.py - Legal Term Extraction Module
from transformers import pipeline
import re

def extract_terms_from_query(user_query):
    """
    Extract legal terms from user query
    
    Args:
        user_query (str): The legal scenario from user
        
    Returns:
        list: List of relevant legal terms (max 15 terms)
    """
    
    clean_query = user_query.lower().strip()
    
    # Layer 1: Extended legal keywords
    keyword_terms = extract_legal_keywords_balanced(clean_query)
    
    # Layer 2: Legal-BERT
    bert_terms = extract_with_legal_bert_balanced(user_query)
    
    # Layer 3: Important context words
    context_terms = extract_context_words(clean_query)
    
    # Layer 4: Entities and data types
    entity_terms = extract_entities_and_data_types(clean_query)
    
    # Combine and deduplicate
    final_terms = balanced_combine_terms(keyword_terms, bert_terms, context_terms, entity_terms, clean_query)
    
    return final_terms

# ============================================================================
# LAYER 1: LEGAL KEYWORDS
# ============================================================================

def extract_legal_keywords_balanced(text):
    """Extract predefined legal keywords"""
    
    legal_keywords = {
        # Core PDPA terms (high priority)
        'core_pdpa': [
            'personal data', 'sensitive data', 'data protection', 'privacy',
            'consent', 'breach', 'notification', 'pdpa', 'pdpc'
        ],
        
        # Data processing actions (important verbs)
        'actions': [
            'collect', 'use', 'disclose', 'process', 'store', 'transfer', 
            'share', 'access', 'expose', 'leak', 'send', 'transmit'
        ],
        
        # Data types and subjects
        'data_types': [
            'records', 'information', 'data', 'details',
            'patient records', 'medical records', 'health records',
            'customer information', 'financial information',
            'email', 'phone', 'contact', 'location'
        ],
        
        # Legal entities and roles
        'entities': [
            'hospital', 'bank', 'company', 'organisation', 'business',
            'insurance company', 'data controller', 'data processor',
            'individual', 'patient', 'customer', 'employee', 'third party'
        ],
        
        # Important context/modifier words
        'context': [
            'without', 'unauthorized', 'proper', 'explicit', 'adequate',
            'overseas', 'international', 'cross-border'
        ]
    }
    
    found_terms = []
    
    # Extract from each category
    for category, terms in legal_keywords.items():
        for term in terms:
            # Use word boundaries for exact matching
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text):
                found_terms.append(term)
    
    return found_terms

# ============================================================================
# LAYER 2: LEGAL-BERT
# ============================================================================

def extract_with_legal_bert_balanced(text):
    """Extract terms using Legal-BERT model"""
    
    try:
        ner_pipeline = pipeline(
            "ner", 
            model="nlpaueb/legal-bert-base-uncased",
            tokenizer="nlpaueb/legal-bert-base-uncased",
            aggregation_strategy="simple"
        )
        
        results = ner_pipeline(text)
        
        bert_terms = []
        for result in results:
            if result['score'] > 0.6:
                term = clean_bert_term_balanced(result['word'])
                if term and is_meaningful_term(term):
                    bert_terms.append(term)
        
        return bert_terms
        
    except Exception as e:
        return []

def clean_bert_term_balanced(term):
    """Clean BERT terms"""
    
    # Remove BERT artifacts
    term = re.sub(r'[##\[\]]', '', term)
    term = term.strip().lower()
    
    # Basic validation
    if len(term) < 2:
        return None
    
    # Remove obvious junk
    if re.search(r'^[\d@#$%^&*()]+$|^[a-z]$', term):
        return None
    
    return term

def is_meaningful_term(term):
    """Check if term is meaningful"""
    
    # Skip common English words
    very_common_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'up', 'about', 'into', 'during', 'before', 'after', 'such', 'than',
        'can', 'will', 'just', 'should', 'now', 'may', 'also', 'were', 'been'
    }
    
    if term in very_common_words:
        return False
    
    return True

# ============================================================================
# LAYER 3: CONTEXT WORDS
# ============================================================================

def extract_context_words(text):
    """Extract important context words"""
    
    important_context = [
        # Negation and qualification
        'without', 'not', 'no', 'unauthorized', 'improper', 'inadequate',
        'proper', 'adequate', 'appropriate', 'explicit', 'informed',
        
        # Location/transfer context
        'overseas', 'international', 'cross-border', 'foreign', 'domestic',
        
        # Time/manner context
        'immediately', 'promptly', 'delayed', 'failed', 'successful',
        
        # Severity/impact words
        'major', 'minor', 'significant', 'massive', 'widespread', 'limited'
    ]
    
    found_context = []
    for word in important_context:
        if re.search(r'\b' + word + r'\b', text):
            found_context.append(word)
    
    return found_context

# ============================================================================
# LAYER 4: ENTITIES AND DATA TYPES
# ============================================================================

def extract_entities_and_data_types(text):
    """Extract specific entities and data types"""
    
    entities = []
    
    # Specific data types mentioned
    data_type_patterns = [
        r'\b(email|emails)\b',
        r'\b(phone|telephone|mobile)\s*(number|numbers)?\b',
        r'\b(sms|text)\s*(messages?|marketing)?\b',
        r'\b(credit card|payment)\s*(information|data|details)?\b',
        r'\b(location|gps)\s*(data|information|history)?\b',
        r'\b(user\s+profiles?|customer\s+profiles?)\b',
        r'\b(behavioral|behaviour)\s*(analytics?|data)?\b',
        r'\b(biometric|fingerprint|facial)\s*(data|information)?\b',
        r'\b(health|medical|patient)\s*(records|information|data)\b',
        r'\b(financial|banking)\s*(information|data|records|statements)\b',
        r'\b(performance\s+appraisals?|performance\s+reviews?)\b',
        r'\b(account\s+balances?|bank\s+statements?)\b',
        r'\b(contact\s+information|contact\s+details)\b',
        r'\b(customer|client|patient|employee|alumni)\s*(information|data|records)?\b'
    ]
    
    for pattern in data_type_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                entity = ' '.join([m for m in match if m]).strip().lower()
            else:
                entity = match.strip().lower()
            
            # Apply length constraint: max 4 words
            if entity and len(entity) > 1 and len(entity.split()) <= 4:
                entities.append(entity)
    
    # Countries and places
    places = [
        'singapore', 'malaysia', 'thailand', 'indonesia', 'vietnam', 'philippines',
        'usa', 'america', 'europe', 'china', 'india', 'japan', 'korea', 'australia'
    ]
    
    for place in places:
        if re.search(r'\b' + place + r'\b', text):
            entities.append(place)
    
    # Organizations
    known_orgs = [
        'grab', 'shopee', 'lazada', 'gojek', 'foodpanda',
        'dbs', 'ocbc', 'uob', 'maybank', 'citibank',
        'google', 'facebook', 'microsoft', 'apple', 'amazon'
    ]
    
    for org in known_orgs:
        if re.search(r'\b' + org + r'\b', text):
            entities.append(org)
    
    return entities

# ============================================================================
# COMBINATION AND DEDUPLICATION
# ============================================================================

def balanced_combine_terms(keyword_terms, bert_terms, context_terms, entity_terms, original_query):
    """Combine terms with balanced deduplication"""
    
    # Combine all terms
    all_terms = keyword_terms + bert_terms + context_terms + entity_terms
    
    # Remove exact duplicates while preserving order
    unique_terms = []
    seen = set()
    for term in all_terms:
        if term not in seen and len(term.strip()) > 1:
            seen.add(term)
            unique_terms.append(term)
    
    # Smart deduplication
    deduplicated_terms = smart_deduplication(unique_terms)
    
    # Score and rank
    scored_terms = []
    for term in deduplicated_terms:
        score = calculate_balanced_score(term, original_query, keyword_terms, bert_terms)
        scored_terms.append((term, score))
    
    # Sort by score and return top 15 terms
    scored_terms.sort(key=lambda x: x[1], reverse=True)
    final_terms = [term for term, score in scored_terms[:15] if score > 0]
    
    return final_terms

def smart_deduplication(terms):
    """Remove obvious duplicates"""
    
    duplicate_groups = [
        ['email', 'emails', 'email address'],
        ['phone', 'phone number', 'telephone'],
        ['data', 'information'],
        ['company', 'organisation', 'organization'],
        ['customer', 'client'],
        ['records', 'record']
    ]
    
    final_terms = []
    used_groups = set()
    
    for term in terms:
        group_found = False
        for i, group in enumerate(duplicate_groups):
            if term in group and i not in used_groups:
                if i == 0:  # email group
                    final_terms.append('email')
                elif i == 1:  # phone group  
                    final_terms.append('phone number' if 'phone number' in group else 'phone')
                elif i == 2:  # data/information
                    final_terms.append('data')
                elif i == 3:  # company/org
                    final_terms.append('company')
                elif i == 4:  # customer/client
                    final_terms.append('customer')
                elif i == 5:  # records
                    final_terms.append('records')
                
                used_groups.add(i)
                group_found = True
                break
        
        if not group_found:
            final_terms.append(term)
    
    return final_terms

def calculate_balanced_score(term, original_query, keyword_terms, bert_terms):
    """Calculate term relevance score"""
    
    score = 0
    
    # Exact match bonus
    exact_matches = len(re.findall(r'\b' + re.escape(term) + r'\b', original_query))
    score += exact_matches * 3
    
    # Source bonuses
    if term in keyword_terms:
        score += 2
    if term in bert_terms:
        score += 2
    
    # High priority terms
    high_priority = ['personal data', 'consent', 'breach', 'without', 'unauthorized']
    if term in high_priority:
        score += 3
    
    # Data type bonus
    data_indicators = ['email', 'phone', 'records', 'information', 'data']
    if any(indicator in term for indicator in data_indicators):
        score += 1
    
    # Multi-word specificity bonus
    if len(term.split()) > 1:
        score += 1
    
    return score