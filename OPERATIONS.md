# Operations Guide

## Deployment

### Prerequisites

#### Local Development

- Python 3.8+ with pip
- Git access to repository
- Zendesk API access (token-based authentication)
- SharePoint/Office 365 tenant access

#### Production Environment

- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- Azure Functions Core Tools v4+
- Application registration in Azure AD

### Environment Configuration

#### Environment Variables

Create environment-specific configuration:

```bash
# .env.local (Local Development)
ZENDESK_API_TOKEN=your_zendesk_token
CLIENT_ID=your_azure_app_id
CLIENT_SECRET=your_azure_app_secret
TENANT_ID=your_azure_tenant_id
SHAREPOINT_SITE_URL=https://tenant.sharepoint.com/sites/ITOperations
SHAREPOINT_REMOTE_PATH=/Shared%20Documents
AZURE_FUNCTION_URL=https://function-app.azurewebsites.net/api/HttpTrigger1
AZURE_FUNCTION_KEY=function_access_key
```

#### Azure Key Vault Setup

```bash
# Create Key Vault
az keyvault create --name rca-app-kv --resource-group rg-rca --location eastus2

# Store secrets
az keyvault secret set --vault-name rca-app-kv --name "ZendeskApiToken" --value "your_token"
az keyvault secret set --vault-name rca-app-kv --name "ClientSecret" --value "your_secret"

# Configure Function App to use Key Vault
az functionapp config appsettings set --name rca-function-app --resource-group rg-rca \
  --settings "ZENDESK_API_TOKEN=@Microsoft.KeyVault(VaultName=rca-app-kv;SecretName=ZendeskApiToken)"
```

### Local Development Deployment

#### Step 1: Environment Setup

```bash
# Clone repository
git clone https://github.com/company/daily-rca-app.git
cd daily-rca-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Update with your credentials
```

#### Step 3: Validate Setup

```bash
# Test Zendesk connectivity
python -c "
import sys
sys.path.append('src')
from extract import fetch_groups
groups = fetch_groups()
print(f'Connected to Zendesk. Found {len(groups)} groups.')
"

# Test SharePoint connectivity
python -c "
import sys
sys.path.append('src')
from sharepoint_upload import authenticate_to_graph
token = authenticate_to_graph()
print('SharePoint authentication successful.')
"
```

#### Step 4: Run Application

```bash
# Start Flask development server
python app.py

# Access web interface
open http://localhost:10000
```

### Azure Functions Deployment

#### Step 1: Resource Group Creation

```bash
# Create resource group
az group create --name rg-rca-prod --location eastus2

# Create storage account
az storage account create \
  --name rcastorageacct \
  --resource-group rg-rca-prod \
  --location eastus2 \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group rg-rca-prod \
  --consumption-plan-location eastus2 \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name rca-function-app \
  --storage-account rcastorageacct
```

#### Step 2: Deploy Function Code

```bash
# Initialize Functions project (if not already done)
func init --python

# Deploy to Azure
func azure functionapp publish rca-function-app

# Verify deployment
func azure functionapp list-functions rca-function-app
```

#### Step 3: Configure Timer Trigger

```bash
# Set up daily execution at 8 AM UTC
az functionapp config appsettings set \
  --name rca-function-app \
  --resource-group rg-rca-prod \
  --settings "FUNCTIONS_CRON_SCHEDULE=0 0 8 * * *"
```

#### Step 4: Configure Application Settings

```bash
# Set environment variables
az functionapp config appsettings set \
  --name rca-function-app \
  --resource-group rg-rca-prod \
  --settings \
    "CLIENT_ID=your_client_id" \
    "TENANT_ID=your_tenant_id" \
    "SHAREPOINT_SITE_URL=https://tenant.sharepoint.com/sites/ITOperations" \
    "SHAREPOINT_REMOTE_PATH=/Shared Documents"
```

### Container Deployment (Optional)

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
```

#### Docker Deployment

```bash
# Build image
docker build -t rca-app:latest .

# Run container
docker run -d \
  --name rca-app \
  -p 10000:10000 \
  --env-file .env \
  rca-app:latest
```

## Monitoring

### Application Insights Setup

#### Enable Application Insights

```bash
# Create Application Insights resource
az monitor app-insights component create \
  --app rca-insights \
  --location eastus2 \
  --resource-group rg-rca-prod

# Get instrumentation key
az monitor app-insights component show \
  --app rca-insights \
  --resource-group rg-rca-prod \
  --query instrumentationKey

# Configure Function App
az functionapp config appsettings set \
  --name rca-function-app \
  --resource-group rg-rca-prod \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=your_key"
