#!/usr/bin/env python3
"""
📋 ENHANCED COMMANDS MODULE
==========================
Comprehensive command handlers with AI-powered responses and advanced analytics
"""

from telegram import Update
from telegram.ext import ContextTypes
import datetime
from summaries import send_summary
from menus import MenuSystem
from decorators import handle_errors, rate_limit
from logger import logger
from company_manager import company_manager
from ai_response_engine import ai_response_engine

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 Enhanced start command with AI-powered personalized welcome"""
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
    
    # Generate AI-powered personalized greeting
    ai_greeting = ai_response_engine.generate_greeting_response(user.first_name)
    
    welcome_text = (
        f"{ai_greeting}\n\n"
        f"🏢 **Current Company:** {company_info['display_name']}\n\n"
        "🚀 **WHAT'S NEW & POWERFUL:**\n"
        "• 🤖 AI-powered natural language processing\n"
        "• 📍 GPS location tracking for territory insights\n"
        "• 📊 Advanced business intelligence & forecasting\n"
        "• 📈 Professional analytics dashboard & charts\n"
        "• 🔄 Smart batch processing for multiple entries\n"
        "• ⚡ Real-time data validation and insights\n\n"
        "📊 **ANALYTICS & INTELLIGENCE:**\n"
        "• `/dashboard` - Executive business overview\n"
        "• `/predictions` - AI-powered forecasts & insights\n"
        "• `/charts` - Professional analytical charts\n"
        "• `/top` - Top performing clients & locations\n"
        "• `/location_analytics` - Territory performance insights\n\n"
        "📝 **SMART ENTRY COMMANDS:**\n"
        "• `/sales` - Log sales with AI assistance\n"
        "• `/purchase` - Log purchases with smart parsing\n"
        "• `/batch` - Process multiple entries at once\n\n"
        "📍 **GPS LOCATION FEATURES:**\n"
        "• `/location` - Share GPS for automatic territory tracking\n"
        "• `/location_status` - Check your GPS location status\n"
        "• `/location_analytics` - Territory performance insights\n\n"
        "📈 **QUICK REPORTS:**\n"
        "• `/today` - Today's performance summary\n"
        "• `/week` - Weekly business review\n"
        "• `/month` - Monthly performance analysis\n\n"
        "🏢 **COMPANY MANAGEMENT:**\n"
        "• `/company` - Switch companies or view info\n\n"
        f"💡 **AI Tip:** {ai_response_engine.generate_tip_of_the_day()}"
    )
    
    menu_system = MenuSystem()
    logger.debug(f"📋 Sending enhanced main menu to user {user.id}")
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=menu_system.create_main_menu(),
        parse_mode='Markdown'
    )
    logger.info(f"✅ Enhanced start command completed for user {user.id}")

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Enhanced sales command with AI guidance and smart features"""
    user = update.effective_user
    logger.info(f"📊 Sales command called by user {user.id} ({user.full_name or 'No name'})")
    
    context.user_data['type'] = 'Sales'
    logger.debug(f"🔧 Set user {user.id} context to 'Sales' mode")
    
    # Generate AI-powered motivational message
    motivation = ai_response_engine.generate_motivation_message()
    
    sales_text = (
        "📊 **SALES ENTRY MODE ACTIVATED!** 🚀\n\n"
        f"{motivation}\n\n"
        "🤖 **AI-POWERED ENTRY METHODS:**\n\n"
        "**📝 Method 1: Structured Format**\n"
        "```\n"
        "Client: Apollo Pharmacy\n"
        "Location: Bandra\n"
        "Orders: 3 boxes + 5 bottles\n"
        "Amount: ₹24000\n"
        "Remarks: Great conversation with manager\n"
        "```\n\n"
        "**🗣 Method 2: Natural Language (AI-Powered)**\n"
        "Just describe your sale naturally - our AI understands:\n"
        "_\"Sold 5 medicines to City Hospital in Andheri for ₹15000. Great meeting with procurement head.\"_\n\n"
        "**📦 Method 3: Batch Processing**\n"
        "Process multiple sales at once:\n"
        "_Use `/batch` command for multiple entries_\n\n"
        "**🌍 GPS LOCATION ENHANCEMENT:**\n"
        "• Share your location with `/location` for automatic territory tracking\n"
        "• Get territory insights with `/location_analytics`\n"
        "• Your GPS location will be automatically added to entries\n\n"
        "**✨ SMART AI FEATURES:**\n"
        "• 🧠 Advanced natural language understanding\n"
        "• 📊 Automatic data validation and suggestions\n"
        "• ⚠️ Intelligent warnings for unusual entries\n"
        "• 🎯 Smart client and location recognition\n"
        "• 📈 Real-time performance insights\n"
        "• 🔄 Automatic duplicate detection\n\n"
        "**🏆 PRO FEATURES:**\n"
        "• **Smart Orders Parsing:** \"3 boxes + 5 bottles\" = 8 units\n"
        "• **Currency Recognition:** ₹, Rs, rupees all work\n"
        "• **Client Intelligence:** Remembers your frequent clients\n"
        "• **Location Tracking:** GPS-based territory analytics\n"
        "• **Performance Insights:** Instant feedback on your sales\n\n"
        "💡 **Pro Tips:**\n"
        "• Include client name, location, quantity, and amount\n"
        "• Use specific details for better analytics\n"
        "• Share GPS location for territory insights\n"
        "• Check `/dashboard` for performance overview\n\n"
        "🎯 **Ready to log your sales? Just type your entry naturally!**"
    )
    
    await update.message.reply_text(
        text=sales_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def purchase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📦 Enhanced purchase command with AI guidance and smart features"""
    context.user_data['type'] = 'Purchase'
    user = update.effective_user
    logger.info(f"📦 Purchase command called by user {user.id}")
    
    # Generate AI-powered motivational message
    motivation = ai_response_engine.generate_motivation_message()
    
    purchase_text = (
        "📦 **PURCHASE ENTRY MODE ACTIVATED!** 🚀\n\n"
        f"{motivation}\n\n"
        "🤖 **AI-POWERED ENTRY METHODS:**\n\n"
        "**📝 Method 1: Structured Format**\n"
        "```\n"
        "Client: ABC Suppliers\n"
        "Location: Lower Parel\n"
        "Orders: 2 cartons + 10 bottles\n"
        "Amount: ₹18000\n"
        "Remarks: Emergency stock replenishment\n"
        "```\n\n"
        "**🗣 Method 2: Natural Language (AI-Powered)**\n"
        "Just describe your purchase naturally:\n"
        "_\"Bought 10 units from MedSupply in Worli for ₹25000. Emergency stock replenishment.\"_\n\n"
        "**📦 Method 3: Batch Processing**\n"
        "Process multiple purchases at once:\n"
        "_Use `/batch` command for multiple entries_\n\n"
        "**🌍 GPS LOCATION ENHANCEMENT:**\n"
        "• Share your location with `/location` for supplier tracking\n"
        "• Get supplier analytics with `/location_analytics`\n"
        "• Your GPS location will be automatically added to entries\n\n"
        "**✨ SMART AI FEATURES:**\n"
        "• 🧠 Advanced supplier recognition\n"
        "• 💰 Automatic cost analysis and warnings\n"
        "• 📊 Inventory tracking suggestions\n"
        "• 🎯 Smart supplier and location recognition\n"
        "• 📈 Real-time cost insights\n"
        "• 🔄 Automatic duplicate detection\n\n"
        "**🏆 PRO FEATURES:**\n"
        "• **Smart Quantity Parsing:** \"2 cartons + 10 bottles\" = 12 units\n"
        "• **Cost Intelligence:** Tracks supplier pricing trends\n"
        "• **Supplier Analytics:** Performance tracking by supplier\n"
        "• **Location Tracking:** GPS-based supplier mapping\n"
        "• **Inventory Insights:** Stock level recommendations\n\n"
        "💡 **Pro Tips:**\n"
        "• Include supplier name, delivery location, quantity, and cost\n"
        "• Note delivery conditions in remarks\n"
        "• Share GPS location for supplier analytics\n"
        "• Check `/dashboard` for cost analysis\n\n"
        "🎯 **Ready to log your purchases? Just type your entry naturally!**"
    )
    
    await update.message.reply_text(
        text=purchase_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📦 Batch processing command for multiple entries"""
    user = update.effective_user
    logger.info(f"📦 Batch command called by user {user.id}")
    
    batch_text = (
        "📦 **BATCH PROCESSING MODE** 🚀\n\n"
        "Process multiple sales or purchases at once with AI intelligence!\n\n"
        "**📋 HOW TO USE:**\n"
        "1. First, set your entry type: `/sales` or `/purchase`\n"
        "2. Then send multiple entries separated by double line breaks\n\n"
        "**📝 BATCH FORMAT EXAMPLE:**\n"
        "```\n"
        "Sold 5 units to Apollo Pharmacy for ₹15000\n\n"
        "Client: MedPlus, Orders: 3, Amount: ₹8000\n\n"
        "Bought 10 bottles from XYZ Supplier - ₹12000\n"
        "```\n\n"
        "**✨ SMART FEATURES:**\n"
        "• 🤖 AI processes each entry individually\n"
        "• 📊 Automatic validation for all entries\n"
        "• ⚠️ Detailed error reporting per entry\n"
        "• 🌍 GPS location added to all entries\n"
        "• 📈 Batch performance summary\n\n"
        "**🎯 BATCH LIMITS:**\n"
        "• Maximum 10 entries per batch\n"
        "• Each entry validated separately\n"
        "• Failed entries reported individually\n\n"
        "💡 **Pro Tip:** Use clear separators (double line breaks) between entries!"
    )
    
    await update.message.reply_text(batch_text, parse_mode='Markdown')

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📅 Enhanced today command with AI insights"""
    user = update.effective_user
    logger.info(f"📅 Today summary requested by user {user.id}")
    
    # Send AI-powered loading message
    loading_messages = [
        "📊 Analyzing today's performance...",
        "🔍 Gathering your business data...",
        "📈 Calculating today's insights...",
        "🤖 AI is processing your data..."
    ]
    loading_msg = await update.message.reply_text(
        ai_response_engine.generate_motivation_message() + "\n\n" + 
        loading_messages[user.id % len(loading_messages)]
    )
    
    try:
        today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Today's", today_date)
        
        # Delete loading message and add AI insight
        await loading_msg.delete()
        
        # Generate AI insight about today's performance
        insight_msg = f"🧠 **AI Insight:** {ai_response_engine.generate_tip_of_the_day()}"
        await update.message.reply_text(insight_msg, parse_mode='Markdown')
        
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating today's summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📈 Enhanced weekly command with AI insights"""
    user = update.effective_user
    logger.info(f"📈 Weekly summary requested by user {user.id}")
    
    # Send AI-powered loading message
    loading_msg = await update.message.reply_text(
        "📈 **Weekly Performance Analysis**\n\n"
        "🤖 AI is analyzing your weekly patterns and trends..."
    )
    
    try:
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        week_ago = week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Weekly", week_ago)
        
        # Delete loading message
        await loading_msg.delete()
        
        # Generate AI insight about weekly performance
        insight_msg = (
            "🧠 **Weekly AI Insights:**\n"
            "• Consistency is key to long-term success!\n"
            "• Weekly tracking helps identify patterns\n"
            "• Use `/predictions` for future forecasts\n\n"
            f"💡 **Tip:** {ai_response_engine.generate_tip_of_the_day()}"
        )
        await update.message.reply_text(insight_msg, parse_mode='Markdown')
        
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating weekly summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📅 Enhanced monthly command with comprehensive AI insights"""
    user = update.effective_user
    logger.info(f"📅 Monthly summary requested by user {user.id}")
    
    # Send AI-powered loading message
    loading_msg = await update.message.reply_text(
        "📅 **Monthly Business Review**\n\n"
        "🤖 AI is conducting comprehensive monthly analysis...\n"
        "📊 Analyzing trends, patterns, and opportunities..."
    )
    
    try:
        month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Monthly", month_ago)
        
        # Delete loading message
        await loading_msg.delete()
        
        # Generate comprehensive AI insights for monthly review
        insight_msg = (
            "🧠 **Monthly AI Business Intelligence:**\n\n"
            "📈 **Performance Insights:**\n"
            "• Monthly reviews reveal long-term trends\n"
            "• Consistent tracking builds business intelligence\n"
            "• Use patterns to optimize future performance\n\n"
            "🎯 **Strategic Recommendations:**\n"
            "• Review top clients for relationship building\n"
            "• Analyze territory performance for expansion\n"
            "• Use `/predictions` for next month's forecast\n\n"
            "📊 **Advanced Analytics Available:**\n"
            "• `/dashboard` - Executive overview\n"
            "• `/charts` - Visual performance analysis\n"
            "• `/location_analytics` - Territory insights\n\n"
            f"💡 **Monthly Tip:** {ai_response_engine.generate_tip_of_the_day()}"
        )
        await update.message.reply_text(insight_msg, parse_mode='Markdown')
        
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating monthly summary: {e}")

# ═══════════════════════════════════════════════════════════════
# 🚀 ADVANCED ANALYTICS COMMANDS WITH AI ENHANCEMENT
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔥 Executive Dashboard - Complete business overview with AI insights"""
    user = update.effective_user
    logger.info(f"📊 Dashboard command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n"
            "📊 Executive analytics are restricted to administrators.\n\n"
            "💡 Available commands for you:\n"
            "• `/today` - Today's summary\n"
            "• `/week` - Weekly report\n"
            "• `/location_analytics` - Territory insights", 
            parse_mode='Markdown'
        )
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    # AI-powered loading message
    loading_msg = await update.message.reply_text(
        "📊 **EXECUTIVE DASHBOARD LOADING**\n\n"
        "🤖 AI is analyzing comprehensive business data...\n"
        "📈 Processing KPIs, trends, and insights...\n"
        "🧠 Generating intelligent business recommendations..."
    )
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Dashboard Error: {dashboard['error']}")
            return
        
        # Enhanced dashboard message with AI insights
        message = f"📊 **EXECUTIVE DASHBOARD** 🚀\n"
        message += f"📅 Period: {dashboard['period']}\n"
        message += f"🤖 AI-Enhanced Business Intelligence\n\n"
        
        message += "📈 **KEY PERFORMANCE INDICATORS:**\n"
        for kpi, value in dashboard['kpis'].items():
            emoji = "💰" if "revenue" in kpi else "📦" if "order" in kpi else "👥" if "client" in kpi else "📈"
            message += f"{emoji} {kpi.replace('_', ' ').title()}: **{value}**\n"
        
        message += "\n🏆 **TOP PERFORMERS:**\n"
        message += "👑 **Top Clients:**\n"
        for i, (client, revenue) in enumerate(list(dashboard['top_clients'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {client}: ₹{revenue:,.0f}\n"
        
        message += "\n📍 **Top Territories:**\n"
        for i, (location, revenue) in enumerate(list(dashboard['top_locations'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {location}: ₹{revenue:,.0f}\n"
        
        message += "\n🧠 **AI BUSINESS INSIGHTS:**\n"
        for insight, value in dashboard['insights'].items():
            message += f"• {insight.replace('_', ' ').title()}: **{value}**\n"
        
        # Add AI-generated insights
        ai_insight = ai_response_engine.generate_analytics_insight(dashboard)
        message += f"\n{ai_insight}\n"
        
        message += f"\n⏰ Generated: {dashboard['generated_at'][:19]}"
        message += f"\n🤖 Enhanced with AI Intelligence"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"✅ Enhanced dashboard delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate dashboard. Please try again.")
        logger.error(f"Dashboard command error: {e}")

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def predictions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔮 AI-Powered Predictive Analytics with Enhanced Intelligence"""
    user = update.effective_user
    logger.info(f"🔮 Predictions command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n"
            "🔮 Predictive analytics are restricted to administrators.\n\n"
            "💡 Try these commands:\n"
            "• `/today` - Today's performance\n"
            "• `/trends` - Basic trend analysis", 
            parse_mode='Markdown'
        )
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text(
        "🔮 **AI PREDICTIVE ANALYTICS**\n\n"
        "🤖 Advanced AI is analyzing patterns...\n"
        "📊 Processing historical data for forecasts...\n"
        "🧠 Generating intelligent predictions...\n"
        "🎯 Identifying growth opportunities..."
    )
    
    try:
        from analytics import analytics_engine
        
        predictions = analytics_engine.generate_predictive_insights(user.id)
        
        if "error" in predictions:
            await loading_msg.edit_text(f"❌ Predictions Error: {predictions['error']}")
            return
        
        message = "🔮 **AI-POWERED PREDICTIONS** 🚀\n"
        message += "🤖 Enhanced with Machine Learning Intelligence\n\n"
        
        # Revenue Forecast with AI enhancement
        if "revenue_forecast" in predictions and "error" not in predictions["revenue_forecast"]:
            forecast = predictions["revenue_forecast"]
            message += "📈 **REVENUE FORECAST:**\n"
            message += f"• Next 30 Days: **{forecast.get('next_30_days', 'N/A')}**\n"
            message += f"• Daily Average: **{forecast.get('daily_average', 'N/A')}**\n"
            message += f"• Growth Rate: **{forecast.get('growth_rate', 'N/A')}**\n"
            message += f"• AI Confidence: **{forecast.get('confidence', 'N/A')}**\n\n"
        
        # Enhanced Churn Risk Analysis
        if "churn_risk" in predictions and "error" not in predictions["churn_risk"]:
            churn = predictions["churn_risk"]
            risk_emoji = "🚨" if churn.get('risk_level') == "HIGH" else "⚠️" if churn.get('risk_level') == "MODERATE" else "✅"
            message += f"{risk_emoji} **CLIENT RETENTION ANALYSIS:**\n"
            message += f"• Churn Rate: **{churn.get('churn_rate', 'N/A')}**\n"
            message += f"• Risk Level: **{churn.get('risk_level', 'N/A')}**\n"
            message += f"• At-Risk Clients: **{churn.get('inactive_clients', 'N/A')}**\n\n"
        
        # Enhanced Seasonal Intelligence
        if "seasonal_patterns" in predictions and "error" not in predictions["seasonal_patterns"]:
            patterns = predictions["seasonal_patterns"]
            message += "📅 **SEASONAL INTELLIGENCE:**\n"
            message += f"• Optimal Weekday: **{patterns.get('best_weekday', 'N/A')}**\n"
            message += f"• Challenging Day: **{patterns.get('worst_weekday', 'N/A')}**\n"
            message += f"• Peak Month: **{patterns.get('best_month', 'N/A')}**\n"
            message += f"• Prime Hours: **{patterns.get('peak_hour', 'N/A')}**\n\n"
        
        # AI-Enhanced Growth Opportunities
        if "growth_opportunities" in predictions:
            message += "🚀 **AI GROWTH OPPORTUNITIES:**\n"
            for opp in predictions["growth_opportunities"][:3]:
                message += f"• {opp}\n"
            message += "\n"
        
        # Intelligent Risk Assessment
        if "risk_assessment" in predictions:
            message += "⚠️ **INTELLIGENT RISK ASSESSMENT:**\n"
            for risk in predictions["risk_assessment"][:3]:
                message += f"• {risk}\n"
            message += "\n"
        
        # Add AI-powered strategic recommendations
        message += "🧠 **AI STRATEGIC RECOMMENDATIONS:**\n"
        message += "• Focus on high-confidence forecasts\n"
        message += "• Monitor at-risk client relationships\n"
        message += "• Optimize timing based on seasonal patterns\n"
        message += "• Leverage growth opportunities identified\n\n"
        
        message += "🎯 **Next Steps:**\n"
        message += "• Use `/charts` for visual analysis\n"
        message += "• Check `/location_analytics` for territory insights\n"
        message += "• Review `/dashboard` for current performance\n\n"
        
        message += "🤖 **Powered by Advanced AI & Machine Learning**"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🔮 Enhanced predictions delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate predictions. Please try again.")
        logger.error(f"Predictions command error: {e}")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def charts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Generate Professional Analytics Charts with AI Enhancement"""
    user = update.effective_user
    logger.info(f"📊 Charts command called by user {user.id}")
    
    # 👑 ADMIN CHECK
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n"
            "📈 Professional charts are restricted to administrators.\n\n"
            "💡 Try basic analytics:\n"
            "• `/today` - Today's summary\n"
            "• `/week` - Weekly trends", 
            parse_mode='Markdown'
        )
        return
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text(
        "📊 **PROFESSIONAL CHART GENERATION**\n\n"
        "🤖 AI is creating professional visualizations...\n"
        "📈 Generating trend analysis charts...\n"
        "🎨 Applying professional styling...\n"
        "📊 Creating business intelligence visuals..."
    )
    
    try:
        from analytics import analytics_engine
        
        chart_files = analytics_engine.generate_advanced_charts(user.id)
        
        if not chart_files:
            await loading_msg.edit_text(
                "❌ **Chart Generation Failed**\n\n"
                "Possible reasons:\n"
                "• Insufficient data for visualization\n"
                "• Technical configuration issue\n"
                "• Try again after adding more entries\n\n"
                "💡 Use `/today` for text-based analytics"
            )
            return
        
        await loading_msg.edit_text(
            f"✅ **Professional Charts Generated!**\n\n"
            f"📊 Created {len(chart_files)} AI-enhanced visualizations\n"
            f"🎨 Professional business intelligence charts\n"
            f"📈 Ready for executive presentation"
        )
        
        # Send each chart with AI-enhanced descriptions
        chart_descriptions = {
            'revenue_trends': '📈 Revenue performance over time with trend analysis',
            'client_performance': '👥 Client performance ranking and analysis',
            'location_analysis': '📍 Territory performance and geographical insights',
            'growth_patterns': '🚀 Growth patterns and seasonal analysis',
            'correlation_matrix': '🔗 Business metrics correlation intelligence'
        }
        
        for chart_path in chart_files:
            if chart_path and chart_path.endswith('.png'):
                try:
                    chart_name = chart_path.split('/')[-1].split('\\')[-1].replace('.png', '')
                    description = chart_descriptions.get(chart_name, f"📊 Professional {chart_name.replace('_', ' ').title()} Analysis")
                    
                    with open(chart_path, 'rb') as chart_file:
                        await update.message.reply_photo(
                            photo=chart_file,
                            caption=f"**{description}**\n🤖 AI-Enhanced Business Intelligence"
                        )
                    logger.info(f"📈 Sent enhanced chart {chart_name} to user {user.id}")
                except Exception as chart_error:
                    logger.error(f"Failed to send chart {chart_path}: {chart_error}")
        
        # Send AI insights about the charts
        insights_msg = (
            "🧠 **AI CHART INSIGHTS:**\n\n"
            "📊 **How to Use These Charts:**\n"
            "• Look for trend patterns in revenue charts\n"
            "• Identify top performers in client analysis\n"
            "• Use location insights for territory planning\n"
            "• Monitor correlations for business optimization\n\n"
            "🎯 **Strategic Applications:**\n"
            "• Present to stakeholders for decision making\n"
            "• Use for performance reviews and planning\n"
            "• Identify opportunities and risks visually\n"
            "• Track progress against business goals\n\n"
            "💡 **Pro Tip:** Combine with `/predictions` for complete analysis!"
        )
        await update.message.reply_text(insights_msg, parse_mode='Markdown')
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate charts. Please try again.")
        logger.error(f"Charts command error: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True) 
async def analytics_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📚 Comprehensive Analytics Help with AI Enhancement"""
    user = update.effective_user
    logger.info(f"📚 Analytics help requested by user {user.id}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    is_admin = company_manager.is_admin(user.id)
    
    help_text = f"""
📚 **COMPREHENSIVE ANALYTICS GUIDE** 🤖
🏢 **Company:** {company_info['display_name']}
👤 **Access Level:** {'Administrator' if is_admin else 'Standard User'}

🚀 **AI-POWERED FEATURES:**
• 🤖 Natural language processing for entries
• 📍 GPS location tracking and territory analytics
• 🧠 Machine learning insights and predictions
• 📊 Professional business intelligence charts
• 🔮 Predictive analytics and forecasting

{'🔥 **EXECUTIVE LEVEL (Admin Only):**' if is_admin else '📊 **AVAILABLE ANALYTICS:**'}
{'• `/dashboard` - AI-enhanced executive overview' if is_admin else '• `/today` - Today\\'s performance summary'}
{'• `/predictions` - Machine learning forecasts' if is_admin else '• `/week` - Weekly performance report'}
{'• `/charts` - Professional analytical visualizations' if is_admin else '• `/month` - Monthly business review'}

📍 **GPS LOCATION INTELLIGENCE:**
• `/location` - Share GPS for automatic territory tracking
• `/location_status` - Check your GPS location status
• `/location_analytics` - Territory performance insights
• `/location_clear` - Remove stored GPS data

📈 **PERFORMANCE TRACKING:**
• `/today` - AI-enhanced daily performance
• `/week` - Weekly trends with insights
• `/month` - Comprehensive monthly review

🔍 **QUICK INSIGHTS:**
• `/top` - Top clients & locations analysis
• `/batch` - Process multiple entries efficiently

🤖 **AI ENTRY METHODS:**
• **Natural Language:** "Sold 5 units to Apollo for ₹15000"
• **Structured Format:** Client: Apollo, Orders: 5, Amount: ₹15000
• **Batch Processing:** Multiple entries at once

💡 **PRO TIPS WITH AI:**
• Share GPS location for territory insights
• Use natural language - AI understands context
• Check `/dashboard` for comprehensive overview
• Combine `/predictions` with `/charts` for complete analysis
• Use `/batch` for multiple entries efficiently

🎯 **GETTING STARTED:**
1. Share your location: `/location`
2. Set entry mode: `/sales` or `/purchase`
3. Type naturally: "Sold 10 medicines to City Hospital for ₹25000"
4. Check insights: `/location_analytics`
5. Review performance: `/today`

🧠 **AI INTELLIGENCE FEATURES:**
• Smart client and location recognition
• Automatic data validation and suggestions
• Intelligent duplicate detection
• Performance insights and recommendations
• Predictive analytics for business planning

{'🔐 **Admin Features:** Use `/dashboard`, `/predictions`, `/charts` for advanced analytics' if not is_admin else ''}

🤖 **Powered by Advanced AI & Machine Learning**
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
    logger.info(f"📚 Comprehensive analytics help delivered to user {user.id}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def top_performers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 Enhanced Top Performers with AI Insights"""
    user = update.effective_user
    logger.info(f"🏆 Top performers requested by user {user.id}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text(
        "🏆 **TOP PERFORMERS ANALYSIS**\n\n"
        "🤖 AI is analyzing performance data...\n"
        "📊 Ranking clients and territories...\n"
        "🧠 Generating intelligent insights..."
    )
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Error: {dashboard['error']}")
            return
        
        message = "🏆 **TOP PERFORMERS** 🚀\n"
        message += "🤖 AI-Enhanced Performance Analysis\n\n"
        
        message += "👑 **TOP CLIENTS:**\n"
        for i, (client, revenue) in enumerate(list(dashboard['top_clients'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {client}: **₹{revenue:,.0f}**\n"
        
        message += "\n🏢 **TOP TERRITORIES:**\n"
        for i, (location, revenue) in enumerate(list(dashboard['top_locations'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {location}: **₹{revenue:,.0f}**\n"
        
        # Add AI-enhanced quick stats
        kpis = dashboard['kpis']
        message += f"\n📊 **AI PERFORMANCE METRICS:**\n"
        message += f"• Total Revenue: **{kpis.get('total_revenue', 'N/A')}**\n"
        message += f"• Total Orders: **{kpis.get('total_orders', 'N/A')}**\n"
        message += f"• Growth Trend: **{kpis.get('growth_trend', 'N/A')}**\n"
        message += f"• Client Diversity: **{len(dashboard['top_clients'])} active clients**\n"
        
        # Add AI insights
        message += f"\n🧠 **AI INSIGHTS:**\n"
        if len(dashboard['top_clients']) > 0:
            top_client = list(dashboard['top_clients'].keys())[0]
            message += f"• **{top_client}** is your strongest client relationship\n"
        
        if len(dashboard['top_locations']) > 0:
            top_location = list(dashboard['top_locations'].keys())[0]
            message += f"• **{top_location}** is your most profitable territory\n"
        
        message += f"• Diversification across {len(dashboard['top_clients'])} clients reduces risk\n"
        
        # Add strategic recommendations
        message += f"\n🎯 **AI RECOMMENDATIONS:**\n"
        message += f"• Strengthen relationships with top 3 clients\n"
        message += f"• Expand presence in high-performing territories\n"
        message += f"• Use `/location_analytics` for territory optimization\n"
        message += f"• Consider `/predictions` for growth forecasting\n"
        
        # Add motivational AI message
        motivation = ai_response_engine.generate_motivation_message({'top_performers': True})
        message += f"\n{motivation}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🏆 Enhanced top performers delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to get top performers. Please try again.")
        logger.error(f"Top performers command error: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def location_analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📍 Enhanced GPS Location Analytics with AI Territory Insights"""
    user = update.effective_user
    logger.info(f"📍 Location analytics requested by user {user.id}")
    
    # Check if user is registered with a company
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text(
        "📍 **GPS LOCATION ANALYTICS**\n\n"
        "🤖 AI is analyzing your territory data...\n"
        "🗺️ Processing GPS location patterns...\n"
        "📊 Generating territory performance insights...\n"
        "🧠 Creating strategic recommendations..."
    )
    
    try:
        from analytics import analytics_engine
        
        location_analytics = analytics_engine.generate_location_analytics(user.id)
        
        if not location_analytics['has_location_data']:
            await loading_msg.edit_text(
                "📍 **GPS LOCATION ANALYTICS**\n\n"
                f"{location_analytics['message']}\n\n"
                "🚀 **Get Started with GPS Tracking:**\n"
                "1. Share your location: `/location`\n"
                "2. Make some sales entries\n"
                "3. Return here for territory insights!\n\n"
                "🌍 **Benefits of GPS Tracking:**\n"
                "• Automatic territory performance analysis\n"
                "• Client distribution insights\n"
                "• Route optimization recommendations\n"
                "• Market penetration analysis\n\n"
                "💡 **Pro Tip:** GPS location is automatically added to all your entries!"
            )
            return
        
        message = "📍 **GPS LOCATION ANALYTICS** 🚀\n"
        message += "🤖 AI-Enhanced Territory Intelligence\n\n"
        
        # Territory Overview with AI enhancement
        distribution = location_analytics['distribution']
        message += "🗺️ **TERRITORY OVERVIEW:**\n"
        message += f"📍 Active GPS Locations: **{distribution['total_locations']}**\n"
        message += f"💰 Total Territory Revenue: **₹{distribution['total_revenue']:,.0f}**\n"
        message += f"🏆 Top Performing Territory: **{distribution['top_location']['name']}**\n"
        message += f"💎 Top Territory Revenue: **₹{distribution['top_location']['revenue']:,.0f}**\n\n"
        
        # Performance by Location with AI insights
        performance = location_analytics['performance']
        message += "📊 **TERRITORY PERFORMANCE RANKING:**\n"
        for i, (location, stats) in enumerate(list(performance.items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} **{location}**\n"
            message += f"   💰 Revenue: ₹{stats['revenue']:,.0f}\n"
            message += f"   📦 Orders: {stats['orders']} | 👥 Clients: {stats['clients']}\n"
            message += f"   📈 Avg per Entry: ₹{stats['avg_revenue']:,.0f}\n\n"
        
        # AI-Enhanced Growth Opportunities
        if location_analytics['opportunities']:
            message += "🚀 **AI TERRITORY OPPORTUNITIES:**\n"
            for opp in location_analytics['opportunities'][:3]:
                message += f"• {opp}\n"
            message += "\n"
        
        # Enhanced Coverage Stats
        message += f"📊 **GPS COVERAGE INTELLIGENCE:**\n"
        message += f"• Entries with GPS: **{location_analytics['total_entries_with_gps_location']}/{location_analytics['total_entries']}**\n"
        message += f"• GPS Coverage Rate: **{location_analytics['gps_location_coverage']:.1f}%**\n"
        
        coverage_rating = "🔥 Excellent" if location_analytics['gps_location_coverage'] >= 80 else "📈 Good" if location_analytics['gps_location_coverage'] >= 60 else "⚡ Improving"
        message += f"• Coverage Rating: **{coverage_rating}**\n\n"
        
        # AI Strategic Recommendations
        message += "🧠 **AI STRATEGIC RECOMMENDATIONS:**\n"
        if location_analytics['gps_location_coverage'] < 80:
            message += "• Share GPS location more frequently for better insights\n"
        
        if len(performance) >= 3:
            message += "• Focus on expanding top 3 territories\n"
            message += "• Analyze underperforming areas for improvement\n"
        
        message += "• Use territory data for route optimization\n"
        message += "• Consider client density when planning visits\n\n"
        
        # Advanced Analytics Suggestions
        message += "🎯 **ADVANCED ANALYTICS:**\n"
        message += "• Use `/dashboard` for complete business overview\n"
        message += "• Try `/predictions` for territory growth forecasts\n"
        message += "• Check `/charts` for visual territory analysis\n"
        message += "• Review `/top` for client-territory combinations\n\n"
        
        # GPS Management
        message += "📱 **GPS MANAGEMENT:**\n"
        message += "• `/location` - Update your current GPS location\n"
        message += "• `/location_status` - Check GPS location status\n"
        message += "• `/location_clear` - Remove stored GPS data\n\n"
        
        # Add motivational AI message
        motivation = ai_response_engine.generate_motivation_message({'territory_analysis': True})
        message += f"{motivation}\n\n"
        
        message += "🤖 **Powered by AI Territory Intelligence**"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"📍 Enhanced location analytics delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate location analytics. Please try again.")
        logger.error(f"Location analytics command error: {e}")

# ═══════════════════════════════════════════════════════════════
# 🎯 UTILITY AND HELPER COMMANDS
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """❓ Comprehensive help command with AI enhancement"""
    user = update.effective_user
    logger.info(f"❓ Help command called by user {user.id}")
    
    # Generate AI-powered personalized help
    help_text = (
        f"❓ **COMPREHENSIVE HELP GUIDE** 🤖\n\n"
        f"{ai_response_engine.generate_greeting_response(user.first_name)}\n\n"
        "🚀 **QUICK START:**\n"
        "1. `/company` - Select your company\n"
        "2. `/location` - Share GPS for territory tracking\n"
        "3. `/sales` or `/purchase` - Set entry mode\n"
        "4. Type naturally: \"Sold 5 units to Apollo for ₹15000\"\n\n"
        "🤖 **AI-POWERED FEATURES:**\n"
        "• Natural language understanding\n"
        "• GPS location tracking\n"
        "• Intelligent data validation\n"
        "• Predictive analytics\n"
        "• Professional chart generation\n\n"
        "📊 **ANALYTICS COMMANDS:**\n"
        "• `/analytics` - Complete analytics guide\n"
        "• `/dashboard` - Executive overview (Admin)\n"
        "• `/predictions` - AI forecasts (Admin)\n"
        "• `/location_analytics` - Territory insights\n\n"
        "💡 **Need specific help?**\n"
        "• `/analytics` - Analytics guide\n"
        "• Type your question naturally - AI understands!\n\n"
        f"🎯 **Daily Tip:** {ai_response_engine.generate_tip_of_the_day()}"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 System status with AI enhancement"""
    user = update.effective_user
    logger.info(f"📊 Status command called by user {user.id}")
    
    # Check user registration
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    
    # Get GPS location status
    try:
        from location_storage import location_storage
        gps_status = location_storage.get_location_status(str(user.id), current_company)
    except:
        gps_status = {'has_location': False}
    
    status_text = (
        f"📊 **SYSTEM STATUS** 🤖\n\n"
        f"👤 **User:** {user.first_name} {user.last_name or ''}\n"
        f"🏢 **Company:** {company_info['display_name']}\n"
        f"🆔 **User ID:** {user.id}\n"
        f"📱 **Username:** @{user.username or 'Not set'}\n\n"
        f"📍 **GPS Status:** {'✅ Active' if gps_status['has_location'] else '❌ Not shared'}\n"
        f"🤖 **AI Features:** ✅ Active\n"
        f"📊 **Analytics:** ✅ Available\n"
        f"🔄 **Entry Mode:** {context.user_data.get('type', 'Not set')}\n\n"
        f"🎯 **Quick Actions:**\n"
        f"• Share GPS: `/location`\n"
        f"• Set entry mode: `/sales` or `/purchase`\n"
        f"• View analytics: `/analytics`\n\n"
        f"💡 **AI Tip:** {ai_response_engine.generate_tip_of_the_day()}"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')