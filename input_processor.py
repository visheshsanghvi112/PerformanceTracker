# input_processor.py
# 🧠 Unified input processing: validation, parsing, and fallback handling

import re
import string
import random
from typing import Tuple, List, Dict, Any, Optional
from logger import logger

class InputProcessor:
    """
    Unified input processor that handles:
    1. Input validation (gibberish detection)
    2. Business context validation  
    3. Fallback responses for unrecognized input
    """
    
    def __init__(self):
        # Business keywords for validation
        self.business_keywords = [
            'sold', 'sale', 'sales', 'buy', 'bought', 'purchase', 'client', 'customer',
            'amount', 'rupees', '₹', 'rs', 'money', 'payment', 'invoice', 'order',
            'units', 'items', 'products', 'goods', 'delivered', 'delivery', 'shipped',
            'apollo', 'pharmacy', 'medical', 'hospital', 'clinic', 'doctor',
            'today', 'yesterday', 'morning', 'evening', 'urgent', 'completed'
        ]
        
        # Gibberish patterns
        self.gibberish_patterns = [
            r'^[a-z]{1,3}$',                    # Too short (1-3 chars)
            r'^[qwxz]{3,}',                     # Uncommon letter clusters
            r'[aeiou]{4,}',                     # Too many vowels together
            r'[bcdfghjklmnpqrstvwxyz]{5,}',     # Too many consonants
            r'(.)\1{4,}',                       # Repeated characters (5+ times)
            r'^[^a-zA-Z]*$',                    # No letters at all
            r'[!@#$%^&*()]{3,}',               # Too many special chars
        ]
        
        # Casual conversation patterns (not business)
        self.casual_patterns = [
            r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bhow are you\b',
            r'\bweather\b', r'\bfeeling\b', r'\bgood morning\b',
            r'\bgood evening\b', r'\bthanks\b', r'\bthank you\b'
        ]
        
        # Structured format examples for fallback
        self.format_examples = [
            "Client: Apollo Pharmacy, Orders: 5, Amount: ₹25000",
            "Sold 10 units to MedCorp for ₹15000",
            "Purchase from XYZ supplier - 20 items - ₹8000",
            "Apollo - 3 boxes - ₹12000 - urgent delivery"
        ]
        
        logger.debug("🧠 InputProcessor initialized with unified validation and fallback")
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Complete input processing pipeline
        Returns: {
            'is_valid': bool,
            'reason': str,
            'suggestions': list,
            'should_use_ai': bool,
            'fallback_response': str (optional)
        }
        """
        logger.debug(f"🔍 Processing input: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Step 1: Basic validation
        is_valid, reason, suggestions = self._validate_input(text)
        
        if not is_valid:
            logger.debug(f"❌ Input failed validation: {reason}")
            return {
                'is_valid': False,
                'reason': reason,
                'suggestions': suggestions,
                'should_use_ai': False,
                'fallback_response': self._get_rejection_response(reason, suggestions)
            }
        
        # Step 2: Input is valid - should use AI
        logger.debug("✅ Input passed validation - ready for AI processing")
        return {
            'is_valid': True,
            'reason': 'valid_business_input',
            'suggestions': [],
            'should_use_ai': True,
            'fallback_response': None
        }
    
    def _validate_input(self, text: str) -> Tuple[bool, str, List[str]]:
        """Internal validation logic"""
        if not text or not text.strip():
            return False, "empty_input", ["Please type a message"]
        
        text_clean = text.strip().lower()
        
        # Check length
        if len(text_clean) < 3:
            return False, "too_short", ["Please provide more details about your transaction"]
        
        if len(text_clean) > 500:
            return False, "too_long", ["Please keep your message under 500 characters"]
        
        # Check for gibberish patterns
        for pattern in self.gibberish_patterns:
            if re.search(pattern, text_clean):
                return False, "gibberish_detected", [
                    "I couldn't understand that. Please describe your transaction clearly.",
                    "Example: 'Sold 5 units to Apollo Pharmacy for ₹25000'"
                ]
        
        # Check for casual conversation
        for pattern in self.casual_patterns:
            if re.search(pattern, text_clean):
                return False, "casual_conversation", [
                    "I'm here to help with business transactions.",
                    "Please describe a sale or purchase transaction."
                ]
        
        # Check for business context
        has_business_context = any(keyword in text_clean for keyword in self.business_keywords)
        has_numbers = bool(re.search(r'\d+', text))
        
        if not has_business_context and not has_numbers:
            return False, "no_business_context", [
                "Please include business details like client name, amount, or quantity.",
                "Example: 'Apollo Pharmacy - 5 units - ₹25000'"
            ]
        
        return True, "valid", []
    
    def _get_rejection_response(self, reason: str, suggestions: List[str]) -> str:
        """Generate user-friendly rejection response"""
        responses = {
            "empty_input": "Please type a message to get started! 📝",
            "too_short": "Could you provide more details about your transaction? 🤔",
            "too_long": "That message is quite long! Please keep it concise. ✂️",
            "gibberish_detected": "I couldn't understand that message. Let me help you format it properly! 🤖",
            "casual_conversation": "Hi there! I'm here to help with business transactions. 💼",
            "no_business_context": "I need more business details to help you. 📊"
        }
        
        base_response = responses.get(reason, "I need help understanding your message. 🤔")
        
        if suggestions:
            suggestion_text = "\n\n💡 Try something like:\n" + suggestions[0]
            if len(suggestions) > 1:
                suggestion_text += f"\n\n📋 Format examples:\n{random.choice(self.format_examples)}"
            return base_response + suggestion_text
        
        return base_response
    
    def get_fallback_response(self, text: str) -> str:
        """
        Generate fallback response for valid input that couldn't be parsed by AI
        """
        logger.debug(f"🔄 Generating fallback response for: '{text[:30]}...'")
        
    def get_parsing_failure_response(self, user_type: str = "sales") -> str:
        """
        Generate response for parsing failures with structured format help
        """
        logger.debug(f"🔄 Generating parsing failure response for {user_type}")
        
        base_response = (
            "🔧 **Unable to parse your message automatically.**\n\n"
            "📋 Please use this format:\n"
            "```\n"
            "Client: [Customer Name]\n"
            "Location: [Area/City]\n"
            "Orders: [Number of items]\n"
            "Amount: [₹Amount]\n"
            "Remarks: [Any additional notes]\n"
            "```\n\n"
            "💡 Example:\n"
            "`Client: Apollo Pharmacy\n"
            "Location: Mumbai\n"
            "Orders: 5\n"
            "Amount: ₹5000\n"
            "Remarks: Regular order`"
        )
        
        return base_response
        
        response = """I understand you're trying to record a transaction, but I need it in a clearer format.

