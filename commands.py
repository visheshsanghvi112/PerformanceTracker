from telegram import Update
from telegram.ext import ContextTypes
import datetime
from summaries import send_summary
from menus import MenuSystem
from decorators import handle_errors, rate_limit
from logger import logger
from company_manager import company_manager

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command with company integration"""
    user = update.effective_user
    logger.info(f"🚀 Start command called by user {user.id} ({user.full_name or 'No name'})")
    logger.debug(f"👤 User details - ID: {user.id}, Username: {user.username}, Name: {user.first_name} {user.last_name or ''}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        welcome_text = (
            f"👋 **Welcome to Performance Tracker, {user.first_name}!**\n\n"
            "🏢 **Company Registration Required**\n"
            "To use this bot, please select your company first.\n\n"
            "💡 Use `/company` to get started!"
        )
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        return
    
    # Get user's current company
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    
    welcome_text = (
        f"👋 **Welcome to Performance Tracker, {user.first_name}!**\n\n"
        f"🏢 **Current Company:** {company_info['display_name']}\n\n"
        "🚀 **What's New:**\n"
        "• AI-powered business intelligence & forecasting\n"
        "• Professional analytics dashboard & charts\n"
        "• Smart AI parsing for natural language entries\n"
        "• Real-time data validation and warnings\n\n"
        "📊 **ANALYTICS COMMANDS:**\n"
        "• `/dashboard` - Executive business overview\n"
        "• `/predictions` - AI-powered forecasts & insights\n"
        "• `/charts` - Professional analytical charts\n"
        "• `/top` - Top performing clients & locations\n\n"
        "📝 **ENTRY COMMANDS:**\n"
        "• `/sales` - Log a sales entry\n"
        "• `/purchase` - Log a purchase entry\n"
        "• `/today` - View today's summary\n\n"
        "🏢 **COMPANY COMMANDS:**\n"
        "• `/company` - Switch companies or view company info\n\n"
        "💡 **Pro Tip:** Try `/analytics` for complete guide to advanced features!"
    )
    
    menu_system = MenuSystem()
    logger.debug(f"📋 Sending main menu to user {user.id}")
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=menu_system.create_main_menu(),
        parse_mode='Markdown'
    )
    logger.info(f"✅ Start command completed for user {user.id}")

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced sales command with better guidance"""
    user = update.effective_user
    logger.info(f"📊 Sales command called by user {user.id} ({user.full_name or 'No name'})")
    
    context.user_data['type'] = 'Sales'
    logger.debug(f"🔧 Set user {user.id} context to 'Sales' mode")
    
    sales_text = (
        "📊 **Sales Entry Mode Activated!**\n\n"
        "You can now log your sales in multiple ways:\n\n"
        "**📝 Method 1: Structured Format**\n"
        "```\n"
        "Client: Apollo Pharmacy\n"
        "Location: Bandra\n"
        "Orders: 3\n"
        "Amount: ₹24000\n"
        "Remarks: Good conversation\n"
        "```\n\n"
        "**🗣 Method 2: Natural Language**\n"
        "Just describe your sale naturally:\n"
        "_\"Sold 5 medicines to City Hospital in Andheri for ₹15000. Great meeting with procurement head.\"_\n\n"
        "**✨ Smart Features:**\n"
        "• AI understands natural language\n"
        "• Automatic data validation\n"
        "• Helpful warnings for unusual entries\n"
        "• Instant confirmation with entry ID\n\n"
        "💡 **Pro Tip:** Include client name, location, quantity, and amount for best results!"
    )
    
    await update.message.reply_text(
        text=sales_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def purchase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced purchase command with better guidance"""
    context.user_data['type'] = 'Purchase'
    user = update.effective_user
    logger.info(f"Purchase command called by user {user.id}")
    
    purchase_text = (
        "📦 **Purchase Entry Mode Activated!**\n\n"
        "You can now log your purchases in multiple ways:\n\n"
        "**📝 Method 1: Structured Format**\n"
        "```\n"
        "Client: ABC Suppliers\n"
        "Location: Lower Parel\n"
        "Orders: 2\n"
        "Amount: ₹18000\n"
        "Remarks: Delivered new stock\n"
        "```\n\n"
        "**🗣 Method 2: Natural Language**\n"
        "Just describe your purchase naturally:\n"
        "_\"Bought 10 units from MedSupply in Worli for ₹25000. Emergency stock replenishment.\"_\n\n"
        "**✨ Smart Features:**\n"
        "• AI understands natural language\n"
        "• Automatic supplier validation\n"
        "• Cost analysis and warnings\n"
        "• Instant confirmation with tracking ID\n\n"
        "💡 **Pro Tip:** Include supplier name, delivery location, quantity, and total cost!"
    )
    
    await update.message.reply_text(
        text=purchase_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced today command with loading indicator"""
    user = update.effective_user
    logger.info(f"Today summary requested by user {user.id}")
    
    # Send loading message
    loading_msg = await update.message.reply_text("📊 Generating today's summary...")
    
    try:
        today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Today's", today_date)
        
        # Delete loading message
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating today's summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced week command with loading indicator"""
    user = update.effective_user
    logger.info(f"Weekly summary requested by user {user.id}")
    
    # Send loading message
    loading_msg = await update.message.reply_text("📈 Generating weekly summary...")
    
    try:
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        week_ago = week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Weekly", week_ago)
        
        # Delete loading message
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating weekly summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced month command with loading indicator"""
    user = update.effective_user
    logger.info(f"Monthly summary requested by user {user.id}")
    
    # Send loading message
    loading_msg = await update.message.reply_text("📅 Generating monthly summary...")
    
    try:
        month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Monthly", month_ago)
        
        # Delete loading message
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating monthly summary: {e}") 

# ═══════════════════════════════════════════════════════════════
# 🚀 ADVANCED ANALYTICS COMMANDS
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔥 Executive Dashboard - Complete business overview (ADMIN ONLY)"""
    user = update.effective_user
    logger.info(f"📊 Dashboard command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    from company_manager import company_manager
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ **Access Denied**\n\n📊 Analytics commands are restricted to administrators only.", parse_mode='Markdown')
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("📊 Generating executive dashboard...")
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Dashboard Error: {dashboard['error']}")
            return
        
        # Format dashboard message
        message = f"📊 **EXECUTIVE DASHBOARD**\n"
        message += f"📅 Period: {dashboard['period']}\n\n"
        
        message += "📈 **KEY PERFORMANCE INDICATORS:**\n"
        for kpi, value in dashboard['kpis'].items():
            emoji = "💰" if "revenue" in kpi else "📦" if "order" in kpi else "👥" if "client" in kpi else "📈"
            message += f"{emoji} {kpi.replace('_', ' ').title()}: **{value}**\n"
        
        message += "\n🏆 **TOP CLIENTS:**\n"
        for i, (client, revenue) in enumerate(list(dashboard['top_clients'].items())[:5], 1):
            message += f"{i}. {client}: ₹{revenue:,.0f}\n"
        
        message += "\n📍 **TOP LOCATIONS:**\n"
        for i, (location, revenue) in enumerate(list(dashboard['top_locations'].items())[:5], 1):
            message += f"{i}. {location}: ₹{revenue:,.0f}\n"
        
        message += "\n🧠 **BUSINESS INSIGHTS:**\n"
        for insight, value in dashboard['insights'].items():
            message += f"• {insight.replace('_', ' ').title()}: **{value}**\n"
        
        message += f"\n⏰ Generated: {dashboard['generated_at'][:19]}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"✅ Dashboard delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate dashboard. Please try again.")
        logger.error(f"Dashboard command error: {e}")

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def predictions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔮 AI-Powered Predictive Analytics (ADMIN ONLY)"""
    user = update.effective_user
    logger.info(f"🔮 Predictions command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    from company_manager import company_manager
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ **Access Denied**\n\n🔮 Analytics commands are restricted to administrators only.", parse_mode='Markdown')
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🔮 Generating AI predictions...")
    
    try:
        from analytics import analytics_engine
        
        predictions = analytics_engine.generate_predictive_insights(user.id)
        
        if "error" in predictions:
            await loading_msg.edit_text(f"❌ Predictions Error: {predictions['error']}")
            return
        
        message = "🔮 **AI-POWERED PREDICTIONS**\n\n"
        
        # Revenue Forecast
        if "revenue_forecast" in predictions and "error" not in predictions["revenue_forecast"]:
            forecast = predictions["revenue_forecast"]
            message += "📈 **REVENUE FORECAST:**\n"
            message += f"• Next 30 Days: **{forecast.get('next_30_days', 'N/A')}**\n"
            message += f"• Daily Average: **{forecast.get('daily_average', 'N/A')}**\n"
            message += f"• Growth Rate: **{forecast.get('growth_rate', 'N/A')}**\n"
            message += f"• Confidence: **{forecast.get('confidence', 'N/A')}**\n\n"
        
        # Churn Risk
        if "churn_risk" in predictions and "error" not in predictions["churn_risk"]:
            churn = predictions["churn_risk"]
            risk_emoji = "🚨" if churn.get('risk_level') == "HIGH" else "⚠️" if churn.get('risk_level') == "MODERATE" else "✅"
            message += f"{risk_emoji} **CHURN RISK ANALYSIS:**\n"
            message += f"• Churn Rate: **{churn.get('churn_rate', 'N/A')}**\n"
            message += f"• Risk Level: **{churn.get('risk_level', 'N/A')}**\n"
            message += f"• Inactive Clients: **{churn.get('inactive_clients', 'N/A')}**\n\n"
        
        # Seasonal Patterns
        if "seasonal_patterns" in predictions and "error" not in predictions["seasonal_patterns"]:
            patterns = predictions["seasonal_patterns"]
            message += "📅 **SEASONAL PATTERNS:**\n"
            message += f"• Best Weekday: **{patterns.get('best_weekday', 'N/A')}**\n"
            message += f"• Worst Weekday: **{patterns.get('worst_weekday', 'N/A')}**\n"
            message += f"• Best Month: **{patterns.get('best_month', 'N/A')}**\n"
            message += f"• Peak Hour: **{patterns.get('peak_hour', 'N/A')}**\n\n"
        
        # Growth Opportunities
        if "growth_opportunities" in predictions:
            message += "🚀 **GROWTH OPPORTUNITIES:**\n"
            for opp in predictions["growth_opportunities"][:3]:
                message += f"• {opp}\n"
            message += "\n"
        
        # Risk Assessment
        if "risk_assessment" in predictions:
            message += "⚠️ **RISK ASSESSMENT:**\n"
            for risk in predictions["risk_assessment"][:3]:
                message += f"• {risk}\n"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🔮 Predictions delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate predictions. Please try again.")
        logger.error(f"Predictions command error: {e}")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def charts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Generate Professional Analytics Charts (ADMIN ONLY)"""
    user = update.effective_user
    logger.info(f"📊 Charts command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    from company_manager import company_manager
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ **Access Denied**\n\n📈 Analytics commands are restricted to administrators only.", parse_mode='Markdown')
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("📊 Creating professional charts...")
    
    try:
        from analytics import analytics_engine
        
        chart_files = analytics_engine.generate_advanced_charts(user.id)
        
        if not chart_files:
            await loading_msg.edit_text("❌ No charts generated. Need more data or check configuration.")
            return
        
        await loading_msg.edit_text(f"✅ Generated {len(chart_files)} professional charts!")
        
        # Send each chart as a photo
        for chart_path in chart_files:
            if chart_path and chart_path.endswith('.png'):
                try:
                    chart_name = chart_path.split('/')[-1].split('\\')[-1]
                    with open(chart_path, 'rb') as chart_file:
                        await update.message.reply_photo(
                            photo=chart_file,
                            caption=f"📊 **{chart_name.replace('_', ' ').replace('.png', '').title()}**"
                        )
                    logger.info(f"📈 Sent chart {chart_name} to user {user.id}")
                except Exception as chart_error:
                    logger.error(f"Failed to send chart {chart_path}: {chart_error}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate charts. Please try again.")
        logger.error(f"Charts command error: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True) 
async def analytics_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📚 Analytics Help - Show all available analytics commands"""
    user = update.effective_user
    logger.info(f"📚 Analytics help requested by user {user.id}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    
    help_text = f"""
📚 **ADVANCED ANALYTICS COMMANDS**
🏢 **Current Company:** {company_info['display_name']}

🚀 **EXECUTIVE LEVEL:**
• `/dashboard` - Complete business overview with KPIs
• `/predictions` - AI-powered forecasts & insights

📊 **VISUAL ANALYTICS:**  
• `/charts` - Professional analytical charts
• `/trends` - Revenue & performance trends

📈 **PERFORMANCE TRACKING:**
• `/today` - Today's performance summary
• `/week` - Weekly performance report  
• `/month` - Monthly business review

🔍 **QUICK INSIGHTS:**
• `/top` - Top clients & locations
• `/risks` - Business risk assessment
• `/opportunities` - Growth recommendations

💡 **PRO TIPS:**
• Use `/dashboard` for complete overview
• `/predictions` gives AI-powered forecasts
• `/charts` creates professional visualizations
• All analytics update automatically from your data!

🎯 **Example Usage:**
Just type `/dashboard` and get instant business insights!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
    logger.info(f"📚 Analytics help delivered to user {user.id}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def top_performers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 Quick Top Performers Summary"""
    user = update.effective_user
    logger.info(f"🏆 Top performers requested by user {user.id}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🏆 Finding top performers...")
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Error: {dashboard['error']}")
            return
        
        message = "🏆 **TOP PERFORMERS**\n\n"
        
        message += "👑 **TOP CLIENTS:**\n"
        for i, (client, revenue) in enumerate(list(dashboard['top_clients'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {client}: **₹{revenue:,.0f}**\n"
        
        message += "\n🏢 **TOP LOCATIONS:**\n"
        for i, (location, revenue) in enumerate(list(dashboard['top_locations'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {location}: **₹{revenue:,.0f}**\n"
        
        # Add quick stats
        kpis = dashboard['kpis']
        message += f"\n📊 **QUICK STATS:**\n"
        message += f"• Total Revenue: **{kpis.get('total_revenue', 'N/A')}**\n"
        message += f"• Total Orders: **{kpis.get('total_orders', 'N/A')}**\n"
        message += f"• Growth Trend: **{kpis.get('growth_trend', 'N/A')}**\n"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🏆 Top performers delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to get top performers. Please try again.")
        logger.error(f"Top performers command error: {e}")