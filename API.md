# API Documentation

## Overview

The Daily Root Cause Analysis App provides both REST API endpoints and Azure Function interfaces for triggering data pipeline operations and monitoring system status.

## Base URLs

|Environment      |URL                                            |
|-----------------|-----------------------------------------------|
|Local Development|`http://localhost:10000`                       |
|Azure Functions  |`https://<function-app-name>.azurewebsites.net`|
|Production       |`https://rca-app.azurewebsites.net`            |

## Authentication

### Local Development

No authentication required for local development endpoints.

### Azure Functions

Azure Functions use function keys for authentication:

```http
Authorization: Bearer <function-key>
```

Or append to URL:

```
https://function-app.azurewebsites.net/api/sync?code=<function-key>
```

## Endpoints

### 1. Trigger Data Pipeline

Initiates the complete data processing pipeline for previous day’s tickets.

**Endpoint:** `POST /sync`

**Request:**

```http
POST /sync HTTP/1.1
Content-Type: application/json

{}
```

**Response:**

```json
{
    "status": "success",
    "message": "Script task started",
    "link": "/path/to/sharepoint",
    "timestamp": "2024-12-15T08:00:00Z"
}
```

**Response Codes:**

- `200 OK` - Pipeline started successfully
- `400 Bad Request` - Pipeline already running or configuration error
- `500 Internal Server Error` - System error preventing pipeline start

**Example Usage:**

```bash
# Local development
curl -X POST http://localhost:10000/sync

# Azure Functions
curl -X POST https://rca-app.azurewebsites.net/api/sync?code=<function-key>
```

### 2. Check Pipeline Status

Returns current status of the data processing pipeline.

**Endpoint:** `GET /status`

**Request:**

```http
GET /status HTTP/1.1
```

**Response:**

```json
{
    "status": "Sync completed",
    "last_updated": "2024-12-15T08:15:00Z",
    "processing_time": "00:08:32",
    "tickets_processed": 1247,
    "records_created": 1198,
    "errors": 0
}
```

**Status Values:**

- `"Sync not started"` - No pipeline execution initiated
- `"Sync running"` - Pipeline currently processing
- `"Sync completed"` - Pipeline completed successfully
- `"Sync failed"` - Pipeline encountered errors

**Response Codes:**

- `200 OK` - Status retrieved successfully
- `500 Internal Server Error` - Unable to determine status

**Example Usage:**

```bash
# Check status
curl http://localhost:10000/status

# Response
{
    "status": "Sync running",
    "last_updated": "2024-12-15T08:05:00Z",
    "current_stage": "filter_subjects",
    "progress": "60%"
}
```

### 3. Web Dashboard

Serves the HTML interface for manual pipeline management.

**Endpoint:** `GET /`

**Request:**

```http
GET / HTTP/1.1
```

**Response:**
HTML dashboard with:

- Current pipeline status
- Manual trigger button
- Processing logs
- Historical execution data

### 4. Static Assets

Serves CSS, JavaScript, and other static files for the web interface.

**Endpoint:** `GET /static/<path:path>`

**Request:**

```http
GET /static/css/dashboard.css HTTP/1.1
```

**Response:**
Static file content with appropriate MIME type.

## Azure Function Specific Endpoints

### HTTP Trigger Function

**Endpoint:** `POST /api/HttpTrigger1`

**Function Configuration:**

```json
{
    "authLevel": "function",
    "type": "httpTrigger",
    "direction": "in",
    "name": "req",
    "methods": ["post"]
}
```

**Request:**

```http
POST /api/HttpTrigger1?code=<function-key> HTTP/1.1
Content-Type: application/json

{
    "trigger": "manual",
    "date_override": "2024-12-14"  // Optional: process specific date
}
```

**Response:**

```json
{
    "status": "success",
    "message": "All scripts executed successfully and all required CSV files are present.",
    "execution_id": "exec_20241215_080000",
    "files_processed": [
        "extracted_data.csv",
        "filtered_groups.csv", 
        "filtered_subjects.csv",
        "mapped_filtered_subjects.csv",
        "aggregated_data.csv",
        "detailed_analysis.csv"
    ],
    "sharepoint_uploads": [
        "zendesk_ticket_analysis.xlsx",
        "zendesk_ticket_analysis_backup.xlsx"
    ]
}
```

### Timer Trigger Function

**Schedule:** Daily at 8:00 AM UTC
**CRON Expression:** `0 0 8 * * *`

**Automatic Execution:**

```json
{
    "trigger_type": "timer",
    "schedule": "0 0 8 * * *",
    "execution_time": "2024-12-15T08:00:00Z",
    "status": "scheduled"
}
```

## Error Responses

### Standard Error Format

```json
{
    "error": {
        "code": "PIPELINE_FAILED",
        "message": "Data processing pipeline failed at stage: filter_subjects",
        "details": {
            "stage": "filter_subjects",
            "error_type": "ValidationError",
            "timestamp": "2024-12-15T08:05:30Z",
            "retry_possible": true
        }
    }
}
```

### Common Error Codes

