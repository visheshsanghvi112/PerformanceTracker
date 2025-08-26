import uuid
import datetime
import re
from sheets import append_row
from config import ADMIN_IDS
from telegram import Update
from telegram.ext import ContextTypes
from gemini_parser import extract_with_gemini
from input_processor import input_processor, validate_entry, ValidationError
from error_handler import handle_error, handle_validation_error, handle_api_error, handle_database_error
from decorators import rate_limit, handle_errors, measure_time
from logger import logger
from company_manager import company_manager
from multi_company_sheets import multi_sheet_manager

def parse_orders_value(orders_str: str) -> int:
    """
    📊 Enhanced orders parser - handles multiple formats:
    - Simple numbers: "5" → 5
    - Addition: "3 + 5" → 8
    - With text: "3 boxes + 5 bottles" → 8
    - Complex: "10 tablets + 5 injections + 2 syringes" → 17
    """
    try:
        # Remove common words and clean the string
        cleaned = orders_str.lower().strip()
        
        # Extract all numbers from the string
        numbers = re.findall(r'\d+', cleaned)
        
        if not numbers:
            return 0  # No numbers found
        
        # If contains '+' or 'and', sum all numbers
        if '+' in cleaned or ' and ' in cleaned or ',' in cleaned:
            total = sum(int(num) for num in numbers)
            logger.debug(f"📊 Parsed multiple orders '{orders_str}' → {total}")
            return total
        else:
            # Single number
            result = int(numbers[0])
            logger.debug(f"📊 Parsed single order '{orders_str}' → {result}")
            return result
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to parse orders '{orders_str}': {e}")
        return int(orders_str)  # Fallback to original parsing

# ✅ Validate Gemini-parsed entry
def is_valid_entry(entry):
    return (
        isinstance(entry, dict) and
        entry.get("client") and
        entry.get("orders") and
        entry.get("amount")
    )

