# Tests Directory

This directory contains all test files for the HomayOMS project.

## Contents

### Core System Tests
- `test_comprehensive_logging.py` - Comprehensive logging system tests
- `test_user_logging.py` - User activity logging tests
- `test_processing_order.py` - Order processing workflow tests
- `test_selected_products.py` - Selected products page functionality tests

### Payment System Tests
- `test_payment_system.py` - Payment system integration tests
- `test_payment_fixes.py` - Payment bug fixes and edge cases
- `test_payment_failure_logic.py` - Payment failure scenarios
- `test_new_order_flow.py` - New order flow implementation tests

### Order Management Tests
- `test_order_cancellation.py` - Order cancellation system tests
- `test_zero_issue.py` - Zero amount and edge case tests

### Validation & Localization Tests
- `test_number_validation.py` - Number validation system tests
- `test_persian_numbers.py` - Persian number handling tests
- `test_persian_numbers_quick.py` - Quick Persian number validation

### Automation Tests
- `test_automation_quick.py` - Quick automation workflow tests

## Running Tests

### Run All Tests
```bash
python manage.py test tests/
```

### Run Specific Test File
```bash
python manage.py test tests.test_payment_system
python manage.py test tests.test_order_cancellation
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test tests/
coverage report
coverage html
```

## Test Categories

### Unit Tests
- Individual component testing
- Model validation tests
- Utility function tests

### Integration Tests
- Payment gateway integration
- Order workflow testing
- User authentication flow

### System Tests
- End-to-end workflow testing
- Cross-module integration
- Performance testing

## Test Data
Tests use fixtures and factory patterns to create test data. See individual test files for specific data setup requirements. 