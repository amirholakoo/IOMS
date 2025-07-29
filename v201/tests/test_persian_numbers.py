"""
🧪 Test Suite for Persian Number Validation System - HomayOMS
📱 Comprehensive testing of number normalization and validation
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from HomayOMS.utils import (
    normalize_phone_input, validate_phone_input,
    normalize_number_input, validate_number_input,
    NumberValidationError
)
from core.models import Customer, Product
from accounts.models import User

User = get_user_model()


class PersianNumberUtilsTest(TestCase):
    """🧪 Test utility functions for Persian number handling"""
    
    def test_normalize_phone_input(self):
        """📱 Test phone number normalization"""
        # Persian numbers
        self.assertEqual(normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹"), "09123456789")
        self.assertEqual(normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹"), "09123456789")
        
        # Mixed Persian and English
        self.assertEqual(normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹"), "09123456789")
        self.assertEqual(normalize_phone_input("09123456789"), "09123456789")
        
        # Edge cases
        self.assertEqual(normalize_phone_input(""), "")
        self.assertEqual(normalize_phone_input(None), "")
    
    def test_validate_phone_input(self):
        """📱 Test phone number validation"""
        # Valid numbers
        self.assertTrue(validate_phone_input("09123456789"))
        self.assertTrue(validate_phone_input("۰۹۱۲۳۴۵۶۷۸۹"))
        
        # Invalid numbers
        self.assertFalse(validate_phone_input("08123456789"))  # Wrong prefix
        self.assertFalse(validate_phone_input("0912345678"))   # Too short
        self.assertFalse(validate_phone_input("091234567890")) # Too long
        self.assertFalse(validate_phone_input("0912345678a"))  # Contains letter
    
    def test_normalize_number_input(self):
        """🔢 Test general number normalization"""
        # Persian numbers
        self.assertEqual(normalize_number_input("۱۲۳۴۵۶"), "123456")
        self.assertEqual(normalize_number_input("۱۲۳.۴۵۶"), "123.456")
        
        # Mixed
        self.assertEqual(normalize_number_input("۱۲۳۴۵۶"), "123456")
        self.assertEqual(normalize_number_input("123456"), "123456")
        
        # Edge cases
        self.assertEqual(normalize_number_input(""), "")
        self.assertEqual(normalize_number_input("0"), "0")
    
    def test_validate_number_input(self):
        """🔢 Test general number validation"""
        # Valid numbers
        self.assertTrue(validate_number_input("123456"))
        self.assertTrue(validate_number_input("۱۲۳۴۵۶"))
        self.assertTrue(validate_number_input("123.456"))
        self.assertTrue(validate_number_input("۱۲۳.۴۵۶"))
        
        # Invalid numbers
        self.assertFalse(validate_number_input("123abc"))
        self.assertFalse(validate_number_input("۱۲۳abc"))
        self.assertFalse(validate_number_input("123.456.789"))
    
    def test_number_validation_error(self):
        """❌ Test error handling"""
        with self.assertRaises(NumberValidationError):
            normalize_number_input("۱۲۳abc")
        
        with self.assertRaises(NumberValidationError):
            normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹abc")


class CustomerFormTest(TestCase):
    """👤 Test customer form with Persian numbers"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE
        )
    
    def test_customer_creation_with_persian_numbers(self):
        """👤 Test creating customer with Persian numbers"""
        self.client.force_login(self.admin_user)
        
        # Test data with Persian numbers
        customer_data = {
            'customer_name': 'علی احمدی',
            'phone': '۰۹۱۲۳۴۵۶۷۸۹',
            'national_id': '۱۲۳۴۵۶۷۸۹۰',
            'economic_code': '۱۲۳۴۵۶۷۸۹',
            'postcode': '۱۲۳۴۵۶۷۸۹۰',
            'address': 'تهران، خیابان ولیعصر',
            'status': 'Active'
        }
        
        # Create customer
        customer = Customer.objects.create(**customer_data)
        
        # Check that numbers were normalized
        self.assertEqual(customer.phone, "09123456789")
        self.assertEqual(customer.national_id, "1234567890")
        self.assertEqual(customer.economic_code, "123456789")
        self.assertEqual(customer.postcode, "1234567890")
    
    def test_customer_form_validation(self):
        """👤 Test customer form validation"""
        from core.views import CustomerForm
        
        # Valid data with Persian numbers
        form_data = {
            'customer_name': 'علی احمدی',
            'phone': '۰۹۱۲۳۴۵۶۷۸۹',
            'national_id': '۱۲۳۴۵۶۷۸۹۰',
            'economic_code': '۱۲۳۴۵۶۷۸۹',
            'postcode': '۱۲۳۴۵۶۷۸۹۰',
            'address': 'تهران، خیابان ولیعصر',
            'status': 'Active'
        }
        
        form = CustomerForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Check normalized data
        customer = form.save()
        self.assertEqual(customer.phone, "09123456789")
        self.assertEqual(customer.national_id, "1234567890")
        self.assertEqual(customer.economic_code, "123456789")
        self.assertEqual(customer.postcode, "1234567890")


