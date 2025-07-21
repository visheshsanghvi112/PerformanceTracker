import uuid
import datetime
from sheets import append_row
from config import ADMIN_IDS
from telegram import Update
from telegram.ext import ContextTypes
from gemini_parser import extract_with_gemini

# ✅ Validate Gemini-parsed entry
def is_valid_entry(entry):
    return (
        isinstance(entry, dict) and
        entry.get("client") and
        entry.get("orders") and
        entry.get("amount")
    )

# ✅ Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    # 1. Handle casual greetings
    casual_starts = ['hi', 'hello', 'hey', 'yo', 'good morning', 'good evening']
    if text.lower() in casual_starts or len(text.split()) < 3:
        await update.message.reply_text(
            "👋 Hello! Please select what you'd like to log:\n\n"
            "➡️ /sales\n➡️ /purchase"
        )
        return

    # 2. Get user's log type (sales or purchase)
    user_type = context.user_data.get('type')
    if not user_type:
        await update.message.reply_text("ℹ️ Please start by choosing /sales or /purchase.")
        return

    # 3. Try strict format parsing
    try:
        lines = text.split('\n')
        client = [l for l in lines if "Client" in l][0].split(":", 1)[1].strip()
        location = [l for l in lines if "Location" in l][0].split(":", 1)[1].strip()
        orders = int([l for l in lines if "Orders" in l][0].split(":")[1].strip())
        amount_line = [l for l in lines if "Amount" in l][0]
        amount_str = amount_line.split(":")[1].replace("₹", "").replace(",", "").strip()
        amount = int(amount_str)
        remarks = [l for l in lines if "Remarks" in l][0].split(":", 1)[1].strip()
    except Exception:
        # 🔁 Fallback to Gemini parser
        await update.message.reply_text("⚠️ Format not detected. Trying smart parser...")

        parsed = extract_with_gemini(text)
        if not parsed or not is_valid_entry(parsed):
            await update.message.reply_text(
                "❌ Could not understand the entry. Please try again with more details or use the format:\n\n"
                "Client: Apollo\nLocation: Bandra\nOrders: 3\nAmount: ₹24000\nRemarks: Good conversation"
            )
            return

        client = parsed.get("client")
        location = parsed.get("location")
        orders = parsed.get("orders")
        amount = parsed.get("amount")
        remarks = parsed.get("remarks") or text  # fallback to original message

    # 4. Log to Google Sheet
    now = datetime.datetime.now()
    entry_id = str(uuid.uuid4())[:8]
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M")

    row = [
        entry_id,       # Unique ID
        date_str,       # Date
        user.full_name, # Name
        user_type,      # Sales or Purchase
        client,
        location,
        orders,
        amount,
        remarks,
        user.id,        # Telegram ID
        time_str        # Timestamp
    ]
    append_row(row)

    # 5. Confirmation message
    await update.message.reply_text(
        f"✅ *{user_type} Logged!*\n\n"
        f"🧑 Name: {user.full_name}\n"
        f"📍 Client: {client}\n"
        f"📦 Orders: {orders}\n"
        f"💰 Amount: ₹{amount}\n"
        f"📝 Remarks: {remarks}\n"
        f"⏰ Time: {time_str}",
        parse_mode='Markdown'
    )
