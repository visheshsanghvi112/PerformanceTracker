# 🚀 Deployment Guide - AI-Enhanced Performance Tracker

## 📋 Table of Contents
1. [Production Deployment](#production-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Configuration Management](#configuration-management)
5. [Monitoring & Logging](#monitoring--logging)
6. [Security Best Practices](#security-best-practices)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling & Performance](#scaling--performance)

---

## 🏭 Production Deployment

### **Server Requirements**

#### **Minimum Requirements**
- **OS:** Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **CPU:** 2 cores, 2.4 GHz
- **RAM:** 2 GB
- **Storage:** 10 GB SSD
- **Network:** Stable internet connection

#### **Recommended Requirements**
- **OS:** Ubuntu 22.04 LTS
- **CPU:** 4 cores, 3.0 GHz
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **Network:** High-speed internet with low latency

### **Step-by-Step Production Setup**

#### **1. Server Preparation**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.12 python3.12-venv python3.12-pip git curl wget

# Install additional dependencies
sudo apt install -y build-essential libssl-dev libffi-dev python3.12-dev

# Create application user
sudo useradd -m -s /bin/bash botuser
sudo usermod -aG sudo botuser

# Switch to application user
sudo su - botuser
```

#### **2. Application Setup**

```bash
# Clone repository
git clone <repository-url> performance-tracker
cd performance-tracker

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/charts data/logs
chmod 755 data
chmod 644 data/*
```

#### **3. Configuration**

```bash
# Create production environment file
cp .env.example .env
nano .env
```

**Production .env Configuration:**
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_production_bot_token_here

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=/home/botuser/performance-tracker/yugrow-dd1d5-6676a7b2d2ea.json
SPREADSHEET_ID=your_production_spreadsheet_id

# AI Configuration
GEMINI_API_KEY=your_production_gemini_api_key

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=/home/botuser/performance-tracker/data/bot.log

# Performance Configuration
MAX_WORKERS=4
BATCH_SIZE_LIMIT=10
RATE_LIMIT_CALLS_PER_MINUTE=60
PARALLEL_PROCESSING_ENABLED=true

# Security Settings
ALLOWED_USERS=123456789,987654321
ADMIN_USERS=123456789

# Location Settings
LOCATION_EXPIRY_DAYS=30
GEOCODING_RATE_LIMIT=1
LOCATION_PRIVACY_MODE=true

# Analytics Settings
ANALYTICS_CACHE_TTL=300
CHART_OUTPUT_DIR=/home/botuser/performance-tracker/data/charts
PREDICTIVE_ANALYTICS_ENABLED=true
```

#### **4. Service Configuration**

Create systemd service file:

```bash
sudo nano /etc/systemd/system/performance-tracker.service
```

**Service Configuration:**
```ini
[Unit]
Description=AI-Enhanced Performance Tracker Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/home/botuser/performance-tracker
Environment=PATH=/home/botuser/performance-tracker/venv/bin
ExecStart=/home/botuser/performance-tracker/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=performance-tracker

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/botuser/performance-tracker/data

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

#### **5. Service Management**

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable performance-tracker

# Start the service
sudo systemctl start performance-tracker

# Check service status
sudo systemctl status performance-tracker

# View service logs
sudo journalctl -u performance-tracker -f

# Restart service
sudo systemctl restart performance-tracker

# Stop service
sudo systemctl stop performance-tracker
```

#### **6. Log Rotation Setup**

```bash
sudo nano /etc/logrotate.d/performance-tracker
```

**Log Rotation Configuration:**
```
/home/botuser/performance-tracker/data/bot.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 botuser botuser
    postrotate
        systemctl reload performance-tracker
    endscript
}
```

#### **7. Firewall Configuration**

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow outbound HTTPS (for API calls)
sudo ufw allow out 443

# Check firewall status
sudo ufw status
```

---

## 🐳 Docker Deployment

### **Dockerfile**

```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/charts data/logs && \
    chmod 755 data

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Expose port for health checks
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
```

### **Docker Compose**

```yaml
version: '3.8'

services:
  performance-tracker:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: performance-tracker-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - SPREADSHEET_ID=${SPREADSHEET_ID}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - MAX_WORKERS=4
    volumes:
      - ./data:/app/data
      - ./yugrow-dd1d5-6676a7b2d2ea.json:/app/yugrow-dd1d5-6676a7b2d2ea.json:ro
      - ./logs:/app/logs
    networks:
      - bot-network
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Redis for caching (future enhancement)
  redis:
    image: redis:7-alpine
    container_name: performance-tracker-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - bot-network
    command: redis-server --appendonly yes

  # Optional: Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: performance-tracker-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - bot-network

volumes:
  redis-data:
  prometheus-data:

networks:
  bot-network:
    driver: bridge
```

### **Docker Environment File**

```env
# .env.docker
TELEGRAM_BOT_TOKEN=your_bot_token_here
SPREADSHEET_ID=your_spreadsheet_id
GEMINI_API_KEY=your_gemini_api_key
COMPOSE_PROJECT_NAME=performance-tracker
```

### **Docker Deployment Commands**

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f performance-tracker

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d --force-recreate

# Clean up unused resources
docker system prune -f
```

---

## ☁️ Cloud Deployment

### **AWS EC2 Deployment**

#### **1. Launch EC2 Instance**

```bash
# Launch instance using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.small \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=performance-tracker}]'
```

#### **2. User Data Script**

```bash
#!/bin/bash
# user-data.sh

# Update system
yum update -y

# Install Docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
cd /home/ec2-user
git clone <repository-url> performance-tracker
cd performance-tracker

# Set up environment
cp .env.example .env
# Note: Update .env with production values

# Start services
docker-compose up -d

# Set up log rotation
echo "0 2 * * * docker-compose -f /home/ec2-user/performance-tracker/docker-compose.yml exec performance-tracker logrotate /etc/logrotate.d/performance-tracker" | crontab -
```

#### **3. Security Group Configuration**

```json
{
    "GroupName": "performance-tracker-sg",
    "Description": "Security group for Performance Tracker bot",
    "SecurityGroupRules": [
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "CidrIp": "your.ip.address/32",
            "Description": "SSH access"
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 443,
            "ToPort": 443,
            "CidrIp": "0.0.0.0/0",
            "Description": "HTTPS outbound"
        }
    ]
}
```

### **AWS ECS Deployment**

#### **1. Task Definition**

```json
{
    "family": "performance-tracker",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "performance-tracker",
            "image": "your-account.dkr.ecr.region.amazonaws.com/performance-tracker:latest",
            "essential": true,
            "environment": [
                {"name": "TELEGRAM_BOT_TOKEN", "value": "your-token"},
                {"name": "SPREADSHEET_ID", "value": "your-spreadsheet-id"},
                {"name": "ENVIRONMENT", "value": "production"}
            ],
            "secrets": [
                {
                    "name": "GEMINI_API_KEY",
                    "valueFrom": "arn:aws:secretsmanager:region:account:secret:gemini-api-key"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/performance-tracker",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "python -c 'import sys; sys.exit(0)'"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
```

#### **2. Service Configuration**

```json
{
    "serviceName": "performance-tracker-service",
    "cluster": "performance-tracker-cluster",
    "taskDefinition": "performance-tracker:1",
    "desiredCount": 1,
    "launchType": "FARGATE",
    "networkConfiguration": {
        "awsvpcConfiguration": {
            "subnets": ["subnet-xxxxxxxxx"],
            "securityGroups": ["sg-xxxxxxxxx"],
            "assignPublicIp": "ENABLED"
        }
    },
    "deploymentConfiguration": {
        "maximumPercent": 200,
        "minimumHealthyPercent": 50
    }
}
```

### **Google Cloud Platform Deployment**

#### **1. Cloud Run Deployment**

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: performance-tracker
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "1Gi"
        run.googleapis.com/cpu: "1"
    spec:
      containerConcurrency: 1
      containers:
      - image: gcr.io/your-project/performance-tracker:latest
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: telegram-bot-token
              key: token
        - name: SPREADSHEET_ID
          value: "your-spreadsheet-id"
        - name: ENVIRONMENT
          value: "production"
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
        ports:
        - containerPort: 8080
```

#### **2. Deployment Commands**

```bash
# Build and push image
gcloud builds submit --tag gcr.io/your-project/performance-tracker

# Deploy to Cloud Run
gcloud run deploy performance-tracker \
    --image gcr.io/your-project/performance-tracker:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --concurrency 1
```

---

## ⚙️ Configuration Management

### **Environment-Specific Configurations**

#### **Development Configuration**
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
MAX_WORKERS=2
BATCH_SIZE_LIMIT=5
RATE_LIMIT_CALLS_PER_MINUTE=30
```

#### **Staging Configuration**
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=3
BATCH_SIZE_LIMIT=8
RATE_LIMIT_CALLS_PER_MINUTE=45
```

#### **Production Configuration**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=4
BATCH_SIZE_LIMIT=10
RATE_LIMIT_CALLS_PER_MINUTE=60
```

### **Configuration Validation**

```python
# config_validator.py
import os
from typing import Dict, List

class ConfigValidator:
    """Validate configuration settings."""
    
    REQUIRED_VARS = [
        'TELEGRAM_BOT_TOKEN',
        'GOOGLE_SHEETS_CREDENTIALS_FILE',
        'SPREADSHEET_ID'
    ]
    
    OPTIONAL_VARS = {
        'GEMINI_API_KEY': None,
        'LOG_LEVEL': 'INFO',
        'MAX_WORKERS': '4',
        'BATCH_SIZE_LIMIT': '10'
    }
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate all configuration settings."""
        errors = []
        warnings = []
        
        # Check required variables
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
        
        # Check optional variables
        for var, default in self.OPTIONAL_VARS.items():
            if not os.getenv(var):
                warnings.append(f"Optional variable {var} not set, using default: {default}")
        
        # Validate specific settings
        try:
            max_workers = int(os.getenv('MAX_WORKERS', '4'))
            if max_workers < 1 or max_workers > 16:
                warnings.append("MAX_WORKERS should be between 1 and 16")
        except ValueError:
            errors.append("MAX_WORKERS must be a valid integer")
        
        return {'errors': errors, 'warnings': warnings}

# Usage
if __name__ == "__main__":
    validator = ConfigValidator()
    result = validator.validate_config()
    
    if result['errors']:
        print("❌ Configuration Errors:")
        for error in result['errors']:
            print(f"  - {error}")
        exit(1)
    
    if result['warnings']:
        print("⚠️ Configuration Warnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    print("✅ Configuration validation passed")
```

---

## 📊 Monitoring & Logging

### **Application Monitoring**

#### **Health Check Endpoint**

```python
# health_check.py
from flask import Flask, jsonify
import threading
import time
from datetime import datetime

app = Flask(__name__)

class HealthMonitor:
    def __init__(self):
        self.last_activity = datetime.now()
        self.status = "healthy"
        self.checks = {}
    
    def update_activity(self):
        self.last_activity = datetime.now()
    
    def run_health_checks(self):
        """Run comprehensive health checks."""
        checks = {}
        
        # Check bot status
        try:
            # Add bot health check logic
            checks['bot'] = 'healthy'
        except Exception as e:
            checks['bot'] = f'unhealthy: {str(e)}'
        
        # Check database connection
        try:
            # Add database health check logic
            checks['database'] = 'healthy'
        except Exception as e:
            checks['database'] = f'unhealthy: {str(e)}'
        
        # Check AI services
        try:
            # Add AI service health check logic
            checks['ai_services'] = 'healthy'
        except Exception as e:
            checks['ai_services'] = f'unhealthy: {str(e)}'
        
        self.checks = checks
        return checks

health_monitor = HealthMonitor()

@app.route('/health')
def health_check():
    """Health check endpoint."""
    checks = health_monitor.run_health_checks()
    
    # Determine overall status
    overall_status = 'healthy'
    if any('unhealthy' in status for status in checks.values()):
        overall_status = 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'last_activity': health_monitor.last_activity.isoformat(),
        'checks': checks
    })

@app.route('/metrics')
def metrics():
    """Metrics endpoint for monitoring."""
    # Add metrics collection logic
    return jsonify({
        'uptime': time.time() - start_time,
        'memory_usage': get_memory_usage(),
        'cpu_usage': get_cpu_usage(),
        'active_connections': get_active_connections()
    })

if __name__ == '__main__':
    # Start health check server in separate thread
    def run_health_server():
        app.run(host='0.0.0.0', port=8080, debug=False)
    
    health_thread = threading.Thread(target=run_health_server)
    health_thread.daemon = True
    health_thread.start()
```

### **Logging Configuration**

#### **Structured Logging**

```python
# logging_config.py
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated', 
                          'thread', 'threadName', 'processName', 'process',
                          'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

def setup_logging():
    """Set up structured logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler('data/bot.log')
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    return logger
```

### **Prometheus Metrics**

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
REQUEST_COUNT = Counter('bot_requests_total', 'Total bot requests', ['command', 'status'])
REQUEST_DURATION = Histogram('bot_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('bot_active_users', 'Number of active users')
ERROR_COUNT = Counter('bot_errors_total', 'Total errors', ['error_type'])

class MetricsCollector:
    """Collect and expose metrics."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def record_request(self, command: str, status: str, duration: float):
        """Record request metrics."""
        REQUEST_COUNT.labels(command=command, status=status).inc()
        REQUEST_DURATION.observe(duration)
    
    def record_error(self, error_type: str):
        """Record error metrics."""
        ERROR_COUNT.labels(error_type=error_type).inc()
    
    def update_active_users(self, count: int):
        """Update active users count."""
        ACTIVE_USERS.set(count)

# Start metrics server
def start_metrics_server(port=8000):
    """Start Prometheus metrics server."""
    start_http_server(port)
    print(f"Metrics server started on port {port}")

metrics_collector = MetricsCollector()
```

---

## 🔒 Security Best Practices

### **Environment Security**

#### **Secrets Management**

```bash
# Use environment variables for secrets
export TELEGRAM_BOT_TOKEN="$(cat /etc/secrets/telegram_token)"
export GEMINI_API_KEY="$(cat /etc/secrets/gemini_key)"

# Set proper file permissions
chmod 600 /etc/secrets/*
chown root:root /etc/secrets/*
```

#### **Network Security**

```bash
# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow out 443/tcp  # HTTPS
ufw enable

# Disable unused services
systemctl disable apache2
systemctl disable nginx
systemctl stop apache2
systemctl stop nginx
```

### **Application Security**

#### **Input Validation**

```python
# security.py
import re
from typing import Optional

class SecurityValidator:
    """Security validation utilities."""
    
    @staticmethod
    def validate_user_input(text: str) -> bool:
        """Validate user input for security threats."""
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
            r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
            r"(--|#|/\*|\*/)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*="
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()
```

#### **Rate Limiting**

```python
# rate_limiter.py
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    """Advanced rate limiting."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.blocked_users: Dict[str, float] = {}
    
    def is_allowed(self, user_id: str, limit: int = 60, window: int = 60) -> Tuple[bool, int]:
        """Check if request is allowed."""
        now = time.time()
        
        # Check if user is temporarily blocked
        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                remaining_time = int(self.blocked_users[user_id] - now)
                return False, remaining_time
            else:
                del self.blocked_users[user_id]
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < window
        ]
        
        # Check rate limit
        if len(self.requests[user_id]) >= limit:
            # Block user for 5 minutes
            self.blocked_users[user_id] = now + 300
            return False, 300
        
        # Allow request
        self.requests[user_id].append(now)
        return True, 0

rate_limiter = RateLimiter()
```

---

## 💾 Backup & Recovery

### **Data Backup Strategy**

#### **Automated Backup Script**

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/home/botuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application data
echo "Starting backup at $(date)"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /home/botuser/performance-tracker/.env \
    /home/botuser/performance-tracker/yugrow-dd1d5-6676a7b2d2ea.json

# Backup data directory
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" \
    /home/botuser/performance-tracker/data/

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" \
    /home/botuser/performance-tracker/data/bot.log*

# Export Google Sheets data (if needed)
python3 /home/botuser/performance-tracker/backup_sheets.py > "$BACKUP_DIR/sheets_$DATE.json"

# Clean old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.json" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"

# Upload to cloud storage (optional)
# aws s3 sync "$BACKUP_DIR" s3://your-backup-bucket/performance-tracker/
```

#### **Google Sheets Backup**

```python
# backup_sheets.py
import json
from datetime import datetime
from multi_company_sheets import multi_company_sheets

def backup_all_sheets():
    """Backup all company sheets data."""
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'companies': {}
    }
    
    companies = ['johnlee', 'yugrow', 'ambica', 'baker']
    
    for company in companies:
        try:
            # Get all data from company sheet
            sheet_data = multi_company_sheets.get_all_data(company)
            backup_data['companies'][company] = sheet_data
            print(f"✅ Backed up {company} data: {len(sheet_data)} records")
        except Exception as e:
            print(f"❌ Failed to backup {company}: {e}")
            backup_data['companies'][company] = {'error': str(e)}
    
    return json.dumps(backup_data, indent=2)

if __name__ == "__main__":
    backup_json = backup_all_sheets()
    print(backup_json)
```

### **Recovery Procedures**

#### **Application Recovery**

```bash
#!/bin/bash
# restore.sh

BACKUP_DATE=$1
BACKUP_DIR="/home/botuser/backups"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -la "$BACKUP_DIR" | grep tar.gz
    exit 1
fi

echo "Restoring from backup: $BACKUP_DATE"

# Stop service
sudo systemctl stop performance-tracker

# Restore configuration
if [ -f "$BACKUP_DIR/config_$BACKUP_DATE.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/config_$BACKUP_DATE.tar.gz" -C /
    echo "✅ Configuration restored"
fi

# Restore data
if [ -f "$BACKUP_DIR/data_$BACKUP_DATE.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/data_$BACKUP_DATE.tar.gz" -C /home/botuser/performance-tracker/
    echo "✅ Data restored"
fi

# Set permissions
chown -R botuser:botuser /home/botuser/performance-tracker/data/
chmod 755 /home/botuser/performance-tracker/data/
chmod 644 /home/botuser/performance-tracker/data/*

# Start service
sudo systemctl start performance-tracker

echo "✅ Recovery completed"
```

#### **Disaster Recovery Plan**

1. **Immediate Response (0-15 minutes)**
   - Assess the situation
   - Stop affected services
   - Identify backup requirements

2. **Recovery Phase (15-60 minutes)**
   - Restore from latest backup
   - Verify data integrity
   - Test critical functions

3. **Validation Phase (60-120 minutes)**
   - Run comprehensive tests
   - Verify all features working
   - Monitor for issues

4. **Post-Recovery (2+ hours)**
   - Document incident
   - Update recovery procedures
   - Implement preventive measures

---

## 📈 Scaling & Performance

### **Horizontal Scaling**

#### **Load Balancer Configuration**

```nginx
# nginx.conf
upstream performance_tracker {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://performance_tracker;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### **Multi-Instance Deployment**

```bash
# deploy_multiple.sh
#!/bin/bash

INSTANCES=3
BASE_PORT=8001

for i in $(seq 1 $INSTANCES); do
    PORT=$((BASE_PORT + i - 1))
    
    # Create instance directory
    mkdir -p "instance_$i"
    cp -r performance-tracker/* "instance_$i/"
    
    # Update configuration
    sed -i "s/PORT=8080/PORT=$PORT/" "instance_$i/.env"
    
    # Start instance
    cd "instance_$i"
    python main.py &
    cd ..
    
    echo "Started instance $i on port $PORT"
done
```

### **Performance Optimization**

#### **Database Connection Pooling**

```python
# connection_pool.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

class ConnectionPool:
    """Connection pool for external services."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.executor = ThreadPoolExecutor(max_workers=max_connections)
    
    async def get_connection(self):
        """Get connection from pool."""
        try:
            return await asyncio.wait_for(self.pool.get(), timeout=5.0)
        except asyncio.TimeoutError:
            raise Exception("Connection pool exhausted")
    
    async def return_connection(self, connection):
        """Return connection to pool."""
        await self.pool.put(connection)
    
    async def execute_with_pool(self, func, *args, **kwargs):
        """Execute function with pooled connection."""
        connection = await self.get_connection()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, func, connection, *args, **kwargs
            )
            return result
        finally:
            await self.return_connection(connection)

# Global connection pool
connection_pool = ConnectionPool(max_connections=10)
```

#### **Caching Strategy**

```python
# cache.py
import asyncio
import json
import time
from typing import Any, Optional

class AsyncCache:
    """Asynchronous cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        async with self.lock:
            self.cache[key] = (value, expiry)
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self.lock:
            self.cache.pop(key, None)
    
    async def clear_expired(self) -> None:
        """Clear expired cache entries."""
        now = time.time()
        async with self.lock:
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if now >= expiry
            ]
            for key in expired_keys:
                del self.cache[key]

# Global cache instance
cache = AsyncCache(default_ttl=300)

# Cache decorator
def cached(ttl: int = 300):
    """Cache decorator for async functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = await cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator
```

---

This comprehensive deployment guide covers all aspects of deploying the AI-Enhanced Performance Tracker in production environments, from basic server setup to advanced scaling strategies. Choose the deployment method that best fits your infrastructure and requirements.