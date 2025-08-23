"""
Decorators for error handling, retries, and performance monitoring
"""

import functools
import asyncio
import time
from typing import Callable, Any, Optional
from logger import logger


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise last_exception
            
            return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise last_exception
            
            return None
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def handle_errors(default_return: Any = None, notify_user: bool = True):
    """
    Error handling decorator that catches exceptions and provides user feedback
    
    Args:
        default_return: Value to return if function fails
        notify_user: Whether to send error message to user
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if notify_user and len(args) > 0:
                    # Try to find update object in args to send error message
                    update = None
                    for arg in args:
                        if hasattr(arg, 'message') and hasattr(arg.message, 'reply_text'):
                            update = arg
                            break
                    
                    if update:
                        try:
                            await update.message.reply_text(
                                "⚠️ Something went wrong. Please try again or contact support if the issue persists."
                            )
                        except:
                            pass  # Don't fail if we can't send error message
                
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                return default_return
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def measure_time(log_level: str = "INFO"):
    """
    Decorator to measure and log function execution time
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                getattr(logger, log_level.lower())(
                    f"{func.__name__} executed in {execution_time:.3f} seconds"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f} seconds: {str(e)}"
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                getattr(logger, log_level.lower())(
                    f"{func.__name__} executed in {execution_time:.3f} seconds"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f} seconds: {str(e)}"
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def rate_limit(calls_per_minute: int = 10):
    """
    Rate limiting decorator to prevent spam
    """
    call_times = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Try to extract user ID from args
            user_id = None
            for arg in args:
                if hasattr(arg, 'effective_user') and hasattr(arg.effective_user, 'id'):
                    user_id = arg.effective_user.id
                    break
            
            if user_id:
                current_time = time.time()
                user_calls = call_times.get(user_id, [])
                
                # Remove calls older than 1 minute
                user_calls = [call_time for call_time in user_calls if current_time - call_time < 60]
                
                if len(user_calls) >= calls_per_minute:
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    # Try to send rate limit message
                    for arg in args:
                        if hasattr(arg, 'message') and hasattr(arg.message, 'reply_text'):
                            try:
                                await arg.message.reply_text(
                                    "⏰ You're sending messages too quickly. Please wait a moment and try again."
                                )
                            except:
                                pass
                            break
                    return None
                
                user_calls.append(current_time)
                call_times[user_id] = user_calls
            
            return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return func  # Rate limiting only works for async functions
    
    return decorator