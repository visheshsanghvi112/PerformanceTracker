#!/usr/bin/env python3
"""
📦 BATCH HANDLER MODULE
======================
Handles batch processing of multiple entries and bulk operations
"""

import asyncio
import datetime
from typing import List, Dict, Any, Tuple, Optional
from telegram import Update
from telegram.ext import ContextTypes

from logger import logger
from gemini_parser import extract_with_gemini, extract_with_gemini_parallel, get_api_status
from input_processor import input_processor, validate_entry, ValidationError
from multi_company_sheets import multi_sheet_manager
from company_manager import company_manager
from location_handler import location_handler

class BatchHandler:
    """🔄 Handles batch processing of multiple business entries"""
    
    def __init__(self):
        self.batch_size_limit = 10  # Maximum entries per batch
        self.processing_timeout = 30  # Seconds
        logger.info("📦 Batch Handler initialized")
    
    async def process_batch_entries(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  entries_text: str, user_type: str) -> Dict[str, Any]:
        """Process multiple entries from a single message with parallel AI processing"""
        try:
            user = update.effective_user
            logger.info(f"📦 Processing batch entries for user {user.id}")
            
            # Split entries (by lines or common separators)
            raw_entries = self._split_entries(entries_text)
            
            if len(raw_entries) > self.batch_size_limit:
                return {
                    'success': False,
                    'error': f'Too many entries. Maximum {self.batch_size_limit} entries per batch.',
                    'processed': 0,
                    'failed': len(raw_entries)
                }
            
            # Check API status for parallel processing
            api_status = get_api_status()
            use_parallel = api_status['parallel_capable'] and len(raw_entries) > 1
            
            if use_parallel:
                logger.info(f"🚀 Using parallel processing with {api_status['total_keys']} API keys")
                return await self._process_entries_parallel(raw_entries, user_type, user)
            else:
                logger.info(f"⚡ Using sequential processing with {api_status['total_keys']} API key(s)")
                return await self._process_entries_sequential(raw_entries, user_type, user)
                
        except Exception as e:
            logger.error(f"📦 Batch processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': 0
            }
    
    async def _process_entries_parallel(self, raw_entries: List[str], user_type: str, user) -> Dict[str, Any]:
        """Process entries in parallel using multiple API keys"""
        try:
            # Pre-validate all entries
            valid_entries = []
            failed_entries = []
            
            for i, entry_text in enumerate(raw_entries):
                process_result = input_processor.process_input(entry_text.strip())
                if process_result['is_valid']:
                    valid_entries.append((i + 1, entry_text.strip()))
                else:
                    failed_entries.append({
                        'text': entry_text,
                        'error': process_result['reason'],
                        'index': i + 1
                    })
            
            if not valid_entries:
                return {
                    'success': False,
                    'error': 'No valid entries found',
                    'processed': 0,
                    'failed': len(failed_entries)
                }
            
            # Extract text for parallel AI processing
            valid_texts = [entry[1] for entry in valid_entries]
            
            # 🚀 PARALLEL AI PROCESSING - This is where multiple API keys shine!
            logger.info(f"🚀 Starting parallel AI processing of {len(valid_texts)} entries")
            start_time = datetime.datetime.now()
            
            parsed_results = await extract_with_gemini_parallel(valid_texts)
            
            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.info(f"⚡ Parallel AI processing completed in {processing_time:.2f} seconds")
            
            # Process parsed results
            processed_entries = []
            for i, parsed_data in enumerate(parsed_results):
                original_index, original_text = valid_entries[i]
                
                if not parsed_data or not self._is_valid_entry(parsed_data):
                    failed_entries.append({
                        'text': original_text,
                        'error': 'parsing_failed',
                        'index': original_index
                    })
                    continue
                
                try:
                    # Create entry data
                    entry_data = {
                        'client': parsed_data.get('client'),
                        'location': parsed_data.get('location'),
                        'orders': parsed_data.get('orders'),
                        'amount': parsed_data.get('amount'),
                        'remarks': parsed_data.get('remarks') or original_text,
                        'type': user_type,
                        'date': datetime.datetime.now()
                    }
                    
                    validated_data, warnings = validate_entry(entry_data)
                    processed_entries.append({
                        'data': validated_data,
                        'warnings': warnings,
                        'original_text': original_text,
                        'index': original_index
                    })
                    
                except Exception as e:
                    logger.error(f"📦 Error validating entry {original_index}: {e}")
                    failed_entries.append({
                        'text': original_text,
                        'error': str(e),
                        'index': original_index
                    })
            
            return await self._store_processed_entries(processed_entries, failed_entries, user, processing_time)
            
        except Exception as e:
            logger.error(f"📦 Parallel processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': len(raw_entries)
            }
    
    async def _process_entries_sequential(self, raw_entries: List[str], user_type: str, user) -> Dict[str, Any]:
        """Process entries sequentially (fallback method)"""
        try:
            processed_entries = []
            failed_entries = []
            
            for i, entry_text in enumerate(raw_entries):
                try:
                    logger.debug(f"📝 Processing batch entry {i+1}/{len(raw_entries)}")
                    
                    # Validate input
                    process_result = input_processor.process_input(entry_text.strip())
                    if not process_result['is_valid']:
                        failed_entries.append({
                            'text': entry_text,
                            'error': process_result['reason'],
                            'index': i + 1
                        })
                        continue
                    
                    # Parse with Gemini
                    parsed_data = extract_with_gemini(entry_text)
                    if not parsed_data or not self._is_valid_entry(parsed_data):
                        failed_entries.append({
                            'text': entry_text,
                            'error': 'parsing_failed',
                            'index': i + 1
                        })
                        continue
                    
                    # Validate entry
                    entry_data = {
                        'client': parsed_data.get('client'),
                        'location': parsed_data.get('location'),
                        'orders': parsed_data.get('orders'),
                        'amount': parsed_data.get('amount'),
                        'remarks': parsed_data.get('remarks') or entry_text,
                        'type': user_type,
                        'date': datetime.datetime.now()
                    }
                    
                    validated_data, warnings = validate_entry(entry_data)
                    processed_entries.append({
                        'data': validated_data,
                        'warnings': warnings,
                        'original_text': entry_text,
                        'index': i + 1
                    })
                    
                except Exception as e:
                    logger.error(f"📦 Error processing batch entry {i+1}: {e}")
                    failed_entries.append({
                        'text': entry_text,
                        'error': str(e),
                        'index': i + 1
                    })
            
            # Save successful entries to database
            saved_entries = []
            if processed_entries:
                saved_entries = await self._save_batch_entries(
                    processed_entries, user, user_type
                )
            
            return await self._store_processed_entries(processed_entries, failed_entries, user, 0.0)
            
        except Exception as e:
            logger.error(f"📦 Sequential processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': len(raw_entries)
            }
    
    async def _store_processed_entries(self, processed_entries: List[Dict[str, Any]], 
                                     failed_entries: List[Dict[str, Any]], 
                                     user: Any, processing_time: float) -> Dict[str, Any]:
        """Store successfully processed entries and return results"""
        try:
            # Save successful entries to database
            saved_entries = []
            if processed_entries:
                saved_entries = await self._save_batch_entries(
                    processed_entries, user, "sale"  # Default to sale type
                )
            
            return {
                'success': len(saved_entries) > 0,
                'processed': len(saved_entries),
                'failed': len(failed_entries),
                'total': len(processed_entries) + len(failed_entries),
                'saved_entries': saved_entries,
                'failed_entries': failed_entries,
                'warnings': self._collect_warnings(processed_entries),
                'processing_time_seconds': processing_time,
                'used_parallel_processing': processing_time > 0
            }
            
        except Exception as e:
            logger.error(f"📦 Error storing processed entries: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': len(failed_entries)
            }
    
    def _split_entries(self, text: str) -> List[str]:
        """Split text into individual entries"""
        # Split by common separators
        separators = ['\n\n', '\n---', '\n***', '\n===']
        
        entries = [text]  # Start with full text
        
        for separator in separators:
            new_entries = []
            for entry in entries:
                new_entries.extend(entry.split(separator))
            entries = new_entries
        
        # Filter out empty entries and clean
        cleaned_entries = []
        for entry in entries:
            cleaned = entry.strip()
            if cleaned and len(cleaned) > 10:  # Minimum length check
                cleaned_entries.append(cleaned)
        
        # If no clear separation found, try line-by-line for structured format
        if len(cleaned_entries) <= 1 and '\n' in text:
            lines = text.split('\n')
            potential_entries = []
            current_entry = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_entry:
                        potential_entries.append('\n'.join(current_entry))
                        current_entry = []
                elif any(keyword in line.lower() for keyword in ['client:', 'sold', 'bought', 'purchase']):
                    if current_entry:
                        potential_entries.append('\n'.join(current_entry))
                    current_entry = [line]
                else:
                    current_entry.append(line)
            
            if current_entry:
                potential_entries.append('\n'.join(current_entry))
            
            if len(potential_entries) > 1:
                cleaned_entries = potential_entries
        
        logger.debug(f"📦 Split text into {len(cleaned_entries)} entries")
        return cleaned_entries
    
    def _is_valid_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate parsed entry data"""
        return (
            isinstance(entry, dict) and
            entry.get("client") and
            entry.get("orders") is not None and
            entry.get("amount") is not None
        )
    
    async def _save_batch_entries(self, processed_entries: List[Dict[str, Any]], 
                                user: Any, user_type: str) -> List[Dict[str, Any]]:
        """Save batch entries to database"""
        saved_entries = []
        current_company = company_manager.get_user_company(user.id)
        
        try:
            for entry_info in processed_entries:
                try:
                    validated_data = entry_info['data']
                    
                    # Get GPS location data for entry (same for all batch entries)
                    gps_location_str = location_handler.get_location_for_entry(str(user.id), current_company)
                    
                    # Create row data
                    now = datetime.datetime.now()
                    entry_id = f"batch_{now.strftime('%Y%m%d_%H%M%S')}_{entry_info['index']}"
                    
                    row_data = [
                        entry_id,                           # Entry ID
                        now.strftime("%d-%m-%Y"),          # Date
                        user.full_name,                    # User Name
                        validated_data['type'],            # Type
                        validated_data['client'],          # Client
                        validated_data['location'],        # Original Location
                        validated_data['orders'],          # Orders
                        validated_data['amount'],          # Amount
                        validated_data.get('remarks', ''), # Remarks
                        user.id,                           # User ID
                        now.strftime("%H:%M"),             # Time
                        current_company,                   # Company
                        now.isoformat(),                   # Entry Timestamp
                        now.isoformat(),                   # Last Modified
                        gps_location_str or ""             # GPS_Location
                    ]
                    
                    # Save to company sheet
                    success = multi_sheet_manager.append_row(row_data, current_company)
                    
                    if success:
                        saved_entries.append({
                            'entry_id': entry_id,
                            'data': validated_data,
                            'warnings': entry_info['warnings'],
                            'original_text': entry_info['original_text'],
                            'index': entry_info['index']
                        })
                        logger.info(f"📦 Saved batch entry {entry_id}")
                    else:
                        logger.error(f"📦 Failed to save batch entry {entry_info['index']}")
                        
                except Exception as e:
                    logger.error(f"📦 Error saving batch entry {entry_info['index']}: {e}")
                    continue
            
            return saved_entries
            
        except Exception as e:
            logger.error(f"📦 Batch save error: {e}")
            return saved_entries
    
    def _collect_warnings(self, processed_entries: List[Dict[str, Any]]) -> List[str]:
        """Collect all warnings from processed entries"""
        all_warnings = []
        for entry in processed_entries:
            if entry.get('warnings'):
                for warning in entry['warnings']:
                    all_warnings.append(f"Entry {entry['index']}: {warning}")
        return all_warnings
    
    def format_batch_response(self, result: Dict[str, Any]) -> str:
        """Format batch processing result for user"""
        if not result['success'] and result.get('error'):
            return f"❌ **Batch Processing Failed**\n\n{result['error']}"
        
        response = f"📦 **BATCH PROCESSING COMPLETE**\n\n"
        response += f"✅ **Processed:** {result['processed']}/{result['total']} entries\n"
        
        if result['failed'] > 0:
            response += f"❌ **Failed:** {result['failed']} entries\n"
        
        # Show successful entries
        if result.get('saved_entries'):
            response += f"\n📋 **SUCCESSFUL ENTRIES:**\n"
            for entry in result['saved_entries'][:5]:  # Show first 5
                data = entry['data']
                response += f"• {data['client']} - ₹{data['amount']:,} ({data['orders']} units)\n"
            
            if len(result['saved_entries']) > 5:
                response += f"... and {len(result['saved_entries']) - 5} more entries\n"
        
        # Show warnings
        if result.get('warnings'):
            response += f"\n⚠️ **WARNINGS:**\n"
            for warning in result['warnings'][:3]:  # Show first 3
                response += f"• {warning}\n"
            
            if len(result['warnings']) > 3:
                response += f"... and {len(result['warnings']) - 3} more warnings\n"
        
        # Show failed entries
        if result.get('failed_entries'):
            response += f"\n❌ **FAILED ENTRIES:**\n"
            for failed in result['failed_entries'][:3]:  # Show first 3
                response += f"• Entry {failed['index']}: {failed['error']}\n"
            
            if len(result['failed_entries']) > 3:
                response += f"... and {len(result['failed_entries']) - 3} more failed entries\n"
        
        return response
    
    def detect_batch_input(self, text: str) -> bool:
        """Detect if input contains multiple entries"""
        text_lower = text.lower()  # Make case-insensitive
        
        # Check for multiple entry indicators
        indicators = [
            text.count('\n\n') >= 1,  # Double line breaks
            text_lower.count('client:') > 1,  # Multiple client fields
            text_lower.count('sold') + text_lower.count('bought') + text_lower.count('purchase') > 1,  # Multiple transactions
            len(text.split('\n')) > 6,  # Many lines
            any(sep in text for sep in ['---', '***', '===']),  # Explicit separators
        ]
        
        return sum(indicators) >= 2  # At least 2 indicators

# Global instance
batch_handler = BatchHandler()