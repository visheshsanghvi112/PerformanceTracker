"""
🏢 COMPANY SELECTION & ADMIN COMMANDS
===================================
Handle company selection, switching, and admin management
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from company_manager import company_manager
from multi_company_sheets import multi_sheet_manager
from decorators import handle_errors, rate_limit
from logger import logger
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════
# 🏢 COMPANY SELECTION COMMANDS
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def company_select_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏢 Company Selection Menu"""
    user = update.effective_user
    logger.info(f"🏢 Company selection requested by user {user.id}")
    
    # Check if user is registered
    if not company_manager.is_user_registered(user.id):
        # Show initial company registration
        await show_company_registration_menu(update, context)
        return
    
    # Show company switching menu
    await show_company_switching_menu(update, context)

async def show_company_registration_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📝 Show initial company registration menu"""
    user = update.effective_user
    
    text = (
        f"👋 **Welcome {user.first_name}!**\n\n"
        "🏢 **Please select your company to get started:**\n\n"
        "You'll be able to switch companies later if needed."
    )
    
    # Create company selection keyboard
    keyboard = []
    companies = company_manager.get_all_companies()
    
    for company_key, company_info in companies.items():
        keyboard.append([InlineKeyboardButton(
            company_info['display_name'], 
            callback_data=f"register_company_{company_key}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    logger.info(f"📝 Sent company registration menu to user {user.id}")

async def show_company_switching_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔄 Show company switching menu"""
    user = update.effective_user
    current_company = company_manager.get_user_company(user.id)
    allowed_companies = company_manager.get_user_allowed_companies(user.id)
    
    current_display = company_manager.get_company_display_name(current_company) if current_company else "None"
    
    text = (
        f"🏢 **Company Management**\n\n"
        f"📍 **Current Company:** {current_display}\n\n"
        f"🔄 **Switch to different company:**"
    )
    
    # Create switching keyboard
    keyboard = []
    companies = company_manager.get_all_companies()
    
    for company_key, company_info in companies.items():
        if company_key in allowed_companies and company_key != current_company:
            keyboard.append([InlineKeyboardButton(
                f"➡️ {company_info['display_name']}", 
                callback_data=f"switch_company_{company_key}"
            )])
    
    # Add current company info button
    if current_company:
        keyboard.append([InlineKeyboardButton(
            f"📊 Current: {current_display}", 
            callback_data=f"company_info_{current_company}"
        )])
    
    # Add close button
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    logger.info(f"🔄 Sent company switching menu to user {user.id}")

# ═══════════════════════════════════════════════════════════════
# ⚡ CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════

