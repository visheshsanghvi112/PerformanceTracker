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