# ✅ Main message handler with comprehensive error handling
@rate_limit(calls_per_minute=15)
@handle_errors(notify_user=True)
@measure_time()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        text = update.message.text.strip()
        
        # Log incoming message details
        logger.info(f"📨 Message received from user {user.id} ({user.username or user.first_name}): '{text[:50]}{'...' if len(text) > 50 else ''}'")
        logger.debug(f"🔍 Full message content: '{text}'")
        logger.debug(f"👤 User details: ID={user.id}, Username={user.username}, Name={user.first_name} {user.last_name or ''}")

        # 0. Check if user is registered with a company
        if not company_manager.is_user_registered(user.id):
            logger.warning(f"🚫 Unregistered user {user.id} attempting to use bot")
            await update.message.reply_text(
                "🏢 **Company Registration Required**\n\n"
                "To use this bot, you must first select your company.\n\n"
                "💡 Use `/company` to get started!"
            )
            return

        # 1. Handle casual greetings
        casual_starts = ['hi', 'hello', 'hey', 'yo', 'good morning', 'good evening']
        if text.lower() in casual_starts or len(text.split()) < 3:
            logger.info(f"💬 Responding to casual greeting from user {user.id}")
            current_company = company_manager.get_user_company(user.id)
            company_info = company_manager.get_company_info(current_company)
            await update.message.reply_text(
                f"👋 Hello! Welcome to {company_info['display_name']}!\n\n"
                "Please select what you'd like to log:\n\n"
                "➡️ /sales\n➡️ /purchase"
            )
            return

        # 2. Get user's log type (sales or purchase)
        user_type = context.user_data.get('type')
        if not user_type:
            logger.warning(f"⚠️ User {user.id} hasn't selected log type yet")
            await update.message.reply_text("ℹ️ Please start by choosing /sales or /purchase.")
            return
        
        logger.info(f"📊 Processing {user_type} entry for user {user.id}")

        # 2.5. Process input through unified processor
        process_result = input_processor.process_input(text)
        
        if not process_result['is_valid']:
            logger.warning(f"🚫 Invalid input detected for user {user.id}: {process_result['reason']}")
            logger.debug(f"🔍 Rejected text: '{text}'")
            
            # Send the fallback response from processor
            await update.message.reply_text(process_result['fallback_response'], parse_mode='Markdown')
            return

        # 3. Try strict format parsing
        entry_data = {}
        try:
            logger.debug(f"🔄 Attempting strict format parsing for user {user.id}")
            lines = text.split('\n')
            client = [l for l in lines if "Client" in l][0].split(":", 1)[1].strip()
            location = [l for l in lines if "Location" in l][0].split(":", 1)[1].strip()
            
            # 📊 Enhanced Orders parsing - handle multiple formats
            orders_line = [l for l in lines if "Orders" in l][0].split(":", 1)[1].strip()
            orders = parse_orders_value(orders_line)
            
            amount_line = [l for l in lines if "Amount" in l][0]
            amount_str = amount_line.split(":")[1].replace("₹", "").replace(",", "").strip()
            amount = int(amount_str)
            remarks = [l for l in lines if "Remarks" in l][0].split(":", 1)[1].strip()
            
            entry_data = {
                'client': client,
                'location': location,
                'orders': orders,
                'amount': amount,
                'remarks': remarks,
                'type': user_type,
                'date': datetime.datetime.now()
            }
            logger.info(f"✅ Strict format parsing successful for user {user.id}: {entry_data}")
            
        except Exception as parse_error:
            logger.warning(f"⚠️ Strict format parsing failed for user {user.id}: {str(parse_error)}")
            # 🔁 Fallback to Gemini parser (input already validated above)
            await update.message.reply_text("⚠️ Format not detected. Trying smart parser...")
            logger.info(f"🤖 Initiating Gemini AI parsing for user {user.id} (input pre-validated)")
            
            try:
                parsed = extract_with_gemini(text)
                if not parsed or not is_valid_entry(parsed):
                    logger.error(f"❌ Gemini parsing failed or invalid data for user {user.id}: {parsed}")
                    # Since input was pre-validated, provide structured format help
                    response = input_processor.get_parsing_failure_response(user_type)
                    await update.message.reply_text(response, parse_mode='Markdown')
                    
                    # Log the unrecognized input for analysis
                    logger.warning(f"🔍 Unrecognized valid input from user {user.id}: '{text}'")
                    return

                entry_data = {
                    'client': parsed.get("client"),
                    'location': parsed.get("location"), 
                    'orders': parsed.get("orders"),
                    'amount': parsed.get("amount"),
                    'remarks': parsed.get("remarks") or text,
                    'type': user_type,
                    'date': datetime.datetime.now()
                }
                logger.info(f"✅ Gemini parsing successful for user {user.id}: {entry_data}")
                
            except Exception as gemini_error:
                logger.error(f"❌ Gemini parsing exception for user {user.id}: {str(gemini_error)}")
                # AI service is down, provide manual entry guidance
                response = (
                    "🔧 **AI parsing service is temporarily unavailable.**\n\n"
                    f"{input_processor.get_parsing_failure_response(user_type)}\n\n"
                    "🔄 **You can also try again in a few minutes.**"
                )
                await update.message.reply_text(response, parse_mode='Markdown')
                return

        # 4. Validate the entry data (rest remains the same...)
        try:
            logger.debug(f"🔍 Validating entry data for user {user.id}: {entry_data}")
            validated_data, warnings = validate_entry(entry_data)
            
            if warnings:
                logger.warning(f"⚠️ Validation warnings for user {user.id}: {warnings}")
                warning_text = "⚠️ **Warnings:**\n" + "\n".join(f"• {w}" for w in warnings)
                warning_text += "\n\nProceed anyway? The entry will be saved."
                await update.message.reply_text(warning_text, parse_mode='Markdown')
            else:
                logger.info(f"✅ Entry validation passed for user {user.id}")
            
        except ValidationError as ve:
            logger.error(f"❌ Validation error for user {user.id}: {str(ve)}")
            await handle_validation_error(ve, update)
            return

        # 5. Log to Google Sheet
        now = datetime.datetime.now()
        entry_id = str(uuid.uuid4())[:8]
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H:%M")

        row = [
            entry_id,                           # Unique ID
            date_str,                          # Date
            user.full_name,                    # Name
            validated_data['type'],            # Sales or Purchase
            validated_data['client'],
            validated_data['location'],
            validated_data['orders'],
            validated_data['amount'],
            validated_data.get('remarks', ''),
            user.id,                           # Telegram ID
            time_str                           # Timestamp
        ]
        
        logger.info(f"💾 Preparing to save entry {entry_id} for user {user.id} to database")
        logger.debug(f"📄 Row data: {row}")
        
        # Try to save to company-specific sheet
        try:
            logger.info(f"🔄 Attempting to save entry {entry_id} to company sheet...")
            current_company = company_manager.get_user_company(user.id)
            success = multi_sheet_manager.append_row(row, current_company)
            if not success:
                logger.error(f"❌ Company sheet save failed for entry {entry_id}")
                raise Exception("Failed to save to company sheet")
            logger.info(f"✅ Successfully saved entry {entry_id} to {current_company} sheet")
                
        except Exception as db_error:
            logger.error(f"❌ Database error for entry {entry_id}: {str(db_error)}")
            await handle_database_error(db_error, update, validated_data)
            return

        # 6. Confirmation message
        logger.info(f"📤 Sending confirmation message to user {user.id} for entry {entry_id}")
        await update.message.reply_text(
            f"✅ *{validated_data['type']} Logged Successfully!*\n\n"
            f"🧑 Name: {user.full_name}\n"
            f"📍 Client: {validated_data['client']}\n"
            f"🏢 Location: {validated_data['location']}\n"
            f"📦 Orders: {validated_data['orders']}\n"
            f"💰 Amount: ₹{validated_data['amount']:,}\n"
            f"📝 Remarks: {validated_data.get('remarks', 'None')}\n"
            f"⏰ Time: {time_str}\n"
            f"🆔 Entry ID: {entry_id}",
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Entry logged successfully for user {user.id}: {entry_id} - Amount: ₹{validated_data['amount']:,}")
        logger.info(f"📊 Transaction summary - User: {user.id}, Type: {validated_data['type']}, Client: {validated_data['client']}, Amount: ₹{validated_data['amount']:,}")
        
    except Exception as e:
        await handle_error(e, update, context)
