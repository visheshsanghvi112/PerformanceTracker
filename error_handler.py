"""
Centralized error handling system for the Performance Tracker bot
"""

import traceback
from enum import Enum
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from logger import logger


class ErrorType(Enum):
    """Types of errors that can occur"""
    VALIDATION_ERROR = "validation"
    API_ERROR = "api"
    DATABASE_ERROR = "database"
    NETWORK_ERROR = "network"
    PERMISSION_ERROR = "permission"
    RATE_LIMIT_ERROR = "rate_limit"
    LOCATION_ERROR = "location"
    GEOCODING_ERROR = "geocoding"
    GPS_ERROR = "gps"
    UNKNOWN_ERROR = "unknown"


class ErrorHandler:
    """Centralized error handling system"""
    
    # User-friendly error messages
    ERROR_MESSAGES = {
        ErrorType.VALIDATION_ERROR: {
            'title': '❌ Invalid Input',
            'message': 'Please check your input and try again.',
            'action': 'Use the correct format or ask for help with /help'
        },
        ErrorType.API_ERROR: {
            'title': '🔧 Service Temporarily Unavailable',
            'message': 'Our AI service is temporarily unavailable.',
            'action': 'Please try again in a few moments or use the structured format'
        },
        ErrorType.DATABASE_ERROR: {
            'title': '💾 Data Service Issue',
            'message': 'Unable to save your data right now.',
            'action': 'Please try again. Your data will be saved once the service is restored'
        },
        ErrorType.NETWORK_ERROR: {
            'title': '🌐 Connection Issue',
            'message': 'Network connection problem detected.',
            'action': 'Please check your connection and try again'
        },
        ErrorType.PERMISSION_ERROR: {
            'title': '🔒 Access Denied',
            'message': 'You don\'t have permission to perform this action.',
            'action': 'Contact an administrator if you believe this is an error'
        },
        ErrorType.RATE_LIMIT_ERROR: {
            'title': '⏰ Too Many Requests',
            'message': 'You\'re sending messages too quickly.',
            'action': 'Please wait a moment before trying again'
        },
        ErrorType.LOCATION_ERROR: {
            'title': '📍 Location Service Issue',
            'message': 'Unable to process your location data.',
            'action': 'Try sharing your location again or check your GPS settings'
        },
        ErrorType.GEOCODING_ERROR: {
            'title': '🌍 Address Resolution Failed',
            'message': 'Unable to convert your coordinates to an address.',
            'action': 'Your location will be saved with coordinates only'
        },
        ErrorType.GPS_ERROR: {
            'title': '🛰️ GPS Signal Issue',
            'message': 'Your GPS coordinates appear to be invalid or inaccurate.',
            'action': 'Please ensure GPS is enabled and try sharing location again'
        },
        ErrorType.UNKNOWN_ERROR: {
            'title': '⚠️ Unexpected Error',
            'message': 'Something unexpected happened.',
            'action': 'Please try again or contact support if the issue persists'
        }
    }
    
    @classmethod
    def classify_error(cls, error: Exception) -> ErrorType:
        """Classify an error based on its type and message"""
        error_message = str(error).lower()
        
        # Check for specific error types
        if 'validation' in error_message or 'invalid' in error_message:
            return ErrorType.VALIDATION_ERROR
        elif 'api' in error_message or 'gemini' in error_message:
            return ErrorType.API_ERROR
        elif 'sheet' in error_message or 'database' in error_message or 'gspread' in error_message:
            return ErrorType.DATABASE_ERROR
        elif 'network' in error_message or 'connection' in error_message or 'timeout' in error_message:
            return ErrorType.NETWORK_ERROR
        elif 'permission' in error_message or 'unauthorized' in error_message or 'forbidden' in error_message:
            return ErrorType.PERMISSION_ERROR
        elif 'rate limit' in error_message or 'too many' in error_message:
            return ErrorType.RATE_LIMIT_ERROR
        elif 'location' in error_message or 'coordinates' in error_message:
            return ErrorType.LOCATION_ERROR
        elif 'geocoding' in error_message or 'address' in error_message or 'nominatim' in error_message:
            return ErrorType.GEOCODING_ERROR
        elif 'gps' in error_message or 'latitude' in error_message or 'longitude' in error_message:
            return ErrorType.GPS_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    @classmethod
    async def handle_error(cls, error: Exception, update: Optional[Update] = None, 
                          context: Optional[ContextTypes.DEFAULT_TYPE] = None,
                          custom_message: Optional[str] = None) -> None:
        """
        Handle an error by logging it and optionally notifying the user
        
        Args:
            error: The exception that occurred
            update: Telegram update object (for user notification)
            context: Telegram context object
            custom_message: Custom error message to show user
        """
        # Log the error with full traceback
        error_type = cls.classify_error(error)
        logger.error(
            f"Error occurred - Type: {error_type.value}, "
            f"Message: {str(error)}, "
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Store error in context for potential retry
        if context and hasattr(context, 'user_data'):
            context.user_data['last_error'] = {
                'type': error_type.value,
                'message': str(error),
                'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                    'error', 40, '', 0, '', (), None
                ))
            }
        
        # Notify user if update is available
        if update and hasattr(update, 'message') and update.message:
            try:
                if custom_message:
                    await update.message.reply_text(custom_message)
                else:
                    error_info = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])
                    
                    message = f"{error_info['title']}\n\n"
                    message += f"{error_info['message']}\n\n"
                    message += f"💡 {error_info['action']}"
                    
                    # Add specific error details for validation errors
                    if error_type == ErrorType.VALIDATION_ERROR:
                        message += f"\n\n📝 Details: {str(error)}"
                    
                    await update.message.reply_text(message)
            except Exception as notification_error:
                logger.error(f"Failed to send error notification: {notification_error}")
    
    @classmethod
    def create_error_report(cls, error: Exception, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a detailed error report for debugging"""
        error_type = cls.classify_error(error)
        
        report = {
            'error_type': error_type.value,
            'error_message': str(error),
            'error_class': error.__class__.__name__,
            'traceback': traceback.format_exc(),
            'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'error', 40, '', 0, '', (), None
            ))
        }
        
        if context_data:
            report['context'] = context_data
        
        return report
    
    @classmethod
    async def handle_validation_error(cls, error: Exception, update: Update, 
                                    field_name: Optional[str] = None) -> None:
        """Handle validation errors with specific guidance"""
        error_message = f"❌ **Input Error**\n\n"
        
        if field_name:
            error_message += f"Issue with **{field_name}**: {str(error)}\n\n"
        else:
            error_message += f"{str(error)}\n\n"
        
        error_message += "💡 **How to fix:**\n"
        error_message += "• Use the correct format shown in the examples\n"
        error_message += "• Check for typos in numbers and text\n"
        error_message += "• Make sure all required fields are filled\n\n"
        error_message += "Need help? Use /help for examples and guidance."
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception as e:
            # Fallback to plain text if markdown fails
            await update.message.reply_text(error_message.replace('*', ''))
    
    @classmethod
    async def handle_api_error(cls, error: Exception, update: Update) -> None:
        """Handle API-related errors with fallback suggestions"""
        error_message = "🔧 **Service Issue**\n\n"
        error_message += "Our AI parsing service is temporarily unavailable.\n\n"
        error_message += "💡 **What you can do:**\n"
        error_message += "• Try using the structured format:\n"
        error_message += "```\n"
        error_message += "Client: Apollo Pharmacy\n"
        error_message += "Location: Bandra\n"
        error_message += "Orders: 3\n"
        error_message += "Amount: ₹24000\n"
        error_message += "Remarks: Good conversation\n"
        error_message += "```\n"
        error_message += "• Or try again in a few minutes"
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            # Fallback without markdown
            plain_message = error_message.replace('*', '').replace('`', '')
            await update.message.reply_text(plain_message)
    
    @classmethod
    async def handle_database_error(cls, error: Exception, update: Update, 
                                  entry_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle database errors with data preservation"""
        error_message = "💾 **Data Service Issue**\n\n"
        error_message += "Unable to save your entry right now, but don't worry!\n\n"
        
        if entry_data:
            error_message += "📋 **Your entry details:**\n"
            for key, value in entry_data.items():
                if key and value:
                    error_message += f"• {key.title()}: {value}\n"
            error_message += "\n"
        
        error_message += "💡 **What happens next:**\n"
        error_message += "• Your data is temporarily stored\n"
        error_message += "• Try again in a few minutes\n"
        error_message += "• Contact support if the issue persists"
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            plain_message = error_message.replace('*', '')
            await update.message.reply_text(plain_message)


# Convenience functions for common error scenarios
async def handle_error(error: Exception, update: Optional[Update] = None, 
                      context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
    """Quick error handling function"""
    await ErrorHandler.handle_error(error, update, context)


async def handle_validation_error(error: Exception, update: Update, field_name: Optional[str] = None) -> None:
    """Quick validation error handling"""
    await ErrorHandler.handle_validation_error(error, update, field_name)


async def handle_api_error(error: Exception, update: Update) -> None:
    """Quick API error handling"""
    await ErrorHandler.handle_api_error(error, update)


async def handle_database_error(error: Exception, update: Update, entry_data: Optional[Dict[str, Any]] = None) -> None:
    """Quick database error handling"""
    await ErrorHandler.handle_database_error(error, update, entry_data)  
  @classmethod
    async def handle_location_error(cls, error: Exception, update: Update, 
                                  error_context: Optional[str] = None) -> None:
        """Handle location-related errors with specific guidance"""
        error_message = "📍 **Location Service Issue**\n\n"
        
        if error_context:
            error_message += f"Context: {error_context}\n\n"
        
        error_message += f"Issue: {str(error)}\n\n"
        error_message += "💡 **Troubleshooting Steps:**\n"
        error_message += "• Ensure GPS is enabled on your device\n"
        error_message += "• Check that Telegram has location permissions\n"
        error_message += "• Try moving to an area with better GPS signal\n"
        error_message += "• Wait a moment and try sharing location again\n\n"
        error_message += "🔄 **Alternative:** You can continue without GPS - just enter location manually in your sales entries."
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(error_message.replace('*', ''))
    
    @classmethod
    async def handle_geocoding_error(cls, error: Exception, update: Update,
                                   coordinates: Optional[tuple] = None) -> None:
        """Handle geocoding service errors with fallback options"""
        error_message = "🌍 **Address Resolution Issue**\n\n"
        error_message += "Unable to convert your GPS coordinates to a readable address.\n\n"
        
        if coordinates:
            lat, lon = coordinates
            error_message += f"📍 **Your Coordinates:** {lat:.6f}, {lon:.6f}\n\n"
        
        error_message += "💡 **What this means:**\n"
        error_message += "• Your location is still saved with GPS coordinates\n"
        error_message += "• Sales entries will include coordinate data\n"
        error_message += "• Analytics will work with coordinate-based insights\n\n"
        error_message += "🔧 **Possible causes:**\n"
        error_message += "• Geocoding service temporarily unavailable\n"
        error_message += "• Location is in a remote area\n"
        error_message += "• Network connectivity issues\n\n"
        error_message += "✅ **Your location data is still valuable for analytics!**"
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(error_message.replace('*', ''))
    
    @classmethod
    async def handle_gps_accuracy_warning(cls, update: Update, accuracy: float,
                                        threshold: float = 100) -> None:
        """Handle GPS accuracy warnings"""
        warning_message = "⚠️ **GPS Accuracy Warning**\n\n"
        warning_message += f"Your GPS accuracy is {accuracy:.0f} meters.\n"
        warning_message += f"For best results, we recommend accuracy under {threshold} meters.\n\n"
        warning_message += "💡 **To improve accuracy:**\n"
        warning_message += "• Move to an open area away from buildings\n"
        warning_message += "• Ensure GPS is enabled in device settings\n"
        warning_message += "• Wait for GPS to get a better signal\n"
        warning_message += "• Try sharing location again in a few moments\n\n"
        warning_message += "🤔 **Continue anyway?**\n"
        warning_message += "Your location will still be saved, but may be less precise for analytics."
        
        try:
            await update.message.reply_text(warning_message, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(warning_message.replace('*', ''))
    
    @classmethod
    async def handle_location_permission_denied(cls, update: Update) -> None:
        """Handle location permission denied scenarios"""
        error_message = "🔒 **Location Permission Required**\n\n"
        error_message += "It looks like location sharing was denied or cancelled.\n\n"
        error_message += "📍 **To enable location features:**\n\n"
        error_message += "**On Android:**\n"
        error_message += "1. Open Telegram settings\n"
        error_message += "2. Go to Privacy and Security\n"
        error_message += "3. Enable Location permissions\n"
        error_message += "4. Try `/location` command again\n\n"
        error_message += "**On iOS:**\n"
        error_message += "1. Go to iPhone Settings\n"
        error_message += "2. Find Telegram in app list\n"
        error_message += "3. Enable Location permissions\n"
        error_message += "4. Try `/location` command again\n\n"
        error_message += "💡 **Benefits of location sharing:**\n"
        error_message += "• Automatic location tagging in sales entries\n"
        error_message += "• Territory performance analytics\n"
        error_message += "• Route optimization insights\n"
        error_message += "• Geographic sales distribution analysis\n\n"
        error_message += "🔄 **Ready to try again?** Use `/location` when you're ready!"
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(error_message.replace('*', ''))
    
    @classmethod
    async def handle_location_service_unavailable(cls, update: Update) -> None:
        """Handle location service unavailable scenarios"""
        error_message = "🛠️ **Location Service Temporarily Unavailable**\n\n"
        error_message += "Our location processing service is currently experiencing issues.\n\n"
        error_message += "💡 **What you can do:**\n"
        error_message += "• Continue with manual location entry in sales\n"
        error_message += "• Try location sharing again in a few minutes\n"
        error_message += "• Your sales entries will still be saved normally\n\n"
        error_message += "🔄 **Service Status:**\n"
        error_message += "• GPS coordinate processing: ⚠️ Limited\n"
        error_message += "• Address resolution: ⚠️ Limited\n"
        error_message += "• Sales entry logging: ✅ Working\n"
        error_message += "• Analytics: ✅ Working\n\n"
        error_message += "📧 **We're working to restore full service quickly!**"
        
        try:
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(error_message.replace('*', ''))
    
    @classmethod
    def log_location_event(cls, event_type: str, user_id: int, details: Dict[str, Any]) -> None:
        """Log location-related events for monitoring and debugging"""
        log_entry = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                'location', 20, '', 0, '', (), None
            )),
            'details': details
        }
        
        if event_type == 'location_shared':
            logger.info(f"📍 Location shared by user {user_id}: {details}")
        elif event_type == 'location_error':
            logger.error(f"📍 Location error for user {user_id}: {details}")
        elif event_type == 'geocoding_failed':
            logger.warning(f"🌍 Geocoding failed for user {user_id}: {details}")
        elif event_type == 'gps_accuracy_warning':
            logger.warning(f"⚠️ GPS accuracy warning for user {user_id}: {details}")
        else:
            logger.info(f"📍 Location event '{event_type}' for user {user_id}: {details}")


