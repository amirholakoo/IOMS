# Scripts Directory

This directory contains utility scripts and debugging tools for the HomayOMS project.

## Contents

### Debug Scripts
- `debug_order.py` - Order debugging and troubleshooting script
- `debug_sms.py` - SMS system debugging script
- `simple_test.py` - Simple test script for basic functionality

## Usage

### Debug Order Script
```bash
python scripts/debug_order.py
```
**Purpose**: Debug order creation, processing, and cancellation issues
**Features**:
- Order status checking
- Order item validation
- Payment status verification
- Product inventory checking

### Debug SMS Script
```bash
python scripts/debug_sms.py
```
**Purpose**: Debug SMS verification and authentication issues
**Features**:
- SMS API testing
- Verification code generation
- User authentication flow testing

### Simple Test Script
```bash
python scripts/simple_test.py
```
**Purpose**: Basic functionality testing and validation
**Features**:
- Database connection testing
- Basic model operations
- Configuration validation

## Script Development Guidelines

### Error Handling
All scripts should include proper error handling:
```python
try:
    # Script logic
    pass
except Exception as e:
    print(f"Error: {e}")
    # Log error details
```

### Logging
Use Django's logging system:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Script execution started")
```

### Configuration
Scripts should use Django settings:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()
```

## Adding New Scripts

When adding new scripts:
1. Follow the naming convention: `debug_*.py` for debug scripts
2. Include proper error handling
3. Add documentation in this README
4. Test thoroughly before committing

## Security Notes
- Debug scripts may contain sensitive information
- Do not commit scripts with hardcoded credentials
- Use environment variables for configuration
- Test in development environment only 