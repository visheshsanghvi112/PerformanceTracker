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
    """🧠 AI-powered response generation with conversation memory"""
    
    def __init__(self):
        # Conversation memory system - stores last 3 messages per user
        self.conversation_memory = {}  # user_id -> list of last messages
        self.max_memory_per_user = 3
        
        # User context tracking
        self.user_contexts = {}  # user_id -> context info
        
        # Initialize context engine for comprehensive AI understanding
        try:
            from ai_context import ai_context_engine
            self.context_engine = ai_context_engine
            logger.info("🧠 AI Context Engine integrated for intelligent responses")
        except Exception as e:
            logger.warning(f"⚠️ Context engine unavailable: {e}")
            self.context_engine = None
        
        self.response_templates = {
            'greeting': [
                "👋 Hello! Ready to track some business today?",
                "🌟 Welcome back! Let's make today productive!",
                "💼 Hi there! What business would you like to log?",
                "🚀 Great to see you! Ready for some sales tracking?"
            ],
            'casual_conversation': [
                "😊 Thanks for chatting! I'm here whenever you need business help.",
                "🤖 Always happy to assist with your performance tracking!",
                "💬 I enjoy our conversations! Let me know how I can help with business.",
                "🌟 Great talking with you! Ready for some analytics when you are!"
            ],
            'time_acknowledgment': [
                "⏰ You're absolutely right about the time!",
                "🕐 Yes, time awareness is important for business!",
                "⏱️ Good observation! Time management matters in business.",
                "🌅 Time flies when you're being productive!"
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
        logger.info("🤖 AI Response Engine initialized with conversation memory")
    
    def add_to_conversation_memory(self, user_id: int, user_message: str, bot_response: str):
        """Add conversation to memory for context awareness"""
        try:
            if user_id not in self.conversation_memory:
                self.conversation_memory[user_id] = []
            
            # Add new conversation entry
            conversation_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "user_message": user_message,
                "bot_response": bot_response
            }
            
            self.conversation_memory[user_id].append(conversation_entry)
            
            # Keep only last 3 conversations
            if len(self.conversation_memory[user_id]) > self.max_memory_per_user:
                self.conversation_memory[user_id] = self.conversation_memory[user_id][-self.max_memory_per_user:]
            
            logger.info(f"💭 Added conversation to memory for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error adding to conversation memory: {e}")
    
    def get_conversation_context(self, user_id: int) -> str:
        """Get formatted conversation context for AI"""
        try:
            if user_id not in self.conversation_memory or not self.conversation_memory[user_id]:
                return "No previous conversation context."
            
            context_parts = []
            for i, conv in enumerate(self.conversation_memory[user_id], 1):
                context_parts.append(f"Message {i}: User said '{conv['user_message']}' -> Bot responded '{conv['bot_response'][:100]}...'")
            
            return "Previous conversation:\n" + "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation context: {e}")
            return "No conversation context available."
    
    def update_user_context(self, user_id: int, context_info: dict):
        """Update user context for better personalization"""
        try:
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = {}
            
            self.user_contexts[user_id].update(context_info)
            logger.info(f"📝 Updated context for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating user context: {e}")
    
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
        """Generate personalized greeting based on current time (IST timezone aware)"""
        try:
            base_greeting = random.choice(self.response_templates['greeting'])
            
            # Add time-based greeting with improved logic
            if not time_of_day:
                # Get current time and log it for debugging
                now = datetime.datetime.now()
                current_hour = now.hour
                current_time = now.strftime("%H:%M")
                
                # Enhanced time-based greetings for Indian context
                if 5 <= current_hour < 12:
                    time_greeting = "🌅 Good morning!"
                elif 12 <= current_hour < 16:
                    time_greeting = "☀️ Good afternoon!"
                elif 16 <= current_hour < 21:
                    time_greeting = "🌆 Good evening!"
                else:
                    time_greeting = "🌙 Good night!"
                
                # Debug logging to track greeting generation
                logger.info(f"🕐 Greeting generated at {current_time} (Hour: {current_hour}) -> {time_greeting}")
                
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
        elif context == "casual_conversation":
            return random.choice(self.response_templates['casual_conversation'])
        elif context == "time_acknowledgment":
            return random.choice(self.response_templates['time_acknowledgment'])
        elif context == "encouragement":
            return random.choice(self.response_templates['encouragement'])
        else:
            return "I'm here to help with your business tracking!"

    def generate_intelligent_conversation(self, user_message: str, user_id: int, user_name: str = None, context: str = None) -> str:
        """Generate truly intelligent conversation using Gemini AI"""
        try:
            # Import Gemini functionality
            from gemini_parser import smart_api_manager
            from smart_rate_limiter import rate_limiter
            
            # Get comprehensive context for intelligent response
            conversation_context = self.get_conversation_context(user_id)
            
            # Get complete system context if available
            if self.context_engine:
                complete_context = self.context_engine.get_complete_context(user_id, user_name, conversation_context)
            else:
                # Fallback context
                complete_context = f"""
BASIC CONTEXT:
System: Performance Tracker by Vishesh Sanghvi (MSc Big Data Analytics)
User: {user_name} (ID: {user_id})
Conversation: {conversation_context}
Time: {datetime.datetime.now().strftime('%H:%M')}
"""
            
            # Create enhanced conversation prompt with complete context
            conversation_prompt = f"""
{complete_context}

CURRENT USER MESSAGE: "{user_message}"

IMPORTANT INSTRUCTIONS:
1. You have complete knowledge of the Performance Tracker system, user's business data, and conversation history
2. Provide contextual responses that reference relevant business insights when appropriate
3. Use the conversation memory to maintain continuity
4. Show understanding of the user's business context (company, recent activity, clients)
5. Be helpful, intelligent, and naturally conversational
6. Reference specific business features when relevant (charts, analytics, multi-company, GPS tracking)
7. Keep responses under 150 words but make them meaningful and context-aware

Generate a natural, intelligent response that demonstrates deep understanding of the system and user context.
"""

            # Get Gemini model for conversation
            model, key_used = smart_api_manager.get_model_for_task("casual_conversation")

            # Get Gemini model for conversation
            model, key_used = smart_api_manager.get_model_for_task("casual_conversation")
            
            # Check rate limiting
            if not rate_limiter.can_use_key(key_used):
                available_keys = rate_limiter.get_available_keys()
                if available_keys:
                    alternative_key = available_keys[0]
                    model = smart_api_manager.models[alternative_key]
                    key_used = alternative_key
                    logger.info(f"� Conversation: Switched to {key_used} due to rate limiting")
                else:
                    logger.warning("🚫 All API keys rate limited, using fallback conversation")
                    fallback_response = self._generate_fallback_conversation(user_message, user_name, conversation_context)
                    self.add_to_conversation_memory(user_id, user_message, fallback_response)
                    return fallback_response
            
            # Generate response with Gemini
            response = model.generate_content(conversation_prompt)
            ai_response = response.text.strip()
            
            # Record successful request
            rate_limiter.record_request(key_used, True)
            
            # Clean up the response
            if ai_response.startswith('"') and ai_response.endswith('"'):
                ai_response = ai_response[1:-1]
            
            # Add to conversation memory
            self.add_to_conversation_memory(user_id, user_message, ai_response)
            
            logger.info(f"🤖 Generated intelligent conversation response with context using {key_used}")
            return ai_response
            
        except Exception as e:
            logger.error(f"� Intelligent conversation generation failed: {e}")
            return self._generate_fallback_conversation(user_message, user_name)
    
    def _generate_fallback_conversation(self, user_message: str, user_name: str = None, conversation_context: str = None) -> str:
        """Enhanced fallback conversation with context awareness"""
        message_lower = user_message.lower()
        
        # Try to use context if available
        context_aware = ""
        if conversation_context and "Previous conversation:" in conversation_context:
            if "tired" in conversation_context.lower() and any(word in message_lower for word in ['good', 'morning', 'better']):
                context_aware = "Hope you're feeling more refreshed now! "
            elif "evening" in conversation_context.lower() and "thank" in message_lower:
                context_aware = "You're welcome! Hope you're enjoying the evening! "
        
        # Generate contextual response
        if any(word in message_lower for word in ['evening', 'afternoon', 'morning', 'time']):
            return f"{context_aware}You're absolutely right about the time{f' {user_name}' if user_name else ''}! 🕐 Perfect time to track some business performance!"
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return f"{context_aware}You're very welcome{f' {user_name}' if user_name else ''}! 😊 Always here to help with your business tracking!"
        elif any(word in message_lower for word in ['bye', 'goodbye']):
            return f"{context_aware}Take care{f' {user_name}' if user_name else ''}! 👋 Come back anytime for business insights!"
        elif any(word in message_lower for word in ['how are you', 'how is everything']):
            return f"{context_aware}I'm doing great, thanks for asking{f' {user_name}' if user_name else ''}! 🤖 Ready to help analyze your business performance!"
        else:
            return f"{context_aware}Thanks for chatting{f' {user_name}' if user_name else ''}! 💬 I'm here whenever you need business tracking assistance!"

# Global instance
ai_response_engine = AIResponseEngine()