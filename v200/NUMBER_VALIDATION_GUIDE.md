# Number Validation System Guide

## Overview

This guide explains how to use the comprehensive number validation system that handles both Persian and English numbers throughout the HomayOMS project. The system automatically converts Persian numbers to English and validates number formats.

## Key Features

- ✅ **Automatic Persian to English conversion**
- ✅ **English numbers remain unchanged**
- ✅ **Phone number validation (Iranian format)**
- ✅ **Price/amount validation with Decimal conversion**
- ✅ **Comprehensive error handling**
- ✅ **Easy integration with Django forms**
- ✅ **Convenience functions for quick use**

## File Structure

```
v200/
├── HomayOMS/
│   ├── utils.py              # Core validation logic
│   └── form_mixins.py        # Django form integration
├── test_number_validation.py # Comprehensive tests
└── NUMBER_VALIDATION_GUIDE.md # This guide
```

## Quick Start

### 1. Basic Usage

```python
from HomayOMS.utils import normalize_number_input, validate_number_input

# Convert Persian numbers to English
result = normalize_number_input("۱۲۳۴")  # Returns "1234"
result = normalize_number_input("456")   # Returns "456" (unchanged)

# Validate numbers
is_valid = validate_number_input("۱۲۳۴")  # Returns True
is_valid = validate_number_input("abc")   # Returns False
```

### 2. Phone Number Validation

```python
from HomayOMS.utils import normalize_phone_input, validate_phone_input

# Normalize phone numbers
phone = normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹")  # Returns "9123456789"
phone = normalize_phone_input("09123456789")   # Returns "9123456789"

# Validate phone numbers
is_valid = validate_phone_input("۰۹۱۲۳۴۵۶۷۸۹")  # Returns True
is_valid = validate_phone_input("1234567890")    # Returns False
```

### 3. Price Validation

```python
from HomayOMS.utils import normalize_price_input, price_to_decimal_input

# Normalize prices
price = normalize_price_input("۱۲۳۴.۵۶")  # Returns "1234.56"
price = normalize_price_input("1,234.56") # Returns "1234.56"

# Convert to Decimal
decimal_price = price_to_decimal_input("۱۲۳۴.۵۶")  # Returns Decimal("1234.56")
```

## Django Forms Integration

### 1. Using the Mixin

```python
from HomayOMS.form_mixins import NumberValidationMixin
from django import forms

class MyForm(forms.Form, NumberValidationMixin):
    phone = forms.CharField(max_length=20)
    price = forms.CharField(max_length=20)
    quantity = forms.CharField(max_length=10)
    
    def clean_phone(self):
        return self.clean_phone_field('phone', allow_empty=False)
    
    def clean_price(self):
        return self.clean_price_field('price', allow_empty=False, min_value=0)
    
    def clean_quantity(self):
        return self.clean_number_field('quantity', allow_empty=False, min_value=1)
```

### 2. Using the Base Form Class

```python
from HomayOMS.form_mixins import AutoNumberValidationForm

class PhoneNumberForm(AutoNumberValidationForm):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '۰۹۱۲۳۴۵۶۷۸۹ یا 09123456789'
        })
    )
    
    def clean_phone(self):
        return self.clean_phone_field('phone', allow_empty=False)
```

### 3. Using Validators

```python
from HomayOMS.form_mixins import create_number_validator
from django import forms

class ProductForm(forms.Form):
    price = forms.CharField(
        max_length=20,
        validators=[create_number_validator('price')]
    )
    quantity = forms.CharField(
        max_length=10,
        validators=[create_number_validator('number', min_value=1)]
    )
```

## Integration Examples

### 1. In Django Views

```python
from django.shortcuts import render
from HomayOMS.utils import normalize_phone_input, normalize_price_input
from HomayOMS.form_mixins import NumberValidationMixin

def process_order(request):
    if request.method == 'POST':
        # Get form data
        phone = request.POST.get('phone')
        price = request.POST.get('price')
        
        try:
            # Normalize the data
            normalized_phone = normalize_phone_input(phone)
            normalized_price = normalize_price_input(price)
            
            # Process the order with normalized data
            # ... your business logic here
            
        except NumberValidationError as e:
            # Handle validation errors
            return render(request, 'error.html', {'error': str(e)})
    
    return render(request, 'order_form.html')
```

### 2. In Model Methods

