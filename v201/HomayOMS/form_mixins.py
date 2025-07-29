"""
Django Form Mixins for Number Validation

This module provides form mixins that automatically apply number validation
to form fields, making it easy to integrate Persian/English number handling
into Django forms.
"""

from django import forms
from django.core.exceptions import ValidationError
from .utils import (
    normalize_number_input, validate_number_input,
    normalize_phone_input, validate_phone_input,
    normalize_price_input, validate_price_input,
    price_to_decimal_input, NumberValidationError
)


class NumberValidationMixin:
    """
    Mixin to automatically validate and normalize numbers in Django forms
    
    This mixin provides methods to clean form fields that may contain
    Persian or English numbers, automatically converting them to English
    and validating their format.
    """
    
    def clean_number_field(self, field_name, allow_empty=True, min_value=None, max_value=None):
        """
        Clean a number field by normalizing Persian numbers and validating format
        
        Args:
            field_name (str): Name of the form field to clean
            allow_empty (bool): Whether empty values are allowed
            min_value (int/float): Minimum allowed value
            max_value (int/float): Maximum allowed value
            
        Returns:
            str: Normalized number string
            
        Raises:
            ValidationError: If validation fails
        """
        value = self.cleaned_data.get(field_name)
        
        if not value and allow_empty:
            return value
        
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} is required.")
        
        try:
            # Normalize the number (convert Persian to English)
            normalized = normalize_number_input(str(value))
            
            # Validate the normalized number
            if not validate_number_input(normalized):
                raise ValidationError(f"{field_name} must be a valid number.")
            
            # Check min/max values if specified
            if min_value is not None:
                try:
                    num_value = float(normalized)
                    if num_value < min_value:
                        raise ValidationError(f"{field_name} must be at least {min_value}.")
                except ValueError:
                    raise ValidationError(f"{field_name} must be a valid number.")
            
            if max_value is not None:
                try:
                    num_value = float(normalized)
                    if num_value > max_value:
                        raise ValidationError(f"{field_name} must be at most {max_value}.")
                except ValueError:
                    raise ValidationError(f"{field_name} must be a valid number.")
            
            return normalized
            
        except NumberValidationError as e:
            raise ValidationError(f"{field_name}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"{field_name}: Invalid number format.")
    
    def clean_phone_field(self, field_name, allow_empty=True):
        """
        Clean a phone number field by normalizing Persian numbers and validating format
        
        Args:
            field_name (str): Name of the form field to clean
            allow_empty (bool): Whether empty values are allowed
            
        Returns:
            str: Normalized phone number
            
        Raises:
            ValidationError: If validation fails
        """
        value = self.cleaned_data.get(field_name)
        
        if not value and allow_empty:
            return value
        
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} is required.")
        
        try:
            # Normalize the phone number
            normalized = normalize_phone_input(str(value))
            
            # Validate the normalized phone number
            if not validate_phone_input(normalized):
                raise ValidationError(f"{field_name} must be a valid Iranian phone number.")
            
            return normalized
            
        except NumberValidationError as e:
            raise ValidationError(f"{field_name}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"{field_name}: Invalid phone number format.")
    
    def clean_price_field(self, field_name, allow_empty=True, min_value=None, max_value=None):
        """
        Clean a price field by normalizing Persian numbers and validating format
        
        Args:
            field_name (str): Name of the form field to clean
            allow_empty (bool): Whether empty values are allowed
            min_value (Decimal): Minimum allowed value
            max_value (Decimal): Maximum allowed value
            
        Returns:
            str: Normalized price string
            
        Raises:
            ValidationError: If validation fails
        """
        value = self.cleaned_data.get(field_name)
        
        if not value and allow_empty:
            return value
        
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} is required.")
        
        try:
            # Normalize the price
            normalized = normalize_price_input(str(value))
            
            # Validate the normalized price
            if not validate_price_input(normalized):
                raise ValidationError(f"{field_name} must be a valid price.")
            
            # Convert to decimal for min/max validation
            decimal_value = price_to_decimal_input(normalized)
            
            # Check min/max values if specified
            if min_value is not None and decimal_value < min_value:
                raise ValidationError(f"{field_name} must be at least {min_value}.")
            
            if max_value is not None and decimal_value > max_value:
                raise ValidationError(f"{field_name} must be at most {max_value}.")
            
            return normalized
            
        except NumberValidationError as e:
            raise ValidationError(f"{field_name}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"{field_name}: Invalid price format.")


class AutoNumberValidationForm(forms.Form, NumberValidationMixin):
    """
    Base form class that automatically applies number validation
    
    This form class extends Django's Form and includes the NumberValidationMixin,
    making it easy to create forms with automatic Persian/English number handling.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add any initialization logic here
        pass


# Example form classes that demonstrate usage
class PhoneNumberForm(AutoNumberValidationForm):
    """
    Example form for phone number input with automatic validation
    """
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '۰۹۱۲۳۴۵۶۷۸۹ یا 09123456789'
        }),
        help_text="Enter your phone number (Persian or English numbers accepted)"
    )
    
    def clean_phone(self):
        return self.clean_phone_field('phone', allow_empty=False)


class PriceForm(AutoNumberValidationForm):
    """
    Example form for price input with automatic validation
    """
    price = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '۱۲۳۴.۵۶ یا 1234.56'
        }),
        help_text="Enter price (Persian or English numbers accepted)"
    )
    
    quantity = forms.CharField(
        max_length=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '۱۲۳ یا 123'
        }),
        help_text="Enter quantity (Persian or English numbers accepted)"
    )
    
    def clean_price(self):
        return self.clean_price_field('price', allow_empty=False, min_value=0)
    
    def clean_quantity(self):
        return self.clean_number_field('quantity', allow_empty=False, min_value=1)


class OrderForm(AutoNumberValidationForm):
    """
    Example form for order input with multiple number fields
    """
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number'
        })
    )
    
    total_amount = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Total amount'
        })
    )
    
    item_count = forms.CharField(
        max_length=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of items'
        })
    )
    
    def clean_customer_phone(self):
        return self.clean_phone_field('customer_phone', allow_empty=False)
    
    def clean_total_amount(self):
        return self.clean_price_field('total_amount', allow_empty=False, min_value=0)
    
    def clean_item_count(self):
        return self.clean_number_field('item_count', allow_empty=False, min_value=1)


# Utility functions for easy integration with existing forms
def apply_number_validation_to_field(form_instance, field_name, field_type='number', **kwargs):
    """
    Apply number validation to a specific field in an existing form
    
    Args:
        form_instance: The form instance
        field_name (str): Name of the field to validate
        field_type (str): Type of validation ('number', 'phone', 'price')
        **kwargs: Additional arguments for validation
        
    Returns:
        The cleaned value
    """
    if not hasattr(form_instance, 'cleaned_data'):
        raise ValueError("Form must be validated before applying number validation")
    
    if field_type == 'phone':
        return form_instance.clean_phone_field(field_name, **kwargs)
    elif field_type == 'price':
        return form_instance.clean_price_field(field_name, **kwargs)
    else:  # number
        return form_instance.clean_number_field(field_name, **kwargs)


def create_number_validator(field_type='number', **kwargs):
    """
    Create a validator function for use in form field definitions
    
    Args:
        field_type (str): Type of validation ('number', 'phone', 'price')
        **kwargs: Additional arguments for validation
        
    Returns:
        function: Validator function
    """
    def validator(value):
        try:
            if field_type == 'phone':
                normalized = normalize_phone_input(str(value))
                if not validate_phone_input(normalized):
                    raise ValidationError("Invalid phone number format.")
                return normalized
            elif field_type == 'price':
                normalized = normalize_price_input(str(value))
                if not validate_price_input(normalized):
                    raise ValidationError("Invalid price format.")
                return normalized
            else:  # number
                normalized = normalize_number_input(str(value))
                if not validate_number_input(normalized):
                    raise ValidationError("Invalid number format.")
                return normalized
        except NumberValidationError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError("Invalid format.")
    
    return validator 