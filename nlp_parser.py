# nlp_parser.py

"""
This module uses spaCy for basic NLP:
- Detecting intent (sales or purchase)
- Extracting entities like client (ORG) and location (GPE)
"""

try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
except Exception as e:
    print(f"[WARNING] spaCy could not be loaded: {e}")
    nlp = None

# -------------------------
# 🔍 Detect intent of message
# -------------------------
def detect_intent(text: str) -> str:
    """
    Tries to detect if the message is related to a sales or purchase entry.
    
    Returns:
        'sales_entry', 'purchase_entry', or 'unknown'
    """
    text_lower = text.lower()

    sales_keywords = ['sale', 'sold', 'order', 'dealt']
    purchase_keywords = ['purchase', 'bought', 'procured', 'acquired']

    if any(keyword in text_lower for keyword in sales_keywords):
        return 'sales_entry'
    elif any(keyword in text_lower for keyword in purchase_keywords):
        return 'purchase_entry'
    
    return 'unknown'

# -------------------------
# 🧠 Extract basic entities
# -------------------------
def extract_entities(text: str) -> dict:
    """
    Extracts key entities like client and location using spaCy NER.

    Returns:
        A dictionary with keys 'client' and 'location'
    """
    entities = {'client': None, 'location': None}

    if not nlp:
        return entities

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'ORG' and not entities['client']:
            entities['client'] = ent.text
        elif ent.label_ == 'GPE' and not entities['location']:
            entities['location'] = ent.text

    return entities
