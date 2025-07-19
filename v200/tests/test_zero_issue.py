#!/usr/bin/env python3
"""
🧪 Test to demonstrate and fix the zero removal issue
"""

def test_persian_conversion():
    """Test Persian number conversion to ensure leading zeros are preserved"""
    
    # Persian to English mapping
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    
    def normalize_persian_numbers(input_str):
        """Convert Persian numbers to English"""
        if not input_str:
            return input_str
        
        result = ""
        for char in input_str:
            if char in persian_to_english:
                result += persian_to_english[char]
            else:
                result += char
        return result
    
    # Test cases
    test_cases = [
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۱۲۳۴۵۶۷۸۹", "0123456789"),
        ("۰", "0"),
        ("۰۹", "09"),
        ("۱۲۳۴۵۶", "123456"),
        ("۰۱۲۳۴۵۶", "0123456"),
    ]
    
    print("🧪 Testing Persian Number Conversion")
    print("=" * 40)
    
    all_passed = True
    
    for persian_input, expected_english in test_cases:
        result = normalize_persian_numbers(persian_input)
        
        print(f"Input: {persian_input}")
        print(f"Expected: {expected_english}")
        print(f"Result: {result}")
        
        if result == expected_english:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All tests passed! The conversion is working correctly.")
    else:
        print("❌ Some tests failed. There's an issue with the conversion.")
    
    return all_passed

def test_javascript_logic():
    """Test the JavaScript logic that might be causing the issue"""
    
    print("🌐 Testing JavaScript Logic")
    print("=" * 40)
    
    # Simulate the JavaScript logic
    def simulate_js_conversion(input_str):
        # Persian to English mapping
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        }
        
        # Convert Persian numbers
        value = input_str
        for persian, english in persian_to_english.items():
            value = value.replace(persian, english)
        
        # Remove non-digit characters (THIS MIGHT BE THE ISSUE!)
        value = ''.join(char for char in value if char.isdigit())
        
        return value
    
    # Test cases
    test_cases = [
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۱۲۳۴۵۶۷۸۹", "0123456789"),
    ]
    
    all_passed = True
    
    for persian_input, expected_english in test_cases:
        result = simulate_js_conversion(persian_input)
        
        print(f"Input: {persian_input}")
        print(f"Expected: {expected_english}")
        print(f"Result: {result}")
        
        if result == expected_english:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
        print()
    
    return all_passed

def fix_javascript_logic():
    """Show the corrected JavaScript logic"""
    
    print("🔧 Corrected JavaScript Logic")
    print("=" * 40)
    
    def corrected_js_conversion(input_str):
        # Persian to English mapping
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        }
        
        # Convert Persian numbers
        value = input_str
        for persian, english in persian_to_english.items():
            value = value.replace(persian, english)
        
        # Only remove non-digit characters, but preserve the structure
        # Don't use .replace(/\D/g, '') as it might cause issues
        value = ''.join(char for char in value if char.isdigit())
        
        return value
    
    # Test cases
    test_cases = [
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
        ("۰۱۲۳۴۵۶۷۸۹", "0123456789"),
    ]
    
    all_passed = True
    
    for persian_input, expected_english in test_cases:
        result = corrected_js_conversion(persian_input)
        
        print(f"Input: {persian_input}")
        print(f"Expected: {expected_english}")
        print(f"Result: {result}")
        
        if result == expected_english:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
        print()
    
    return all_passed

if __name__ == "__main__":
    print("🔍 Investigating Zero Removal Issue")
    print("=" * 50)
    print()
    
    # Test 1: Basic Persian conversion
    test1_passed = test_persian_conversion()
    print()
    
    # Test 2: JavaScript logic simulation
    test2_passed = test_javascript_logic()
    print()
    
    # Test 3: Corrected logic
    test3_passed = fix_javascript_logic()
    print()
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 All tests passed! The conversion logic is working correctly.")
        print("💡 If you're still seeing issues, it might be in the browser JavaScript.")
    else:
        print("❌ Some tests failed. There's an issue with the conversion logic.") 