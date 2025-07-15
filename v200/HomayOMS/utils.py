"""
Number Validation Utilities for HomayOMS

This module provides comprehensive number validation and conversion utilities
that handle both English and Persian numbers throughout the application.

Key Features:
- Persian to English number conversion
- English number validation
- Mixed number handling
- Phone number validation
- Price/amount validation
- Error handling with proper logging
"""

import re
import logging
from typing import Union, Optional, Tuple
from decimal import Decimal, InvalidOperation

# Configure logging
logger = logging.getLogger(__name__)

# Persian to English number mapping
PERSIAN_TO_ENGLISH_MAP = {
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
}

# English to Persian number mapping (for reverse conversion if needed)
ENGLISH_TO_PERSIAN_MAP = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

# Persian number pattern for detection
PERSIAN_NUMBER_PATTERN = re.compile(r'[۰-۹]')

# English number pattern for validation
ENGLISH_NUMBER_PATTERN = re.compile(r'^[0-9]+(\.[0-9]+)?$')

# Phone number pattern (Iranian format)
PHONE_PATTERN = re.compile(r'^(\+98|98|0)?9[0-9]{9}$')

# Price/amount pattern (allows decimal points and commas)
PRICE_PATTERN = re.compile(r'^[0-9,]+(\.[0-9]+)?$')


class NumberValidationError(Exception):
    """Custom exception for number validation errors"""
    pass


class NumberConverter:
    """
    Core number conversion and validation class
    
    This class provides methods to:
    - Convert Persian numbers to English
    - Validate number formats
    - Handle mixed number inputs
    - Provide proper error handling
    """
    
    @staticmethod
    def contains_persian_numbers(text: str) -> bool:
        """
        Check if a string contains Persian numbers
        
        Args:
            text (str): Input string to check
            
        Returns:
            bool: True if Persian numbers are found, False otherwise
        """
        try:
            if not isinstance(text, str):
                return False
            return bool(PERSIAN_NUMBER_PATTERN.search(text))
        except Exception as e:
            logger.error(f"Error checking for Persian numbers in '{text}': {str(e)}")
            return False
    
    @staticmethod
    def convert_persian_to_english(text: str) -> str:
        """
        Convert Persian numbers to English numbers in a string
        
        Args:
            text (str): Input string that may contain Persian numbers
            
        Returns:
            str: String with Persian numbers converted to English
            
        Raises:
            NumberValidationError: If conversion fails
        """
        try:
            if not isinstance(text, str):
                raise NumberValidationError("Input must be a string")
            
            if not text:
                return text
            
            # Convert each Persian digit to English
            converted = text
            for persian, english in PERSIAN_TO_ENGLISH_MAP.items():
                converted = converted.replace(persian, english)
            
            return converted
        except Exception as e:
            logger.error(f"Error converting Persian numbers in '{text}': {str(e)}")
            raise NumberValidationError(f"Failed to convert Persian numbers: {str(e)}")
    
    @staticmethod
    def validate_english_numbers(text: str) -> bool:
        """
        Validate if a string contains only English numbers and decimal points
        
        Args:
            text (str): Input string to validate
            
        Returns:
            bool: True if valid English numbers, False otherwise
        """
        try:
            if not isinstance(text, str):
                return False
            
            if not text.strip():
                return False
            
            # Remove commas for validation (they're allowed in prices)
            clean_text = text.replace(',', '')
            
            return bool(ENGLISH_NUMBER_PATTERN.match(clean_text))
        except Exception as e:
            logger.error(f"Error validating English numbers in '{text}': {str(e)}")
            return False
    
    @staticmethod
    def normalize_number(text: str) -> str:
        """
        Normalize a number string by converting Persian to English and cleaning
        
        Args:
            text (str): Input string that may contain Persian or English numbers
            
        Returns:
            str: Normalized English number string
            
        Raises:
            NumberValidationError: If normalization fails
        """
        try:
            if not isinstance(text, str):
                raise NumberValidationError("Input must be a string")
            
            if not text.strip():
                return text
            
            # Convert Persian to English if needed
            if NumberConverter.contains_persian_numbers(text):
                text = NumberConverter.convert_persian_to_english(text)
            
            # Clean up the number (remove extra spaces, normalize decimal points)
            normalized = text.strip()
            
            # Handle multiple decimal points (keep only the last one)
            decimal_parts = normalized.split('.')
            if len(decimal_parts) > 2:
                normalized = '.'.join(decimal_parts[:-1]) + '.' + decimal_parts[-1]
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing number '{text}': {str(e)}")
            raise NumberValidationError(f"Failed to normalize number: {str(e)}")
    
    @staticmethod
    def validate_and_convert(text: str) -> Tuple[str, bool]:
        """
        Validate and convert a number string
        
        Args:
            text (str): Input string to validate and convert
            
        Returns:
            Tuple[str, bool]: (normalized_number, is_valid)
        """
        try:
            if not isinstance(text, str):
                return text, False
            
            normalized = NumberConverter.normalize_number(text)
            is_valid = NumberConverter.validate_english_numbers(normalized)
            
            return normalized, is_valid
        except Exception as e:
            logger.error(f"Error in validate_and_convert for '{text}': {str(e)}")
            return text, False