async def handle_company_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚡ Handle company selection callbacks"""
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    logger.info(f"⚡ Company callback: {data} from user {user.id}")
    
    try:
        if data.startswith("register_company_"):
            company_key = data.replace("register_company_", "")
            success = company_manager.register_user(user.id, user.full_name or user.first_name, company_key)
            
            if success:
                company_info = company_manager.get_company_info(company_key)
                await query.edit_message_text(
                    f"✅ **Successfully registered!**\n\n"
                    f"🏢 **Company:** {company_info['display_name']}\n"
                    f"👤 **User:** {user.full_name or user.first_name}\n\n"
                    f"🚀 **You can now use all bot features!**\n"
                    f"💡 Use `/start` to begin or `/company` to switch companies later.",
                    parse_mode='Markdown'
                )
                logger.info(f"✅ User {user.id} registered with company {company_key}")
            else:
                await query.edit_message_text("❌ Registration failed. Please try again.")
                logger.error(f"❌ Registration failed for user {user.id}")
        
        elif data.startswith("switch_company_"):
            company_key = data.replace("switch_company_", "")
            success = company_manager.switch_user_company(user.id, company_key)
            
            if success:
                company_info = company_manager.get_company_info(company_key)
                await query.edit_message_text(
                    f"🔄 **Company switched successfully!**\n\n"
                    f"🏢 **New Company:** {company_info['display_name']}\n"
                    f"📊 **All analytics and data will now show {company_info['name']} information.**\n\n"
                    f"💡 Try `/dashboard` to see your new company dashboard!",
                    parse_mode='Markdown'
                )
                logger.info(f"🔄 User {user.id} switched to company {company_key}")
            else:
                await query.edit_message_text("❌ Company switch failed. Please try again.")
                logger.error(f"❌ Company switch failed for user {user.id}")
        
        elif data.startswith("company_info_"):
            company_key = data.replace("company_info_", "")
            company_info = company_manager.get_company_info(company_key)
            stats = multi_sheet_manager.get_company_stats(company_key)
            
            info_text = (
                f"📊 **{company_info['display_name']} Information**\n\n"
                f"📈 **Statistics:**\n"
                f"• Records: {stats.get('total_records', 0)}\n"
                f"• Users: {stats.get('total_users', 0)}\n"
                f"• Revenue: ₹{stats.get('total_revenue', 0):,.2f}\n"
                f"• Period: {stats.get('date_range', 'No data')}\n\n"
                f"🔧 **Sheet:** {company_info.get('sheet_name', 'N/A')}"
            )
            
            await query.edit_message_text(info_text, parse_mode='Markdown')
        
        elif data == "close_menu":
            await query.edit_message_text("👍 Menu closed.")
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"❌ Company callback error: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")
        await query.answer()

# ═══════════════════════════════════════════════════════════════
# 👑 ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin Panel"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    logger.info(f"👑 Admin panel accessed by user {user.id}")
    
    text = (
        "👑 **ADMIN PANEL**\n\n"
        "🏢 **Company Management:**\n"
        "• `/admin_users` - View all users\n"
        "• `/admin_assign <user_id> <company>` - Assign user to company\n"
        "• `/admin_remove <user_id> <company>` - Remove user from company\n"
        "• `/admin_stats` - Company statistics\n\n"
        "📊 **Available Companies:**\n"
    )
    
    companies = company_manager.get_all_companies()
    for company_key, company_info in companies.items():
        text += f"• `{company_key}` - {company_info['display_name']}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: View all users"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    logger.info(f"👑 Admin users list requested by user {user.id}")
    
    all_users = company_manager.admin_get_all_users(user.id)
    
    if not all_users:
        await update.message.reply_text("📋 No users registered yet.")
        return
    
    text = "👥 **ALL REGISTERED USERS:**\n\n"
    
    for user_id, user_info in all_users.items():
        current_company = user_info.get('current_company', 'None')
        allowed_companies = ', '.join(user_info.get('allowed_companies', []))
        
        text += (
            f"👤 **{user_info.get('user_name', 'Unknown')}** (ID: `{user_id}`)\n"
            f"🏢 Current: {company_manager.get_company_display_name(current_company)}\n"
            f"📋 Allowed: {allowed_companies}\n"
            f"🔧 Role: {user_info.get('role', 'user')}\n\n"
        )
    
    # Split message if too long
    if len(text) > 4000:
        text = text[:4000] + "...\n\n(Message truncated - too many users)"
    
    await update.message.reply_text(text, parse_mode='Markdown')

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: Company statistics"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    logger.info(f"👑 Admin stats requested by user {user.id}")
    
    text = "📊 **COMPANY STATISTICS:**\n\n"
    
    companies = company_manager.get_all_companies()
    total_records = 0
    total_users = 0
    total_revenue = 0
    
    for company_key, company_info in companies.items():
        stats = multi_sheet_manager.get_company_stats(company_key)
        
        if 'error' not in stats:
            company_records = stats.get('total_records', 0)
            company_users = stats.get('total_users', 0) 
            company_revenue = stats.get('total_revenue', 0)
            
            text += (
                f"🏢 **{company_info['display_name']}**\n"
                f"📊 Records: {company_records}\n"
                f"👥 Users: {company_users}\n"
                f"💰 Revenue: ₹{company_revenue:,.2f}\n"
                f"📅 Range: {stats.get('date_range', 'No data')}\n\n"
            )
            
            total_records += company_records
            total_users += company_users  
            total_revenue += company_revenue
    
    text += (
        f"📈 **TOTALS ACROSS ALL COMPANIES:**\n"
        f"📊 Total Records: {total_records}\n"
        f"👥 Total Users: {len(company_manager.user_mappings)}\n"
        f"💰 Total Revenue: ₹{total_revenue:,.2f}"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def admin_assign_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: Assign user to company"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ **Usage:** `/admin_assign <user_id> <company_key>`\n\n"
            "**Example:** `/admin_assign 123456789 johnlee`\n\n"
            "**Available companies:** johnlee, yugrow, ambica, baker"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        company_key = context.args[1].lower()
        
        success = company_manager.admin_assign_user(user.id, target_user_id, company_key)
        
        if success:
            company_info = company_manager.get_company_info(company_key)
            await update.message.reply_text(
                f"✅ **User Assignment Successful**\n\n"
                f"👤 **User ID:** `{target_user_id}`\n"
                f"🏢 **Company:** {company_info['display_name']}\n\n"
                f"The user can now access {company_info['name']} data and analytics.",
                parse_mode='Markdown'
            )
            logger.info(f"👑 Admin {user.id} assigned user {target_user_id} to company {company_key}")
        else:
            await update.message.reply_text("❌ Assignment failed. Please check user ID and company key.")
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"❌ Admin assign error: {e}")
        await update.message.reply_text("❌ Assignment failed due to an error.")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def admin_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: Remove user from company"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ **Usage:** `/admin_remove <user_id> <company_key>`\n\n"
            "**Example:** `/admin_remove 123456789 johnlee`\n\n"
            "**Available companies:** johnlee, yugrow, ambica, baker"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        company_key = context.args[1].lower()
        
        success = company_manager.admin_remove_user(user.id, target_user_id, company_key)
        
        if success:
            company_info = company_manager.get_company_info(company_key)
            await update.message.reply_text(
                f"✅ **User Removal Successful**\n\n"
                f"👤 **User ID:** `{target_user_id}`\n"
                f"🏢 **Company:** {company_info['display_name']}\n\n"
                f"The user can no longer access {company_info['name']} data.",
                parse_mode='Markdown'
            )
            logger.info(f"👑 Admin {user.id} removed user {target_user_id} from company {company_key}")
        else:
            await update.message.reply_text("❌ Removal failed. Please check user ID and company key.")
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"❌ Admin remove error: {e}")
        await update.message.reply_text("❌ Removal failed due to an error.")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def admin_assign_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: Assign user to company"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage:** `/admin_assign <user_id> <company_key>`\n\n"
            "**Available companies:** johnlee, yugrow, ambica, baker"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        company_key = context.args[1].lower()
        
        success = company_manager.admin_assign_user(user.id, target_user_id, company_key)
        
        if success:
            company_info = company_manager.get_company_info(company_key)
            await update.message.reply_text(
                f"✅ **User Assignment Successful**\n\n"
                f"👤 **User ID:** `{target_user_id}`\n"
                f"🏢 **Company:** {company_info['display_name']}\n\n"
                f"The user can now access {company_info['name']} data.",
                parse_mode='Markdown'
            )
            logger.info(f"👑 Admin {user.id} assigned user {target_user_id} to company {company_key}")
        else:
            await update.message.reply_text("❌ Assignment failed. Please check user ID and company key.")
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"❌ Admin assign error: {e}")
        await update.message.reply_text("❌ Assignment failed due to an error.")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def admin_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin: Remove user from company"""
    user = update.effective_user
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage:** `/admin_remove <user_id> <company_key>`\n\n"
            "**Available companies:** johnlee, yugrow, ambica, baker"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        company_key = context.args[1].lower()
        
        success = company_manager.admin_remove_user(user.id, target_user_id, company_key)
        
        if success:
            company_info = company_manager.get_company_info(company_key)
            await update.message.reply_text(
                f"✅ **User Removal Successful**\n\n"
                f"👤 **User ID:** `{target_user_id}`\n"
                f"🏢 **Company:** {company_info['display_name']}\n\n"
                f"The user can no longer access {company_info['name']} data.",
                parse_mode='Markdown'
            )
            logger.info(f"👑 Admin {user.id} removed user {target_user_id} from company {company_key}")
        else:
            await update.message.reply_text("❌ Removal failed. Please check user ID and company key.")
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"❌ Admin remove error: {e}")
        await update.message.reply_text("❌ Removal failed due to an error.")
