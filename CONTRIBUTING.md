# Contributing Guide

## Overview

Thank you for your interest in contributing to the Daily Root Cause Analysis App. This guide provides standards, processes, and best practices for maintaining and enhancing the codebase.

## Development Environment Setup

### Prerequisites

#### Required Software

- Python 3.8+ with pip
- Git 2.30+
- VS Code or PyCharm (recommended IDEs)
- Azure CLI 2.40+
- Azure Functions Core Tools v4+

#### Recommended Tools

- Docker Desktop (for containerized testing)
- Postman (for API testing)
- Azure Storage Explorer
- SharePoint Online Management Shell

### Local Environment Configuration

#### Step 1: Repository Setup

```bash
# Clone repository
git clone https://github.com/company/daily-rca-app.git
cd daily-rca-app

# Set up git hooks
cp scripts/git-hooks/* .git/hooks/
chmod +x .git/hooks/*
```

#### Step 2: Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or 
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Step 3: Development Configuration

```bash
# Copy development environment template
cp .env.development .env

# Configure pre-commit hooks
pre-commit install

# Set up IDE configuration
cp .vscode/settings.json.template .vscode/settings.json
```

### Development Dependencies

Create `requirements-dev.txt`:

```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
pytest-asyncio>=0.21.1

# Code Quality
black>=23.7.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.5.0
pylint>=2.17.0

# Development Tools
pre-commit>=3.3.0
bandit>=1.7.5
safety>=2.3.0

# Documentation
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0
```

## Code Standards

### Python Style Guide

#### Code Formatting

