#!/usr/bin/env python3
"""
🤖 AI RESPONSE ENGINE
====================
Intelligent response generation for user interactions and business insights
"""

import random
import datetime
from typing import Dict, List, Any, Optional
from logger import logger

class AIResponseEngine:
    """🧠 AI-powered response generation for enhanced user experience"""
    
    def __init__(self):
        self.response_templates = {
            'greeting': [
                "👋 Hello! Ready to track some business today?",
                "🌟 Welcome back! Let's make today productive!",
                "💼 Hi there! What business would you like to log?",
                "🚀 Great to see you! Ready for some sales tracking?"
            ],
            'success_sales': [
                "🎉 Excellent work! Another successful sale recorded!",
                "💪 Great job! Your sales performance is looking strong!",
                "⭐ Outstanding! Keep up the excellent sales work!",
                "🔥 Fantastic! Another client satisfied and logged!"
            ],
            'success_purchase': [
                "✅ Perfect! Purchase recorded successfully!",
                "📦 Great! Your inventory management is on point!",
                "💯 Excellent! Purchase logged and tracked!",
                "🎯 Well done! Another purchase properly documented!"
            ],
            'encouragement': [
                "Keep up the great work! 💪",
                "You're doing amazing! 🌟",
                "Excellent progress today! 🚀",
                "Your dedication shows! ⭐"
            ],
            'tips': [
                "💡 Pro tip: Include client details for better analytics!",
                "🎯 Tip: Regular logging helps track performance trends!",
                "📊 Insight: Detailed remarks improve business intelligence!",
                "🔍 Suggestion: Use specific amounts for accurate reporting!"
            ]
        }
        
        self.business_insights = {
            'high_amount': [
                "🏆 That's a significant transaction! Great work!",
                "💰 Impressive sale amount! Your efforts are paying off!",
                "🎯 High-value transaction recorded! Excellent performance!"
            ],
            'frequent_client': [
                "🤝 Great to see repeat business with this client!",
                "⭐ Building strong client relationships! Keep it up!",
                "💼 Consistent client engagement - that's professional!"
            ],
            'new_location': [
                "🗺️ Expanding to new territories! Great market coverage!",
                "📍 New location recorded! Your reach is growing!",
                "🌟 Territory expansion - excellent business development!"
            ]
        }
        
        logger.info("🤖 AI Response Engine initialized")
    
    def generate_success_response(self, entry_type: str, entry_data: Dict[str, Any]) -> str:
        """Generate intelligent success response based on entry data"""
        try:
            # Base success message
            if entry_type.lower() == 'sales':
                base_response = random.choice(self.response_templates['success_sales'])
            else:
                base_response = random.choice(self.response_templates['success_purchase'])
            
            # Add business insights
            insights = self._analyze_entry_insights(entry_data)
            if insights:
                base_response += f"\n\n{random.choice(insights)}"
            
            # Add encouragement
            if random.random() < 0.3:  # 30% chance
                base_response += f"\n{random.choice(self.response_templates['encouragement'])}"
            
            # Add tips occasionally
            if random.random() < 0.2:  # 20% chance
                base_response += f"\n\n{random.choice(self.response_templates['tips'])}"
            
            return base_response
            
        except Exception as e:
            logger.error(f"🤖 Error generating success response: {e}")
            return "✅ Entry recorded successfully!"
    
    def _analyze_entry_insights(self, entry_data: Dict[str, Any]) -> List[str]:
        """Analyze entry data for business insights"""
        insights = []
        
        try:
            # High amount detection
            amount = entry_data.get('amount', 0)
            if isinstance(amount, (int, float)) and amount > 20000:
                insights.extend(self.business_insights['high_amount'])
            
            # Add more insights based on patterns
            # This could be expanded with historical data analysis
            
        except Exception as e:
            logger.error(f"🤖 Error analyzing insights: {e}")
        
        return insights
    
    def generate_greeting_response(self, user_name: str = None, time_of_day: str = None) -> str:
        """Generate personalized greeting based on context"""
        try:
            base_greeting = random.choice(self.response_templates['greeting'])
            
            # Add time-based greeting
            if not time_of_day:
                current_hour = datetime.datetime.now().hour
                if 5 <= current_hour < 12:
                    time_greeting = "🌅 Good morning!"
                elif 12 <= current_hour < 17:
                    time_greeting = "☀️ Good afternoon!"
                elif 17 <= current_hour < 21:
                    time_greeting = "🌆 Good evening!"
                else:
                    time_greeting = "🌙 Working late tonight?"
            else:
                time_greeting = time_of_day
            
            # Personalize with name
            if user_name:
                personalized = f"{time_greeting} {user_name}! {base_greeting}"
            else:
                personalized = f"{time_greeting} {base_greeting}"
            
            return personalized
            
        except Exception as e:
            logger.error(f"🤖 Error generating greeting: {e}")
            return "👋 Hello! Ready to track some business?"
    
    def generate_error_response(self, error_type: str, context: Dict[str, Any] = None) -> str:
        """Generate helpful error responses"""
        error_responses = {
            'parsing_failed': [
                "🤔 I couldn't quite understand that format. Let me help you!",
                "📝 That format seems unclear. Here's how to structure it:",
                "🔍 I need a clearer format to process your entry."
            ],
            'validation_failed': [
                "⚠️ I noticed some issues with the data. Let's fix them:",
                "🔧 There are a few validation concerns to address:",
                "📋 Let me help you correct these details:"
            ],
            'system_error': [
                "🛠️ I encountered a technical issue. Let me try to help:",
                "⚙️ Something went wrong on my end. Here's what I can do:",
                "🔄 Technical hiccup! Let's get this sorted:"
            ]
        }
        
        try:
            base_response = random.choice(error_responses.get(error_type, error_responses['system_error']))
            
            # Add context-specific help
            if error_type == 'parsing_failed':
                base_response += "\n\n📋 **Try this format:**\n"
                base_response += "Client: [Company Name]\n"
                base_response += "Orders: [Number]\n"
                base_response += "Amount: ₹[Amount]\n"
                base_response += "Remarks: [Notes]"
            
            return base_response
            
        except Exception as e:
            logger.error(f"🤖 Error generating error response: {e}")
            return "❌ Something went wrong. Please try again."
    
    def generate_analytics_insight(self, analytics_data: Dict[str, Any]) -> str:
        """Generate intelligent insights from analytics data"""
        try:
            insights = []
            
            # Revenue insights
            if 'total_revenue' in analytics_data:
                revenue = analytics_data['total_revenue']
                if revenue > 100000:
                    insights.append("💰 Impressive revenue performance!")
                elif revenue > 50000:
                    insights.append("📈 Solid revenue growth!")
                else:
                    insights.append("🚀 Building momentum!")
            
            # Growth insights
            if 'growth_rate' in analytics_data:
                growth = analytics_data.get('growth_rate', 0)
                if growth > 20:
                    insights.append("🔥 Exceptional growth rate!")
                elif growth > 10:
                    insights.append("📊 Strong growth trajectory!")
                elif growth > 0:
                    insights.append("✅ Positive growth trend!")
            
            # Client insights
            if 'client_count' in analytics_data:
                clients = analytics_data['client_count']
                if clients > 20:
                    insights.append("🤝 Excellent client diversity!")
                elif clients > 10:
                    insights.append("👥 Good client base!")
            
            if insights:
                return f"🧠 **AI Insights:** {' '.join(insights)}"
            else:
                return "📊 Analytics data processed successfully!"
                
        except Exception as e:
            logger.error(f"🤖 Error generating analytics insight: {e}")
            return "📊 Analytics completed!"
    
    def generate_motivation_message(self, performance_data: Dict[str, Any] = None) -> str:
        """Generate motivational messages based on performance"""
        motivational_messages = [
            "🌟 Every entry brings you closer to your goals!",
            "💪 Consistency is the key to success!",
            "🎯 Your dedication to tracking shows professionalism!",
            "🚀 Great businesses are built on great data!",
            "⭐ Your attention to detail makes a difference!",
            "🔥 Keep up the excellent work ethic!",
            "💼 Professional tracking leads to professional results!",
            "🏆 Excellence is a habit - you're building it!"
        ]
        
        try:
            base_message = random.choice(motivational_messages)
            
            # Add performance-specific motivation
            if performance_data:
                if performance_data.get('streak', 0) > 5:
                    base_message += "\n🔥 Amazing consistency streak!"
                elif performance_data.get('daily_entries', 0) > 3:
                    base_message += "\n⚡ High productivity today!"
            
            return base_message
            
        except Exception as e:
            logger.error(f"🤖 Error generating motivation: {e}")
            return "🌟 Keep up the great work!"
    
    def generate_tip_of_the_day(self) -> str:
        """Generate helpful business tips"""
        tips = [
            "💡 **Tip:** Include specific client details for better relationship tracking!",
            "📊 **Insight:** Regular data entry helps identify sales patterns!",
            "🎯 **Strategy:** Track both successful and unsuccessful interactions!",
            "🔍 **Analysis:** Detailed remarks improve future business intelligence!",
            "📈 **Growth:** Consistent tracking leads to better forecasting!",
            "🤝 **Relationships:** Note client preferences in remarks for better service!",
            "⏰ **Timing:** Log entries immediately for maximum accuracy!",
            "🗺️ **Territory:** Track locations to optimize your sales routes!"
        ]
        
        return random.choice(tips)

# Global instance
ai_response_engine = AIResponseEngine()