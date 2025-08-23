# gemini_parser.py

"""
This module uses Google Gemini (via the gemini-2.5-flash model)
to extract structured JSON from natural language updates
sent by field staff in Telegram.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🛡️ Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 🤖 Initialize model
model = genai.GenerativeModel(model_name="gemini-2.5-flash")


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

# 🚀 Function to extract structured info from Gemini
def extract_with_gemini(text: str) -> dict | None:
    try:
        # Format the prompt with user message
        prompt = PROMPT_TEMPLATE.format(text=text)
        
        # Generate content
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

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
            return parsed
        else:
            print("[⚠️ WARNING] Missing one or more required fields:", parsed)
            return None

    except json.JSONDecodeError as je:
        print("[❌ ERROR] Invalid JSON returned by Gemini:", je)
        return None

    except Exception as e:
        print("[❌ ERROR] Gemini API call failed:", e)
        return None