```python
from django.db import models
from HomayOMS.utils import normalize_phone_input, price_to_decimal_input

class Customer(models.Model):
    phone = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    
    def set_phone(self, phone_number):
        """Set phone number with automatic normalization"""
        self.phone = normalize_phone_input(phone_number)
    
    def add_balance(self, amount):
        """Add balance with automatic conversion"""
        decimal_amount = price_to_decimal_input(amount)
        self.balance += decimal_amount
```

### 3. In API Views

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from HomayOMS.utils import normalize_number_input, validate_number_input

@api_view(['POST'])
def update_product_quantity(request):
    quantity = request.data.get('quantity')
    
    # Normalize and validate
    normalized_quantity = normalize_number_input(quantity)
    
    if not validate_number_input(normalized_quantity):
        return Response({'error': 'Invalid quantity format'}, status=400)
    
    # Process the update
    # ... your logic here
    
    return Response({'success': True})
```

## Error Handling

### 1. Custom Exception

```python
from HomayOMS.utils import NumberValidationError

try:
    normalized = normalize_phone_input("invalid")
except NumberValidationError as e:
    print(f"Validation error: {e}")
    # Handle the error appropriately
```

### 2. Graceful Fallback

```python
from HomayOMS.utils import validate_number_input, normalize_number_input

def safe_normalize_number(text):
    """Safely normalize a number with fallback"""
    try:
        normalized = normalize_number_input(text)
        if validate_number_input(normalized):
            return normalized
        else:
            return None
    except Exception:
        return None
```

## Testing

Run the comprehensive test suite:

```bash
cd v200
python test_number_validation.py
```

This will test:
- Basic Persian to English conversion
- Mixed content handling
- Number validation
- Phone number validation
- Price validation
- Error handling
- Form integration examples

## Best Practices

### 1. Always Validate Input

```python
# Good: Validate before processing
if validate_number_input(user_input):
    normalized = normalize_number_input(user_input)
    # Process the data
else:
    # Handle invalid input
    pass

# Bad: Assume input is valid
normalized = normalize_number_input(user_input)  # May raise exception
```

### 2. Use Appropriate Validation Type

```python
# For phone numbers
normalize_phone_input(phone)

# For prices/amounts
normalize_price_input(price)

# For general numbers
normalize_number_input(number)
```

### 3. Handle Errors Gracefully

```python
try:
    result = normalize_phone_input(phone)
except NumberValidationError as e:
    # Log the error and provide user-friendly message
    logger.error(f"Phone validation failed: {e}")
    return "Invalid phone number format"
```

### 4. Use Form Mixins for Django Forms

```python
# Instead of manual validation in clean methods
class MyForm(forms.Form, NumberValidationMixin):
    def clean_phone(self):
        return self.clean_phone_field('phone', allow_empty=False)
```

## Migration Guide

### From Manual Validation

**Before:**
```python
def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    # Manual Persian to English conversion
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', # ... etc
    }
    for persian, english in persian_to_english.items():
        phone = phone.replace(persian, english)
    # Manual validation logic
    if not re.match(r'^9[0-9]{9}$', phone):
        raise ValidationError("Invalid phone number")
    return phone
```

**After:**
```python
def clean_phone(self):
    return self.clean_phone_field('phone', allow_empty=False)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```python
   # Make sure you're importing from the correct path
   from HomayOMS.utils import normalize_number_input
   ```

2. **Validation Failures**
   ```python
   # Check if the input contains unexpected characters
   print(f"Input: '{user_input}'")
   normalized = normalize_number_input(user_input)
   print(f"Normalized: '{normalized}'")
   ```

3. **Form Integration Issues**
   ```python
   # Ensure the mixin is properly inherited
   class MyForm(forms.Form, NumberValidationMixin):
       # Your fields here
   ```

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- The validation system is optimized for performance
- Regular expressions are compiled once at module load
- Conversion maps are stored in memory
- Minimal overhead for English-only numbers

## Security Notes

- All input is validated before processing
- No SQL injection risks (validation happens before database operations)
- Proper error handling prevents information leakage
- Logging helps with audit trails

---

## Summary

This number validation system provides a comprehensive solution for handling Persian and English numbers throughout your HomayOMS project. It's designed to be:

- **Easy to use**: Simple function calls and form mixins
- **Comprehensive**: Handles all number types (general, phone, price)
- **Robust**: Proper error handling and validation
- **Flexible**: Multiple integration options
- **Maintainable**: Well-documented and tested

Start by using the convenience functions for simple cases, then integrate the form mixins for Django forms, and finally use the core classes for advanced customization. 