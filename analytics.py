"""
🚀 ADVANCED ANALYTICS ENGINE FOR PERFORMANCE TRACKER BOT
===============================================================
Next-level business intelligence with AI-powered insights,
predictive analytics, and comprehensive performance tracking.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import json
import warnings
warnings.filterwarnings('ignore')

from config import DATA_DIR
from multi_company_sheets import multi_sheet_manager
from company_manager import company_manager
from logger import logger

# Set professional styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedAnalytics:
    """🧠 AI-Powered Business Intelligence Engine"""
    
    def __init__(self):
        self.data_cache = {}  # Cache per user: {user_id: (data, timestamp)}
        self.cache_duration = timedelta(minutes=5)  # 5-minute cache
        logger.info("🔥 Advanced Analytics Engine initialized with multi-user support")
    
    def load_fresh_data(self, user_id: int) -> pd.DataFrame:
        """💾 Load fresh data from Google Sheets with user-specific filtering and intelligent caching"""
        now = datetime.now()
        
        # Use user-specific cache if still valid
        if (user_id in self.data_cache):
            cached_data, last_update = self.data_cache[user_id]
            if now - last_update < self.cache_duration:
                logger.debug(f"📊 Using cached analytics data for user {user_id}")
                return cached_data
        
        try:
            # Get user's company and load their data
            logger.info(f"🔄 Fetching fresh data for user {user_id}...")
            
            # Get user's current company
            current_company = company_manager.get_user_company(user_id)
            if not current_company:
                logger.error(f"❌ No company found for user {user_id}")
                return pd.DataFrame()
            
            logger.info(f"📊 Loading data for company: {current_company}")
            records = multi_sheet_manager.get_all_records(current_company)
            
            if not records:
                logger.warning(f"⚠️ No data found in Google Sheets for user {user_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # 🔒 CRITICAL: Filter by user ID for data privacy
            if 'user_id' in df.columns or 'telegram_id' in df.columns:
                user_col = 'user_id' if 'user_id' in df.columns else 'telegram_id'
                df = df[df[user_col].astype(str) == str(user_id)]
                logger.info(f"🔒 Filtered to {len(df)} records for user {user_id}")
            else:
                logger.error(f"🚨 CRITICAL PRIVACY VIOLATION: No user_id column found - cannot filter data for user {user_id}")
                # Return empty DataFrame instead of all data to prevent privacy breach
                return pd.DataFrame()
            
            # Clean and normalize data
            df = self._clean_and_normalize_data(df)
            
            # Update user-specific cache
            self.data_cache[user_id] = (df, now)
            
            logger.info(f"✅ Loaded {len(df)} records for user {user_id}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load data from Google Sheets for user {user_id}: {e}")
            # Try to load from local CSV backup
            return self._load_backup_data(user_id)
    
    def _clean_and_normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """🧹 Clean and normalize data for analysis"""
        try:
            # Convert date strings to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Convert numeric columns efficiently
            numeric_cols = ['amount', 'orders']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Clean text columns efficiently
            text_cols = ['client', 'location', 'type', 'remarks']
            for col in text_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            
            # Add calculated columns with proper division by zero handling
            df['revenue_per_order'] = df['amount'] / df['orders'].replace(0, 1)
            # Set revenue_per_order to 0 where orders was originally 0
            df.loc[df['orders'] == 0, 'revenue_per_order'] = 0
            df['month'] = df['date'].dt.to_period('M') if 'date' in df.columns else None
            df['weekday'] = df['date'].dt.day_name() if 'date' in df.columns else None
            df['hour'] = df['date'].dt.hour if 'date' in df.columns else None
            
            logger.debug(f"🧹 Data cleaned: {len(df)} records with {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"❌ Data cleaning failed: {e}")
            return df
    
    def _load_backup_data(self, user_id: int = None) -> pd.DataFrame:
        """💾 Load data from local CSV backup with user filtering"""
        try:
            csv_path = os.path.join(DATA_DIR, 'results.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                
                # Filter by user ID if provided
                if user_id and ('user_id' in df.columns or 'telegram_id' in df.columns):
                    user_col = 'user_id' if 'user_id' in df.columns else 'telegram_id'
                    df = df[df[user_col].astype(str) == str(user_id)]
                    logger.info(f"📋 Loaded {len(df)} records from CSV backup for user {user_id}")
                else:
                    logger.info(f"📋 Loaded {len(df)} records from CSV backup (no user filter)")
                
                return self._clean_and_normalize_data(df)
        except Exception as e:
            logger.error(f"❌ CSV backup load failed for user {user_id}: {e}")
        
        return pd.DataFrame()
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 CORE ANALYTICS FUNCTIONS
    # ═══════════════════════════════════════════════════════════════
    
    def generate_executive_dashboard(self, user_id: int) -> Dict[str, Any]:
        """📈 Generate comprehensive executive dashboard for specific user"""
        df = self.load_fresh_data(user_id)
        
        if df.empty:
            return {"error": "No data available for this user"}
        
        logger.info(f"📊 Generating executive dashboard for user {user_id}...")
        
        # Core KPIs
        total_revenue = df['amount'].sum()
        total_orders = df['orders'].sum()
        unique_clients = df['client'].nunique()
        avg_order_value = df['revenue_per_order'].mean()
        
        # Time-based analysis
        if 'date' in df.columns and not df['date'].isna().all():
            date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
            daily_revenue = df.groupby(df['date'].dt.date)['amount'].sum()
            growth_trend = self._calculate_growth_trend(daily_revenue)
        else:
            date_range = "Date information not available"
            growth_trend = 0
        
        # Top performers
        top_clients = df.groupby('client')['amount'].sum().nlargest(5).to_dict()
        top_locations = df.groupby('location')['amount'].sum().nlargest(5).to_dict()
        
        # Performance metrics
        client_retention = self._calculate_client_retention(df)
        location_efficiency = self._calculate_location_efficiency(df)
        
        dashboard = {
            "period": date_range,
            "kpis": {
                "total_revenue": f"₹{total_revenue:,.2f}",
                "total_orders": int(total_orders),
                "unique_clients": int(unique_clients),
                "avg_order_value": f"₹{avg_order_value:.2f}",
                "growth_trend": f"{growth_trend:+.1f}%"
            },
            "top_clients": top_clients,
            "top_locations": top_locations,
            "insights": {
                "client_retention_score": f"{client_retention:.1f}%",
                "location_efficiency_score": f"{location_efficiency:.1f}%",
                "revenue_concentration": self._calculate_revenue_concentration(df)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("✅ Executive dashboard generated successfully")
        return dashboard
    
    def generate_predictive_insights(self, user_id: int) -> Dict[str, Any]:
        """🔮 AI-powered predictive analytics for specific user"""
        df = self.load_fresh_data(user_id)
        
        if df.empty or len(df) < 10:
            return {"error": "Insufficient data for predictions (need at least 10 records)"}
        
        logger.info(f"🤖 Generating predictive insights for user {user_id}...")
        
        insights = {
            "revenue_forecast": self._forecast_revenue(df),
            "client_churn_risk": self._analyze_churn_risk(df),
            "seasonal_patterns": self._detect_seasonal_patterns(df),
            "growth_opportunities": self._identify_growth_opportunities(df),
            "risk_assessment": self._assess_business_risks(df)
        }
        
        logger.info("🔮 Predictive insights generated")
        return insights
    
    def generate_advanced_charts(self, user_id: int, chart_type: str = "all") -> List[str]:
        """📊 Generate professional analytical charts for specific user"""
        df = self.load_fresh_data(user_id)
        
        if df.empty:
            logger.warning(f"⚠️ No data available for charts for user {user_id}")
            return []
        
        logger.info(f"📊 Generating {chart_type} charts for user {user_id}...")
        
        chart_files = []
        
        if chart_type in ["all", "revenue"]:
            chart_files.append(self._create_revenue_trend_chart(df))
        
        if chart_type in ["all", "client"]:
            chart_files.append(self._create_client_performance_chart(df))
        
        if chart_type in ["all", "location"]:
            chart_files.append(self._create_location_analysis_chart(df))
        
        if chart_type in ["all", "heatmap"]:
            chart_files.append(self._create_performance_heatmap(df))
        
        if chart_type in ["all", "correlation"]:
            chart_files.append(self._create_correlation_matrix(df))
        
        return [f for f in chart_files if f]  # Filter out None values
    
    # ═══════════════════════════════════════════════════════════════
    # 🧮 ADVANCED CALCULATION METHODS
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════
    # 🧮 ADVANCED CALCULATION METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _calculate_growth_trend(self, daily_revenue: pd.Series) -> float:
        """📈 Calculate revenue growth trend"""
        if len(daily_revenue) < 2:
            return 0.0
        
        # Calculate 7-day moving average trend
        if len(daily_revenue) >= 7:
            recent_avg = daily_revenue.tail(7).mean()
            previous_avg = daily_revenue.head(7).mean()
            return ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0.0
        else:
            # Simple trend for smaller datasets
            return ((daily_revenue.iloc[-1] - daily_revenue.iloc[0]) / daily_revenue.iloc[0] * 100) if daily_revenue.iloc[0] > 0 else 0.0
    
    def _calculate_client_retention(self, df: pd.DataFrame) -> float:
        """👥 Calculate client retention score"""
        if 'date' not in df.columns or df['date'].isna().all():
            return 0.0
        
        try:
            # Group by month and count unique clients
            monthly_clients = df.groupby(df['date'].dt.to_period('M'))['client'].nunique()
            
            if len(monthly_clients) < 2:
                return 100.0  # Single month = 100% retention
            
            # Calculate average retention rate
            retention_rates = []
            for i in range(1, len(monthly_clients)):
                current_month = monthly_clients.index[i]
                previous_month = monthly_clients.index[i-1]
                
                current_clients = set(df[df['date'].dt.to_period('M') == current_month]['client'])
                previous_clients = set(df[df['date'].dt.to_period('M') == previous_month]['client'])
                
                if previous_clients:
                    retained = len(current_clients & previous_clients)
                    retention_rate = (retained / len(previous_clients)) * 100
                    retention_rates.append(retention_rate)
            
            return np.mean(retention_rates) if retention_rates else 100.0
            
        except Exception as e:
            logger.error(f"❌ Client retention calculation failed: {e}")
            return 0.0
    
    def _calculate_location_efficiency(self, df: pd.DataFrame) -> float:
        """📍 Calculate location efficiency score"""
        try:
            location_performance = df.groupby('location').agg({
                'amount': 'sum',
                'orders': 'sum'
            }).reset_index()
            
            location_performance['efficiency'] = location_performance['amount'] / location_performance['orders'].replace(0, 1)
            
            # Score based on consistency (lower std dev = higher score)
            efficiency_std = location_performance['efficiency'].std()
            efficiency_mean = location_performance['efficiency'].mean()
            
            # Convert to 0-100 score (lower variance = higher score)
            if efficiency_mean > 0:
                cv = efficiency_std / efficiency_mean  # Coefficient of variation
                score = max(0, 100 - (cv * 100))
                return min(100, score)
            
            return 50.0  # Default middle score
            
        except Exception as e:
            logger.error(f"❌ Location efficiency calculation failed: {e}")
            return 0.0
    
    def _calculate_revenue_concentration(self, df: pd.DataFrame) -> str:
        """💰 Calculate revenue concentration risk"""
        try:
            client_revenue = df.groupby('client')['amount'].sum().sort_values(ascending=False)
            total_revenue = client_revenue.sum()
            
            if total_revenue == 0:
                return "No revenue data"
            
            # Calculate top 20% concentration
            top_20_pct = int(len(client_revenue) * 0.2) or 1
            top_20_revenue = client_revenue.head(top_20_pct).sum()
            concentration = (top_20_revenue / total_revenue) * 100
            
            if concentration > 80:
                return f"HIGH RISK: {concentration:.1f}% from top 20% clients"
            elif concentration > 60:
                return f"MODERATE RISK: {concentration:.1f}% from top 20% clients"
            else:
                return f"LOW RISK: {concentration:.1f}% from top 20% clients"
                
        except Exception as e:
            logger.error(f"❌ Revenue concentration calculation failed: {e}")
            return "Calculation error"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔮 PREDICTIVE ANALYTICS METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _forecast_revenue(self, df: pd.DataFrame) -> Dict[str, Any]:
        """📈 Simple revenue forecasting"""
        if 'date' not in df.columns or len(df) < 7:
            return {"error": "Insufficient data for forecasting"}
        
        try:
            # Daily revenue trend
            daily_revenue = df.groupby(df['date'].dt.date)['amount'].sum()
            
            if len(daily_revenue) < 7:
                return {"error": "Need at least 7 days of data"}
            
            # Simple linear trend
            recent_7_days = daily_revenue.tail(7).mean()
            previous_7_days = daily_revenue.head(7).mean()
            
            growth_rate = (recent_7_days - previous_7_days) / previous_7_days if previous_7_days > 0 else 0
            
            # 30-day forecast
            forecast_30d = recent_7_days * 30 * (1 + growth_rate)
            
            return {
                "next_30_days": f"₹{forecast_30d:,.0f}",
                "daily_average": f"₹{recent_7_days:,.0f}",
                "growth_rate": f"{growth_rate*100:+.1f}%",
                "confidence": "Medium" if len(daily_revenue) > 14 else "Low"
            }
            
        except Exception as e:
            logger.error(f"❌ Revenue forecast failed: {e}")
            return {"error": "Forecast calculation failed"}
    
    def _analyze_churn_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """⚠️ Analyze client churn risk"""
        if 'date' not in df.columns:
            return {"error": "Date information required for churn analysis"}
        
        try:
            current_date = df['date'].max()
            cutoff_date = current_date - timedelta(days=30)
            
            # Recent clients
            recent_clients = set(df[df['date'] > cutoff_date]['client'])
            all_clients = set(df['client'])
            
            inactive_clients = all_clients - recent_clients
            churn_rate = (len(inactive_clients) / len(all_clients) * 100) if all_clients else 0
            
            # Risk level
            if churn_rate > 40:
                risk_level = "HIGH"
            elif churn_rate > 20:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"
            
            return {
                "churn_rate": f"{churn_rate:.1f}%",
                "risk_level": risk_level,
                "inactive_clients": len(inactive_clients),
                "at_risk_clients": list(inactive_clients)[:10]  # Top 10
            }
            
        except Exception as e:
            logger.error(f"❌ Churn analysis failed: {e}")
            return {"error": "Churn analysis failed"}
    
    def _detect_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """📅 Detect seasonal business patterns"""
        if 'date' not in df.columns or 'weekday' not in df.columns:
            return {"error": "Date information required for seasonal analysis"}
        
        try:
            # Weekly patterns
            weekday_performance = df.groupby('weekday')['amount'].agg(['sum', 'count']).round(2)
            
            # Monthly patterns (if data spans multiple months)
            if 'month' in df.columns:
                monthly_performance = df.groupby('month')['amount'].sum()
                best_month = monthly_performance.idxmax() if not monthly_performance.empty else None
            else:
                monthly_performance = pd.Series()
                best_month = None
            
            # Hour patterns (if available)
            if 'hour' in df.columns and not df['hour'].isna().all():
                hourly_performance = df.groupby('hour')['amount'].sum()
                peak_hour = hourly_performance.idxmax() if not hourly_performance.empty else None
            else:
                peak_hour = None
            
            return {
                "best_weekday": weekday_performance['sum'].idxmax() if not weekday_performance.empty else None,
                "worst_weekday": weekday_performance['sum'].idxmin() if not weekday_performance.empty else None,
                "best_month": str(best_month) if best_month else "Insufficient data",
                "peak_hour": f"{peak_hour}:00" if peak_hour else "Time data not available"
            }
            
        except Exception as e:
            logger.error(f"❌ Seasonal analysis failed: {e}")
            return {"error": "Seasonal analysis failed"}
    
    def _identify_growth_opportunities(self, df: pd.DataFrame) -> List[str]:
        """🚀 Identify business growth opportunities"""
        opportunities = []
        
        try:
            # Low-performing locations with potential
            location_stats = df.groupby('location').agg({
                'amount': ['sum', 'count'],
                'orders': 'sum'
            }).round(2)
            
            if not location_stats.empty:
                # Find locations with few entries but good revenue per entry
                location_stats.columns = ['total_revenue', 'entry_count', 'total_orders']
                location_stats['revenue_per_entry'] = location_stats['total_revenue'] / location_stats['entry_count']
                
                underutilized = location_stats[
                    (location_stats['entry_count'] < location_stats['entry_count'].median()) & 
                    (location_stats['revenue_per_entry'] > location_stats['revenue_per_entry'].median())
                ]
                
                if not underutilized.empty:
                    opportunities.append(f"🎯 Focus on {', '.join(underutilized.index[:3])} - high revenue potential")
            
            # Client expansion opportunities
            client_stats = df.groupby('client')['amount'].agg(['sum', 'count'])
            if not client_stats.empty:
                low_frequency_high_value = client_stats[
                    (client_stats['count'] < client_stats['count'].median()) & 
                    (client_stats['sum'] > client_stats['sum'].median())
                ]
                
                if not low_frequency_high_value.empty:
                    opportunities.append(f"💼 Increase engagement with {len(low_frequency_high_value)} high-value clients")
            
            # Time-based opportunities
            if 'weekday' in df.columns:
                weekday_revenue = df.groupby('weekday')['amount'].sum()
                if not weekday_revenue.empty:
                    weak_days = weekday_revenue.nsmallest(2).index.tolist()
                    opportunities.append(f"📅 Boost performance on {', '.join(weak_days)}")
            
            if not opportunities:
                opportunities.append("📈 All metrics performing well - maintain current strategy")
                
        except Exception as e:
            logger.error(f"❌ Growth opportunity analysis failed: {e}")
            opportunities.append("❌ Analysis temporarily unavailable")
        
        return opportunities
    
    def _assess_business_risks(self, df: pd.DataFrame) -> List[str]:
        """⚠️ Assess business risks"""
        risks = []
        
        try:
            # Revenue concentration risk
            client_revenue = df.groupby('client')['amount'].sum().sort_values(ascending=False)
            if not client_revenue.empty:
                top_client_share = (client_revenue.iloc[0] / client_revenue.sum() * 100)
                if top_client_share > 50:
                    risks.append(f"🚨 HIGH RISK: {top_client_share:.1f}% revenue from single client")
                elif top_client_share > 30:
                    risks.append(f"⚠️ MEDIUM RISK: {top_client_share:.1f}% revenue from top client")
            
            # Location dependency risk
            location_revenue = df.groupby('location')['amount'].sum().sort_values(ascending=False)
            if not location_revenue.empty and len(location_revenue) > 1:
                top_location_share = (location_revenue.iloc[0] / location_revenue.sum() * 100)
                if top_location_share > 70:
                    risks.append(f"📍 LOCATION RISK: {top_location_share:.1f}% revenue from single location")
            
            # Recent performance decline
            if 'date' in df.columns and len(df) > 10:
                recent_revenue = df[df['date'] > (df['date'].max() - timedelta(days=7))]['amount'].sum()
                older_revenue = df[df['date'] <= (df['date'].max() - timedelta(days=14))]['amount'].sum()
                
                if older_revenue > 0 and recent_revenue < (older_revenue * 0.7):
                    risks.append("📉 PERFORMANCE RISK: Revenue declined >30% recently")
            
            if not risks:
                risks.append("✅ No significant risks detected")
                
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            risks.append("❌ Risk assessment temporarily unavailable")
        
        return risks
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 ADVANCED CHART GENERATION METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _create_revenue_trend_chart(self, df: pd.DataFrame) -> Optional[str]:
        """📈 Create revenue trend chart"""
        try:
            if 'date' not in df.columns:
                return None
            
            plt.figure(figsize=(12, 6))
            daily_revenue = df.groupby(df['date'].dt.date)['amount'].sum()
            
            plt.plot(daily_revenue.index, daily_revenue.values, marker='o', linewidth=2)
            plt.title('📈 Revenue Trend Analysis', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Revenue (₹)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Add trend line
            if len(daily_revenue) > 1:
                z = np.polyfit(range(len(daily_revenue)), daily_revenue.values, 1)
                p = np.poly1d(z)
                plt.plot(daily_revenue.index, p(range(len(daily_revenue))), "--", alpha=0.7, color='red')
            
            plt.tight_layout()
            
            chart_path = os.path.join(DATA_DIR, 'revenue_trend.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("📈 Revenue trend chart created")
            return chart_path
            
        except Exception as e:
            logger.error(f"❌ Revenue trend chart failed: {e}")
            return None
    
    def _create_client_performance_chart(self, df: pd.DataFrame) -> Optional[str]:
        """👥 Create client performance chart"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Top 10 clients by revenue
            client_revenue = df.groupby('client')['amount'].sum().nlargest(10)
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(client_revenue)))
            bars = plt.bar(range(len(client_revenue)), client_revenue.values, color=colors)
            
            plt.title('👥 Top 10 Client Performance', fontsize=16, fontweight='bold')
            plt.xlabel('Clients')
            plt.ylabel('Revenue (₹)')
            plt.xticks(range(len(client_revenue)), client_revenue.index, rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, client_revenue.values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01, 
                        f'₹{value:,.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            chart_path = os.path.join(DATA_DIR, 'client_performance.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("👥 Client performance chart created")
            return chart_path
            
        except Exception as e:
            logger.error(f"❌ Client performance chart failed: {e}")
            return None
    
    def _create_location_analysis_chart(self, df: pd.DataFrame) -> Optional[str]:
        """📍 Create location analysis chart"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Revenue by location
            location_revenue = df.groupby('location')['amount'].sum().sort_values(ascending=True)
            ax1.barh(range(len(location_revenue)), location_revenue.values, 
                    color=plt.cm.viridis(np.linspace(0, 1, len(location_revenue))))
            ax1.set_yticks(range(len(location_revenue)))
            ax1.set_yticklabels(location_revenue.index)
            ax1.set_title('📍 Revenue by Location', fontweight='bold')
            ax1.set_xlabel('Revenue (₹)')
            
            # Orders by location
            location_orders = df.groupby('location')['orders'].sum().sort_values(ascending=True)
            ax2.barh(range(len(location_orders)), location_orders.values,
                    color=plt.cm.plasma(np.linspace(0, 1, len(location_orders))))
            ax2.set_yticks(range(len(location_orders)))
            ax2.set_yticklabels(location_orders.index)
            ax2.set_title('📦 Orders by Location', fontweight='bold')
            ax2.set_xlabel('Orders')
            
            plt.tight_layout()
            
            chart_path = os.path.join(DATA_DIR, 'location_analysis.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("📍 Location analysis chart created")
            return chart_path
            
        except Exception as e:
            logger.error(f"❌ Location analysis chart failed: {e}")
            return None
    
    def _create_performance_heatmap(self, df: pd.DataFrame) -> Optional[str]:
        """🔥 Create performance heatmap"""
        try:
            if 'date' not in df.columns or 'weekday' not in df.columns:
                return None
            
            # Create day-hour heatmap if hour data is available
            if 'hour' in df.columns and not df['hour'].isna().all():
                pivot_data = df.groupby(['weekday', 'hour'])['amount'].sum().unstack(fill_value=0)
                
                plt.figure(figsize=(14, 8))
                sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', 
                           cbar_kws={'label': 'Revenue (₹)'})
                plt.title('🔥 Performance Heatmap: Revenue by Day & Hour', fontsize=16, fontweight='bold')
                plt.xlabel('Hour of Day')
                plt.ylabel('Day of Week')
            else:
                # Fallback: client-location heatmap
                pivot_data = df.groupby(['client', 'location'])['amount'].sum().unstack(fill_value=0)
                
                # Show only top 10 clients and locations to avoid clutter
                pivot_data = pivot_data.head(10).iloc[:, :10]
                
                plt.figure(figsize=(12, 8))
                sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='Blues',
                           cbar_kws={'label': 'Revenue (₹)'})
                plt.title('🔥 Performance Heatmap: Client-Location Revenue', fontsize=16, fontweight='bold')
                plt.xlabel('Location')
                plt.ylabel('Client')
            
            plt.tight_layout()
            
            chart_path = os.path.join(DATA_DIR, 'performance_heatmap.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("🔥 Performance heatmap created")
            return chart_path
            
        except Exception as e:
            logger.error(f"❌ Performance heatmap failed: {e}")
            return None
    
    def _create_correlation_matrix(self, df: pd.DataFrame) -> Optional[str]:
        """🔗 Create correlation matrix"""
        try:
            # Select numeric columns for correlation
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return None
            
            correlation_matrix = df[numeric_cols].corr()
            
            plt.figure(figsize=(10, 8))
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.2f', 
                       cmap='coolwarm', center=0, square=True,
                       cbar_kws={'label': 'Correlation Coefficient'})
            
            plt.title('🔗 Business Metrics Correlation Matrix', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            chart_path = os.path.join(DATA_DIR, 'correlation_matrix.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("🔗 Correlation matrix created")
            return chart_path
            
        except Exception as e:
            logger.error(f"❌ Correlation matrix failed: {e}")
            return None


# ═══════════════════════════════════════════════════════════════
# 🚀 GLOBAL INSTANCE & LEGACY COMPATIBILITY
# ═══════════════════════════════════════════════════════════════

# Global advanced analytics instance
analytics_engine = AdvancedAnalytics()

# Legacy function compatibility (for backward compatibility)
def load_data(filename='results.csv'):
    """Legacy function - use analytics_engine.load_fresh_data(user_id) instead"""
    logger.warning("⚠️ Using legacy load_data() - consider upgrading to analytics_engine with user_id")
    return analytics_engine._load_backup_data()

def generate_sales_chart(df, output_file='sales_chart.png'):
    """Legacy function - use analytics_engine.generate_advanced_charts() instead"""
    logger.warning("⚠️ Using legacy generate_sales_chart() - consider upgrading to analytics_engine")
    try:
        if 'client' in df.columns and 'amount' in df.columns:
            sales = df.groupby('client')['amount'].sum()
            plt.figure(figsize=(8, 4))
            sales.plot(kind='bar')
            plt.title('Sales by Client')
            plt.ylabel('Amount')
            plt.tight_layout()
            chart_path = os.path.join(DATA_DIR, output_file)
            plt.savefig(chart_path)
            plt.close()
            return chart_path
    except Exception as e:
        logger.error(f"❌ Legacy chart generation failed: {e}")
    return None