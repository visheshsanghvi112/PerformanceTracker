#!/usr/bin/env python3
"""
🧠 AI CONTEXT ENGINE
===================
Comprehensive system context for intelligent AI responses
Created by: Vishesh Sanghvi (MSc Big Data Analytics)
"""

from datetime import datetime
from typing import Dict, Any, List
from logger import logger

class AIContextEngine:
    """🎯 Provides complete system context to AI for intelligent responses"""
    
    def __init__(self):
        self.system_context = self._build_system_context()
        logger.info("🧠 AI Context Engine initialized with complete system knowledge")
    
    def _build_system_context(self) -> str:
        """Build comprehensive system context for AI"""
        return """
🏢 PERFORMANCE TRACKER SYSTEM CONTEXT
=====================================

👨‍💻 CREATOR: Vishesh Sanghvi
   - MSc Big Data Analytics (2nd Year)
   - Software Developer & Business Intelligence Expert
   - GitHub: visheshsanghvi112
   - Platform: Enterprise Business Intelligence System

🎯 SYSTEM PURPOSE:
   - Multi-company business performance tracking
   - AI-powered sales/purchase logging with natural language
   - Professional chart generation and analytics
   - Territory mapping with GPS integration
   - Smart data normalization and client consolidation

🏢 COMPANIES MANAGED:
   1. JohnLee (Medical supplies)
   2. Yugrow (Pharmaceuticals) - Primary company
   3. Ambica (Healthcare distributor)
   4. Baker (Medical equipment)

📊 CORE FEATURES:
   - Natural Language Processing: "Sold 5 boxes to Apollo for ₹25000"
   - Smart Normalization: Apollo Pharmacy → apollo (70% similarity)
   - Professional Charts: Executive dashboard, client analytics, location insights
   - Multi-Company Switching: Independent data tracking per company
   - GPS Territory Mapping: Real-time location capture
   - Live Position Tracking: Sales territory intelligence
   - Batch Processing: Multiple entries in one message
   - Conversation Memory: Contextual AI responses

🤖 AI CAPABILITIES:
   - Google Gemini 2.5 Flash: 3 specialized API keys for load balancing
   - Smart Rate Limiting: Conservative request management
   - Conversation Memory: Last 2-3 interactions per user
   - Context-Aware Responses: References previous conversations
   - Time-Aware Greetings: Morning/Afternoon/Evening/Night detection
   - Business Intelligence: Sales analytics and performance insights

💼 BUSINESS WORKFLOW:
   1. User selects company (/company command)
   2. Choose transaction type (/sales or /purchase)
   3. Natural language entry: "Sold medicine to Fortis Hospital for ₹15000"
   4. AI parsing extracts: client, location, amount, orders
   5. GPS enhancement adds territory data
   6. Smart normalization consolidates similar clients
   7. Data saved to company-specific Google Sheet
   8. Analytics and charts available on demand

📈 ANALYTICS FEATURES:
   - Executive Dashboard: Revenue trends, top clients, performance metrics
   - Client Analytics: Purchase patterns, relationship insights
   - Location Intelligence: Territory performance, GPS mapping
   - Professional Charts: Boardroom-ready visualizations
   - Smart Insights: AI-powered business recommendations

🔧 TECHNICAL STACK:
   - Python 3.12 with async/await architecture
   - Telegram Bot API for user interface
   - Google Sheets API for data storage
   - Google Gemini AI for natural language processing
   - Matplotlib for professional chart generation
   - Advanced caching and parallel processing

⚡ PERFORMANCE METRICS:
   - Chart Generation: 3 charts (229KB, 172KB, 105KB) in seconds
   - Data Processing: 10,000+ rows with sub-second normalization
   - API Response: Multi-key load balancing for 99.9% uptime
   - Memory Efficiency: Optimized conversation tracking
   - Error Handling: Comprehensive fallback systems

🎯 USER EXPERIENCE:
   - Conversational Interface: Natural chat-based commands
   - Intelligent Responses: Context-aware AI conversation
   - Visual Feedback: Professional charts and analytics
   - Multi-Platform: Telegram integration with web dashboard
   - Real-Time Updates: Live position and instant data sync
"""

    def get_user_context(self, user_id: int, user_name: str = None) -> Dict[str, Any]:
        """Get specific user context for personalized AI responses"""
        try:
            from company_manager import company_manager
            
            # Get user's company info
            user_company = company_manager.get_user_company(user_id)
            company_info = company_manager.get_company_info(user_company) if user_company else None
            
            # Build user-specific context
            user_context = {
                "user_id": user_id,
                "user_name": user_name,
                "current_company": user_company,
                "company_display_name": company_info.get('display_name') if company_info else "Unknown",
                "company_sheet": company_info.get('sheet_name') if company_info else "Unknown",
                "registration_status": "registered" if user_company else "unregistered",
                "access_level": "admin" if user_id in [1201911108] else "user",
                "features_available": [
                    "Sales/Purchase logging with AI",
                    "Professional chart generation", 
                    "GPS territory mapping",
                    "Smart data normalization",
                    "Multi-company switching",
                    "Conversation memory"
                ]
            }
            
            return user_context
            
        except Exception as e:
            logger.error(f"❌ Failed to get user context for {user_id}: {e}")
            return {
                "user_id": user_id,
                "user_name": user_name,
                "error": "Context unavailable"
            }
    
    def get_business_context(self, user_id: int) -> Dict[str, Any]:
        """Get business intelligence context for the user"""
        try:
            from analytics import analytics_engine
            from multi_company_sheets import multi_sheet_manager
            from company_manager import company_manager
            
            # Get user's data summary
            company = company_manager.get_user_company(user_id)
            if not company:
                return {"error": "No company selected"}
            
            # Get recent business activity
            records = multi_sheet_manager.get_company_records(company)
            
            if records:
                business_context = {
                    "total_records": len(records),
                    "recent_activity": "active" if len(records) > 5 else "moderate",
                    "data_quality": "excellent" if len(records) > 10 else "good",
                    "top_clients": self._get_top_clients(records),
                    "revenue_trend": self._analyze_revenue_trend(records),
                    "location_spread": self._get_location_summary(records)
                }
            else:
                business_context = {
                    "total_records": 0,
                    "status": "new_user",
                    "suggestion": "Start logging sales/purchases to build analytics"
                }
            
            return business_context
            
        except Exception as e:
            logger.error(f"❌ Failed to get business context for {user_id}: {e}")
            return {"error": "Business context unavailable"}
    
    def _get_top_clients(self, records: List[Dict]) -> List[str]:
        """Extract top clients from records"""
        try:
            client_counts = {}
            for record in records[-10:]:  # Last 10 records
                client = record.get('Client', '').lower()
                if client:
                    client_counts[client] = client_counts.get(client, 0) + 1
            
            # Return top 3 clients
            sorted_clients = sorted(client_counts.items(), key=lambda x: x[1], reverse=True)
            return [client[0].title() for client in sorted_clients[:3]]
        except:
            return []
    
    def _analyze_revenue_trend(self, records: List[Dict]) -> str:
        """Analyze recent revenue trend"""
        try:
            if len(records) < 3:
                return "insufficient_data"
            
            recent_amounts = []
            for record in records[-5:]:  # Last 5 records
                amount_str = str(record.get('Amount', '0'))
                amount = float(amount_str.replace('₹', '').replace(',', '').strip())
                recent_amounts.append(amount)
            
            if len(recent_amounts) >= 3:
                avg_recent = sum(recent_amounts[-3:]) / 3
                avg_earlier = sum(recent_amounts[:-3]) / max(1, len(recent_amounts) - 3)
                
                if avg_recent > avg_earlier * 1.1:
                    return "growing"
                elif avg_recent < avg_earlier * 0.9:
                    return "declining"
                else:
                    return "stable"
            
            return "stable"
        except:
            return "unknown"
    
    def _get_location_summary(self, records: List[Dict]) -> Dict[str, Any]:
        """Get location activity summary"""
        try:
            locations = {}
            for record in records[-10:]:  # Last 10 records
                location = record.get('Location', '').lower()
                if location:
                    locations[location] = locations.get(location, 0) + 1
            
            return {
                "total_locations": len(locations),
                "most_active": max(locations.items(), key=lambda x: x[1])[0].title() if locations else "None",
                "location_diversity": "high" if len(locations) > 5 else "moderate" if len(locations) > 2 else "low"
            }
        except:
            return {"total_locations": 0, "most_active": "None", "location_diversity": "unknown"}
    
    def get_complete_context(self, user_id: int, user_name: str = None, conversation_context: str = None) -> str:
        """Generate complete context for AI conversation"""
        try:
            user_context = self.get_user_context(user_id, user_name)
            business_context = self.get_business_context(user_id)
            
            # Build comprehensive context prompt
            context_prompt = f"""
SYSTEM CONTEXT:
{self.system_context}

USER CONTEXT:
- User ID: {user_context['user_id']}
- Name: {user_context['user_name']}
- Company: {user_context['company_display_name']}
- Access Level: {user_context['access_level']}
- Status: {user_context['registration_status']}

BUSINESS CONTEXT:
- Total Records: {business_context.get('total_records', 0)}
- Activity Level: {business_context.get('recent_activity', 'unknown')}
- Top Clients: {', '.join(business_context.get('top_clients', []))}
- Revenue Trend: {business_context.get('revenue_trend', 'unknown')}
- Territory Spread: {business_context.get('location_spread', {}).get('location_diversity', 'unknown')}

CONVERSATION HISTORY:
{conversation_context if conversation_context else 'No previous conversation'}

CURRENT TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Evening: 16:00-21:00)
"""
            
            return context_prompt
            
        except Exception as e:
            logger.error(f"❌ Failed to build complete context: {e}")
            return f"""
BASIC CONTEXT:
System: Performance Tracker by Vishesh Sanghvi
User: {user_name} (ID: {user_id})
Time: {datetime.now().strftime('%H:%M')}
Conversation: {conversation_context if conversation_context else 'New conversation'}
"""

# Global instance
ai_context_engine = AIContextEngine()