```

### Key Metrics to Monitor

#### Performance Metrics

- **Execution Duration**: Target <10 minutes
- **Success Rate**: Target >99%
- **Memory Usage**: Monitor for memory leaks
- **API Response Times**: Zendesk and SharePoint calls

#### Business Metrics

- **Tickets Processed**: Daily volume trends
- **Categories Identified**: Classification accuracy
- **Data Quality**: Null/invalid data percentage
- **Upload Success**: SharePoint integration health

#### Custom Metrics Implementation

```python
# In your Python code
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Configure Application Insights logging
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your_key'
))

# Custom metrics
logger.info('Pipeline started', extra={
    'custom_dimensions': {
        'execution_id': execution_id,
        'trigger_type': 'scheduled'
    }
})

logger.info('Processing completed', extra={
    'custom_dimensions': {
        'tickets_processed': ticket_count,
        'processing_time': duration,
        'categories_found': category_count
    }
})
```

### Health Checks

#### Automated Health Monitoring

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

# Check Function App health
response=$(curl -s -o /dev/null -w "%{http_code}" "https://rca-function-app.azurewebsites.net/api/status")

if [ $response -eq 200 ]; then
    echo "✅ Function App is healthy"
else
    echo "❌ Function App health check failed (HTTP $response)"
    exit 1
fi

# Check last execution
last_run=$(az functionapp logs show --name rca-function-app --resource-group rg-rca-prod --query "[0].timestamp" -o tsv)
current_time=$(date -u +%s)
last_run_time=$(date -d "$last_run" +%s)
hours_since=$((($current_time - $last_run_time) / 3600))

if [ $hours_since -lt 26 ]; then
    echo "✅ Pipeline executed within last 26 hours"
else
    echo "❌ Pipeline hasn't run in $hours_since hours"
    exit 1
fi
EOF

chmod +x health_check.sh
```

#### Monitoring Dashboard Setup

```bash
# Create Azure Dashboard
az portal dashboard create \
  --resource-group rg-rca-prod \
  --name "RCA-Pipeline-Dashboard" \
  --input-path dashboard.json
```

### Alerting

#### Azure Monitor Alerts

```bash
# Failed execution alert
az monitor metrics alert create \
  --name "RCA Pipeline Failures" \
  --resource-group rg-rca-prod \
  --scopes /subscriptions/{subscription}/resourceGroups/rg-rca-prod/providers/Microsoft.Web/sites/rca-function-app \
  --condition "count 'FunctionExecutionCount' < 1" \
  --window-size 1h \
  --evaluation-frequency 15m \
  --action-group-ids /subscriptions/{subscription}/resourceGroups/rg-rca-prod/providers/microsoft.insights/actionGroups/rca-alerts

# Long execution time alert  
az monitor metrics alert create \
  --name "RCA Pipeline Long Execution" \
  --resource-group rg-rca-prod \
  --scopes /subscriptions/{subscription}/resourceGroups/rg-rca-prod/providers/Microsoft.Web/sites/rca-function-app \
  --condition "average 'FunctionExecutionTime' > 600000" \
  --window-size 15m \
  --evaluation-frequency 5m
```

#### Email Notification Setup

```bash
# Create action group for notifications
az monitor action-group create \
  --resource-group rg-rca-prod \
  --name rca-alerts \
  --short-name rcaalerts \
  --email-receivers name=ops email=ops@company.com \
  --sms-receivers name=oncall countrycode=1 phonenumber=5551234567
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Failures

**Symptoms:**

- HTTP 401 errors in logs
- “Authentication failed” messages
- SharePoint upload failures

**Diagnosis:**

```bash
# Check token expiration
az account get-access-token --resource https://graph.microsoft.com

# Validate app registration
az ad app show --id your_client_id
```

**Solutions:**

```bash
# Rotate client secret
az ad app credential reset --id your_client_id

# Update Function App settings
az functionapp config appsettings set \
  --name rca-function-app \
  --resource-group rg-rca-prod \
  --settings "CLIENT_SECRET=new_secret"
```

#### 2. API Rate Limiting

**Symptoms:**

- HTTP 429 errors
- “Rate limit exceeded” messages
- Incomplete data extraction

**Diagnosis:**

```bash
# Check current rate limit status
curl -I "https://cornerstoneguide.zendesk.com/api/v2/tickets.json" \
  -u "email/token:api_token"
```

**Solutions:**

- Increase delay between API calls in `extract.py`
- Implement exponential backoff
- Contact Zendesk to increase rate limits

#### 3. Data Processing Errors

**Symptoms:**

- Missing CSV files
- Classification errors
- Incomplete aggregation

**Diagnosis:**

```bash
# Check function logs
az functionapp logs tail --name rca-function-app --resource-group rg-rca-prod