📋 **Please use this structure:**
Client: [Company Name]
Orders: [Number of units]  
Amount: ₹[Total amount]
Remarks: [Any notes]

💡 **Or try a simple format like:**
• "Sold 5 units to Apollo for ₹25000"
• "Purchase from MedCorp - 10 boxes - ₹15000"

🤖 This helps me process your transaction accurately!"""
        
        return response
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parsed data for security"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove dangerous characters
                clean_value = re.sub(r'[<>"\';]', '', str(value))
                clean_value = clean_value.strip()[:200]  # Limit length
                sanitized[key] = clean_value
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                if key in ['amount', 'orders'] and (value < 0 or value > 1000000):
                    logger.warning(f"⚠️ Suspicious numeric value for {key}: {value}")
                    sanitized[key] = 0
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        
        return sanitized


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_entry(entry_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Quick entry validation function for compatibility with handlers.py
    Returns sanitized data and list of warnings
    """
    warnings = []
    sanitized_data = {}
    
    # Basic sanitization and validation
    for key, value in entry_data.items():
        if key in ['amount', 'orders']:
            try:
                if value is None or value == '':
                    sanitized_data[key] = 0
                    warnings.append(f"Missing {key}, defaulting to 0")
                else:
                    num_val = float(str(value))
                    if num_val < 0:
                        warnings.append(f"Negative {key} value: {num_val}")
                    sanitized_data[key] = num_val
            except (ValueError, TypeError):
                sanitized_data[key] = 0
                warnings.append(f"Invalid {key} value: {value}, defaulting to 0")
        else:
            # Text fields
            if value is None:
                sanitized_data[key] = ""
                warnings.append(f"Missing {key}")
            else:
                sanitized_data[key] = str(value).strip()
                if len(sanitized_data[key]) == 0 and key in ['client', 'location']:
                    warnings.append(f"Empty {key} field")
    
    return sanitized_data, warnings


# Global instance
input_processor = InputProcessor()
