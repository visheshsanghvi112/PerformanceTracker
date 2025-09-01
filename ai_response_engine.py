#!/usr/bin/env python3
"""
🤖 AI RESPONSE ENGINE
====================
Intelligent response generation using specialized API keys for optimal performance
"""

import random
import datetime
import asyncio
import json
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
    
    def _clean_and_parse_json(self, response_text: str) -> dict | None:
        """Clean and parse JSON response with enhanced error handling"""
        try:
            if not response_text or not response_text.strip():
                logger.warning("🚫 Empty response received")
                return None
            
            # Clean the response
            cleaned_text = response_text.strip()
            
            # Remove code block markers if present
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.strip("`").strip()
                if cleaned_text.lower().startswith("json"):
                    cleaned_text = cleaned_text[4:].strip()
            
            # Try to parse JSON
            parsed = json.loads(cleaned_text)
            logger.info("✅ JSON parsed successfully")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"❌ JSON parsing failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error in JSON parsing: {e}")
            return None
    
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
    
    async def generate_ai_powered_response(self, user_message: str, context: str = "general") -> str:
        """
        🚀 Generate AI-powered responses using specialized API keys
        Uses the dedicated casual chat API key for natural conversations
        """
        try:
            if context == "casual" or self._is_casual_message(user_message):
                # Use specialized casual chat API key
                response = await self._generate_casual_response_internal(user_message)
                logger.info("🗨️ Generated casual response using dedicated chat API key")
                return response
            else:
                # Use template-based responses for business interactions
                return self.generate_contextual_response(user_message, context)
                
        except Exception as e:
            logger.error(f"🤖 AI response generation failed: {e}")
            return "I'm here to help! Please let me know what you'd like to track today."
    
    async def _generate_casual_response_internal(self, text: str) -> str:
        """Generate casual chat response using dedicated chat API key"""
        try:
            # Import here to avoid circular imports
            from gemini_parser import smart_api_manager
            
            chat_prompt = f"""
You are a friendly business assistant. Respond to this casual message naturally and helpfully.
Keep it brief, professional but warm. If they're asking about business data, guide them to use proper commands.

User message: {text}

Response:"""
            
            response = await smart_api_manager.generate_content_specialized(chat_prompt, "casual_chat")
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Casual chat generation failed: {e}")
            return "I'm having trouble responding right now. Please try again or use /help for commands."
    
    async def generate_command_insights(self, command_data: Dict[str, Any]) -> str:
        """
        📊 Generate command analysis using specialized analytics API key
        Uses the dedicated command processing API key for analytics
        """
        try:
            # Import here to avoid circular imports
            from gemini_parser import smart_api_manager
            
            analysis_prompt = f"""
Analyze this command data and provide insights:
{json.dumps(command_data, indent=2)}

Return JSON with:
{{
    "summary": "Brief command summary",
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""
            
            response = await smart_api_manager.generate_content_specialized(analysis_prompt, "command_processing")
            
            # Clean and parse the response
            response_cleaned = response.strip()
            if response_cleaned.startswith("```"):
                # Remove markdown code blocks
                response_cleaned = response_cleaned.strip("`").strip()
                if response_cleaned.lower().startswith("json"):
                    response_cleaned = response_cleaned[4:].strip()
            
            # Validate response before parsing
            if not response_cleaned or len(response_cleaned) < 10:
                logger.warning("⚠️ Empty or too short response from API")
                return "📊 Command processed successfully!"
            
            try:
                analysis = json.loads(response_cleaned)
            except json.JSONDecodeError as je:
                logger.warning(f"⚠️ JSON parsing failed, using fallback: {je}")
                return "📊 Command analysis completed - API response format issue!"
            
            response_parts = []
            if analysis.get("summary"):
                response_parts.append(f"📋 **Summary:** {analysis['summary']}")
            
            if analysis.get("insights"):
                insights_text = "\n".join([f"  • {insight}" for insight in analysis["insights"]])
                response_parts.append(f"💡 **Insights:**\n{insights_text}")
            
            if analysis.get("recommendations"):
                recs_text = "\n".join([f"  • {rec}" for rec in analysis["recommendations"]])
                response_parts.append(f"🎯 **Recommendations:**\n{recs_text}")
            
            if response_parts:
                result = "\n\n".join(response_parts)
                logger.info("📊 Generated command insights using dedicated analytics API key")
                return result
            else:
                return "📊 Analysis completed successfully!"
                
        except Exception as e:
            logger.error(f"📊 Command insights generation failed: {e}")
            return "📊 Command processed successfully!"
    
    def _is_casual_message(self, message: str) -> bool:
        """Detect if message is casual conversation vs business data"""
        casual_indicators = [
            "hi", "hello", "hey", "how are you", "thanks", "thank you",
            "good morning", "good evening", "bye", "goodbye", "ok", "okay"
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in casual_indicators)
    
    def generate_contextual_response(self, message: str, context: str) -> str:
        """Generate contextual response using templates"""
        if context == "greeting":
            return random.choice(self.response_templates['greeting'])
        elif context == "encouragement":
            return random.choice(self.response_templates['encouragement'])
        else:
            return "I'm here to help with your business tracking!"

# Global instance
ai_response_engine = AIResponseEngine()