# Convenience functions for common error scenarios
async def handle_error(error: Exception, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main error handler - delegates to ErrorHandler class"""
    await ErrorHandler.handle_error(error, update, context)

async def handle_validation_error(error: Exception, update: Update, field_name: str = None) -> None:
    """Handle validation errors"""
    await ErrorHandler.handle_validation_error(error, update, field_name)

async def handle_api_error(error: Exception, update: Update) -> None:
    """Handle API errors"""
    await ErrorHandler.handle_api_error(error, update)

async def handle_database_error(error: Exception, update: Update, data: Dict[str, Any] = None) -> None:
    """Handle database errors"""
    await ErrorHandler.handle_database_error(error, update, data)

# New location-specific error handlers
async def handle_location_error(error: Exception, update: Update, context: str = None) -> None:
    """Handle location-related errors"""
    await ErrorHandler.handle_location_error(error, update, context)

async def handle_geocoding_error(error: Exception, update: Update, coordinates: tuple = None) -> None:
    """Handle geocoding service errors"""
    await ErrorHandler.handle_geocoding_error(error, update, coordinates)

async def handle_gps_accuracy_warning(update: Update, accuracy: float, threshold: float = 100) -> None:
    """Handle GPS accuracy warnings"""
    await ErrorHandler.handle_gps_accuracy_warning(update, accuracy, threshold)

async def handle_location_permission_denied(update: Update) -> None:
    """Handle location permission denied"""
    await ErrorHandler.handle_location_permission_denied(update)

async def handle_location_service_unavailable(update: Update) -> None:
    """Handle location service unavailable"""
    await ErrorHandler.handle_location_service_unavailable(update)

def log_location_event(event_type: str, user_id: int, details: Dict[str, Any]) -> None:
    """Log location events"""
    ErrorHandler.log_location_event(event_type, user_id, details)