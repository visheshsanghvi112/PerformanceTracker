# gemini_parser.py

"""
This module uses Google Gemini (via the gemini-2.5-flash model)
to extract structured JSON from natural language updates
sent by field staff in Telegram.

Enhanced with multi-API key support for parallel processing.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from typing import List, Optional
import random
from logger import logger

# 🔐 Load environment variables
load_dotenv()

# 🔑 Support multiple API keys for parallel processing
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

# 🔑 Smart API key allocation strategy
API_KEY_CONFIG = {
    "primary": os.getenv("GEMINI_API_KEY"),        # Heavy parsing & transactions
    "secondary": os.getenv("GEMINI_API_KEY_2"),    # Casual chat & conversation
    "tertiary": os.getenv("GEMINI_API_KEY_3")      # Commands & analytics
}

# Filter out None values and create organized structure
API_KEYS = {}
MODELS = {}

for key_type, api_key in API_KEY_CONFIG.items():
    if api_key:
        API_KEYS[key_type] = api_key
        # Configure and create model for this key
        genai.configure(api_key=api_key)
        MODELS[key_type] = genai.GenerativeModel(model_name="gemini-2.5-flash")
        print(f"✅ {key_type.title()} model initialized with key ending in ...{api_key[-4:]}")

if not API_KEYS:
    raise ValueError("❌ No Gemini API keys found. Please set GEMINI_API_KEY in your .env file")

print(f"🔑 Loaded {len(API_KEYS)} specialized Gemini API keys for optimal performance")

class SmartGeminiManager:
    """🧠 Intelligent API key manager with task-specific allocation"""
    
    def __init__(self):
        self.models = MODELS
        self.usage_stats = {key: {"calls": 0, "errors": 0} for key in API_KEYS.keys()}
        self.task_allocation = {
            "transaction_parsing": "primary",      # Back to primary for parsing (fresh key)
            "casual_chat": "secondary",            # Casual conversation
            "command_processing": "tertiary",      # Commands & analytics
            "batch_processing": "all"              # Use all 3 working keys
        }
    
    def get_model_for_task(self, task_type: str = "transaction_parsing"):
        """Get optimal model based on task type with health checking"""
        from smart_rate_limiter import rate_limiter
        
        preferred_key = self.task_allocation.get(task_type, "secondary")
        
        # Check if preferred key is available and healthy
        if preferred_key in self.models and rate_limiter.can_use_key(preferred_key):
            self.usage_stats[preferred_key]["calls"] += 1
            return self.models[preferred_key], preferred_key
        
        # Find any available healthy key
        for key_type, model in self.models.items():
            if rate_limiter.can_use_key(key_type):
                self.usage_stats[key_type]["calls"] += 1
                logger.info(f"🔄 Using {key_type} key as fallback for {task_type}")
                return model, key_type
        
        # If no keys are available, use secondary as last resort
        logger.warning(f"⚠️ No healthy keys available, using secondary as fallback")
        self.usage_stats["secondary"]["calls"] += 1
        return self.models["secondary"], "secondary"
        
        raise Exception("No API keys available")
    
    def get_all_models(self) -> List[tuple]:
        """Get all available models for parallel processing"""
        return [(model, key_type) for key_type, model in self.models.items()]
    
    async def generate_content_specialized(self, prompt: str, task_type: str = "transaction_parsing") -> str:
        """Generate content using task-specific API key with rate limiting"""
        try:
            # Import rate limiter
            from smart_rate_limiter import rate_limiter
            
            model, key_used = self.get_model_for_task(task_type)
            
            # Check rate limiting
            if not rate_limiter.can_use_key(key_used):
                # Try to find an alternative key
                available_keys = rate_limiter.get_available_keys()
                if available_keys:
                    alternative_key = available_keys[0]
                    model = self.models[alternative_key]
                    key_used = alternative_key
                    logger.info(f"🔄 Switched to {key_used} due to rate limiting")
                else:
                    raise Exception("All API keys are rate limited")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, model.generate_content, prompt)
            
            # Record successful request
            rate_limiter.record_request(key_used, True)
            self.usage_stats[key_used]["calls"] += 1
            
            logger.info(f"✅ Used {key_used} key for {task_type}")
            return response.text
            
        except Exception as e:
            # Record failed request
            if 'key_used' in locals():
                rate_limiter.record_request(key_used, False, str(e))
                self.usage_stats[key_used]["errors"] += 1
            
            raise Exception(f"API call failed with {key_used if 'key_used' in locals() else 'unknown'}: {str(e)}")
    
    async def generate_content_parallel_smart(self, prompts: List[str], task_type: str = "batch_processing") -> List[str]:
        """🚀 Smart parallel processing using all available keys"""
        if len(prompts) == 1:
            result = await self.generate_content_specialized(prompts[0], task_type)
            return [result]
        
        # Get all available models
        available_models = self.get_all_models()
        
        if not available_models:
            raise Exception("No API keys available for processing")
        
        # Distribute prompts across available models
        tasks = []
        for i, prompt in enumerate(prompts):
            model, key_type = available_models[i % len(available_models)]
            task = asyncio.create_task(self._generate_with_key(model, prompt, key_type))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"Error: {str(result)}")
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _generate_with_key(self, model, prompt: str, key_type: str) -> str:
        """Generate content with specific model and track usage"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, model.generate_content, prompt)
            self.usage_stats[key_type]["calls"] += 1
            return response.text
        except Exception as e:
            self.usage_stats[key_type]["errors"] += 1
            raise Exception(f"API call failed with {key_type}: {str(e)}")
    
    def get_usage_stats(self) -> dict:
        """Get detailed usage statistics for all API keys"""
        return {
            "keys_configured": len(self.models),
            "task_allocation": self.task_allocation,
            "usage_stats": self.usage_stats,
            "parallel_capable": len(self.models) > 1
        }

