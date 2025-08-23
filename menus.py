"""
Interactive menu system for the Performance Tracker bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from typing import List, Dict, Any
from logger import logger


class MenuSystem:
    """Interactive menu system for better user experience"""
    
    @staticmethod
    def create_main_menu() -> InlineKeyboardMarkup:
        """Create the main menu with primary options"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Log Sales", callback_data="menu_sales"),
                InlineKeyboardButton("📦 Log Purchase", callback_data="menu_purchase")
            ],
            [
                InlineKeyboardButton("📈 View Summary", callback_data="menu_summary"),
                InlineKeyboardButton("🔍 Search Entries", callback_data="menu_search")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
                InlineKeyboardButton("❓ Help", callback_data="menu_help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_entry_type_menu() -> InlineKeyboardMarkup:
        """Create menu for selecting entry type"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Sales Entry", callback_data="type_sales"),
                InlineKeyboardButton("📦 Purchase Entry", callback_data="type_purchase")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_summary_menu() -> InlineKeyboardMarkup:
        """Create menu for summary options"""
        keyboard = [
            [
                InlineKeyboardButton("📅 Today", callback_data="summary_today"),
                InlineKeyboardButton("📆 This Week", callback_data="summary_week")
            ],
            [
                InlineKeyboardButton("🗓 This Month", callback_data="summary_month"),
                InlineKeyboardButton("📊 Custom Range", callback_data="summary_custom")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_entry_actions_menu(entry_id: str) -> InlineKeyboardMarkup:
        """Create menu for entry actions (edit, delete, etc.)"""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit Entry", callback_data=f"edit_{entry_id}"),
                InlineKeyboardButton("🗑 Delete Entry", callback_data=f"delete_{entry_id}")
            ],
            [
                InlineKeyboardButton("📋 View Details", callback_data=f"view_{entry_id}"),
                InlineKeyboardButton("📤 Share Entry", callback_data=f"share_{entry_id}")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_search")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_confirmation_menu(action: str, item_id: str) -> InlineKeyboardMarkup:
        """Create confirmation menu for destructive actions"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Confirm", callback_data=f"confirm_{action}_{item_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="menu_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_help_menu() -> InlineKeyboardMarkup:
        """Create help menu with different help topics"""
        keyboard = [
            [
                InlineKeyboardButton("📝 How to Log Entries", callback_data="help_logging"),
                InlineKeyboardButton("📊 Understanding Reports", callback_data="help_reports")
            ],
            [
                InlineKeyboardButton("🔍 Search & Filter", callback_data="help_search"),
                InlineKeyboardButton("⚙️ Settings Guide", callback_data="help_settings")
            ],
            [
                InlineKeyboardButton("🆘 Troubleshooting", callback_data="help_troubleshoot"),
                InlineKeyboardButton("📞 Contact Support", callback_data="help_contact")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_settings_menu() -> InlineKeyboardMarkup:
        """Create settings menu"""
        keyboard = [
            [
                InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
                InlineKeyboardButton("🌍 Language", callback_data="settings_language")
            ],
            [
                InlineKeyboardButton("📊 Default View", callback_data="settings_default_view"),
                InlineKeyboardButton("🎨 Theme", callback_data="settings_theme")
            ],
            [
                InlineKeyboardButton("📤 Export Data", callback_data="settings_export"),
                InlineKeyboardButton("🗑 Clear History", callback_data="settings_clear")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)


class MenuHandler:
    """Handler for menu interactions"""
    
    def __init__(self):
        self.menu_system = MenuSystem()
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        
        data = query.data
        logger.info(f"Callback query received: {data} from user {query.from_user.id}")
        
        try:
            if data == "menu_main":
                await self.show_main_menu(query, context)
            elif data == "menu_sales":
                await self.handle_sales_menu(query, context)
            elif data == "menu_purchase":
                await self.handle_purchase_menu(query, context)
            elif data == "menu_summary":
                await self.show_summary_menu(query, context)
            elif data == "menu_search":
                await self.handle_search_menu(query, context)
            elif data == "menu_help":
                await self.show_help_menu(query, context)
            elif data == "menu_settings":
                await self.show_settings_menu(query, context)
            elif data.startswith("type_"):
                await self.handle_type_selection(query, context, data)
            elif data.startswith("summary_"):
                await self.handle_summary_selection(query, context, data)
            elif data.startswith("help_"):
                await self.handle_help_selection(query, context, data)
            elif data.startswith("settings_"):
                await self.handle_settings_selection(query, context, data)
            elif data.startswith("edit_"):
                await self.handle_edit_entry(query, context, data)
            elif data.startswith("delete_"):
                await self.handle_delete_entry(query, context, data)
            elif data.startswith("confirm_"):
                await self.handle_confirmation(query, context, data)
            else:
                await query.edit_message_text("❓ Unknown action. Please try again.")
                
        except Exception as e:
            logger.error(f"Error handling callback query {data}: {str(e)}")
            await query.edit_message_text("⚠️ An error occurred. Please try again.")
    
    async def show_main_menu(self, query, context):
        """Show the main menu"""
        text = (
            "🏠 **Performance Tracker - Main Menu**\n\n"
            "Welcome! What would you like to do today?\n\n"
            "📊 **Log Sales** - Record a new sales entry\n"
            "📦 **Log Purchase** - Record a new purchase entry\n"
            "📈 **View Summary** - See your performance reports\n"
            "🔍 **Search Entries** - Find and manage your entries\n"
            "⚙️ **Settings** - Customize your experience\n"
            "❓ **Help** - Get help and tutorials"
        )
        
        await query.edit_message_text(
            text=text,
            reply_markup=self.menu_system.create_main_menu(),
            parse_mode='Markdown'
        )
    
    async def handle_sales_menu(self, query, context):
        """Handle sales menu selection"""
        context.user_data['type'] = 'Sales'
        text = (
            "📊 **Sales Entry Mode**\n\n"
            "You can now send your sales entry in any of these formats:\n\n"
            "**Structured Format:**\n"
            "```\n"
            "Client: Apollo Pharmacy\n"
            "Location: Bandra\n"
            "Orders: 3\n"
            "Amount: ₹24000\n"
            "Remarks: Good conversation\n"
            "```\n\n"
            "**Natural Language:**\n"
            "Just describe your sale naturally, like:\n"
            "_\"Sold 5 items to City Hospital in Andheri for ₹15000\"_\n\n"
            "💡 **Tip:** The more details you provide, the better!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_purchase_menu(self, query, context):
        """Handle purchase menu selection"""
        context.user_data['type'] = 'Purchase'
        text = (
            "📦 **Purchase Entry Mode**\n\n"
            "You can now send your purchase entry in any of these formats:\n\n"
            "**Structured Format:**\n"
            "```\n"
            "Client: ABC Suppliers\n"
            "Location: Lower Parel\n"
            "Orders: 2\n"
            "Amount: ₹18000\n"
            "Remarks: Delivered new stock\n"
            "```\n\n"
            "**Natural Language:**\n"
            "Just describe your purchase naturally, like:\n"
            "_\"Bought 10 units from MedSupply in Worli for ₹25000\"_\n\n"
            "💡 **Tip:** Include supplier name, location, and amount for best results!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_summary_menu(self, query, context):
        """Show summary menu"""
        text = (
            "📈 **Performance Summary**\n\n"
            "Choose the time period for your summary:\n\n"
            "📅 **Today** - Today's entries\n"
            "📆 **This Week** - Last 7 days\n"
            "🗓 **This Month** - Last 30 days\n"
            "📊 **Custom Range** - Choose specific dates"
        )
        
        await query.edit_message_text(
            text=text,
            reply_markup=self.menu_system.create_summary_menu(),
            parse_mode='Markdown'
        )
    
    async def handle_search_menu(self, query, context):
        """Handle search menu"""
        text = (
            "🔍 **Search Your Entries**\n\n"
            "Send me any of the following to search:\n\n"
            "• **Client name** - Find entries by client\n"
            "• **Location** - Find entries by location\n"
            "• **Date** - Find entries by date (DD-MM-YYYY)\n"
            "• **Amount range** - e.g., \"₹10000 to ₹50000\"\n"
            "• **Entry ID** - Find specific entry\n\n"
            "💡 **Example:** \"Apollo\" or \"Bandra\" or \"15-01-2025\""
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Set search mode
        context.user_data['mode'] = 'search'
    
    async def show_help_menu(self, query, context):
        """Show help menu"""
        text = (
            "❓ **Help & Support**\n\n"
            "Choose a topic to get help with:\n\n"
            "📝 **How to Log Entries** - Learn entry formats\n"
            "📊 **Understanding Reports** - Interpret your data\n"
            "🔍 **Search & Filter** - Find your entries\n"
            "⚙️ **Settings Guide** - Customize the bot\n"
            "🆘 **Troubleshooting** - Fix common issues\n"
            "📞 **Contact Support** - Get human help"
        )
        
        await query.edit_message_text(
            text=text,
            reply_markup=self.menu_system.create_help_menu(),
            parse_mode='Markdown'
        )
    
    async def show_settings_menu(self, query, context):
        """Show settings menu"""
        text = (
            "⚙️ **Settings**\n\n"
            "Customize your bot experience:\n\n"
            "🔔 **Notifications** - Manage alerts\n"
            "🌍 **Language** - Change language\n"
            "📊 **Default View** - Set preferred summary\n"
            "🎨 **Theme** - Choose display style\n"
            "📤 **Export Data** - Download your data\n"
            "🗑 **Clear History** - Reset your data"
        )
        
        await query.edit_message_text(
            text=text,
            reply_markup=self.menu_system.create_settings_menu(),
            parse_mode='Markdown'
        )
    
    async def handle_type_selection(self, query, context, data):
        """Handle entry type selection"""
        entry_type = data.split("_")[1].title()
        context.user_data['type'] = entry_type
        
        await query.edit_message_text(
            f"✅ {entry_type} mode activated!\n\n"
            f"Now send me your {entry_type.lower()} entry details."
        )
    
    async def handle_summary_selection(self, query, context, data):
        """Handle summary period selection"""
        period = data.split("_")[1]
        
        # Import here to avoid circular imports
        from summaries import send_summary
        import datetime
        
        if period == "today":
            today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            await send_summary(query, context, "Today's", today_date)
        elif period == "week":
            week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            week_ago = week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
            await send_summary(query, context, "Weekly", week_ago)
        elif period == "month":
            month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
            await send_summary(query, context, "Monthly", month_ago)
        elif period == "custom":
            await query.edit_message_text(
                "📅 **Custom Date Range**\n\n"
                "Send me the date range in format:\n"
                "`DD-MM-YYYY to DD-MM-YYYY`\n\n"
                "Example: `01-01-2025 to 31-01-2025`",
                parse_mode='Markdown'
            )
            context.user_data['mode'] = 'custom_summary'
    
    async def handle_help_selection(self, query, context, data):
        """Handle help topic selection"""
        topic = data.split("_")[1]
        
        help_content = {
            "logging": (
                "📝 **How to Log Entries**\n\n"
                "**Method 1: Structured Format**\n"
                "```\n"
                "Client: Apollo Pharmacy\n"
                "Location: Bandra\n"
                "Orders: 3\n"
                "Amount: ₹24000\n"
                "Remarks: Good conversation\n"
                "```\n\n"
                "**Method 2: Natural Language**\n"
                "Just describe naturally:\n"
                "_\"Sold 5 items to City Hospital for ₹15000\"_\n\n"
                "**Tips:**\n"
                "• Include client name, location, and amount\n"
                "• Use ₹ symbol or write 'rupees'\n"
                "• Be specific about quantities\n"
                "• Add remarks for context"
            ),
            "reports": (
                "📊 **Understanding Reports**\n\n"
                "**Summary Reports Include:**\n"
                "• Total entries and amounts\n"
                "• Breakdown by client and location\n"
                "• Time-based trends\n"
                "• Performance metrics\n\n"
                "**CSV Exports Contain:**\n"
                "• All entry details\n"
                "• Timestamps and IDs\n"
                "• User information\n"
                "• Filterable data\n\n"
                "**Reading Tips:**\n"
                "• Check date ranges carefully\n"
                "• Look for patterns in client data\n"
                "• Compare periods for trends"
            ),
            "search": (
                "🔍 **Search & Filter Guide**\n\n"
                "**Search by:**\n"
                "• Client name: \"Apollo\"\n"
                "• Location: \"Bandra\"\n"
                "• Date: \"15-01-2025\"\n"
                "• Amount: \"₹10000 to ₹50000\"\n"
                "• Entry ID: \"abc12345\"\n\n"
                "**Advanced Search:**\n"
                "• Use partial names\n"
                "• Combine multiple criteria\n"
                "• Use date ranges\n"
                "• Filter by entry type\n\n"
                "**Tips:**\n"
                "• Search is case-insensitive\n"
                "• Use specific terms for better results\n"
                "• Try different variations"
            )
        }
        
        content = help_content.get(topic, "Help content not available.")
        keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="menu_help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=content,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# Create global menu handler instance
menu_handler = MenuHandler()