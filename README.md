# Daily Root Cause Analysis App

> Automated Zendesk ticket analysis and reporting system for IT Operations


## Overview

The Daily Root Cause Analysis App automatically extracts, categorizes, and analyzes IT support tickets from Zendesk to identify patterns and generate actionable insights for IT operations teams. The system processes ~500-2000 tickets daily through a multi-stage data pipeline and delivers formatted reports to SharePoint.

## Quick Start

### Prerequisites

- Python 3.8+
- Azure subscription (for production deployment)
- Zendesk API access
- SharePoint/Microsoft 365 integration

### Local Development

```bash
# Clone and setup
git clone <repository-url>
cd daily-root-cause-analysis
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
python app.py
```

### Production Deployment

```bash
# Deploy to Azure Functions
func azure functionapp publish <function-app-name>

# Configure application settings in Azure Portal
# Set up daily timer trigger: 0 0 8 * * * (8 AM daily)
```

## Key Features

- **Automated Daily Processing**: Extracts previous day’s tickets at 8 AM daily
- **Intelligent Categorization**: 200+ regex patterns classify tickets into 20+ service categories
- **Business Intelligence**: Generates summary and detailed analytics
- **SharePoint Integration**: Automatically updates organizational trackers
- **Web Interface**: Manual triggers and real-time status monitoring
- **Enterprise Security**: Azure managed identity and token-based authentication

## API Endpoints

|Endpoint |Method|Description                   |
|---------|------|------------------------------|
|`/sync`  |POST  |Trigger data pipeline manually|
|`/status`|GET   |Get current processing status |
|`/`      |GET   |Web interface dashboard       |

## Data Pipeline

```
Zendesk API → Extract → Filter → Categorize → Aggregate → Excel → SharePoint
```

**Processing Time**: ~5-10 minutes for typical daily volume  
**Data Retention**: 90 days in intermediate storage  
**Backup Strategy**: Automatic backup creation on each upload

## Service Categories

The system categorizes tickets into these primary areas:

- **Infrastructure**: Azure AVD, Network, Drive Access, ADUC
- **Business Apps**: HCHB, PCC, Workday, Forcura, Smartsheet
- **Communication**: Exchange, Teams, Fuze, Mobile Devices
- **Hardware**: Equipment orders, Printers, Hardware support
- **Administrative**: User provisioning, Training, Documentation

## Configuration

### Environment Variables

```bash
# Required
ZENDESK_API_TOKEN=your_token
CLIENT_ID=azure_app_id
CLIENT_SECRET=azure_app_secret
TENANT_ID=azure_tenant_id
SHAREPOINT_SITE_URL=https://tenant.sharepoint.com/sites/ITOps

# Optional
AZURE_FUNCTION_URL=function_endpoint
AZURE_FUNCTION_KEY=function_key
```

### Customization

- **Categories**: Edit regex patterns in `filter_subjects.py`
- **Groups**: Modify mappings in `filter_groups.py`
- **Exclusions**: Update patterns in `extract.py`

## Monitoring

### Health Checks

- **Status Endpoint**: `/status` returns current pipeline state
- **Azure Monitoring**: Function App metrics and logs
- **SharePoint Validation**: Automatic backup file creation

### Common Issues

|Issue                 |Cause                 |Resolution             |
|----------------------|----------------------|-----------------------|
|Authentication failure|Expired tokens        |Rotate API credentials |
|Missing data          |API rate limits       |Check extraction logs  |
|Upload errors         |SharePoint permissions|Verify app registration|

## Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical design and data flow
- **[API Documentation](docs/API.md)** - Detailed endpoint specifications
- **[Operations Guide](docs/OPERATIONS.md)** - Deployment and monitoring
- **[Business Guide](docs/BUSINESS.md)** - KPIs and stakeholder information
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development guidelines

## Support

- **Technical Issues**: IT Operations Team
- **Business Questions**: Data Analytics Team
- **Access Requests**: Submit ServiceNow ticket
- **Documentation**: Confluence space

## License

Internal use only - Proprietary software for [Company Name]

-----

**Last Updated**: December 2024  
**Version**: 2.1.0  