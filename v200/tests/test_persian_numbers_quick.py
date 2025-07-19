#!/usr/bin/env python3
"""
🧪 Quick Test Script for Persian Number Validation System
📱 Run this script to quickly test if the system is working
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from HomayOMS.utils import (
    normalize_phone_input, validate_phone_input,
    normalize_number_input, validate_number_input,
    NumberValidationError
)

def test_phone_numbers():
    """📱 Test phone number normalization and validation"""
    print("📱 Testing Phone Numbers...")
    
    test_cases = [
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789", True),
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789", True),
        ("09123456789", "09123456789", True),
        ("۰۸۱۲۳۴۵۶۷۸۹", "08123456789", False),  # Wrong prefix
        ("۰۹۱۲۳۴۵۶۷۸", "0912345678", False),     # Too short
        ("۰۹۱۲۳۴۵۶۷۸۹۰", "091234567890", False), # Too long
    ]
    
    for persian_input, expected_english, should_be_valid in test_cases:
        try:
            normalized = normalize_phone_input(persian_input)
            is_valid = validate_phone_input(normalized)
            
            print(f"  Input: {persian_input}")
            print(f"  Normalized: {normalized}")
            print(f"  Expected: {expected_english}")
            print(f"  Valid: {is_valid} (Expected: {should_be_valid})")
            
            if normalized == expected_english and is_valid == should_be_valid:
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()

def test_general_numbers():
    """🔢 Test general number normalization and validation"""
    print("🔢 Testing General Numbers...")
    
    test_cases = [
        ("۱۲۳۴۵۶", "123456", True),
        ("۱۲۳.۴۵۶", "123.456", True),
        ("123456", "123456", True),
        ("۱۲۳abc", None, False),  # Invalid
        ("123.456.789", "123.456.789", False),  # Multiple decimals
    ]
    
    for persian_input, expected_english, should_be_valid in test_cases:
        try:
            if should_be_valid:
                normalized = normalize_number_input(persian_input)
                is_valid = validate_number_input(normalized)
                
                print(f"  Input: {persian_input}")
                print(f"  Normalized: {normalized}")
                print(f"  Expected: {expected_english}")
                print(f"  Valid: {is_valid}")
                
                if normalized == expected_english and is_valid == should_be_valid:
                    print("  ✅ PASS")
                else:
                    print("  ❌ FAIL")
            else:
                try:
                    normalize_number_input(persian_input)
                    print(f"  Input: {persian_input}")
                    print("  ❌ FAIL - Should have raised error")
                except NumberValidationError:
                    print(f"  Input: {persian_input}")
                    print("  ✅ PASS - Correctly raised error")
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()

def test_edge_cases():
    """🔍 Test edge cases"""
    print("🔍 Testing Edge Cases...")
    
    edge_cases = [
        ("", ""),
        (None, ""),
        ("0", "0"),
        ("۰", "0"),
    ]
    
    for input_val, expected in edge_cases:
        try:
            normalized = normalize_number_input(input_val)
            print(f"  Input: {input_val}")
            print(f"  Normalized: {normalized}")
            print(f"  Expected: {expected}")
            
            if normalized == expected:
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()

def test_performance():
    """⚡ Test performance"""
    print("⚡ Testing Performance...")
    
    import time
    
    start_time = time.time()
    
    # Test 1000 normalizations
    for i in range(1000):
        normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹")
        normalize_number_input("۱۲۳۴۵۶۷۸۹۰")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"  1000 normalizations took: {execution_time:.3f} seconds")
    
    if execution_time < 1.0:
        print("  ✅ PASS - Performance is good")
    else:
        print("  ⚠️  SLOW - Performance might need optimization")
    print()

def test_javascript_file():
    """🌐 Test JavaScript file existence"""
    print("🌐 Testing JavaScript File...")
    
    js_file_path = 'static/js/persian-numbers.js'
    
    if os.path.exists(js_file_path):
        print(f"  ✅ JavaScript file exists: {js_file_path}")
        
        # Check file size
        file_size = os.path.getsize(js_file_path)
        print(f"  📁 File size: {file_size} bytes")
        
        if file_size > 1000:  # Should be substantial
            print("  ✅ File size is reasonable")
        else:
            print("  ⚠️  File seems too small")
    else:
        print(f"  ❌ JavaScript file not found: {js_file_path}")
    print()

def test_sms_login_functionality():
    """📱 Test SMS login functionality with Persian numbers"""
    print("📱 Testing SMS Login Functionality...")
    
    # Test phone number normalization for SMS login
    test_cases = [
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789", True),
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789", True),
        ("09123456789", "09123456789", True),
        ("۰۸۱۲۳۴۵۶۷۸۹", "08123456789", False),  # Wrong prefix
        ("۰۹۱۲۳۴۵۶۷۸", "0912345678", False),     # Too short
    ]
    
    for persian_input, expected_english, should_be_valid in test_cases:
        try:
            normalized = normalize_phone_input(persian_input)
            is_valid = validate_phone_input(normalized)
            
            print(f"  Input: {persian_input}")
            print(f"  Normalized: {normalized}")
            print(f"  Expected: {expected_english}")
            print(f"  Valid: {is_valid} (Expected: {should_be_valid})")
            
            if normalized == expected_english and is_valid == should_be_valid:
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()
    
    # Test verification code normalization
    print("  Testing Verification Code...")
    verification_cases = [
        ("۱۲۳۴۵۶", "123456", True),
        ("123456", "123456", True),
        ("۱۲۳۴۵۶", "123456", True),
    ]
    
    for persian_input, expected_english, should_be_valid in verification_cases:
        try:
            normalized = normalize_number_input(persian_input)
            is_valid = validate_number_input(normalized) and len(normalized) == 6
            
            print(f"    Input: {persian_input}")
            print(f"    Normalized: {normalized}")
            print(f"    Expected: {expected_english}")
            print(f"    Valid: {is_valid}")
            
            if normalized == expected_english and is_valid == should_be_valid:
                print("    ✅ PASS")
            else:
                print("    ❌ FAIL")
            print()
            
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            print()

def main():
    """🏃‍♂️ Run all tests"""
    print("🧪 Persian Number Validation System - Quick Test")
    print("=" * 50)
    print()
    
    try:
        test_phone_numbers()
        test_general_numbers()
        test_edge_cases()
        test_performance()
        test_javascript_file()
        test_sms_login_functionality()
        
        print("🎉 All tests completed!")
        print("💡 To run full Django tests: python manage.py test tests.test_persian_numbers")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 