# 🌍 Global smart API manager instance
smart_api_manager = SmartGeminiManager()


# 📝 Instruction template
PROMPT_TEMPLATE = """
You are an intelligent assistant for a pharmaceutical company's internal sales and purchase tracking bot. 

Your task is to extract structured information from unstructured or casually written human messages.

---
🔍 CONTEXT:
Field staff send updates via Telegram. These can be messy, semi-structured, or casual language.

Extract values for the following schema:
{{
  "client": "Name of the pharmacy or vendor, e.g. Apollo Pharmacy",
  "location": "Area of sale/purchase, e.g. Chembur",
  "orders": Number of total items/units (e.g. 8 if '3 boxes + 5 bottles'),
  "amount": Numeric value of amount in INR (e.g. ₹24000), strip currency and commas,
  "remarks": Exact text from user (no paraphrasing)
}}

---
📌 IMPORTANT RULES:
1. Respond ONLY with the JSON. No text before/after.
2. If a field is missing, assign `null`.
3. Do NOT assume. Only extract what's mentioned.
4. Format numbers properly (e.g., ₹24,000 → 24000).
5. For ORDERS: If multiple items mentioned (e.g., "3 boxes + 5 bottles"), sum them up to single number (8).
6. For ORDERS: If unclear quantities like "some tablets", use `null`.
7. No code blocks, markdown, or explanation. Just clean JSON.

---
💡 EXAMPLES:
Input: "Sold 3 boxes of paracetamol and 5 bottles of syrup to Apollo for ₹25000"
Output: {{"client": "Apollo", "location": null, "orders": 8, "amount": 25000, "remarks": "Sold 3 boxes of paracetamol and 5 bottles of syrup to Apollo for ₹25000"}}

Input: "Client: XYZ Hospital, Location: Mumbai, Orders: 10 tablets + 5 injections, Amount: ₹15000, Remarks: urgent delivery"
Output: {{"client": "XYZ Hospital", "location": "Mumbai", "orders": 15, "amount": 15000, "remarks": "urgent delivery"}}
```

---
✉️ Message:
{text}

---
✅ Output:
"""

