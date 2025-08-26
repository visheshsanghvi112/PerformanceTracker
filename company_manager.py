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
        """🔄 Switch user's current company with enhanced validation"""
        try:
            # Input validation
            if not user_id or not isinstance(user_id, int):
                logger.error(f"❌ Invalid user_id: {user_id}")
                return False
            
            if not new_company or not isinstance(new_company, str):
                logger.error(f"❌ Invalid company: {new_company}")
                return False
            
            user_str = str(user_id)
            
            # Check if user is registered
            if user_str not in self.user_mappings:
                logger.error(f"❌ User {user_id} not registered")
                return False
            
            # Check if company exists and is active
            if new_company not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {new_company}")
                return False
            
            company_info = self.COMPANIES[new_company]
            if not company_info.get("active", True):
                logger.error(f"❌ Company {new_company} is not active")
                return False
            
            # Check user permissions
            user_data = self.user_mappings[user_str]
            allowed_companies = user_data.get("allowed_companies", [])
            if new_company not in allowed_companies:
                logger.error(f"❌ User {user_id} not allowed access to {new_company}")
                return False
            
            # Check if already on this company
            current_company = user_data.get("current_company")
            if current_company == new_company:
                logger.info(f"ℹ️ User {user_id} already on company {new_company}")
                return True  # Not an error, just already there
            
            # Perform the switch
            self.user_mappings[user_str]["current_company"] = new_company
            self.user_mappings[user_str]["last_switched"] = datetime.now().isoformat()
            
            # Save with error handling
            try:
                self._save_user_mappings()
            except Exception as save_error:
                logger.error(f"❌ Failed to save user mappings after switch: {save_error}")
                # Rollback the change
                self.user_mappings[user_str]["current_company"] = current_company
                return False
            
            logger.info(f"🔄 User {user_id} switched from {current_company} to {new_company}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to switch user {user_id} to {new_company}: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════
    # 👑 ADMIN MANAGEMENT METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def admin_assign_user_to_company(self, admin_id: int, user_id: int, company: str) -> bool:
        """👑 Admin: Assign user to a company with enhanced validation"""
        # Admin permission check
        if not self.is_admin(admin_id):
            logger.error(f"❌ User {admin_id} is not admin")
            return False
        
        try:
            # Input validation
            if not user_id or not isinstance(user_id, int):
                logger.error(f"❌ Invalid user_id: {user_id}")
                return False
            
            if not company or not isinstance(company, str):
                logger.error(f"❌ Invalid company: {company}")
                return False
            
            user_str = str(user_id)
            
            # Check if company exists and is active
            if company not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {company}")
                return False
            
            company_info = self.COMPANIES[company]
            if not company_info.get("active", True):
                logger.error(f"❌ Company {company} is not active")
                return False
            
            # Create user if doesn't exist (for admin assignment)
            if user_str not in self.user_mappings:
                logger.info(f"📝 Creating new user {user_id} during admin assignment")
                self.user_mappings[user_str] = {
                    "user_name": f"User_{user_id}",  # Will be updated when user first interacts
                    "current_company": company,
                    "allowed_companies": [company],
                    "role": "user",
                    "created_date": datetime.now().isoformat(),
                    "last_switched": datetime.now().isoformat(),
                    "created_by_admin": admin_id
                }
            else:
                # Update existing user
                user_data = self.user_mappings[user_str]
                
                # Add company to allowed companies if not already there
                allowed = user_data.get("allowed_companies", [])
                if company not in allowed:
                    allowed.append(company)
                    user_data["allowed_companies"] = allowed
                    logger.info(f"📝 Added {company} to allowed companies for user {user_id}")
                
                # Switch user to this company
                old_company = user_data.get("current_company")
                user_data["current_company"] = company
                user_data["last_switched"] = datetime.now().isoformat()
                user_data["last_assigned_by"] = admin_id
                
                logger.info(f"🔄 User {user_id} switched from {old_company} to {company} by admin {admin_id}")
            
            # Save with error handling
            try:
                self._save_user_mappings()
            except Exception as save_error:
                logger.error(f"❌ Failed to save user mappings after assignment: {save_error}")
                return False
            
            logger.info(f"👑 Admin {admin_id} successfully assigned user {user_id} to company {company}")
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
    
    def assign_user_to_company(self, user_id: int, company_key: str) -> bool:
        """
        🔄 Simplified user assignment method with fallback behavior.
        Used by company registration and admin commands.
        """
        try:
            # Input validation
            if not user_id or not isinstance(user_id, int):
                logger.error(f"❌ Invalid user_id: {user_id}")
                return False
            
            if not company_key or company_key not in self.COMPANIES:
                logger.error(f"❌ Invalid company: {company_key}")
                return False
            
            user_str = str(user_id)
            
            # Create or update user mapping
            if user_str not in self.user_mappings:
                # New user registration
                self.user_mappings[user_str] = {
                    "user_name": f"User_{user_id}",
                    "current_company": company_key,
                    "allowed_companies": [company_key],
                    "role": "user",
                    "created_date": datetime.now().isoformat(),
                    "last_switched": datetime.now().isoformat()
                }
                logger.info(f"📝 New user {user_id} registered with company {company_key}")
            else:
                # Existing user - switch company
                return self.switch_user_company(user_id, company_key)
            
            # Save with error handling
            try:
                self._save_user_mappings()
                return True
            except Exception as save_error:
                logger.error(f"❌ Failed to save user assignment: {save_error}")
                # Remove the user mapping if save failed
                if user_str in self.user_mappings:
                    del self.user_mappings[user_str]
                return False
                
        except Exception as e:
            logger.error(f"❌ User assignment failed: {e}")
            return False
    
    def remove_user_from_company(self, user_id: int) -> bool:
        """
        🗑️ Remove user from current company (admin function).
        """
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                logger.error(f"❌ User {user_id} not found")
                return False
            
            # Get current company before removal
            current_company = self.user_mappings[user_str].get("current_company")
            
            # Remove user completely
            del self.user_mappings[user_str]
            
            # Save changes
            try:
                self._save_user_mappings()
                logger.info(f"🗑️ User {user_id} removed from company {current_company}")
                return True
            except Exception as save_error:
                logger.error(f"❌ Failed to save user removal: {save_error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ User removal failed: {e}")
            return False
    
    def validate_user_access(self, user_id: int, company_key: str) -> bool:
        """
        🔍 Validate if user has access to specific company.
        """
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                return False
            
            if company_key not in self.COMPANIES:
                return False
            
            allowed_companies = self.user_mappings[user_str].get("allowed_companies", [])
            return company_key in allowed_companies
            
        except Exception as e:
            logger.error(f"❌ Access validation failed: {e}")
            return False
    
    def get_user_info(self, user_id: int) -> Dict:
        """
        📋 Get complete user information with fallback values.
        """
        try:
            user_str = str(user_id)
            
            if user_str not in self.user_mappings:
                return {
                    "registered": False,
                    "current_company": None,
                    "allowed_companies": [],
                    "role": "user"
                }
            
            user_data = self.user_mappings[user_str].copy()
            user_data["registered"] = True
            
            # Add company display names
            current_company = user_data.get("current_company")
            if current_company:
                user_data["current_company_display"] = self.get_company_display_name(current_company)
            
            return user_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get user info for {user_id}: {e}")
            return {
                "registered": False,
                "current_company": None,
                "allowed_companies": [],
                "role": "user",
                "error": str(e)
            }


# Global company manager instance
company_manager = CompanyManager()