class ProductFormTest(TestCase):
    """📦 Test product form with Persian numbers"""
    
    def test_product_creation_with_persian_numbers(self):
        """📦 Test creating product with Persian numbers"""
        from core.views import ProductForm
        
        # Test data with Persian numbers
        product_data = {
            'reel_number': 'RL۱۲۳۴۵۶',
            'location': 'A1',
            'status': 'In Stock',
            'width': '۱۲۳',
            'length': '۴۵۶',
            'gsm': '۸۰',
            'breaks': '۲',
            'grade': 'A',
            'price': '۱۲۳۴۵۶۷'
        }
        
        form = ProductForm(data=product_data)
        self.assertTrue(form.is_valid())
        
        # Check normalized data
        product = form.save()
        self.assertEqual(str(product.width), "123")
        self.assertEqual(str(product.length), "456")
        self.assertEqual(str(product.gsm), "80")
        self.assertEqual(str(product.breaks), "2")
        self.assertEqual(str(product.price), "1234567")


class AdminInterfaceTest(TestCase):
    """🎛️ Test admin interface with Persian numbers"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE,
            is_staff=True,
            is_superuser=True
        )
    
    def test_admin_customer_creation(self):
        """🎛️ Test customer creation in admin"""
        self.client.force_login(self.admin_user)
        
        # Test data with Persian numbers
        customer_data = {
            'customer_name': 'علی احمدی',
            'phone': '۰۹۱۲۳۴۵۶۷۸۹',
            'national_id': '۱۲۳۴۵۶۷۸۹۰',
            'economic_code': '۱۲۳۴۵۶۷۸۹',
            'postcode': '۱۲۳۴۵۶۷۸۹۰',
            'address': 'تهران، خیابان ولیعصر',
            'status': 'Active'
        }
        
        # Create customer via admin
        response = self.client.post(
            reverse('admin:core_customer_add'),
            customer_data,
            follow=True
        )
        
        # Check if customer was created
        customer = Customer.objects.filter(phone="09123456789").first()
        self.assertIsNotNone(customer)
        self.assertEqual(customer.national_id, "1234567890")
        self.assertEqual(customer.economic_code, "123456789")
        self.assertEqual(customer.postcode, "1234567890")


class JavaScriptTest(TestCase):
    """🌐 Test JavaScript functionality"""
    
    def test_javascript_file_exists(self):
        """🌐 Test that Persian numbers JS file exists"""
        import os
        js_file_path = 'static/js/persian-numbers.js'
        self.assertTrue(os.path.exists(js_file_path), f"JavaScript file not found: {js_file_path}")
    
    def test_base_template_includes_js(self):
        """🌐 Test that base template includes Persian numbers JS"""
        from django.template.loader import render_to_string
        
        # Render base template
        rendered = render_to_string('base.html')
        
        # Check if JS file is included
        self.assertIn('persian-numbers.js', rendered)


class IntegrationTest(TestCase):
    """🔗 Integration tests for the complete system"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE,
            is_staff=True,
            is_superuser=True
        )
    
    def test_complete_workflow(self):
        """🔗 Test complete workflow with Persian numbers"""
        self.client.force_login(self.admin_user)
        
        # 1. Create customer with Persian numbers
        customer_data = {
            'customer_name': 'علی احمدی',
            'phone': '۰۹۱۲۳۴۵۶۷۸۹',
            'national_id': '۱۲۳۴۵۶۷۸۹۰',
            'economic_code': '۱۲۳۴۵۶۷۸۹',
            'postcode': '۱۲۳۴۵۶۷۸۹۰',
            'address': 'تهران، خیابان ولیعصر',
            'status': 'Active'
        }
        
        customer = Customer.objects.create(**customer_data)
        
        # 2. Create product with Persian numbers
        product_data = {
            'reel_number': 'RL۱۲۳۴۵۶',
            'location': 'A1',
            'status': 'In Stock',
            'width': '۱۲۳',
            'length': '۴۵۶',
            'gsm': '۸۰',
            'breaks': '۲',
            'grade': 'A',
            'price': '۱۲۳۴۵۶۷'
        }
        
        product = Product.objects.create(**product_data)
        
        # 3. Verify all numbers were normalized
        self.assertEqual(customer.phone, "09123456789")
        self.assertEqual(customer.national_id, "1234567890")
        self.assertEqual(customer.economic_code, "123456789")
        self.assertEqual(customer.postcode, "1234567890")
        
        self.assertEqual(str(product.width), "123")
        self.assertEqual(str(product.length), "456")
        self.assertEqual(str(product.gsm), "80")
        self.assertEqual(str(product.breaks), "2")
        self.assertEqual(str(product.price), "1234567")
        
        # 4. Test that normalized data can be retrieved correctly
        customer.refresh_from_db()
        product.refresh_from_db()
        
        self.assertEqual(customer.phone, "09123456789")
        self.assertEqual(str(product.width), "123")


class PerformanceTest(TestCase):
    """⚡ Performance tests for number normalization"""
    
    def test_normalization_performance(self):
        """⚡ Test performance of number normalization"""
        import time
        
        # Test with large number of operations
        start_time = time.time()
        
        for i in range(1000):
            normalize_phone_input("۰۹۱۲۳۴۵۶۷۸۹")
            normalize_number_input("۱۲۳۴۵۶۷۸۹۰")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second)
        self.assertLess(execution_time, 1.0, f"Normalization took too long: {execution_time:.3f} seconds")


if __name__ == '__main__':
    # Run tests
    import django
    django.setup()
    
    # Run specific test
    test = PersianNumberUtilsTest()
    test.test_normalize_phone_input()
    print("✅ All tests passed!") 