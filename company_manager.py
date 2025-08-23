"""
🏢 MULTI-COMPANY MANAGEMENT SYSTEM
=================================
Handles company selection, user assignments, and admin controls
for JohnLee, Yugrow Pharmacy, Ambica Pharma, Baker and Davis
"""

import json
import os
from typing import Dict, List, Optional, Set
from datetime import datetime
from logger import logger

class CompanyManager:
    """🏢 Company Management System"""
    
    # Company configurations
    COMPANIES = {
        "johnlee": {
            "name": "JohnLee",
            "display_name": "🏪 JohnLee",
            "sheet_name": "JohnLee_Data",
            "color": "🔵",
            "active": True
        },
        "yugrow": {
            "name": "Yugrow Pharmacy", 
            "display_name": "💊 Yugrow Pharmacy",
            "sheet_name": "Yugrow_Data",
            "color": "🟢",
            "active": True
        },
        "ambica": {
            "name": "Ambica Pharma",
            "display_name": "🏥 Ambica Pharma", 
            "sheet_name": "Ambica_Data",
            "color": "🟡",
            "active": True
        },
        "baker": {
            "name": "Baker and Davis",
            "display_name": "🏢 Baker and Davis",
            "sheet_name": "Baker_Data", 
            "color": "🔴",
            "active": True
        }
    }
    
    # Admin user IDs (add your admin Telegram IDs here)
    ADMIN_USERS = {
        1201911108: "Vishesh Sanghvi",  # Main admin
        # Add more admin user IDs here if needed:
        # 123456789: "Admin Name",
        # 987654321: "Another Admin"
    }
    
    def __init__(self):
        self.data_file = os.path.join("data", "user_company_mapping.json")
        self.user_mappings = self._load_user_mappings()
        logger.info("🏢 Company Manager initialized")
    
    def _load_user_mappings(self) -> Dict:
        """📂 Load user-company mappings from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    mappings = json.load(f)
                logger.info(f"📂 Loaded {len(mappings)} user mappings")
                return mappings
            else:
                logger.info("📂 No existing user mappings found, starting fresh")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load user mappings: {e}")
            return {}
    
    def _save_user_mappings(self):
        """💾 Save user-company mappings to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.user_mappings, f, indent=2)
            logger.info("💾 User mappings saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to save user mappings: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 👤 USER MANAGEMENT METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def get_user_company(self, user_id: int) -> Optional[str]:
        """🏢 Get user's current company"""
        user_str = str(user_id)
        if user_str in self.user_mappings:
            return self.user_mappings[user_str].get("current_company")
        return None
    
    def get_user_allowed_companies(self, user_id: int) -> List[str]:
        """📋 Get companies user is allowed to access"""
        user_str = str(user_id)
        if user_str in self.user_mappings:
            return self.user_mappings[user_str].get("allowed_companies", [])
        return []
    
    def is_user_registered(self, user_id: int) -> bool:
        """✅ Check if user is registered with any company"""
        return str(user_id) in self.user_mappings
    
    def is_admin(self, user_id: int) -> bool:
        """👑 Check if user is admin"""
        # Check if user is in ADMIN_USERS list
        if user_id in self.ADMIN_USERS:
            return True
        
        # Check if user has admin role in mappings
        user_data = self.user_mappings.get(str(user_id), {})
        if user_data and user_data.get("role") == "admin":
            return True
            
        return False
    
    def register_user(self, user_id: int, user_name: str, initial_company: str, role: str = "user") -> bool:
        """📝 Register new user with initial company"""
        try:
            if initial_company not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {initial_company}")
                return False
            
            user_str = str(user_id)
            self.user_mappings[user_str] = {
                "user_name": user_name,
                "current_company": initial_company,
                "allowed_companies": [initial_company],
                "role": role,
                "created_date": datetime.now().isoformat(),
                "last_switched": datetime.now().isoformat()
            }
            
            self._save_user_mappings()
            logger.info(f"📝 Registered user {user_id} ({user_name}) with company {initial_company}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register user {user_id}: {e}")
            return False
    
    def switch_user_company(self, user_id: int, new_company: str) -> bool:
        """🔄 Switch user's current company"""
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                logger.error(f"❌ User {user_id} not registered")
                return False
            
            if new_company not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {new_company}")
                return False
            
            allowed_companies = self.user_mappings[user_str].get("allowed_companies", [])
            if new_company not in allowed_companies:
                logger.error(f"❌ User {user_id} not allowed access to {new_company}")
                return False
            
            self.user_mappings[user_str]["current_company"] = new_company
            self.user_mappings[user_str]["last_switched"] = datetime.now().isoformat()
            
            self._save_user_mappings()
            logger.info(f"🔄 User {user_id} switched to company {new_company}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to switch user {user_id} to {new_company}: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════
    # 👑 ADMIN MANAGEMENT METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def admin_assign_user_to_company(self, admin_id: int, user_id: int, company: str) -> bool:
        """👑 Admin: Assign user to a company"""
        if not self.is_admin(admin_id):
            logger.error(f"❌ User {admin_id} is not admin")
            return False
        
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                logger.error(f"❌ User {user_id} not found")
                return False
            
            if company not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {company}")
                return False
            
            # Add company to allowed companies if not already there
            allowed = self.user_mappings[user_str].get("allowed_companies", [])
            if company not in allowed:
                allowed.append(company)
                self.user_mappings[user_str]["allowed_companies"] = allowed
            
            # Switch user to this company
            self.user_mappings[user_str]["current_company"] = company
            self.user_mappings[user_str]["last_switched"] = datetime.now().isoformat()
            
            self._save_user_mappings()
            logger.info(f"👑 Admin {admin_id} assigned user {user_id} to company {company}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Admin assign failed: {e}")
            return False
    
    def admin_remove_user_from_company(self, admin_id: int, user_id: int, company: str) -> bool:
        """👑 Admin: Remove user from a company"""
        if not self.is_admin(admin_id):
            logger.error(f"❌ User {admin_id} is not admin")
            return False
        
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                logger.error(f"❌ User {user_id} not found")
                return False
            
            allowed = self.user_mappings[user_str].get("allowed_companies", [])
            if company in allowed:
                allowed.remove(company)
                self.user_mappings[user_str]["allowed_companies"] = allowed
                
                # If current company was removed, switch to first available
                if self.user_mappings[user_str]["current_company"] == company:
                    if allowed:
                        self.user_mappings[user_str]["current_company"] = allowed[0]
                    else:
                        # User has no companies left
                        logger.warning(f"⚠️ User {user_id} has no companies left!")
                        return False
                
                self._save_user_mappings()
                logger.info(f"👑 Admin {admin_id} removed user {user_id} from company {company}")
                return True
            else:
                logger.error(f"❌ User {user_id} not in company {company}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Admin remove failed: {e}")
            return False
    
    def admin_get_all_users(self, admin_id: int) -> Dict:
        """👑 Admin: Get all user mappings"""
        if not self.is_admin(admin_id):
            logger.error(f"❌ User {admin_id} is not admin")
            return {}
        
        return self.user_mappings.copy()
    
    # ═══════════════════════════════════════════════════════════════
    # 🏢 COMPANY UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def get_company_info(self, company_key: str) -> Dict:
        """🏢 Get company information"""
        return self.COMPANIES.get(company_key, {})
    
    def get_all_companies(self) -> Dict:
        """🏢 Get all active companies"""
        return {k: v for k, v in self.COMPANIES.items() if v.get("active", True)}
    
    def get_company_display_name(self, company_key: str) -> str:
        """🏢 Get company display name"""
        return self.COMPANIES.get(company_key, {}).get("display_name", company_key)
    
    def get_company_sheet_name(self, company_key: str) -> str:
        """📊 Get company's Google Sheet name"""
        return self.COMPANIES.get(company_key, {}).get("sheet_name", f"{company_key}_Data")


# Global company manager instance
company_manager = CompanyManager()