We use **Black** for code formatting with these settings:

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Exclude generated files
  migrations
  | .venv
  | build
  | dist
)/
'''
```

#### Import Organization

Use **isort** for import sorting:

```toml
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]
known_third_party = ["pandas", "requests", "azure", "msal"]
```

#### Type Hints

All new code must include type hints:

```python
from typing import Dict, List, Optional, Union
import pandas as pd

def process_tickets(
    tickets: List[Dict[str, Union[str, int]]], 
    group_mapping: Dict[int, str]
) -> pd.DataFrame:
    """Process raw ticket data with type safety."""
    # Implementation
    pass
```

### Naming Conventions

#### Variables and Functions

```python
# Use snake_case for variables and functions
ticket_count = 0
user_account_data = {}

def extract_ticket_data() -> pd.DataFrame:
    pass

def calculate_daily_totals(df: pd.DataFrame) -> Dict[str, int]:
    pass
```

#### Classes

```python
# Use PascalCase for classes
class TicketProcessor:
    def __init__(self, config: Dict[str, str]) -> None:
        self.config = config
    
    def process_batch(self, tickets: List[Dict]) -> pd.DataFrame:
        pass
```

#### Constants

```python
# Use UPPER_SNAKE_CASE for constants
API_TIMEOUT_SECONDS = 30
MAX_RETRY_ATTEMPTS = 3
DEFAULT_BATCH_SIZE = 500
```

#### Files and Directories

```
# Use snake_case for file names
extract_tickets.py
filter_subjects.py
sharepoint_integration.py

# Use kebab-case for directory names
data-processing/
api-clients/
config-templates/
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def categorize_ticket(
    subject: str, 
    group: str, 
    action_taken: Optional[str] = None
) -> str:
    """Categorize a ticket based on subject and metadata.
    
    Applies regex pattern matching and business rules to determine
    the appropriate service category for a support ticket.
    
    Args:
        subject: The ticket subject line to analyze
        group: The support group assigned to the ticket
        action_taken: Optional action taken field from custom fields
        
    Returns:
        String representing the service category (e.g., 'HCHB', 'Equipment')
        
    Raises:
        ValueError: If subject is empty or None
        
    Example:
        >>> categorize_ticket("Cannot access HCHB", "IT", "troubleshooting")
        'HCHB'
    """
    if not subject:
        raise ValueError("Subject cannot be empty")
    
    # Implementation
    return category
```

#### Code Comments

```python
# Good comments explain WHY, not WHAT
def apply_regex_patterns(subject: str, patterns: Dict[str, List[str]]) -> str:
    """Apply pattern matching for ticket categorization."""
    
    # Convert to lowercase for case-insensitive matching
    # This improves classification accuracy by ~12%
    subject_lower = subject.lower()
    
    # Process patterns in priority order to handle overlapping categories
    # Equipment patterns must be checked before general hardware patterns
    for category in PRIORITY_ORDER:
        if category in patterns:
            for pattern in patterns[category]:
                if re.search(pattern, subject_lower):
                    return category
    
    return 'Other'  # Default fallback category
```

## Testing Standards

### Test Structure

#### Unit Tests

```python
# tests/test_extract.py
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from src.extract import extract_tickets, filter_ticket

class TestExtractTickets:
    """Test suite for ticket extraction functionality."""
    
    def test_extract_tickets_success(self):
        """Test successful ticket extraction from API."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'id': 1, 'subject': 'Test ticket', 'group_id': 123}
            ]
        }
        
        # Act
        with patch('requests.get', return_value=mock_response):
            result = extract_tickets('2024-12-15', '2024-12-16')
        
        # Assert
        assert len(result) == 1
        assert result[0]['subject'] == 'Test ticket'
    
    def test_filter_ticket_excluded_pattern(self):
        """Test that excluded patterns are properly filtered."""
        # Arrange
        ticket = {
            'subject': 'Termination-John Doe',
            'group_id': 123
        }
        group_map = {123: 'IT'}
        
        # Act
        result = filter_ticket(ticket, group_map)
        
        # Assert
        assert result is False
    
    @pytest.mark.parametrize("subject,expected", [
        ("Cannot access HCHB", True),
        ("Voicemail from user", False),
        ("Equipment request", True),
    ])
    def test_filter_ticket_parameterized(self, subject, expected):
        """Test ticket filtering with multiple scenarios."""
        ticket = {'subject': subject, 'group_id': 123}
        group_map = {123: 'IT'}
        
        result = filter_ticket(ticket, group_map)
        assert result == expected
```

#### Integration Tests

```python
# tests/test_integration.py
import pytest
import tempfile
import os
from unittest.mock import patch

from src.main import run_all_scripts

class TestPipelineIntegration:
    """Test complete data pipeline integration."""
    
    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            yield temp_dir
    
    def test_complete_pipeline(self, temp_directory):
        """Test end-to-end pipeline execution."""
        # Arrange - mock external API calls
        with patch('src.extract.fetch_tickets') as mock_fetch:
            mock_fetch.return_value = self._create_sample_tickets()
            
            # Act
            result = run_all_scripts()
            
            # Assert
            assert result is True
            assert os.path.exists('aggregated_data.xlsx')
            assert os.path.exists('detailed_analysis.xlsx')
    
    def _create_sample_tickets(self):
        """Create sample ticket data for testing."""
        return [
            {
                'Product - Service Desk Tool': 'Equipment',
                'Ticket subject': 'Laptop not working',
                'Ticket created - Day of month': 15,
                'Ticket created - Month': 12,
                'Ticket created - Year': 2024,
                'Tickets': 1
            }
        ]
```

### Test Coverage Requirements

#### Minimum Coverage Targets

- **Overall Code Coverage**: 85%
- **Critical Functions**: 95% (extract, classify, aggregate)
- **Business Logic**: 90% (filtering, mapping, categorization)
- **Integration Points**: 80% (API calls, file I/O)

#### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "venv/*",
    "setup.py",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

### Test Execution

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_extract.py

# Run tests with specific marker
pytest -m "integration"

# Run tests in parallel
pytest -n auto
```

#### Test Markers

```python
# Mark tests appropriately
@pytest.mark.unit
def test_function_logic():
    pass

@pytest.mark.integration  
def test_api_integration():
    pass

@pytest.mark.slow
def test_large_dataset_processing():
    pass

@pytest.mark.external
def test_sharepoint_upload():
    pass
```

## Git Workflow

### Branching Strategy

#### Branch Types

```
main                    # Production-ready code
├── develop            # Integration branch
├── feature/JIRA-123   # Feature development  
├── bugfix/JIRA-456    # Bug fixes
├── hotfix/JIRA-789    # Emergency fixes
└── release/v2.1.0     # Release preparation
```

#### Branch Naming Conventions

- `feature/JIRA-123-add-new-category` - New features
- `bugfix/JIRA-456-fix-regex-pattern` - Bug fixes
- `hotfix/JIRA-789-urgent-auth-fix` - Emergency fixes
- `release/v2.1.0` - Release branches
- `chore/update-dependencies` - Maintenance tasks

### Commit Message Format

#### Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Examples

```bash
# Feature addition
feat(classification): add new regex patterns for Office 365 tickets

# Bug fix
fix(extract): handle API timeout errors with exponential backoff

# Documentation
docs(api): update endpoint documentation with new parameters

# Performance improvement
perf(aggregate): optimize pandas operations for large datasets

# Breaking change
feat(config)!: change environment variable names for consistency

BREAKING CHANGE: Environment variables renamed for consistency.
ZENDESK_TOKEN is now ZENDESK_API_TOKEN.
```

### Pull Request Process

#### PR Requirements

1. **Code Quality Checks**
- [ ] All tests passing
- [ ] Code coverage >85%
- [ ] Linting passes (flake8, black, isort)
- [ ] Type checking passes (mypy)
- [ ] Security scan passes (bandit)
1. **Documentation Requirements**
- [ ] Code changes documented
- [ ] API documentation updated
- [ ] Changelog updated
- [ ] Breaking changes noted
1. **Review Requirements**
- [ ] At least 2 reviewers approved
- [ ] Security review (if applicable)
- [ ] Performance impact assessed

#### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
- [ ] All tests pass locally

## Related Issues
Closes #123
Related to #456
```

## Configuration Management

### Environment Variables

#### Required Variables

```bash
# Production environment variables
ZENDESK_API_TOKEN=production_token
CLIENT_ID=azure_client_id
CLIENT_SECRET=azure_client_secret
TENANT_ID=azure_tenant_id
SHAREPOINT_SITE_URL=https://company.sharepoint.com/sites/ITOps
```

#### Configuration Validation

```python
# src/config_validator.py
from typing import Dict, List
import os

REQUIRED_VARS: List[str] = [
    'ZENDESK_API_TOKEN',
    'CLIENT_ID',
    'CLIENT_SECRET',
    'TENANT_ID',
    'SHAREPOINT_SITE_URL'
]

def validate_configuration() -> Dict[str, bool]:
    """Validate that all required configuration is present."""
    results = {}
    for var in REQUIRED_VARS:
        results[var] = bool(os.getenv(var))
    return results

def get_missing_config() -> List[str]:
    """Return list of missing configuration variables."""
    return [var for var in REQUIRED_VARS if not os.getenv(var)]
```

### Feature Flags

#### Implementation

```python
# src/feature_flags.py
import os
from typing import Dict, Any

class FeatureFlags:
    """Manage feature flags for gradual rollouts."""
    
    def __init__(self):
        self.flags = {
            'ENABLE_ADVANCED_CLASSIFICATION': self._get_bool('ENABLE_ADVANCED_CLASSIFICATION', False),
            'ENABLE_REAL_TIME_ALERTS': self._get_bool('ENABLE_REAL_TIME_ALERTS', False),
            'ENABLE_ML_PREDICTIONS': self._get_bool('ENABLE_ML_PREDICTIONS', False),
        }
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def is_enabled(self, flag: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.flags.get(flag, False)
```

## Release Process

### Version Management

#### Semantic Versioning

```
MAJOR.MINOR.PATCH
2.1.3

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

#### Release Checklist

```markdown
## Pre-Release
- [ ] All tests passing on main branch
- [ ] Documentation updated
- [ ] Changelog updated with all changes
- [ ] Version number bumped
- [ ] Security scan completed
- [ ] Performance regression testing completed

## Release
- [ ] Create release branch: `release/v2.1.0`
- [ ] Final testing in staging environment
- [ ] Create release tag
- [ ] Deploy to production
- [ ] Monitor deployment for issues

## Post-Release
- [ ] Verify production functionality
- [ ] Update monitoring dashboards
- [ ] Communicate release to stakeholders
- [ ] Close related issues and tickets
```

### Deployment Pipeline

#### CI/CD Configuration

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 src tests
        black --check src tests
        isort --check-only src tests
    
    - name: Run type checking
      run: mypy src
    
    - name: Run security scan
      run: bandit -r src
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Performance Guidelines

### Code Optimization

#### Pandas Best Practices

```python
# Good: Vectorized operations
df['new_column'] = df['column1'] + df['column2']

# Avoid: Iterating through rows
# for index, row in df.iterrows():
#     df.at[index, 'new_column'] = row['column1'] + row['column2']

# Good: Use efficient data types
df['category'] = df['category'].astype('category')
df['count'] = df['count'].astype('int32')

# Good: Use query for filtering
result = df.query('ticket_count > 15 and category != "UAP"')
```

#### Memory Management

```python
# Good: Process data in chunks for large datasets
def process_large_dataset(file_path: str, chunk_size: int = 10000):
    """Process large CSV files in chunks to manage memory."""
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        processed_chunk = process_chunk(chunk)
        yield processed_chunk

# Good: Use context managers for file operations
def save_results(data: pd.DataFrame, filename: str):
    """Save data with proper resource management."""
    with open(filename, 'w') as f:
        data.to_csv(f, index=False)
```

### Performance Monitoring

#### Timing Decorators

```python
import time
import functools
from typing import Callable, Any

def time_function(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        print(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper

@time_function
def extract_tickets(start_date: str, end_date: str) -> List[Dict]:
    # Implementation
    pass
```

## Security Guidelines

### Code Security

#### Input Validation

```python
import re
from typing import Optional

def validate_date_input(date_string: str) -> bool:
    """Validate date input to prevent injection attacks."""
    # Only allow ISO date format: YYYY-MM-DD
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_string))

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove any path separators and dangerous characters
    safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return safe_chars[:100]  # Limit length
```

#### Secret Management

```python
# Good: Use environment variables for secrets
import os

def get_api_token() -> str:
    """Retrieve API token from environment variables."""
    token = os.getenv('ZENDESK_API_TOKEN')
    if not token:
        raise ValueError("ZENDESK_API_TOKEN environment variable not set")
    return token

# Avoid: Hardcoded secrets in code
# API_TOKEN = "hardcoded_token_value"  # Never do this
```

### Dependency Security

#### Security Scanning

```bash
# Check for known vulnerabilities
safety check

# Audit dependencies
pip-audit

# Update dependencies regularly
pip list --outdated
```

## Getting Help

### Resources

- **Technical Documentation**: [Internal Wiki](wiki.company.com/rca-app)
- **Architecture Decisions**: [ADR Repository](github.com/company/rca-app/docs/adr)
- **API Documentation**: [Swagger/OpenAPI](api-docs.company.com/rca-app)

### Support Channels

- **Development Questions**: #rca-app-dev Slack channel
- **Code Reviews**: GitHub pull request reviews
- **Technical Issues**: Create GitHub issue with appropriate labels
- **Architecture Discussions**: Weekly tech talk meetings

### Mentorship

New contributors are paired with experienced team members for:

- Code review guidance
- Architecture understanding
- Best practices training
- Career development