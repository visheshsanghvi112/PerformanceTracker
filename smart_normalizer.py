#!/usr/bin/env python3
"""
🧠 SMART DATA NORMALIZER
========================
Handles client and location name variations using fuzzy matching
- apollo, Apollo, apolo, appollo → apollo
- bandra, BANDRA, bandraa, anderiii → bandra
- mumbai, Mumbai, mummbai → mumbai
"""

from fuzzywuzzy import fuzz, process
from collections import defaultdict
import re
import pandas as pd
from typing import Dict, List, Tuple
from logger import logger

class SmartDataNormalizer:
    """🧠 Smart data normalizer with fuzzy matching"""
    
    def __init__(self):
        """Initialize normalizer with common patterns"""
        self.client_aliases = {}
        self.location_aliases = {}
        self.similarity_threshold = 70  # 70% similarity threshold for better matching
        
        # Common pharmacy client patterns
        self.pharmacy_patterns = {
            'apollo': ['apollo', 'apolo', 'appollo', 'apolloo', 'apolko', 'apollo pharmacy', 'apollo pharma', 'apollo medical'],
            'cipla': ['cipla', 'ciple', 'cipala', 'cyple', 'cipla warehouse', 'cipla medical'],
            'fortis': ['fortis', 'forits', 'fortiss', 'fortius', 'fortis hospital', 'fortis healthcare'],
            'max healthcare': ['max', 'max healthcare', 'maxhealthcare', 'max health', 'max hospital'],
            'city hospital': ['city', 'city hospital', 'cityhospital', 'city hosp', 'city medical'],
            'reliance': ['reliance', 'relianse', 'realiance', 'relians', 'reliance medical store', 'reliance pharmacy']
        }
        
        # Common location patterns  
        self.location_patterns = {
            'mumbai': ['mumbai', 'mummbai', 'mumbaii', 'mumbay', 'bombay'],
            'bandra': ['bandra', 'bandraa', 'bandara', 'bnedra'],
            'andheri': ['andheri', 'anderiii', 'aneri', 'andehri', 'andharii'],
            'pune': ['pune', 'poona', 'punee', 'puen'],
            'chennai': ['chennai', 'chenai', 'chennaii', 'madras']
        }
        
    def normalize_text(self, text: str) -> str:
        """🔤 Basic text normalization"""
        if not text or pd.isna(text):
            return ""
            
        # Remove extra spaces, convert to lowercase, remove special chars
        normalized = re.sub(r'[^\w\s]', '', str(text).lower().strip())
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def find_best_match(self, target: str, known_patterns: Dict[str, List[str]], threshold: int = 80) -> str:
        """🎯 Find best match using fuzzy matching"""
        if not target:
            return target
            
        normalized_target = self.normalize_text(target)
        
        best_match = normalized_target
        best_score = 0
        
        for canonical_name, variations in known_patterns.items():
            for variation in variations:
                score = fuzz.ratio(normalized_target, variation)
                if score > threshold and score > best_score:
                    best_match = canonical_name
                    best_score = score
                    
        return best_match
    
    def normalize_client_name(self, client: str) -> str:
        """👥 Normalize client names with fuzzy matching"""
        if not client or pd.isna(client):
            return ""
            
        # Check cache first
        if client in self.client_aliases:
            return self.client_aliases[client]
            
        # Find best match
        normalized = self.find_best_match(client, self.pharmacy_patterns, self.similarity_threshold)
        
        # Cache the result
        self.client_aliases[client] = normalized
        
        return normalized
    
    def normalize_location_name(self, location: str) -> str:
        """📍 Normalize location names with fuzzy matching"""
        if not location or pd.isna(location):
            return ""
            
        # Remove GPS coordinates if present
        location_clean = re.sub(r'\(GPS:.*?\)', '', str(location)).strip()
        
        # Check cache first
        if location_clean in self.location_aliases:
            return self.location_aliases[location_clean]
            
        # Find best match
        normalized = self.find_best_match(location_clean, self.location_patterns, self.similarity_threshold)
        
        # Cache the result
        self.location_aliases[location_clean] = normalized
        
        return normalized
    
    def auto_learn_patterns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """🤖 Auto-learn similar names from existing data"""
        learned_patterns = {
            'clients': defaultdict(list),
            'locations': defaultdict(list)
        }
        
        try:
            # Get client and location columns
            client_col = 'Client' if 'Client' in df.columns else 'client'
            location_col = 'Location' if 'Location' in df.columns else 'location'
            
            if client_col in df.columns:
                unique_clients = df[client_col].dropna().unique()
                
                # Group similar client names
                for i, client1 in enumerate(unique_clients):
                    normalized1 = self.normalize_text(client1)
                    for client2 in unique_clients[i+1:]:
                        normalized2 = self.normalize_text(client2)
                        similarity = fuzz.ratio(normalized1, normalized2)
                        
                        if similarity > 70:  # 70% similarity for learning
                            # Use the shorter name as canonical
                            canonical = client1 if len(client1) <= len(client2) else client2
                            variant = client2 if canonical == client1 else client1
                            learned_patterns['clients'][self.normalize_text(canonical)].append(variant)
            
            if location_col in df.columns:
                unique_locations = df[location_col].dropna().unique()
                
                # Group similar location names
                for i, loc1 in enumerate(unique_locations):
                    # Clean GPS coordinates
                    clean_loc1 = re.sub(r'\(GPS:.*?\)', '', str(loc1)).strip()
                    normalized1 = self.normalize_text(clean_loc1)
                    
                    for loc2 in unique_locations[i+1:]:
                        clean_loc2 = re.sub(r'\(GPS:.*?\)', '', str(loc2)).strip()
                        normalized2 = self.normalize_text(clean_loc2)
                        similarity = fuzz.ratio(normalized1, normalized2)
                        
                        if similarity > 70:
                            canonical = clean_loc1 if len(clean_loc1) <= len(clean_loc2) else clean_loc2
                            variant = clean_loc2 if canonical == clean_loc1 else clean_loc1
                            learned_patterns['locations'][self.normalize_text(canonical)].append(variant)
            
            # Log learned patterns
            if learned_patterns['clients']:
                logger.info(f"🧠 Auto-learned {len(learned_patterns['clients'])} client patterns")
            if learned_patterns['locations']:
                logger.info(f"🧠 Auto-learned {len(learned_patterns['locations'])} location patterns")
                
        except Exception as e:
            logger.error(f"❌ Auto-learning failed: {e}")
            
        return learned_patterns
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """📊 Normalize entire dataframe"""
        try:
            df_normalized = df.copy()
            
            # Auto-learn patterns first
            learned = self.auto_learn_patterns(df)
            
            # Update patterns with learned data
            for canonical, variants in learned['clients'].items():
                if canonical not in self.pharmacy_patterns:
                    self.pharmacy_patterns[canonical] = variants
                    
            for canonical, variants in learned['locations'].items():
                if canonical not in self.location_patterns:
                    self.location_patterns[canonical] = variants
            
            # Normalize client names
            client_col = 'Client' if 'Client' in df.columns else 'client'
            if client_col in df_normalized.columns:
                df_normalized[f'{client_col}_Normalized'] = df_normalized[client_col].apply(self.normalize_client_name)
                logger.info(f"✅ Normalized {client_col} column")
            
            # Normalize location names
            location_col = 'Location' if 'Location' in df.columns else 'location'
            if location_col in df_normalized.columns:
                df_normalized[f'{location_col}_Normalized'] = df_normalized[location_col].apply(self.normalize_location_name)
                logger.info(f"✅ Normalized {location_col} column")
            
            return df_normalized
            
        except Exception as e:
            logger.error(f"❌ DataFrame normalization failed: {e}")
            return df
    
    def get_normalization_report(self, df: pd.DataFrame) -> Dict[str, Dict[str, List[str]]]:
        """📋 Get report of all normalizations performed"""
        report = {
            'clients': defaultdict(list),
            'locations': defaultdict(list)
        }
        
        try:
            client_col = 'Client' if 'Client' in df.columns else 'client'
            location_col = 'Location' if 'Location' in df.columns else 'location'
            
            # Group clients by normalized name
            if client_col in df.columns:
                for client in df[client_col].dropna().unique():
                    normalized = self.normalize_client_name(client)
                    if normalized != client.lower():
                        report['clients'][normalized].append(client)
            
            # Group locations by normalized name
            if location_col in df.columns:
                for location in df[location_col].dropna().unique():
                    normalized = self.normalize_location_name(location)
                    clean_location = re.sub(r'\(GPS:.*?\)', '', str(location)).strip()
                    if normalized != clean_location.lower():
                        report['locations'][normalized].append(location)
            
        except Exception as e:
            logger.error(f"❌ Normalization report failed: {e}")
            
        return report

# Global instance
smart_normalizer = SmartDataNormalizer()

def normalize_for_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """🧠 Main function to normalize data for analytics"""
    return smart_normalizer.normalize_dataframe(df)

def get_normalization_summary(df: pd.DataFrame) -> str:
    """📊 Get summary of normalizations"""
    report = smart_normalizer.get_normalization_report(df)
    
    summary = "🧠 SMART NORMALIZATION APPLIED:\n"
    
    if report['clients']:
        summary += "\n👥 CLIENT NORMALIZATIONS:\n"
        for canonical, variants in report['clients'].items():
            summary += f"   {canonical} ← {', '.join(variants)}\n"
    
    if report['locations']:
        summary += "\n📍 LOCATION NORMALIZATIONS:\n"
        for canonical, variants in report['locations'].items():
            summary += f"   {canonical} ← {', '.join(variants)}\n"
    
    if not report['clients'] and not report['locations']:
        summary += "✅ No normalizations needed - data already consistent"
    
    return summary
