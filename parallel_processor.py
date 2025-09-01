#!/usr/bin/env python3
"""
⚡ PARALLEL PROCESSOR MODULE
===========================
High-performance parallel processing for analytics and bulk operations
"""

import asyncio
import concurrent.futures
import multiprocessing
from typing import List, Dict, Any, Callable, Optional
from functools import partial
import time

from logger import logger
from functools import wraps

class ParallelProcessor:
    """⚡ High-performance parallel processing engine"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(4, multiprocessing.cpu_count())
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        logger.info(f"⚡ Parallel Processor initialized with {self.max_workers} workers")
    
    async def process_parallel_tasks(self, tasks: List[Dict[str, Any]], 
                                   processor_func: Callable, 
                                   use_processes: bool = False) -> List[Any]:
        """Process multiple tasks in parallel"""
        try:
            start_time = time.time()
            logger.info(f"⚡ Starting parallel processing of {len(tasks)} tasks")
            
            # Choose executor based on task type
            executor = self.process_pool if use_processes else self.thread_pool
            
            # Create partial function with common parameters
            loop = asyncio.get_event_loop()
            
            # Submit all tasks
            futures = []
            for task in tasks:
                future = loop.run_in_executor(executor, processor_func, task)
                futures.append(future)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*futures, return_exceptions=True)
            
            # Process results and handle exceptions
            successful_results = []
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"⚡ Task {i} failed: {result}")
                    failed_count += 1
                else:
                    successful_results.append(result)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"⚡ Parallel processing completed: {len(successful_results)} successful, "
                       f"{failed_count} failed in {processing_time:.2f}s")
            
            return successful_results
            
        except Exception as e:
            logger.error(f"⚡ Parallel processing error: {e}")
            return []
    
    def process_data_chunks(self, data: List[Any], chunk_size: int, 
                          processor_func: Callable) -> List[Any]:
        """Process data in parallel chunks"""
        try:
            # Split data into chunks
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            logger.info(f"⚡ Processing {len(data)} items in {len(chunks)} chunks")
            
            # Process chunks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                chunk_results = list(executor.map(processor_func, chunks))
            
            # Flatten results
            results = []
            for chunk_result in chunk_results:
                if isinstance(chunk_result, list):
                    results.extend(chunk_result)
                else:
                    results.append(chunk_result)
            
            logger.info(f"⚡ Chunk processing completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"⚡ Chunk processing error: {e}")
            return []
    
    async def process_analytics_parallel(self, user_ids: List[int], 
                                       analytics_func: Callable) -> Dict[int, Any]:
        """Process analytics for multiple users in parallel"""
        try:
            logger.info(f"⚡ Processing analytics for {len(user_ids)} users in parallel")
            
            # Create tasks for each user
            tasks = [{'user_id': user_id} for user_id in user_ids]
            
            # Process in parallel
            results = await self.process_parallel_tasks(tasks, analytics_func)
            
            # Map results back to user IDs
            user_analytics = {}
            for i, result in enumerate(results):
                if i < len(user_ids) and result:
                    user_analytics[user_ids[i]] = result
            
            logger.info(f"⚡ Analytics processing completed for {len(user_analytics)} users")
            return user_analytics
            
        except Exception as e:
            logger.error(f"⚡ Parallel analytics error: {e}")
            return {}
    
    def process_batch_validation(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate multiple entries in parallel"""
        try:
            logger.info(f"⚡ Validating {len(entries)} entries in parallel")
            
            def validate_entry(entry):
                try:
                    from input_processor import validate_entry
                    validated_data, warnings = validate_entry(entry)
                    return {
                        'success': True,
                        'data': validated_data,
                        'warnings': warnings,
                        'original': entry
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'original': entry
                    }
            
            # Process validations in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(validate_entry, entries))
            
            logger.info(f"⚡ Batch validation completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"⚡ Batch validation error: {e}")
            return []
    
    async def process_geocoding_batch(self, coordinates_list: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Process multiple geocoding requests in parallel"""
        try:
            logger.info(f"⚡ Processing {len(coordinates_list)} geocoding requests in parallel")
            
            def geocode_coordinates(coords):
                try:
                    from geocoding import geocoding_service
                    return geocoding_service.get_location_info(
                        coords['latitude'], 
                        coords['longitude']
                    )
                except Exception as e:
                    logger.error(f"⚡ Geocoding error for {coords}: {e}")
                    return None
            
            # Process geocoding in parallel with rate limiting
            results = []
            batch_size = 5  # Limit concurrent requests to respect API limits
            
            for i in range(0, len(coordinates_list), batch_size):
                batch = coordinates_list[i:i + batch_size]
                
                # Process batch
                loop = asyncio.get_event_loop()
                batch_futures = [
                    loop.run_in_executor(self.thread_pool, geocode_coordinates, coords)
                    for coords in batch
                ]
                
                batch_results = await asyncio.gather(*batch_futures, return_exceptions=True)
                results.extend(batch_results)
                
                # Rate limiting delay between batches
                if i + batch_size < len(coordinates_list):
                    await asyncio.sleep(1)  # 1 second delay between batches
            
            logger.info(f"⚡ Geocoding batch completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"⚡ Geocoding batch error: {e}")
            return []
    
    async def process_chart_generation_parallel(self, chart_configs: List[Dict[str, Any]]) -> List[str]:
        """Generate multiple charts in parallel"""
        try:
            logger.info(f"⚡ Generating {len(chart_configs)} charts in parallel")
            
            def generate_chart(config):
                try:
                    from analytics import analytics_engine
                    
                    chart_type = config.get('type', 'default')
                    user_id = config.get('user_id')
                    
                    # Generate specific chart based on type
                    if chart_type == 'revenue_trend':
                        return analytics_engine._create_revenue_trend_chart_for_user(user_id)
                    elif chart_type == 'client_performance':
                        return analytics_engine._create_client_performance_chart_for_user(user_id)
                    elif chart_type == 'location_analysis':
                        return analytics_engine._create_location_analysis_chart_for_user(user_id)
                    else:
                        # Fallback to general chart generation
                        charts = analytics_engine.generate_advanced_charts(user_id)
                        return charts[0] if charts else None
                        
                except Exception as e:
                    logger.error(f"⚡ Chart generation error for {config}: {e}")
                    return None
            
            # Generate charts in parallel using asyncio
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(self.thread_pool, generate_chart, config)
                for config in chart_configs
            ]
            
            chart_paths = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out failed generations and exceptions
            successful_charts = [
                path for path in chart_paths 
                if path and not isinstance(path, Exception) and isinstance(path, str)
            ]
            
            logger.info(f"⚡ Chart generation completed: {len(successful_charts)} charts")
            return successful_charts
            
        except Exception as e:
            logger.error(f"⚡ Chart generation error: {e}")
            return []
    
    def cleanup(self):
        """Clean up executor resources"""
        try:
            self.thread_pool.shutdown(wait=True)
            self.process_pool.shutdown(wait=True)
            logger.info("⚡ Parallel processor cleaned up")
        except Exception as e:
            logger.error(f"⚡ Cleanup error: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass

    # Global instance
parallel_processor = ParallelProcessor()

# Decorator for parallel processing
def parallel_process(max_workers: int = 4):
    """Decorator to enable parallel processing for functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            processor = ParallelProcessor(max_workers=max_workers)
            try:
                # If first argument is a list, process in parallel
                if args and isinstance(args[0], list) and len(args[0]) > 1:
                    items = args[0]
                    other_args = args[1:]
                    
                    # Create processing function
                    def process_item(item):
                        return func(item, *other_args, **kwargs)
                    
                    # Process in parallel
                    results = await processor.process_with_rate_limit(items, process_item)
                    return results
                else:
                    # Single item processing
                    return func(*args, **kwargs)
                    
            finally:
                await processor.shutdown()
        
        return wrapper
    return decorator

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            processing_time = time.time() - start_time
            logger.info(f"⚡ {func.__name__} completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"⚡ {func.__name__} failed after {processing_time:.2f}s: {e}")
            raise
    
    return wrapper

# Global instance
parallel_processor = ParallelProcessor()