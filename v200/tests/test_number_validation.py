"""
Test file for Number Validation System

This file demonstrates how to use the number validation utilities
and shows various test cases for Persian and English number handling.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from HomayOMS.utils import (
    NumberConverter, PhoneNumberValidator, PriceValidator,
    normalize_number_input, validate_number_input,
    normalize_phone_input, validate_phone_input,
    normalize_price_input, validate_price_input,
    price_to_decimal_input, NumberValidationError
)


def test_basic_number_conversion():
    """Test basic Persian to English number conversion"""
    print("=== Testing Basic Number Conversion ===")
    
    # Test Persian numbers
    test_cases = [
        ("۱۲۳", "123"),
        ("۴۵۶", "456"),
        ("۷۸۹", "789"),
        ("۰۱۲۳۴۵۶۷۸۹", "0123456789"),
    ]
    
    for persian, expected in test_cases:
        result = NumberConverter.convert_persian_to_english(persian)
        print(f"Persian: '{persian}' -> English: '{result}' (Expected: '{expected}')")
        assert result == expected, f"Failed: {persian} should convert to {expected}"
    
    print("✅ Basic number conversion tests passed\n")


def test_mixed_content():
    """Test conversion with mixed Persian and English content"""
    print("=== Testing Mixed Content ===")
    
    test_cases = [
        ("۱۲۳abc", "123abc"),
        ("abc۱۲۳def", "abc123def"),
        ("۱۲۳.۴۵۶", "123.456"),
        ("Price: ۱۲۳۴ تومان", "Price: 1234 تومان"),
    ]
    
    for mixed, expected in test_cases:
        result = NumberConverter.convert_persian_to_english(mixed)
        print(f"Mixed: '{mixed}' -> Result: '{result}' (Expected: '{expected}')")
        assert result == expected, f"Failed: {mixed} should convert to {expected}"
    
    print("✅ Mixed content tests passed\n")


def test_number_validation():
    """Test number validation functionality"""
    print("=== Testing Number Validation ===")
    
    # Valid cases
    valid_cases = [
        "123",
        "123.45",
        "۱۲۳",
        "۱۲۳.۴۵",
        "1,234",
        "1,234.56",
    ]
    
    # Invalid cases
    invalid_cases = [
        "abc",
        "12.34.56",
        "12abc",
        "",
        "   ",
    ]
    
    print("Testing valid cases:")
    for case in valid_cases:
        normalized, is_valid = NumberConverter.validate_and_convert(case)
        print(f"  '{case}' -> Normalized: '{normalized}', Valid: {is_valid}")
        assert is_valid, f"Should be valid: {case}"
    
    print("\nTesting invalid cases:")
    for case in invalid_cases:
        normalized, is_valid = NumberConverter.validate_and_convert(case)
        print(f"  '{case}' -> Normalized: '{normalized}', Valid: {is_valid}")
        assert not is_valid, f"Should be invalid: {case}"
    
    print("✅ Number validation tests passed\n")


def test_phone_number_validation():
    """Test phone number validation and normalization"""
    print("=== Testing Phone Number Validation ===")
    
    # Valid Iranian phone numbers
    valid_phones = [
        "09123456789",  # Standard format
        "9123456789",   # Without leading 0
        "+989123456789",  # With country code
        "989123456789",   # Country code without +
        "۰۹۱۲۳۴۵۶۷۸۹",   # Persian numbers
    ]
    
    # Invalid phone numbers
    invalid_phones = [
        "1234567890",   # Doesn't start with 9
        "0912345678",   # Too short
        "091234567890", # Too long
        "abc12345678",  # Contains letters
    ]
    
    print("Testing valid phone numbers:")
    for phone in valid_phones:
        try:
            normalized = PhoneNumberValidator.normalize_phone_number(phone)
            is_valid = PhoneNumberValidator.validate_phone_number(phone)
            print(f"  '{phone}' -> Normalized: '{normalized}', Valid: {is_valid}")
            assert is_valid, f"Should be valid: {phone}"
        except NumberValidationError as e:
            print(f"  '{phone}' -> Error: {e}")
            assert False, f"Should be valid: {phone}"
    
    print("\nTesting invalid phone numbers:")
    for phone in invalid_phones:
        try:
            normalized = PhoneNumberValidator.normalize_phone_number(phone)
            is_valid = PhoneNumberValidator.validate_phone_number(phone)
            print(f"  '{phone}' -> Normalized: '{normalized}', Valid: {is_valid}")
            assert not is_valid, f"Should be invalid: {phone}"
        except NumberValidationError:
            print(f"  '{phone}' -> Correctly rejected")
    
    print("✅ Phone number validation tests passed\n")


def test_price_validation():
    """Test price validation and conversion"""
    print("=== Testing Price Validation ===")
    
    # Valid prices
    valid_prices = [
        "123",
        "123.45",
        "۱۲۳",
        "۱۲۳.۴۵",
        "1,234",
        "1,234.56",
        "۱۲۳۴",
    ]
    
    # Invalid prices
    invalid_prices = [
        "abc",
        "12.34.56",
        "12abc",
        "",
    ]
    
    print("Testing valid prices:")
    for price in valid_prices:
        try:
            normalized = PriceValidator.normalize_price(price)
            is_valid = PriceValidator.validate_price(price)
            decimal_value = PriceValidator.price_to_decimal(price)
            print(f"  '{price}' -> Normalized: '{normalized}', Valid: {is_valid}, Decimal: {decimal_value}")
            assert is_valid, f"Should be valid: {price}"
        except NumberValidationError as e:
            print(f"  '{price}' -> Error: {e}")
            assert False, f"Should be valid: {price}"
    
    print("\nTesting invalid prices:")
    for price in invalid_prices:
        try:
            normalized = PriceValidator.normalize_price(price)
            is_valid = PriceValidator.validate_price(price)
            print(f"  '{price}' -> Normalized: '{normalized}', Valid: {is_valid}")
            assert not is_valid, f"Should be invalid: {price}"
        except NumberValidationError:
            print(f"  '{price}' -> Correctly rejected")
    
    print("✅ Price validation tests passed\n")


def test_convenience_functions():
    """Test the convenience functions"""
    print("=== Testing Convenience Functions ===")
    
    # Test number normalization
    test_inputs = [
        ("۱۲۳", "123"),
        ("456", "456"),
        ("۷۸۹", "789"),
    ]
    
    for input_val, expected in test_inputs:
        result = normalize_number_input(input_val)
        print(f"normalize_number_input('{input_val}') -> '{result}' (Expected: '{expected}')")
        assert result == expected
    
    # Test phone normalization
    phone_result = normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹")
    print(f"normalize_phone_input('۰۹۱۲۳۴۵۶۷۸۹') -> '{phone_result}'")
    assert phone_result == "9123456789"
    
    # Test price normalization
    price_result = normalize_price_input("۱۲۳۴.۵۶")
    print(f"normalize_price_input('۱۲۳۴.۵۶') -> '{price_result}'")
    assert price_result == "1234.56"
    
    # Test price to decimal
    decimal_result = price_to_decimal_input("۱۲۳۴.۵۶")
    print(f"price_to_decimal_input('۱۲۳۴.۵۶') -> {decimal_result} (type: {type(decimal_result)})")
    assert str(decimal_result) == "1234.56"
    
    print("✅ Convenience functions tests passed\n")


def test_error_handling():
    """Test error handling and edge cases"""
    print("=== Testing Error Handling ===")
    
    # Test with None values
    try:
        result = normalize_number_input(None)
        print(f"normalize_number_input(None) -> '{result}'")
    except NumberValidationError as e:
        print(f"normalize_number_input(None) -> Correctly raised: {e}")
    
    # Test with empty strings
    result = normalize_number_input("")
    print(f"normalize_number_input('') -> '{result}'")
    
    # Test with whitespace
    result = normalize_number_input("   ")
    print(f"normalize_number_input('   ') -> '{result}'")
    
    # Test invalid phone number
    try:
        result = normalize_phone_input("invalid")
        print(f"normalize_phone_input('invalid') -> '{result}'")
    except NumberValidationError as e:
        print(f"normalize_phone_input('invalid') -> Correctly raised: {e}")
    
    print("✅ Error handling tests passed\n")


def demonstrate_usage_in_forms():
    """Demonstrate how to use the validation in Django forms"""
    print("=== Usage in Django Forms Example ===")
    
    # Simulate form data
    form_data = {
        'phone': '۰۹۱۲۳۴۵۶۷۸۹',
        'price': '۱۲۳۴.۵۶',
        'quantity': '۱۲۳',
        'amount': '1,234.56'
    }
    
    print("Original form data:")
    for field, value in form_data.items():
        print(f"  {field}: '{value}'")
    
    print("\nAfter validation and normalization:")
    
    # Phone number
    try:
        normalized_phone = normalize_phone_input(form_data['phone'])
        is_valid_phone = validate_phone_input(form_data['phone'])
        print(f"  phone: '{form_data['phone']}' -> '{normalized_phone}' (Valid: {is_valid_phone})")
    except NumberValidationError as e:
        print(f"  phone: '{form_data['phone']}' -> Error: {e}")
    
    # Price
    try:
        normalized_price = normalize_price_input(form_data['price'])
        is_valid_price = validate_price_input(form_data['price'])
        decimal_price = price_to_decimal_input(form_data['price'])
        print(f"  price: '{form_data['price']}' -> '{normalized_price}' (Valid: {is_valid_price}, Decimal: {decimal_price})")
    except NumberValidationError as e:
        print(f"  price: '{form_data['price']}' -> Error: {e}")
    
    # Quantity
    normalized_quantity = normalize_number_input(form_data['quantity'])
    is_valid_quantity = validate_number_input(form_data['quantity'])
    print(f"  quantity: '{form_data['quantity']}' -> '{normalized_quantity}' (Valid: {is_valid_quantity})")
    
    # Amount
    normalized_amount = normalize_price_input(form_data['amount'])
    is_valid_amount = validate_price_input(form_data['amount'])
    print(f"  amount: '{form_data['amount']}' -> '{normalized_amount}' (Valid: {is_valid_amount})")
    
    print("✅ Form usage demonstration completed\n")


if __name__ == "__main__":
    print("🧪 Running Number Validation System Tests\n")
    
    try:
        test_basic_number_conversion()
        test_mixed_content()
        test_number_validation()
        test_phone_number_validation()
        test_price_validation()
        test_convenience_functions()
        test_error_handling()
        demonstrate_usage_in_forms()
        
        print("🎉 All tests passed successfully!")
        print("\n📋 Summary:")
        print("- Persian numbers are automatically converted to English")
        print("- English numbers remain unchanged")
        print("- Phone numbers are normalized to Iranian format")
        print("- Prices are cleaned and converted to Decimal objects")
        print("- All functions include proper error handling")
        print("- Convenience functions make integration easy")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 