# 🚀 Enhanced functions with multi-API key support
# 🚀 Enhanced functions with smart API key allocation
def extract_with_gemini(text: str) -> dict | None:
    """Extract structured info using optimal API key with rate limiting"""
    try:
        # Import rate limiter
        from smart_rate_limiter import rate_limiter
        
        # Format the prompt with user message
        prompt = PROMPT_TEMPLATE.format(text=text)
        
        # Use smart manager for transaction parsing with rate limiting
        model, key_used = smart_api_manager.get_model_for_task("transaction_parsing")
        
        # Check rate limiting
        if not rate_limiter.can_use_key(key_used):
            # Try to find an alternative key
            available_keys = rate_limiter.get_available_keys()
            if available_keys:
                alternative_key = available_keys[0]
                model = smart_api_manager.models[alternative_key]
                key_used = alternative_key
                logger.info(f"🔄 Switched to {key_used} due to rate limiting")
            else:
                logger.warning("🚫 All API keys are rate limited")
                return None
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Record successful request
        rate_limiter.record_request(key_used, True)

        # 🧹 Clean the output if wrapped in ```json or similar
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").strip()
            if raw_text.lower().startswith("json"):
                raw_text = raw_text[4:].strip()

        # 🧪 Try parsing the JSON output
        parsed = json.loads(raw_text)

        # ✅ Validate essential keys
        required_keys = {"client", "location", "orders", "amount", "remarks"}
        if required_keys.issubset(parsed.keys()):
            logger.info(f"✅ Transaction parsed successfully using {key_used} key")
            return parsed
        else:
            print("[⚠️ WARNING] Missing one or more required fields:", parsed)
            return None

    except json.JSONDecodeError as je:
        print("[❌ ERROR] Invalid JSON returned by Gemini:", je)
        if 'key_used' in locals():
            rate_limiter.record_request(key_used, False, str(je))
        return None

    except Exception as e:
        print("[❌ ERROR] Gemini API call failed:", e)
        if 'key_used' in locals():
            rate_limiter.record_request(key_used, False, str(e))
        return None

async def extract_with_gemini_parallel(texts: List[str]) -> List[Optional[dict]]:
    """
    🚀 Extract structured info from multiple texts in parallel
    Uses all available API keys for maximum throughput
    """
    try:
        if not texts:
            return []
        
        if len(texts) == 1:
            # Single text - use regular function
            result = extract_with_gemini(texts[0])
            return [result]
        
        print(f"🚀 Processing {len(texts)} texts in parallel using {len(API_KEYS)} API keys")
        
        # Create prompts for all texts
        prompts = [PROMPT_TEMPLATE.format(text=text) for text in texts]
        
        # Process in parallel using API manager
        # 🚀 Use smart parallel processing
        responses = await smart_api_manager.generate_content_parallel_smart(prompts, "batch_processing")
        
        # Parse all responses
        results = []
        for i, raw_text in enumerate(responses):
            try:
                if raw_text.startswith("Error:"):
                    print(f"❌ API error for text {i+1}: {raw_text}")
                    results.append(None)
                    continue
                
                # Clean response
                if raw_text.startswith("```"):
                    raw_text = raw_text.strip("`").strip()
                    if raw_text.lower().startswith("json"):
                        raw_text = raw_text[4:].strip()
                
                # Parse JSON
                parsed = json.loads(raw_text)
                
                # Validate required keys
                required_keys = {"client", "location", "orders", "amount", "remarks"}
                if required_keys.issubset(parsed.keys()):
                    results.append(parsed)
                else:
                    print(f"[⚠️ WARNING] Text {i+1} missing required fields:", parsed)
                    results.append(None)
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error for text {i+1}: {e}")
                results.append(None)
        
        successful_parses = sum(1 for r in results if r is not None)
        print(f"✅ Successfully parsed {successful_parses}/{len(texts)} texts in parallel")
        
        return results
        
    except Exception as e:
        print(f"❌ Parallel extraction error: {e}")
        return [None] * len(texts)

def get_api_status() -> dict:
    """Get comprehensive status of all configured API keys"""
    usage_stats = smart_api_manager.get_usage_stats()
    return {
        "total_keys": len(API_KEYS),
        "active_models": len(MODELS),
        "parallel_capable": len(API_KEYS) > 1,
        "key_allocation": smart_api_manager.task_allocation,
        "usage_statistics": usage_stats["usage_stats"]
    }