class PhoneNumberValidator:
    """
    Phone number validation and conversion utilities
    """
    
    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """
        Normalize phone number by converting Persian numbers and standardizing format
        
        Args:
            phone (str): Phone number that may contain Persian numbers
            
        Returns:
            str: Normalized phone number in standard format
            
        Raises:
            NumberValidationError: If normalization fails
        """
        try:
            if not isinstance(phone, str):
                raise NumberValidationError("Phone number must be a string")
            
            # Convert Persian numbers to English
            normalized = NumberConverter.normalize_number(phone)
            
            # Remove all non-digit characters
            digits_only = re.sub(r'[^0-9]', '', normalized)
            
            # Handle Iranian phone number formats
            if digits_only.startswith('98'):
                digits_only = digits_only[2:]
            elif digits_only.startswith('0098'):
                digits_only = digits_only[4:]

            # Ensure it starts with 09 and has 11 digits (Iranian mobile format)
            if len(digits_only) == 10 and digits_only.startswith('9'):
                return '0' + digits_only
            elif len(digits_only) == 11 and digits_only.startswith('09'):
                return digits_only
            else:
                raise NumberValidationError("Invalid phone number format")
                
        except Exception as e:
            logger.error(f"Error normalizing phone number '{phone}': {str(e)}")
            raise NumberValidationError(f"Failed to normalize phone number: {str(e)}")
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate if a phone number is in correct Iranian format
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            normalized = PhoneNumberValidator.normalize_phone_number(phone)
            return bool(PHONE_PATTERN.match(normalized))
        except NumberValidationError:
            return False
        except Exception as e:
            logger.error(f"Error validating phone number '{phone}': {str(e)}")
            return False


class PriceValidator:
    """
    Price and amount validation utilities
    """
    
    @staticmethod
    def normalize_price(price: str) -> str:
        """
        Normalize price string by converting Persian numbers and cleaning format
        
        Args:
            price (str): Price string that may contain Persian numbers
            
        Returns:
            str: Normalized price string
            
        Raises:
            NumberValidationError: If normalization fails
        """
        try:
            if not isinstance(price, str):
                raise NumberValidationError("Price must be a string")
            
            # Convert Persian numbers to English
            normalized = NumberConverter.normalize_number(price)
            
            # Remove commas and extra spaces
            normalized = normalized.replace(',', '').strip()
            
            # Validate it's a proper number
            if not NumberConverter.validate_english_numbers(normalized):
                raise NumberValidationError("Invalid price format")
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing price '{price}': {str(e)}")
            raise NumberValidationError(f"Failed to normalize price: {str(e)}")
    
    @staticmethod
    def validate_price(price: str) -> bool:
        """
        Validate if a price string is in correct format
        
        Args:
            price (str): Price string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            normalized = PriceValidator.normalize_price(price)
            return bool(PRICE_PATTERN.match(normalized))
        except NumberValidationError:
            return False
        except Exception as e:
            logger.error(f"Error validating price '{price}': {str(e)}")
            return False
    
    @staticmethod
    def price_to_decimal(price: str) -> Decimal:
        """
        Convert price string to Decimal object
        
        Args:
            price (str): Price string to convert
            
        Returns:
            Decimal: Price as Decimal object
            
        Raises:
            NumberValidationError: If conversion fails
        """
        try:
            normalized = PriceValidator.normalize_price(price)
            return Decimal(normalized)
        except InvalidOperation as e:
            logger.error(f"Error converting price '{price}' to Decimal: {str(e)}")
            raise NumberValidationError(f"Invalid price format: {str(e)}")
        except Exception as e:
            logger.error(f"Error converting price '{price}' to Decimal: {str(e)}")
            raise NumberValidationError(f"Failed to convert price: {str(e)}")


# Convenience functions for easy use throughout the application
def normalize_number_input(text: str) -> str:
    """
    Convenience function to normalize any number input
    
    Args:
        text (str): Input text that may contain Persian or English numbers
        
    Returns:
        str: Normalized English number string
    """
    return NumberConverter.normalize_number(text)


def validate_number_input(text: str) -> bool:
    """
    Convenience function to validate any number input
    
    Args:
        text (str): Input text to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        normalized, is_valid = NumberConverter.validate_and_convert(text)
        return is_valid
    except Exception:
        return False


def normalize_phone_input(phone: str) -> str:
    """
    Convenience function to normalize phone number input
    
    Args:
        phone (str): Phone number that may contain Persian numbers
        
    Returns:
        str: Normalized phone number
    """
    return PhoneNumberValidator.normalize_phone_number(phone)


def validate_phone_input(phone: str) -> bool:
    """
    Convenience function to validate phone number input
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return PhoneNumberValidator.validate_phone_number(phone)


def normalize_price_input(price: str) -> str:
    """
    Convenience function to normalize price input
    
    Args:
        price (str): Price that may contain Persian numbers
        
    Returns:
        str: Normalized price string
    """
    return PriceValidator.normalize_price(price)


def validate_price_input(price: str) -> bool:
    """
    Convenience function to validate price input
    
    Args:
        price (str): Price to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return PriceValidator.validate_price(price)


def price_to_decimal_input(price: str) -> Decimal:
    """
    Convenience function to convert price input to Decimal
    
    Args:
        price (str): Price string to convert
        
    Returns:
        Decimal: Price as Decimal object
    """
    return PriceValidator.price_to_decimal(price) 