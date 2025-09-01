import uuid
import datetime
import re
# from sheets import append_row  # Replaced by multi_company_sheets
from config import ADMIN_IDS
from telegram import Update
from telegram.ext import ContextTypes
from gemini_parser import extract_with_gemini
from ai_response_engine import ai_response_engine
from input_processor import input_processor, validate_entry, ValidationError
from error_handler import handle_error, handle_validation_error, handle_api_error, handle_database_error
from decorators import rate_limit, handle_errors, measure_time
from input_processor import input_processor
from logger import logger
from company_manager import company_manager
from multi_company_sheets import multi_sheet_manager
from location_handler import location_handler
from ai_response_engine import ai_response_engine
from batch_handler import batch_handler

def detect_company_switch_intent(text: str) -> bool:
    """
    🔍 Fallback company switching intent detection using keywords.
    Used when AI intent analysis is unavailable or fails.
    
    Args:
        text (str): User message text to analyze
        
    Returns:
        bool: True if company switching intent is detected
    """
    try:
        # Normalize text for analysis
        text_lower = text.lower().strip()
        
        # Primary company switching keywords
        company_keywords = [
            'change company', 'switch company', 'select company',
            'company change', 'company switch', 'different company',
            'another company', 'new company', 'other company',
            'i want to change company', 'want to switch company',
            'can i change company', 'how to change company',
            'change my company', 'switch my company'
        ]
        
        # Check for exact keyword matches
        for keyword in company_keywords:
            if keyword in text_lower:
                logger.info(f"🎯 Company switch intent detected via keyword: '{keyword}'")
                return True
        
        # Check for pattern-based matches
        patterns = [
            r'\b(change|switch|select)\s+(to\s+)?(company|companies)\b',
            r'\b(company)\s+(change|switch|selection)\b',
            r'\bi\s+want\s+to\s+(change|switch)\s+company\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                logger.info(f"🎯 Company switch intent detected via pattern: '{pattern}'")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in company switch intent detection: {e}")
        return False

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

        # 0.5. Check for company switching intent (fallback detection)
        if detect_company_switch_intent(text):
            logger.info(f"🏢 Company switching intent detected for user {user.id}")
            
            # Import company menu functionality
            from company_commands import show_company_switching_menu
            
            try:
                await show_company_switching_menu(update, context)
                return
            except Exception as menu_error:
                logger.error(f"❌ Failed to show company menu for user {user.id}: {menu_error}")
                await update.message.reply_text(
                    "🏢 **Company Selection**\n\n"
                    "I detected you want to change companies! Use `/company` to see available options.\n\n"
                    "💡 **Available Commands:**\n"
                    "• `/company` - Select your company\n"
                    "• `/admin` - Admin panel (if you're an admin)"
                )
                return

        # 1. Handle casual conversation with REAL AI intelligence
        casual_conversation_patterns = [
            'it is evening', 'this is evening', 'good evening', 'evening time',
            'it is morning', 'this is morning', 'morning time', 
            'it is afternoon', 'this is afternoon', 'afternoon time',
            'what time', 'current time', 'time now', 'how are you',
            'thank you', 'thanks', 'bye', 'goodbye', 'see you',
            'weather', 'how is everything', 'all good', 'fine',
            'nice', 'great', 'cool', 'awesome', 'perfect',
            'busy', 'tired', 'good day', 'bad day', 'working'
        ]
        
        text_lower = text.lower()
        is_casual_conversation = any(pattern in text_lower for pattern in casual_conversation_patterns)
        
        # Also detect short conversational messages
        if not is_casual_conversation and len(text.split()) <= 5:
            # Check if it's not business data (no numbers, amounts, or business keywords)
            business_indicators = ['sold', 'bought', 'purchase', 'client', 'pharmacy', 'hospital', '₹', 'rupees', 'amount']
            has_business_indicators = any(indicator in text_lower for indicator in business_indicators)
            if not has_business_indicators and not text.lower().startswith('/'):
                is_casual_conversation = True
        
        if is_casual_conversation:
            logger.info(f"🤖 Using REAL AI for casual conversation from user {user.id}: {text}")
            
            # Use Gemini AI for truly intelligent conversation with memory
            try:
                ai_response = ai_response_engine.generate_intelligent_conversation(
                    text, 
                    user.id,  # User ID for conversation memory
                    user.first_name, 
                    context="casual_chat"
                )
                logger.info(f"✅ Generated intelligent AI response with memory for casual conversation")
                await update.message.reply_text(ai_response)
                return
            except Exception as e:
                logger.error(f"❌ AI conversation failed, using fallback: {e}")
                # Fallback to simple response
                await update.message.reply_text(
                    f"Thanks for chatting {user.first_name}! 😊 I'm here to help with your business tracking needs. "
                    "Try `/sales` or `/purchase` when you're ready!"
                )
                return

        # 2. Get user's log type (sales or purchase)
        user_type = context.user_data.get('type')
        if not user_type:
            logger.warning(f"⚠️ User {user.id} hasn't selected log type yet")
            await update.message.reply_text("ℹ️ Please start by choosing /sales or /purchase.")
            return
        
        logger.info(f"📊 Processing {user_type} entry for user {user.id}")

        # 2.5. Check for batch processing
        if batch_handler.detect_batch_input(text):
            logger.info(f"📦 Batch input detected for user {user.id}")
            await update.message.reply_text("📦 **Batch Processing Detected**\n\nProcessing multiple entries with AI...")
            
            batch_result = await batch_handler.process_batch_entries(update, context, text, user_type)
            response = batch_handler.format_batch_response(batch_result)
            
            # Add AI success message for batch processing
            if batch_result['success']:
                ai_success = ai_response_engine.generate_success_response(user_type, {
                    'amount': sum(entry['data']['amount'] for entry in batch_result.get('saved_entries', [])),
                    'batch_size': batch_result['processed']
                })
                response += f"\n\n{ai_success}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            return

        # 2.6. Process input through unified processor
        process_result = input_processor.process_input(text)
        
        if not process_result['is_valid']:
            logger.warning(f"🚫 Invalid input detected for user {user.id}: {process_result['reason']}")
            logger.debug(f"🔍 Rejected text: '{text}'")
            
            # Generate AI-powered error response
            ai_error_response = ai_response_engine.generate_error_response('parsing_failed', {
                'reason': process_result['reason'],
                'user_type': user_type
            })
            
            await update.message.reply_text(ai_error_response, parse_mode='Markdown')
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

        # 3.5. Keep original location from AI parsing (business location)
        # Do NOT modify the location field with GPS data
        current_company = company_manager.get_user_company(user.id)
        gps_location_str = location_handler.get_location_for_entry(str(user.id), current_company)
        
        # GPS location will be used only for live position, not for business location
        if gps_location_str:
            logger.info(f"📍 GPS location available for user {user.id}: {gps_location_str}")
        
        # 3.6. Add live position data if available (SEPARATE from business location)
        from live_position_handler import live_position_handler
        live_position_str = live_position_handler.get_live_position_for_entry(str(user.id), current_company)
        
        # Store live position separately (will be added to Live_Position column)
        entry_data['live_position'] = live_position_str if live_position_str else ''
        
        if live_position_str:
            logger.info(f"📍 Enhanced entry with live position for user {user.id}: {live_position_str}")
        
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
            time_str,                          # Timestamp
            current_company,                   # Company
            datetime.datetime.now().isoformat(), # Entry Timestamp
            datetime.datetime.now().isoformat(), # Last Modified
            validated_data.get('live_position', '') # Live Position (column 15)
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

        # 7. AI-Enhanced Confirmation message
        logger.info(f"📤 Sending AI-enhanced confirmation message to user {user.id} for entry {entry_id}")
        
        # Generate AI success response
        ai_success_message = ai_response_engine.generate_success_response(validated_data['type'], validated_data)
        
        confirmation_message = (
            f"{ai_success_message}\n\n"
            f"📋 **ENTRY DETAILS:**\n"
            f"🧑 Name: {user.full_name}\n"
            f"📍 Client: {validated_data['client']}\n"
            f"🏢 Location: {validated_data['location']}\n"
            f"📦 Orders: {validated_data['orders']}\n"
            f"💰 Amount: ₹{validated_data['amount']:,}\n"
            f"📝 Remarks: {validated_data.get('remarks', 'None')}\n"
            f"⏰ Time: {time_str}\n"
            f"🆔 Entry ID: {entry_id}"
        )
        
        # Add GPS enhancement note only if GPS data was available (but not mixed with business location)
        if gps_location_str:
            confirmation_message += f"\n\n📍 **GPS Enhanced:** Your current location tracked separately for analysis"
        
        # Add live position note if live position was included
        if live_position_str:
            confirmation_message += f"\n\n📍 **Live Position:** {live_position_str}"
        
        await update.message.reply_text(confirmation_message, parse_mode='Markdown')
        
        # Send additional AI tip occasionally
        if validated_data['amount'] > 20000:  # High-value transaction
            tip = ai_response_engine.generate_tip_of_the_day()
            await update.message.reply_text(f"💡 {tip}", parse_mode='Markdown')
        
        logger.info(f"✅ Entry logged successfully for user {user.id}: {entry_id} - Amount: ₹{validated_data['amount']:,}")
        logger.info(f"📊 Transaction summary - User: {user.id}, Type: {validated_data['type']}, Client: {validated_data['client']}, Amount: ₹{validated_data['amount']:,}")
        
    except Exception as e:
        await handle_error(e, update, context)
