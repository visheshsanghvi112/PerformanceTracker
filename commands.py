#!/usr/bin/env python3
"""
📋 ENHANCED COMMANDS MODULE
==========================
Advanced command handlers with AI integration and intelligent responses
"""

from telegram import Update
from telegram.ext import ContextTypes
import datetime
from typing import Dict, Any, Optional

# Core imports
from summaries import send_summary
from menus import MenuSystem
from decorators import handle_errors, rate_limit
from logger import logger
from company_manager import company_manager

# AI and processing imports
from ai_response_engine import ai_response_engine
from input_processor import input_processor
from batch_handler import batch_handler
from parallel_processor import parallel_processor

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 Enhanced start command with AI-powered personalized greeting"""
    user = update.effective_user
    logger.info(f"🚀 Start command called by user {user.id} ({user.full_name or 'No name'})")
    
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
        "🚀 **WHAT'S NEW:**\n"
        "• 🤖 AI-powered natural language processing\n"
        "• 📍 GPS location tracking for territory insights\n"
        "• 📊 Advanced analytics with predictive insights\n"
        "• 📦 Batch processing for multiple entries\n"
        "• ⚡ High-performance parallel processing\n\n"
        "📊 **ANALYTICS COMMANDS:**\n"
        "• `/dashboard` - Executive business overview\n"
        "• `/predictions` - AI-powered forecasts & insights\n"
        "• `/charts` - Professional analytical charts\n"
        "• `/location_analytics` - Territory performance insights\n"
        "• `/top` - Top performing clients & locations\n\n"
        "📝 **ENTRY COMMANDS:**\n"
        "• `/sales` - Log sales entries (supports natural language)\n"
        "• `/purchase` - Log purchase entries (AI-enhanced)\n"
        "• `/today` - View today's summary\n\n"
        "📍 **LOCATION COMMANDS:**\n"
        "• `/location` - Share GPS location for territory tracking\n"
        "• `/location_status` - Check GPS location status\n"
        "• `/location_clear` - Remove GPS location data\n\n"
        "📍 **LIVE POSITION COMMANDS:**\n"
        "• `/position` - Share live position for real-time tracking\n"
        "• `/position_status` - Check live position status\n"
        "• `/position_clear` - Remove live position data\n"
        "• `/position_update` - Refresh live position\n"
        "• `/position_analytics` - View live position insights\n\n"
        "🏢 **COMPANY COMMANDS:**\n"
        "• `/company` - Switch companies or view company info\n\n"
        "💡 **Pro Tip:** Try natural language! Say 'Sold 5 tablets to Apollo for ₹25000' and I'll understand!"
    )
    
    # Add tip of the day
    tip = ai_response_engine.generate_tip_of_the_day()
    welcome_text += f"\n\n{tip}"
    
    menu_system = MenuSystem()
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=menu_system.create_main_menu(),
        parse_mode='Markdown'
    )
    logger.info(f"✅ Enhanced start command completed for user {user.id}")

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Enhanced sales command with AI guidance and batch processing support"""
    user = update.effective_user
    logger.info(f"📊 Sales command called by user {user.id} ({user.full_name or 'No name'})")
    
    context.user_data['type'] = 'Sales'
    logger.debug(f"🔧 Set user {user.id} context to 'Sales' mode")
    
    # Generate AI-powered sales guidance
    sales_text = (
        "📊 **Sales Entry Mode Activated!**\n\n"
        "🤖 **AI-POWERED ENTRY METHODS:**\n\n"
        "**🗣 Method 1: Natural Language (Recommended)**\n"
        "Just describe your sale naturally - I understand context!\n"
        "_\"Sold 5 medicines to City Hospital in Andheri for ₹15000. Great meeting with procurement head.\"_\n\n"
        "**📝 Method 2: Structured Format**\n"
        "```\n"
        "Client: Apollo Pharmacy\n"
        "Location: Bandra\n"
        "Orders: 3 + 5 (I'll calculate: 8 total)\n"
        "Amount: ₹24000\n"
        "Remarks: Good conversation\n"
        "```\n\n"
        "**📦 Method 3: Batch Processing**\n"
        "Enter multiple sales at once, separated by blank lines:\n"
        "_Sale 1: Apollo - 5 units - ₹15000_\n\n"
        "_Sale 2: MedPlus - 3 boxes - ₹8000_\n\n"
        "**✨ AI FEATURES:**\n"
        "• 🧠 Smart parsing of complex orders (3 boxes + 5 bottles = 8 units)\n"
        "• 📍 Automatic GPS location tagging\n"
        "• ⚠️ Intelligent validation with helpful warnings\n"
        "• 🔄 Batch processing for multiple entries\n"
        "• 💡 Context-aware suggestions and tips\n\n"
        "**🎯 EXAMPLES THAT WORK:**\n"
        "• \"Apollo pharmacy 5 tablets 25000 rupees\"\n"
        "• \"Sold 10 units to MedCorp for ₹15k urgent delivery\"\n"
        "• \"3 boxes + 2 bottles to City Hospital ₹12000\"\n\n"
        "💡 **Pro Tip:** I understand abbreviations, calculations, and casual language!"
    )
    
    await update.message.reply_text(
        text=sales_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def purchase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📦 Enhanced purchase command with AI guidance"""
    user = update.effective_user
    logger.info(f"📦 Purchase command called by user {user.id}")
    
    context.user_data['type'] = 'Purchase'
    
    purchase_text = (
        "📦 **Purchase Entry Mode Activated!**\n\n"
        "🤖 **AI-POWERED PURCHASE TRACKING:**\n\n"
        "**🗣 Natural Language Processing**\n"
        "Describe your purchase naturally:\n"
        "_\"Bought 10 units from MedSupply in Worli for ₹25000. Emergency stock replenishment.\"_\n\n"
        "**📝 Structured Format**\n"
        "```\n"
        "Supplier: ABC Medical Supplies\n"
        "Location: Lower Parel\n"
        "Items: 2 boxes + 5 bottles\n"
        "Amount: ₹18000\n"
        "Remarks: Delivered new stock\n"
        "```\n\n"
        "**📦 Batch Purchase Processing**\n"
        "Log multiple purchases at once:\n"
        "_Purchase 1: MedSupply - 10 units - ₹15000_\n\n"
        "_Purchase 2: PharmaCorp - 5 boxes - ₹8000_\n\n"
        "**✨ AI FEATURES:**\n"
        "• 🧠 Smart supplier name recognition\n"
        "• 📍 GPS location for delivery tracking\n"
        "• 💰 Automatic cost analysis and warnings\n"
        "• 📊 Inventory impact assessment\n"
        "• 🔄 Bulk purchase processing\n\n"
        "**🎯 PURCHASE EXAMPLES:**\n"
        "• \"Bought from XYZ supplier 20 tablets ₹8000\"\n"
        "• \"Emergency purchase MedCorp 15 units ₹12k\"\n"
        "• \"5 boxes + 3 bottles from ABC ₹18000 urgent\"\n\n"
        "💡 **Pro Tip:** Include supplier name, quantity, and total cost for best tracking!"
    )
    
    await update.message.reply_text(
        text=purchase_text,
        parse_mode='Markdown'
    )

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📅 Enhanced today command with AI insights"""
    user = update.effective_user
    logger.info(f"📅 Today summary requested by user {user.id}")
    
    # Send AI-powered loading message
    loading_messages = [
        "📊 Analyzing today's performance...",
        "🔍 Gathering today's business insights...",
        "📈 Processing today's data with AI...",
        "🤖 Generating intelligent summary..."
    ]
    loading_msg = await update.message.reply_text(
        ai_response_engine.response_templates['tips'][0] if hasattr(ai_response_engine, 'response_templates') 
        else "📊 Generating today's summary..."
    )
    
    try:
        today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Today's", today_date)
        
        # Add AI motivation
        motivation = ai_response_engine.generate_motivation_message()
        await update.message.reply_text(f"\n{motivation}")
        
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate summary. Please try again.")
        logger.error(f"Error generating today's summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📈 Enhanced weekly command with trend analysis"""
    user = update.effective_user
    logger.info(f"📈 Weekly summary requested by user {user.id}")
    
    loading_msg = await update.message.reply_text("📈 Analyzing weekly trends with AI...")
    
    try:
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        week_ago = week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Weekly", week_ago)
        
        # Add weekly insights
        insight_msg = "📊 **Weekly Insights:** Consistent performance tracking leads to better business decisions!"
        await update.message.reply_text(insight_msg, parse_mode='Markdown')
        
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate weekly summary. Please try again.")
        logger.error(f"Error generating weekly summary: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📅 Enhanced monthly command with comprehensive analysis"""
    user = update.effective_user
    logger.info(f"📅 Monthly summary requested by user {user.id}")
    
    loading_msg = await update.message.reply_text("📅 Generating comprehensive monthly analysis...")
    
    try:
        month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        await send_summary(update, context, "Monthly", month_ago)
        
        # Add monthly business insight
        monthly_tip = ai_response_engine.generate_tip_of_the_day()
        await update.message.reply_text(f"💡 **Monthly Insight:** {monthly_tip}")
        
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text("⚠️ Failed to generate monthly summary. Please try again.")
        logger.error(f"Error generating monthly summary: {e}")

# ═══════════════════════════════════════════════════════════════
# 🚀 ADVANCED ANALYTICS COMMANDS WITH AI INTEGRATION
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 AI-Enhanced Executive Dashboard"""
    user = update.effective_user
    logger.info(f"📊 Dashboard command called by user {user.id}")
    
    # Admin check
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n📊 Analytics commands are restricted to administrators only.", 
            parse_mode='Markdown'
        )
        return
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🤖 AI is analyzing your business data...")
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Dashboard Error: {dashboard['error']}")
            return
        
        # Generate AI insights for the dashboard
        ai_insights = ai_response_engine.generate_analytics_insight(dashboard)
        
        message = f"📊 **AI-ENHANCED EXECUTIVE DASHBOARD**\n"
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
        
        message += "\n🧠 **AI BUSINESS INSIGHTS:**\n"
        for insight, value in dashboard['insights'].items():
            message += f"• {insight.replace('_', ' ').title()}: **{value}**\n"
        
        message += f"\n{ai_insights}"
        message += f"\n⏰ Generated: {dashboard['generated_at'][:19]}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"✅ AI-enhanced dashboard delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate dashboard. Please try again.")
        logger.error(f"Dashboard command error: {e}")

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def predictions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔮 AI-Powered Predictive Analytics"""
    user = update.effective_user
    logger.info(f"🔮 Predictions command called by user {user.id}")
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n🔮 Analytics commands are restricted to administrators only.", 
            parse_mode='Markdown'
        )
        return
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🔮 AI is analyzing patterns and generating predictions...")
    
    try:
        from analytics import analytics_engine
        
        predictions = analytics_engine.generate_predictive_insights(user.id)
        
        if "error" in predictions:
            await loading_msg.edit_text(f"❌ Predictions Error: {predictions['error']}")
            return
        
        message = "🔮 **AI-POWERED PREDICTIONS & INSIGHTS**\n\n"
        
        # Revenue Forecast
        if "revenue_forecast" in predictions and "error" not in predictions["revenue_forecast"]:
            forecast = predictions["revenue_forecast"]
            message += "📈 **REVENUE FORECAST:**\n"
            message += f"• Next 30 Days: **{forecast.get('next_30_days', 'N/A')}**\n"
            message += f"• Daily Average: **{forecast.get('daily_average', 'N/A')}**\n"
            message += f"• Growth Rate: **{forecast.get('growth_rate', 'N/A')}**\n"
            message += f"• AI Confidence: **{forecast.get('confidence', 'N/A')}**\n\n"
        
        # Churn Risk Analysis
        if "churn_risk" in predictions and "error" not in predictions["churn_risk"]:
            churn = predictions["churn_risk"]
            risk_emoji = "🚨" if churn.get('risk_level') == "HIGH" else "⚠️" if churn.get('risk_level') == "MODERATE" else "✅"
            message += f"{risk_emoji} **CLIENT RETENTION ANALYSIS:**\n"
            message += f"• Churn Rate: **{churn.get('churn_rate', 'N/A')}**\n"
            message += f"• Risk Level: **{churn.get('risk_level', 'N/A')}**\n"
            message += f"• At-Risk Clients: **{churn.get('inactive_clients', 'N/A')}**\n\n"
        
        # Seasonal Intelligence
        if "seasonal_patterns" in predictions and "error" not in predictions["seasonal_patterns"]:
            patterns = predictions["seasonal_patterns"]
            message += "📅 **SEASONAL INTELLIGENCE:**\n"
            message += f"• Optimal Weekday: **{patterns.get('best_weekday', 'N/A')}**\n"
            message += f"• Challenging Day: **{patterns.get('worst_weekday', 'N/A')}**\n"
            message += f"• Peak Month: **{patterns.get('best_month', 'N/A')}**\n"
            message += f"• Prime Hours: **{patterns.get('peak_hour', 'N/A')}**\n\n"
        
        # AI Growth Opportunities
        if "growth_opportunities" in predictions:
            message += "🚀 **AI-IDENTIFIED OPPORTUNITIES:**\n"
            for opp in predictions["growth_opportunities"][:3]:
                message += f"• {opp}\n"
            message += "\n"
        
        # Risk Assessment
        if "risk_assessment" in predictions:
            message += "⚠️ **INTELLIGENT RISK ASSESSMENT:**\n"
            for risk in predictions["risk_assessment"][:3]:
                message += f"• {risk}\n"
        
        # Add AI motivation
        motivation = ai_response_engine.generate_motivation_message()
        message += f"\n💡 **AI Insight:** {motivation}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🔮 AI predictions delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate predictions. Please try again.")
        logger.error(f"Predictions command error: {e}")

@rate_limit(calls_per_minute=2)
@handle_errors(notify_user=True)
async def charts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 AI-Enhanced Professional Charts Generation"""
    user = update.effective_user
    logger.info(f"📊 Charts command called by user {user.id}")
    
    if not company_manager.is_admin(user.id):
        await update.message.reply_text(
            "❌ **Access Denied**\n\n📈 Analytics commands are restricted to administrators only.", 
            parse_mode='Markdown'
        )
        return
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("📊 AI is creating professional charts with parallel processing...")
    
    try:
        from analytics import analytics_engine
        
        # Use parallel processing for chart generation
        chart_files = await parallel_processor.process_chart_generation_parallel([
            {'type': 'revenue_trend', 'user_id': user.id},
            {'type': 'client_performance', 'user_id': user.id},
            {'type': 'location_analysis', 'user_id': user.id}
        ])
        
        if not chart_files:
            # Fallback to regular chart generation
            chart_files = analytics_engine.generate_advanced_charts(user.id)
        
        if not chart_files:
            await loading_msg.edit_text("❌ No charts generated. Need more data or check configuration.")
            return
        
        await loading_msg.edit_text(f"✅ AI generated {len(chart_files)} professional charts with insights!")
        
        # Send each chart with AI-generated insights
        for i, chart_path in enumerate(chart_files):
            if chart_path and chart_path.endswith('.png'):
                try:
                    chart_name = chart_path.split('/')[-1].split('\\')[-1]
                    
                    # Generate AI insight for each chart
                    chart_insight = f"📊 **{chart_name.replace('_', ' ').replace('.png', '').title()}**\n"
                    chart_insight += f"🤖 AI Analysis: Professional visualization #{i+1} with intelligent data processing"
                    
                    with open(chart_path, 'rb') as chart_file:
                        await update.message.reply_photo(
                            photo=chart_file,
                            caption=chart_insight
                        )
                    logger.info(f"📈 Sent AI-enhanced chart {chart_name} to user {user.id}")
                except Exception as chart_error:
                    logger.error(f"Failed to send chart {chart_path}: {chart_error}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate charts. Please try again.")
        logger.error(f"Charts command error: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def location_analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📍 Enhanced GPS Location Analytics with Comprehensive Territory Intelligence"""
    user = update.effective_user
    logger.info(f"📍 Location analytics requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("📍 AI is analyzing GPS location data and territory patterns...")
    
    try:
        from analytics import AdvancedAnalytics
        analytics_engine = AdvancedAnalytics()
        
        location_analytics = analytics_engine.generate_location_analytics(user.id)
        
        if "error" in location_analytics:
            await loading_msg.edit_text(f"❌ {location_analytics['error']}")
            return
        
        message = "📍 **COMPREHENSIVE GPS LOCATION ANALYTICS**\n\n"
        message += f"📅 **Analysis Period:** {location_analytics['period']}\n\n"
        
        # GPS Coverage Overview
        gps_coverage = location_analytics['gps_coverage']
        coverage_pct = gps_coverage['coverage_percentage']
        coverage_emoji = "🎯" if coverage_pct > 80 else "📈" if coverage_pct > 60 else "💡"
        
        message += f"{coverage_emoji} **GPS COVERAGE ANALYSIS:**\n"
        message += f"• Total Entries: {gps_coverage['total_entries']}\n"
        message += f"• GPS Enhanced: {gps_coverage['gps_enhanced_entries']}\n"
        message += f"• Coverage Rate: {coverage_pct:.1f}%\n\n"
        
        # Territory Performance
        territory_perf = location_analytics['territory_performance']
        if territory_perf.get('total_territories', 0) > 0:
            message += "🗺️ **TERRITORY PERFORMANCE:**\n"
            message += f"• Total Territories: {territory_perf['total_territories']}\n"
            
            top_territory = territory_perf['top_territory']
            message += f"• Top Territory: **{top_territory['name']}**\n"
            message += f"  💰 Revenue: {top_territory['revenue']}\n"
            message += f"  📍 Visits: {top_territory['visits']}\n\n"
            
            # Territory Rankings
            rankings = territory_perf.get('territory_rankings', {})
            if rankings:
                message += "🏆 **TOP TERRITORIES:**\n"
                for i, (location, stats) in enumerate(list(rankings.items())[:3], 1):
                    efficiency_emoji = "🔥" if stats['efficiency_score'] > 20000 else "📈" if stats['efficiency_score'] > 10000 else "💡"
                    message += f"{i}. {efficiency_emoji} **{location}**\n"
                    message += f"   💰 {stats['revenue']} | 📍 {stats['visits']} visits\n"
                    message += f"   👥 {stats['clients']} clients | ⚡ ₹{stats['efficiency_score']}/visit\n"
                message += "\n"
        
        # Location Efficiency Analysis
        efficiency = location_analytics['location_efficiency']
        if 'overall_metrics' in efficiency:
            overall = efficiency['overall_metrics']
            message += "📊 **LOCATION EFFICIENCY:**\n"
            message += f"• Avg Revenue/Location: {overall['avg_revenue_per_location']}\n"
            message += f"• Avg Visits/Location: {overall['avg_visits_per_location']}\n"
            
            # GPS vs Manual comparison
            gps_vs_manual = efficiency.get('gps_vs_manual', {})
            if gps_vs_manual:
                gps_data = gps_vs_manual['gps_enhanced']
                manual_data = gps_vs_manual['manual_entry']
                
                message += f"\n🎯 **GPS vs Manual Entry:**\n"
                message += f"• GPS Enhanced: {gps_data['count']} entries, {gps_data['avg_revenue']} avg\n"
                message += f"• Manual Entry: {manual_data['count']} entries, {manual_data['avg_revenue']} avg\n"
                
                advantage = gps_vs_manual.get('gps_advantage', {})
                if advantage.get('revenue_boost') != 'N/A':
                    message += f"• GPS Advantage: {advantage['revenue_boost']} revenue boost\n"
            message += "\n"
        
        # Geographic Distribution
        geo_dist = location_analytics['geographic_distribution']
        if geo_dist.get('status') == 'success':
            coverage_area = geo_dist['coverage_area']
            message += "🌍 **GEOGRAPHIC DISTRIBUTION:**\n"
            message += f"• Coverage Area: {coverage_area['approximate_coverage']}\n"
            message += f"• Center Point: {coverage_area['center_point']}\n"
            
            zones = geo_dist.get('performance_zones', {})
            if zones:
                message += f"• Performance Zones:\n"
                for zone, stats in zones.items():
                    message += f"  - {zone}: {stats['total_revenue']} ({stats['visit_count']} visits)\n"
            message += "\n"
        
        # Route Optimization
        route_insights = location_analytics['route_optimization']
        if route_insights.get('status') == 'success':
            route_metrics = route_insights['route_metrics']
            optimization = route_insights['optimization_insights']
            
            message += "🛣️ **ROUTE OPTIMIZATION:**\n"
            message += f"• Total Distance: {route_metrics['total_distance_covered']}\n"
            message += f"• Avg Distance/Visit: {route_metrics['average_distance_between_visits']}\n"
            message += f"• Efficiency Score: {optimization['efficiency_score']:.0f}%\n"
            message += f"• Optimization Potential: {optimization['optimization_potential']}\n"
            message += f"• Recommendation: {optimization['recommendation']}\n\n"
        
        # Location Trends
        trends = location_analytics['location_trends']
        if 'trending_locations' in trends:
            trending = trends['trending_locations']
            if trending.get('growing'):
                message += "📈 **TRENDING LOCATIONS:**\n"
                message += "Growing:\n"
                for location, trend in list(trending['growing'].items())[:2]:
                    message += f"  • {location}: {trend}\n"
            
            gps_adoption = trends.get('gps_adoption', {})
            if gps_adoption:
                message += f"\n📍 **GPS Adoption:** {gps_adoption['trend']} ({gps_adoption['current_rate']})\n"
                message += f"💡 {gps_adoption['recommendation']}\n"
        
        # AI Recommendations
        if coverage_pct < 80:
            message += f"\n🤖 **AI RECOMMENDATION:**\n"
            message += f"Share your GPS location more frequently to unlock:\n"
            message += f"• Advanced territory insights\n"
            message += f"• Route optimization suggestions\n"
            message += f"• Geographic performance analysis\n"
        else:
            message += f"\n🎉 **EXCELLENT GPS COVERAGE!**\n"
            message += f"Your territory data enables advanced business intelligence.\n"
        
        # Add motivational AI message
        motivation = ai_response_engine.generate_motivation_message()
        message += f"\n💪 {motivation}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"📍 Enhanced location analytics delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate location analytics. Please try again.")
        logger.error(f"Location analytics command error: {e}")

@rate_limit(calls_per_minute=3)
@handle_errors(notify_user=True)
async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Enhanced Executive Dashboard with Location Intelligence"""
    user = update.effective_user
    logger.info(f"📊 Dashboard requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("📊 AI is generating your executive dashboard with location intelligence...")
    
    try:
        from analytics import AdvancedAnalytics
        analytics_engine = AdvancedAnalytics()
        
        # Generate executive dashboard
        dashboard_data = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard_data:
            await loading_msg.edit_text(f"❌ {dashboard_data['error']}")
            return
        
        # Generate location analytics for dashboard integration
        location_data = analytics_engine.generate_location_analytics(user.id)
        
        # Build comprehensive dashboard message
        message = "📊 **EXECUTIVE DASHBOARD**\n\n"
        message += f"📅 **Period:** {dashboard_data['period']}\n\n"
        
        # Core KPIs
        kpis = dashboard_data['kpis']
        message += "💼 **KEY PERFORMANCE INDICATORS:**\n"
        message += f"💰 Total Revenue: **{kpis['total_revenue']}**\n"
        message += f"📦 Total Orders: **{kpis['total_orders']}**\n"
        message += f"👥 Unique Clients: **{kpis['unique_clients']}**\n"
        message += f"📊 Avg Order Value: **{kpis['avg_order_value']}**\n"
        message += f"📈 Growth Trend: **{kpis['growth_trend']}**\n\n"
        
        # Top Performers
        top_clients = dashboard_data['top_clients']
        if top_clients:
            message += "🏆 **TOP CLIENTS:**\n"
            for i, (client, revenue) in enumerate(list(top_clients.items())[:3], 1):
                message += f"{i}. **{client}**: ₹{revenue:,.0f}\n"
            message += "\n"
        
        top_locations = dashboard_data['top_locations']
        if top_locations:
            message += "📍 **TOP LOCATIONS:**\n"
            for i, (location, revenue) in enumerate(list(top_locations.items())[:3], 1):
                message += f"{i}. **{location}**: ₹{revenue:,.0f}\n"
            message += "\n"
        
        # Business Insights
        insights = dashboard_data['insights']
        message += "🧠 **BUSINESS INSIGHTS:**\n"
        message += f"🔄 Client Retention: **{insights['client_retention_score']}**\n"
        message += f"⚡ Location Efficiency: **{insights['location_efficiency_score']}**\n"
        message += f"📊 Revenue Concentration: **{insights['revenue_concentration']}**\n\n"
        
        # Location Intelligence Integration
        if "error" not in location_data:
            gps_coverage = location_data.get('gps_coverage', {})
            coverage_pct = gps_coverage.get('coverage_percentage', 0)
            
            message += "📍 **LOCATION INTELLIGENCE:**\n"
            message += f"🎯 GPS Coverage: **{coverage_pct:.1f}%**\n"
            
            if coverage_pct > 0:
                territory_perf = location_data.get('territory_performance', {})
                if territory_perf.get('total_territories', 0) > 0:
                    message += f"🗺️ Active Territories: **{territory_perf['total_territories']}**\n"
                    
                    top_territory = territory_perf.get('top_territory', {})
                    if top_territory.get('name'):
                        message += f"🏆 Top Territory: **{top_territory['name']}**\n"
                
                # Route efficiency if available
                route_insights = location_data.get('route_optimization', {})
                if route_insights.get('status') == 'success':
                    efficiency_score = route_insights.get('optimization_insights', {}).get('efficiency_score', 0)
                    message += f"🛣️ Route Efficiency: **{efficiency_score:.0f}%**\n"
            
            message += "\n"
        
        # AI Recommendations
        message += "🤖 **AI RECOMMENDATIONS:**\n"
        
        # Performance-based recommendations
        if float(kpis['growth_trend'].replace('%', '').replace('+', '')) < 0:
            message += "• Focus on client retention and upselling\n"
        
        if coverage_pct < 50:
            message += "• Share GPS location to unlock territory insights\n"
        elif coverage_pct < 80:
            message += "• Increase GPS sharing for better route optimization\n"
        else:
            message += "• Excellent GPS coverage - leverage territory analytics\n"
        
        # Add motivational message
        motivation = ai_response_engine.generate_motivation_message()
        message += f"\n💪 **DAILY MOTIVATION:**\n{motivation}\n\n"
        
        message += f"📊 **Quick Actions:**\n"
        message += f"• `/location_analytics` - Detailed territory insights\n"
        message += f"• `/predictions` - AI forecasts\n"
        message += f"• `/charts` - Visual analytics\n"
        message += f"• `/location` - Share GPS for better insights"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"📊 Executive dashboard with location intelligence delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate dashboard. Please try again.")
        logger.error(f"Dashboard command error: {e}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True) 
async def analytics_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📚 AI-Enhanced Analytics Help"""
    user = update.effective_user
    logger.info(f"📚 Analytics help requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    
    help_text = f"""
📚 **AI-ENHANCED ANALYTICS COMMANDS**
🏢 **Current Company:** {company_info['display_name']}

🤖 **AI-POWERED EXECUTIVE LEVEL:**
• `/dashboard` - AI-enhanced business overview with intelligent insights
• `/predictions` - Machine learning forecasts & predictive analytics

📊 **INTELLIGENT VISUAL ANALYTICS:**  
• `/charts` - AI-generated professional charts with parallel processing
• `/trends` - Smart revenue & performance trend analysis

📍 **GPS TERRITORY INTELLIGENCE:**
• `/location_analytics` - AI territory insights with GPS data analysis
• `/location` - Share GPS for intelligent territory tracking

📈 **PERFORMANCE TRACKING:**
• `/today` - AI-enhanced daily performance with insights
• `/week` - Weekly analysis with trend intelligence  
• `/month` - Comprehensive monthly review with predictions

🔍 **QUICK AI INSIGHTS:**
• `/top` - AI-ranked top clients & locations with performance analysis
• Natural language queries - "Show me sales trends" (coming soon)

🚀 **AI FEATURES:**
• 🧠 Natural language processing for entries
• 📍 GPS location intelligence and territory optimization  
• ⚡ Parallel processing for faster analytics
• 🔮 Predictive insights and forecasting
• 📊 Automated chart generation with AI insights
• 🤖 Intelligent recommendations and tips

💡 **PRO AI TIPS:**
• Use natural language: "Sold 5 tablets to Apollo for ₹25000"
• Share GPS location for territory intelligence
• Enable batch processing for multiple entries
• All analytics update automatically with AI enhancement!

🎯 **Example Usage:**
Just type `/dashboard` and get instant AI-powered business insights!

{ai_response_engine.generate_tip_of_the_day()}
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
    logger.info(f"📚 AI-enhanced analytics help delivered to user {user.id}")

@rate_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def top_performers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 AI-Enhanced Top Performers Analysis"""
    user = update.effective_user
    logger.info(f"🏆 Top performers requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🏆 AI is analyzing top performers with intelligent ranking...")
    
    try:
        from analytics import analytics_engine
        
        dashboard = analytics_engine.generate_executive_dashboard(user.id)
        
        if "error" in dashboard:
            await loading_msg.edit_text(f"❌ Error: {dashboard['error']}")
            return
        
        message = "🏆 **AI-ENHANCED TOP PERFORMERS**\n\n"
        
        message += "👑 **AI-RANKED TOP CLIENTS:**\n"
        for i, (client, revenue) in enumerate(list(dashboard['top_clients'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            performance_indicator = "🔥" if revenue > 50000 else "⭐" if revenue > 25000 else "📈"
            message += f"{medal} {performance_indicator} {client}: **₹{revenue:,.0f}**\n"
        
        message += "\n🏢 **AI-RANKED TOP LOCATIONS:**\n"
        for i, (location, revenue) in enumerate(list(dashboard['top_locations'].items())[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            territory_strength = "🎯" if revenue > 40000 else "📍" if revenue > 20000 else "🗺️"
            message += f"{medal} {territory_strength} {location}: **₹{revenue:,.0f}**\n"
        
        # AI Performance Insights
        kpis = dashboard['kpis']
        message += f"\n🤖 **AI PERFORMANCE INSIGHTS:**\n"
        message += f"• Total Revenue: **{kpis.get('total_revenue', 'N/A')}**\n"
        message += f"• Total Orders: **{kpis.get('total_orders', 'N/A')}**\n"
        message += f"• AI Growth Trend: **{kpis.get('growth_trend', 'N/A')}**\n"
        message += f"• Performance Score: **{kpis.get('performance_score', 'Calculating...')}**\n"
        
        # Add AI-generated insight
        ai_insight = ai_response_engine.generate_analytics_insight(dashboard)
        message += f"\n{ai_insight}"
        
        # Add motivational message
        motivation = ai_response_engine.generate_motivation_message({
            'top_client_revenue': list(dashboard['top_clients'].values())[0] if dashboard['top_clients'] else 0
        })
        message += f"\n\n💪 {motivation}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🏆 AI-enhanced top performers delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to get top performers. Please try again.")
        logger.error(f"Top performers command error: {e}")

# ═══════════════════════════════════════════════════════════════
# 🤖 AI UTILITY COMMANDS
# ═══════════════════════════════════════════════════════════════

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def ai_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🤖 AI Features Help"""
    help_text = """
🤖 **AI-POWERED FEATURES GUIDE**

🧠 **NATURAL LANGUAGE PROCESSING:**
• Describe transactions naturally: "Sold 5 tablets to Apollo for ₹25000"
• AI understands context, abbreviations, and calculations
• Smart parsing of complex orders: "3 boxes + 5 bottles = 8 units"

📦 **BATCH PROCESSING:**
• Enter multiple transactions at once
• AI processes them in parallel for speed
• Automatic validation and error handling

📍 **GPS INTELLIGENCE:**
• Share location once, auto-tag all entries
• Territory performance analysis
• Route optimization suggestions

⚡ **PARALLEL PROCESSING:**
• High-speed analytics generation
• Simultaneous chart creation
• Faster response times

🔮 **PREDICTIVE ANALYTICS:**
• AI forecasts future revenue
• Client churn risk analysis
• Seasonal pattern recognition

💡 **SMART RECOMMENDATIONS:**
• Context-aware tips and suggestions
• Performance optimization advice
• Business growth opportunities

🎯 **GETTING STARTED:**
1. Use `/sales` or `/purchase` to start
2. Describe your transaction naturally
3. Share GPS location with `/location`
4. View insights with `/dashboard`

Try saying: "Sold 10 medicines to City Hospital for ₹15000 urgent delivery"
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
@rat
e_limit(calls_per_minute=5)
@handle_errors(notify_user=True)
async def top_performers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 Top Performers Analysis with Location Intelligence"""
    user = update.effective_user
    logger.info(f"🏆 Top performers requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    loading_msg = await update.message.reply_text("🏆 AI is analyzing top performers with location intelligence...")
    
    try:
        from analytics import AdvancedAnalytics
        analytics_engine = AdvancedAnalytics()
        
        # Get dashboard data for top performers
        dashboard_data = analytics_engine.generate_executive_dashboard(user.id)
        location_data = analytics_engine.generate_location_analytics(user.id)
        
        if "error" in dashboard_data:
            await loading_msg.edit_text(f"❌ {dashboard_data['error']}")
            return
        
        message = "🏆 **TOP PERFORMERS ANALYSIS**\n\n"
        
        # Top Clients
        top_clients = dashboard_data.get('top_clients', {})
        if top_clients:
            message += "👥 **TOP CLIENTS BY REVENUE:**\n"
            for i, (client, revenue) in enumerate(list(top_clients.items())[:5], 1):
                performance_emoji = "🔥" if revenue > 50000 else "⭐" if revenue > 25000 else "📈"
                message += f"{i}. {performance_emoji} **{client}**\n"
                message += f"   💰 Revenue: ₹{revenue:,.0f}\n"
            message += "\n"
        
        # Top Locations
        top_locations = dashboard_data.get('top_locations', {})
        if top_locations:
            message += "📍 **TOP LOCATIONS BY REVENUE:**\n"
            for i, (location, revenue) in enumerate(list(top_locations.items())[:5], 1):
                performance_emoji = "🎯" if revenue > 40000 else "📍" if revenue > 20000 else "💡"
                message += f"{i}. {performance_emoji} **{location}**\n"
                message += f"   💰 Revenue: ₹{revenue:,.0f}\n"
            message += "\n"
        
        # Territory Performance (if GPS data available)
        if "error" not in location_data:
            territory_perf = location_data.get('territory_performance', {})
            territory_rankings = territory_perf.get('territory_rankings', {})
            
            if territory_rankings:
                message += "🗺️ **TOP TERRITORIES (GPS ENHANCED):**\n"
                for i, (location, stats) in enumerate(list(territory_rankings.items())[:3], 1):
                    efficiency_emoji = "🔥" if stats['efficiency_score'] > 20000 else "⚡" if stats['efficiency_score'] > 10000 else "📊"
                    message += f"{i}. {efficiency_emoji} **{location}**\n"
                    message += f"   💰 {stats['revenue']} | 📍 {stats['visits']} visits\n"
                    message += f"   👥 {stats['clients']} clients | ⚡ ₹{stats['efficiency_score']}/visit\n"
                message += "\n"
        
        # Performance Insights
        insights = dashboard_data.get('insights', {})
        message += "🧠 **PERFORMANCE INSIGHTS:**\n"
        message += f"🔄 Client Retention Score: **{insights.get('client_retention_score', 'N/A')}**\n"
        message += f"⚡ Location Efficiency Score: **{insights.get('location_efficiency_score', 'N/A')}**\n"
        message += f"📊 Revenue Concentration: **{insights.get('revenue_concentration', 'N/A')}**\n\n"
        
        # AI Recommendations
        message += "🤖 **AI RECOMMENDATIONS:**\n"
        if top_clients:
            top_client_revenue = list(top_clients.values())[0]
            if top_client_revenue > 100000:
                message += "• Focus on maintaining your top client relationships\n"
            else:
                message += "• Consider strategies to grow your top client accounts\n"
        
        if "error" not in location_data:
            gps_coverage = location_data.get('gps_coverage', {}).get('coverage_percentage', 0)
            if gps_coverage < 70:
                message += "• Share GPS location to identify high-performing territories\n"
            else:
                message += "• Leverage territory insights for expansion planning\n"
        
        # Add motivational message
        motivation = ai_response_engine.generate_motivation_message()
        message += f"\n💪 {motivation}"
        
        await loading_msg.edit_text(message, parse_mode='Markdown')
        logger.info(f"🏆 Top performers analysis delivered to user {user.id}")
        
    except Exception as e:
        await loading_msg.edit_text("❌ Failed to generate top performers analysis. Please try again.")
        logger.error(f"Top performers command error: {e}")

@rate_limit(calls_per_minute=10)
@handle_errors(notify_user=True)
async def ai_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🤖 AI Features Help and Guidance"""
    user = update.effective_user
    logger.info(f"🤖 AI help requested by user {user.id}")
    
    if not company_manager.is_user_registered(user.id):
        await update.message.reply_text("❌ Please register with a company first using `/company`")
        return
    
    current_company = company_manager.get_user_company(user.id)
    company_info = company_manager.get_company_info(current_company)
    
    help_text = f"""
🤖 **AI-POWERED PERFORMANCE TRACKER**
🏢 **Current Company:** {company_info['display_name']}

🧠 **ARTIFICIAL INTELLIGENCE FEATURES:**

📝 **NATURAL LANGUAGE PROCESSING:**
• Smart entry parsing - just describe your sale naturally
• Example: "Sold 5 tablets to Apollo Pharmacy for ₹25000"
• AI understands context, quantities, and amounts
• Automatic error correction and validation

📍 **LOCATION INTELLIGENCE:**
• GPS-powered territory analytics
• Automatic location tagging for sales entries
• Route optimization suggestions
• Geographic performance insights
• Territory trend analysis

🔮 **PREDICTIVE ANALYTICS:**
• AI-powered sales forecasting
• Trend prediction and analysis
• Performance pattern recognition
• Growth opportunity identification

📊 **INTELLIGENT DASHBOARDS:**
• Real-time business intelligence
• AI-generated insights and recommendations
• Performance benchmarking
• Automated report generation

⚡ **ADVANCED PROCESSING:**
• Parallel processing for faster analytics
• Batch entry processing for multiple sales
• Smart data validation and cleanup
• Automated chart generation

🎯 **SMART RECOMMENDATIONS:**
• Personalized business insights
• Territory optimization suggestions
• Client relationship recommendations
• Performance improvement tips

🚀 **HOW TO USE AI FEATURES:**

1️⃣ **Natural Language Entries:**
   Just type: "Sold 10 medicines to City Hospital for ₹15000"
   AI will parse: Client, Location, Orders, Amount automatically

2️⃣ **GPS Location Sharing:**
   Use `/location` to share GPS for territory insights
   AI will enhance all future entries with location data

3️⃣ **AI Analytics:**
   • `/dashboard` - AI-powered executive overview
   • `/predictions` - Machine learning forecasts
   • `/location_analytics` - Territory intelligence

4️⃣ **Batch Processing:**
   Enter multiple sales at once, AI will process them all

💡 **PRO AI TIPS:**
• Be descriptive in your entries for better AI parsing
• Share GPS location regularly for territory insights
• Use natural language - AI understands context
• Check `/predictions` for growth opportunities
• Review `/location_analytics` for territory optimization

🔬 **AI TECHNOLOGY STACK:**
• Google Gemini 2.5 Flash for natural language processing
• Advanced analytics engine with machine learning
• GPS coordinate processing and geocoding
• Parallel processing for high performance
• Intelligent caching for faster responses

🎉 **GETTING STARTED:**
Try saying: "I sold 3 boxes of medicine to Metro Hospital for ₹12000"
The AI will automatically understand and log your sale!

💪 **Remember:** The more you use AI features, the smarter the system becomes at understanding your business patterns!
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
    logger.info(f"🤖 AI help delivered to user {user.id}")