# Validate data locally
python -c "
import pandas as pd
df = pd.read_csv('extracted_data.csv')
print(f'Records: {len(df)}')
print(f'Columns: {list(df.columns)}')
print(f'Null values: {df.isnull().sum().sum()}')
"
```

**Solutions:**

- Update regex patterns for new ticket types
- Validate Zendesk custom field IDs
- Check for schema changes in Zendesk

#### 4. SharePoint Upload Failures

**Symptoms:**

- Files not appearing in SharePoint
- Permission denied errors
- Backup files created but main files missing

**Diagnosis:**

```bash
# Test SharePoint connectivity
python -c "
from sharepoint_upload import authenticate_to_graph
try:
    token = authenticate_to_graph()
    print('✅ Authentication successful')
except Exception as e:
    print(f'❌ Authentication failed: {e}')
"
```

**Solutions:**

- Verify SharePoint site permissions
- Check file path configuration
- Validate Graph API permissions

### Performance Troubleshooting

#### Memory Issues

```bash
# Monitor memory usage during execution
python -c "
import psutil
import time
process = psutil.Process()
for i in range(60):
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f'Memory usage: {memory_mb:.2f} MB')
    time.sleep(1)
"
```

#### Processing Time Analysis

```python
# Add timing to pipeline stages
import time

def time_stage(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"{func.__name__} completed in {duration:.2f} seconds")
        return result
    return wrapper

# Apply to pipeline functions
@time_stage
def extract_data():
    # extraction logic
    pass
```

### Log Analysis

#### Key Log Patterns to Monitor

```bash
# Success patterns
grep "successfully" /var/log/rca-app.log

# Error patterns  
grep -E "(ERROR|FAILED|Exception)" /var/log/rca-app.log

# Performance patterns
grep "completed in" /var/log/rca-app.log

# Data quality patterns
grep -E "(Missing|Invalid|Null)" /var/log/rca-app.log
```

#### Automated Log Analysis

```python
# Log analysis script
import re
from collections import Counter

def analyze_logs(log_file):
    error_patterns = Counter()
    processing_times = []
    
    with open(log_file, 'r') as f:
        for line in f:
            # Extract errors
            if 'ERROR' in line:
                error_type = re.search(r'ERROR: ([^:]+)', line)
                if error_type:
                    error_patterns[error_type.group(1)] += 1
            
            # Extract processing times
            time_match = re.search(r'completed in (\d+\.\d+) seconds', line)
            if time_match:
                processing_times.append(float(time_match.group(1)))
    
    print(f"Top errors: {error_patterns.most_common(5)}")
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        print(f"Average processing time: {avg_time:.2f} seconds")
```

## Maintenance

### Regular Maintenance Tasks

#### Weekly Tasks

- [ ] Review execution logs for errors
- [ ] Validate data quality metrics
- [ ] Check SharePoint report accuracy
- [ ] Monitor API usage against limits

#### Monthly Tasks

- [ ] Update dependencies (`pip list --outdated`)
- [ ] Review and update regex patterns
- [ ] Analyze performance trends
- [ ] Validate backup procedures

#### Quarterly Tasks

- [ ] Security review (rotate secrets)
- [ ] Capacity planning review
- [ ] Update documentation
- [ ] Disaster recovery testing

### Backup and Recovery

#### Data Backup Strategy

```bash
# SharePoint backup (automated via pipeline)
# - Main file: zendesk_ticket_analysis.xlsx
# - Backup file: zendesk_ticket_analysis_backup.xlsx

# Configuration backup
az functionapp config backup create \
  --resource-group rg-rca-prod \
  --name rca-function-app \
  --backup-name "config-$(date +%Y%m%d)"

# Source code backup (Git repository)
git tag "release-$(date +%Y%m%d)"
git push origin --tags
```

#### Disaster Recovery Procedures

1. **Service Outage Response**
- Switch to manual processing mode
- Use backup SharePoint files
- Execute pipeline locally if needed
1. **Data Loss Recovery**
- Restore from SharePoint backup files
- Re-run pipeline for missing days
- Validate data integrity post-recovery
1. **Complete System Recovery**
- Redeploy from Git repository
- Restore configuration from Key Vault
- Validate all integrations before resuming

### Scaling Considerations

#### Vertical Scaling

```bash
# Upgrade Function App plan
az functionapp plan update \
  --name rca-plan \
  --resource-group rg-rca-prod \
  --sku P1V2  # Premium plan for better performance
```

#### Horizontal Scaling

- Implement parallel processing for large datasets
- Separate extraction and processing into different functions
- Use Azure Storage Queues for async processing

#### Performance Optimization

- Cache regex compilation
- Implement data streaming for large files
- Use connection pooling for API calls
- Optimize pandas operations