|Code                      |Description                   |Resolution                                  |
|--------------------------|------------------------------|--------------------------------------------|
|`PIPELINE_RUNNING`        |Pipeline already in progress  |Wait for completion or check status         |
|`AUTH_FAILED`             |Authentication failure        |Check API tokens and credentials            |
|`API_LIMIT_EXCEEDED`      |Zendesk rate limit hit        |Wait and retry, system handles automatically|
|`SHAREPOINT_ACCESS_DENIED`|SharePoint upload failed      |Verify permissions and app registration     |
|`DATA_VALIDATION_ERROR`   |Invalid data format detected  |Check Zendesk custom field configuration    |
|`MISSING_CONFIG`          |Required configuration missing|Verify environment variables                |

## Request/Response Examples

### Successful Pipeline Execution

**Request:**

```bash
curl -X POST http://localhost:10000/sync \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**

```json
{
    "status": "success",
    "message": "Script task started",
    "link": "/path/to/sharepoint",
    "execution_id": "exec_20241215_080000"
}
```

**Status Check During Processing:**

```bash
curl http://localhost:10000/status
```

```json
{
    "status": "Sync running",
    "current_stage": "aggregate",
    "progress": "75%",
    "estimated_completion": "2024-12-15T08:12:00Z"
}
```

**Final Status:**

```json
{
    "status": "Sync completed",
    "processing_time": "00:08:32",
    "tickets_processed": 1247,
    "categories_identified": 18,
    "high_volume_categories": 3,
    "sharepoint_upload": "success",
    "backup_created": true
}
```

### Error Handling Example

**Failed Authentication:**

```json
{
    "error": {
        "code": "AUTH_FAILED",
        "message": "Zendesk authentication failed",
        "details": {
            "error_type": "InvalidCredentials",
            "timestamp": "2024-12-15T08:01:15Z",
            "retry_possible": false
        }
    }
}
```

**Rate Limit Error:**

```json
{
    "error": {
        "code": "API_LIMIT_EXCEEDED", 
        "message": "Zendesk API rate limit exceeded",
        "details": {
            "retry_after": 60,
            "timestamp": "2024-12-15T08:03:22Z",
            "retry_possible": true
        }
    }
}
```

## Integration Examples

### Python Client

```python
import requests
import time

class RCAClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def trigger_pipeline(self):
        response = requests.post(f"{self.base_url}/sync")
        return response.json()
    
    def wait_for_completion(self, poll_interval=30):
        while True:
            status = self.get_status()
            if status['status'] in ['Sync completed', 'Sync failed']:
                return status
            time.sleep(poll_interval)
    
    def get_status(self):
        response = requests.get(f"{self.base_url}/status")
        return response.json()

# Usage
client = RCAClient("http://localhost:10000")
result = client.trigger_pipeline()
final_status = client.wait_for_completion()
```

### PowerShell Integration

```powershell
# Trigger pipeline
$response = Invoke-RestMethod -Uri "https://rca-app.azurewebsites.net/api/sync?code=$functionKey" -Method POST

# Monitor status
do {
    Start-Sleep -Seconds 30
    $status = Invoke-RestMethod -Uri "https://rca-app.azurewebsites.net/api/status?code=$functionKey"
    Write-Host "Status: $($status.status)"
} while ($status.status -eq "Sync running")
```

### Azure Logic Apps Integration

```json
{
    "definition": {
        "triggers": {
            "Recurrence": {
                "type": "Recurrence",
                "recurrence": {
                    "frequency": "Day",
                    "interval": 1,
                    "timeZone": "UTC",
                    "startTime": "2024-01-01T08:00:00Z"
                }
            }
        },
        "actions": {
            "TriggerRCA": {
                "type": "Http",
                "inputs": {
                    "method": "POST",
                    "uri": "https://rca-app.azurewebsites.net/api/sync?code=@{parameters('functionKey')}"
                }
            },
            "WaitForCompletion": {
                "type": "Until",
                "expression": "@not(equals(body('CheckStatus')['status'], 'Sync running'))",
                "actions": {
                    "CheckStatus": {
                        "type": "Http",
                        "inputs": {
                            "method": "GET", 
                            "uri": "https://rca-app.azurewebsites.net/api/status?code=@{parameters('functionKey')}"
                        }
                    },
                    "Delay": {
                        "type": "Wait",
                        "inputs": {
                            "interval": {
                                "count": 1,
                                "unit": "Minute"
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## Rate Limits and Throttling

### API Limits

- **Local Development**: No limits
- **Azure Functions**:
  - Consumption Plan: 200 executions/hour
  - Premium Plan: No limits

### Zendesk API Limits

- **Rate Limit**: 700 requests/minute
- **Daily Limit**: 200,000 requests/day
- **Handling**: Automatic backoff and retry logic

### SharePoint API Limits

- **Microsoft Graph**: 10,000 requests/10 minutes per app
- **Throttling**: Automatic retry with exponential backoff

## Monitoring and Logging

### Request Logging

All API requests are logged with:

- Timestamp
- HTTP method and endpoint
- Response status
- Processing time
- Error details (if applicable)

### Performance Metrics

- Average response time
- Success/failure rates
- Pipeline completion times
- Data volume processed

### Application Insights Integration

```json
{
    "request": {
        "name": "POST /sync",
        "duration": 500,
        "responseCode": 200,
        "success": true
    },
    "customDimensions": {
        "tickets_processed": 1247,
        "execution_id": "exec_20241215_080000"
    }
}
```