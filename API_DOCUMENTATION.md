# 🔧 API Documentation - AI-Enhanced Performance Tracker

## 📋 Table of Contents
1. [Core APIs](#core-apis)
2. [Data Models](#data-models)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Authentication](#authentication)
6. [Examples](#examples)

---

## 🔧 Core APIs

### **Input Processing API**

#### `input_processor.process_input(text: str) -> Dict[str, Any]`
**Purpose:** Validates and preprocesses user input with business intelligence.

**Parameters:**
- `text` (str): User input text to process

**Returns:**
```python
{
    'is_valid': bool,           # Whether input is valid
    'should_use_ai': bool,      # Whether to use AI processing
    'reason': str,              # Validation result reason
    'fallback_response': str    # Fallback response if invalid
}
```

**Example:**
```python
from input_processor import input_processor

result = input_processor.process_input("Sold 5 tablets to Apollo for ₹25000")
# Returns: {
#     'is_valid': True,
#     'should_use_ai': True,
#     'reason': 'business_related',
#     'fallback_response': None
# }
```

#### `input_processor.is_business_related(text: str) -> bool`
**Purpose:** Check if text contains business-related content.

**Parameters:**
- `text` (str): Text to analyze

**Returns:** Boolean indicating business relevance

#### `input_processor.is_gibberish(text: str) -> bool`
**Purpose:** Detect gibberish or meaningless input.

**Parameters:**
- `text` (str): Text to analyze

**Returns:** Boolean indicating if text is gibberish

---

### **AI Response Engine API**

#### `ai_response_engine.generate_greeting_response(user_name: str, time_of_day: str) -> str`
**Purpose:** Generate personalized greeting based on time and user.

**Parameters:**
- `user_name` (str): User's display name
- `time_of_day` (str): Time period ('morning', 'afternoon', 'evening')

**Returns:** Personalized greeting string

**Example:**
```python
from ai_response_engine import ai_response_engine

greeting = ai_response_engine.generate_greeting_response("John", "morning")
# Returns: "🌅 Good morning, John! Ready to track some business today?"
```

#### `ai_response_engine.generate_success_response(entry_type: str, entry_data: Dict) -> str`
**Purpose:** Generate success message with business insights.

**Parameters:**
- `entry_type` (str): Type of entry ('Sales', 'Purchase')
- `entry_data` (Dict): Entry data with client, amount, etc.

**Returns:** Success message with insights

#### `ai_response_engine.generate_error_response(error_type: str, context: Dict) -> str`
**Purpose:** Generate helpful error guidance.

**Parameters:**
- `error_type` (str): Type of error ('parsing_failed', 'invalid_format')
- `context` (Dict): Error context information

**Returns:** Helpful error message

#### `ai_response_engine.generate_tip_of_the_day() -> str`
**Purpose:** Generate business tip or recommendation.

**Returns:** Business tip string

---

### **Location Storage API**

#### `location_storage.store_location(user_id: str, company_id: str, location_data: Dict) -> bool`
**Purpose:** Store GPS location data securely.

**Parameters:**
- `user_id` (str): User identifier
- `company_id` (str): Company identifier
- `location_data` (Dict): Location data with coordinates and address

**Returns:** Boolean indicating success

**Example:**
```python
from location_storage import location_storage

success = location_storage.store_location(
    user_id="123456",
    company_id="johnlee",
    location_data={
        'coordinates': {'latitude': 18.947974, 'longitude': 72.829952},
        'address': {'city': 'Mumbai', 'area': 'Kalbadevi'},
        'timestamp': '2025-01-25T18:30:00Z'
    }
)
```

#### `location_storage.get_location(user_id: str, company_id: str) -> Optional[Dict]`
**Purpose:** Retrieve stored location data.

**Parameters:**
- `user_id` (str): User identifier
- `company_id` (str): Company identifier

**Returns:** Location data dictionary or None

#### `location_storage.clear_location(user_id: str, company_id: str) -> bool`
**Purpose:** Remove stored location data.

**Parameters:**
- `user_id` (str): User identifier
- `company_id` (str): Company identifier

**Returns:** Boolean indicating success

#### `location_storage.get_location_status(user_id: str, company_id: str) -> Dict`
**Purpose:** Get location data status and metadata.

**Returns:**
```python
{
    'has_location': bool,
    'last_updated': str,
    'expires_at': str,
    'address_summary': str
}
```

---

### **Geocoding API**

#### `geocoding_service.reverse_geocode(latitude: float, longitude: float) -> Optional[Dict]`
**Purpose:** Convert GPS coordinates to readable address.

**Parameters:**
- `latitude` (float): GPS latitude
- `longitude` (float): GPS longitude

**Returns:** Address data dictionary or None

**Example:**
```python
from geocoding import geocoding_service

address = geocoding_service.reverse_geocode(18.947974, 72.829952)
# Returns: {
#     'city': 'Mumbai',
#     'area': 'Kalbadevi',
#     'state': 'Maharashtra',
#     'country': 'India',
#     'postal_code': '400002'
# }
```

#### `geocoding_service.get_location_info(latitude: float, longitude: float) -> Dict`
**Purpose:** Get comprehensive location information.

**Returns:**
```python
{
    'coordinates': {'latitude': float, 'longitude': float},
    'address': Dict,
    'formatted_address': str,
    'accuracy': str
}
```

---

### **Analytics Engine API**

#### `analytics_engine.generate_executive_dashboard(user_id: str) -> Dict`
**Purpose:** Generate comprehensive executive dashboard.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
```python
{
    'kpis': {
        'total_revenue': float,
        'total_orders': int,
        'avg_order_value': float,
        'growth_rate': float
    },
    'trends': List[Dict],
    'top_clients': List[Dict],
    'insights': List[str],
    'recommendations': List[str]
}
```

#### `analytics_engine.generate_predictive_insights(user_id: str) -> Dict`
**Purpose:** Generate predictive analytics and forecasts.

**Returns:**
```python
{
    'revenue_forecast': List[float],
    'growth_predictions': Dict,
    'risk_factors': List[str],
    'opportunities': List[str],
    'confidence_score': float
}
```

#### `analytics_engine.generate_advanced_charts(user_id: str) -> List[str]`
**Purpose:** Generate professional analytical charts.

**Returns:** List of chart file paths

#### `analytics_engine.generate_location_analytics(user_id: str) -> Dict`
**Purpose:** Generate GPS-based territory analytics.

**Returns:**
```python
{
    'territory_performance': Dict,
    'coverage_stats': Dict,
    'route_optimization': List[str],
    'growth_opportunities': List[str]
}
```

---

### **Batch Processing API**

#### `batch_handler.detect_batch_input(text: str) -> bool`
**Purpose:** Detect if input contains multiple entries.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:** Boolean indicating batch input

#### `batch_handler.process_batch_entries(update, context, text: str, user_type: str) -> Dict`
**Purpose:** Process multiple entries simultaneously.

**Parameters:**
- `update`: Telegram update object
- `context`: Telegram context object
- `text` (str): Batch input text
- `user_type` (str): User type ('admin', 'user')

**Returns:**
```python
{
    'total_entries': int,
    'successful': int,
    'failed': int,
    'results': List[Dict],
    'summary': str
}
```

---

### **Parallel Processing API**

#### `parallel_processor.process_parallel_analytics(user_ids: List[str], analytics_func) -> List`
**Purpose:** Process analytics for multiple users in parallel.

**Parameters:**
- `user_ids` (List[str]): List of user identifiers
- `analytics_func`: Analytics function to execute

**Returns:** List of analytics results

#### `parallel_processor.get_performance_metrics() -> Dict`
**Purpose:** Get parallel processing performance metrics.

**Returns:**
```python
{
    'active_workers': int,
    'completed_tasks': int,
    'average_processing_time': float,
    'memory_usage': float
}
```

---

## 📊 Data Models

### **Entry Data Model**
```python
{
    "client": str,           # Client name
    "orders": int,           # Number of orders/units
    "amount": float,         # Transaction amount
    "remarks": str,          # Additional notes
    "type": str,             # Entry type (Sales/Purchase)
    "timestamp": datetime,   # Entry timestamp
    "location": str,         # GPS location (optional)
    "user_id": str,          # User identifier
    "company_id": str        # Company identifier
}
```

### **Location Data Model**
```python
{
    "coordinates": {
        "latitude": float,
        "longitude": float
    },
    "address": {
        "city": str,
        "area": str,
        "state": str,
        "country": str,
        "postal_code": str
    },
    "timestamp": datetime,
    "accuracy": float,
    "expires_at": datetime
}
```

### **Analytics Response Model**
```python
{
    "dashboard": {
        "kpis": Dict[str, Any],
        "trends": List[Dict],
        "insights": List[str],
        "recommendations": List[str]
    },
    "predictions": {
        "revenue_forecast": List[float],
        "growth_rate": float,
        "risk_factors": List[str],
        "opportunities": List[str]
    },
    "charts": List[str]  # File paths to generated charts
}
```

### **User Data Model**
```python
{
    "user_id": str,
    "username": str,
    "full_name": str,
    "company_id": str,
    "role": str,             # 'admin' or 'user'
    "last_active": datetime,
    "preferences": Dict
}
```

### **Company Data Model**
```python
{
    "company_id": str,
    "display_name": str,
    "sheet_name": str,
    "admin_users": List[str],
    "features": List[str],   # Available features
    "settings": Dict
}
```

---

## ⚠️ Error Handling

### **Error Response Format**
```python
{
    "error": True,
    "error_type": str,       # Error category
    "message": str,          # User-friendly message
    "details": str,          # Technical details
    "suggestions": List[str], # Helpful suggestions
    "timestamp": datetime
}
```

### **Common Error Types**

#### **Input Processing Errors**
- `invalid_input` - Input doesn't meet validation criteria
- `gibberish_detected` - Input appears to be meaningless
- `not_business_related` - Input not related to business

#### **AI Processing Errors**
- `ai_service_unavailable` - AI service is down
- `parsing_failed` - Failed to extract data from input
- `rate_limit_exceeded` - Too many AI requests

#### **Location Errors**
- `location_not_found` - No location data available
- `geocoding_failed` - Failed to convert coordinates to address
- `location_expired` - Stored location data has expired

#### **Analytics Errors**
- `insufficient_data` - Not enough data for analytics
- `chart_generation_failed` - Failed to create charts
- `calculation_error` - Error in analytics calculations

### **Error Handling Best Practices**

```python
from decorators import handle_errors

@handle_errors(notify_user=True)
async def command_handler(update, context):
    """Command handler with automatic error handling."""
    try:
        # Command logic here
        result = process_command()
        return result
    except SpecificException as e:
        logger.error(f"Specific error: {e}")
        raise  # Re-raise for decorator to handle
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
```

---

## 🚦 Rate Limiting

### **Rate Limit Configuration**
```python
# Default rate limits
RATE_LIMITS = {
    'commands': 60,          # Commands per minute
    'ai_requests': 30,       # AI requests per minute
    'analytics': 10,         # Analytics requests per minute
    'location': 20,          # Location requests per minute
    'admin': 120             # Admin commands per minute
}
```

### **Rate Limit Decorator**
```python
from decorators import rate_limit

@rate_limit(calls_per_minute=10)
async def limited_command(update, context):
    """Command with rate limiting."""
    pass
```

### **Rate Limit Response**
```python
{
    "error": True,
    "error_type": "rate_limit_exceeded",
    "message": "Too many requests. Please wait before trying again.",
    "retry_after": 60,       # Seconds to wait
    "limit": 10,             # Requests per minute
    "remaining": 0           # Remaining requests
}
```

---

## 🔐 Authentication

### **User Authentication**
- **Telegram User ID** - Primary identifier
- **Company Assignment** - User-company mapping
- **Role-based Access** - Admin vs regular user permissions

### **Admin Verification**
```python
from company_manager import company_manager

def is_admin(user_id: int) -> bool:
    """Check if user has admin privileges."""
    return company_manager.is_admin(user_id)

def get_user_company(user_id: int) -> Optional[str]:
    """Get user's assigned company."""
    return company_manager.get_user_company(user_id)
```

### **Access Control**
```python
from decorators import admin_required

@admin_required
async def admin_command(update, context):
    """Command requiring admin privileges."""
    pass
```

---

## 💡 Examples

### **Complete Entry Processing Example**
```python
async def process_user_entry(update, context):
    """Complete example of processing user entry."""
    user = update.effective_user
    text = update.message.text
    
    # Step 1: Validate input
    validation = input_processor.process_input(text)
    if not validation['is_valid']:
        await update.message.reply_text(validation['fallback_response'])
        return
    
    # Step 2: Extract data with AI
    if validation['should_use_ai']:
        entry_data = await gemini_parser.extract_with_gemini(text)
    else:
        entry_data = basic_parser.parse_entry(text)
    
    # Step 3: Add location if available
    location = location_handler.get_location_for_entry(
        user.id, 
        company_manager.get_user_company(user.id)
    )
    if location:
        entry_data['location'] = location
    
    # Step 4: Save to sheets
    success = multi_company_sheets.add_entry(entry_data)
    
    # Step 5: Generate AI response
    if success:
        response = ai_response_engine.generate_success_response(
            entry_data['type'], 
            entry_data
        )
    else:
        response = ai_response_engine.generate_error_response(
            'save_failed', 
            {'entry_data': entry_data}
        )
    
    await update.message.reply_text(response)
```

### **Analytics Dashboard Example**
```python
async def generate_dashboard_command(update, context):
    """Generate executive dashboard."""
    user = update.effective_user
    
    # Check admin access
    if not company_manager.is_admin(user.id):
        await update.message.reply_text("❌ Admin access required")
        return
    
    # Generate dashboard
    dashboard = analytics_engine.generate_executive_dashboard(user.id)
    
    # Format response
    response = f"""
📊 **Executive Dashboard**

💰 **Revenue:** ₹{dashboard['kpis']['total_revenue']:,.2f}
📦 **Orders:** {dashboard['kpis']['total_orders']:,}
📈 **Growth:** {dashboard['kpis']['growth_rate']:.1f}%

🔍 **Top Insights:**
{chr(10).join(f"• {insight}" for insight in dashboard['insights'][:3])}

💡 **Recommendations:**
{chr(10).join(f"• {rec}" for rec in dashboard['recommendations'][:3])}
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')
```

### **Location Processing Example**
```python
async def handle_location_sharing(update, context):
    """Handle GPS location sharing."""
    user = update.effective_user
    location = update.message.location
    company_id = company_manager.get_user_company(user.id)
    
    # Reverse geocode coordinates
    address_info = geocoding_service.reverse_geocode(
        location.latitude, 
        location.longitude
    )
    
    # Store location data
    location_data = {
        'coordinates': {
            'latitude': location.latitude,
            'longitude': location.longitude
        },
        'address': address_info,
        'timestamp': datetime.now().isoformat()
    }
    
    success = location_storage.store_location(
        str(user.id), 
        company_id, 
        location_data
    )
    
    if success:
        response = f"""
📍 **Location Saved Successfully**

📍 **Address:** {address_info.get('formatted_address', 'Unknown')}
🏢 **Company:** {company_manager.get_company_info(company_id)['display_name']}
⏰ **Valid Until:** {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}

Your location will be automatically included in future entries.
        """
    else:
        response = "❌ Failed to save location. Please try again."
    
    await update.message.reply_text(response)
```

---

This API documentation provides comprehensive coverage of all available APIs, data models, error handling, and practical examples for integrating with the AI-Enhanced Performance Tracker system.