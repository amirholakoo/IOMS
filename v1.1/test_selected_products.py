#!/usr/bin/env python
"""
🧪 تست عملکرد صفحه محصولات انتخاب‌شده
📋 بررسی تمام قابلیت‌های جدید اضافه شده
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from core.models import Customer, Product, Order, OrderItem
from accounts.models import User

class SelectedProductsTestCase(TestCase):
    """🧪 تست‌های صفحه محصولات انتخاب‌شده"""
    
    def setUp(self):
        """🔧 آماده‌سازی داده‌های تست"""
        # Create test customer
        self.customer = Customer.objects.create(
            customer_name="مشتری تست",
            phone="09123456789",
            status="Active"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            phone="09123456789"
        )
        self.user.customer = self.customer
        self.user.save()
        
        # Create test products
        self.product1 = Product.objects.create(
            reel_number="TEST001",
            width=100,
            gsm=80,
            length=1000,
            grade="A",
            price=100000,
            status="In-stock"
        )
        
        self.product2 = Product.objects.create(
            reel_number="TEST002",
            width=120,
            gsm=90,
            length=800,
            grade="B",
            price=150000,
            status="In-stock"
        )
        
        self.client = Client()
    
    def test_selected_products_page_access(self):
        """🔍 تست دسترسی به صفحه محصولات انتخاب‌شده"""
        # Login
        self.client.login(username="testuser", password="testpass123")
        
        # Set session data
        session = self.client.session
        session['selected_products'] = [
            {'product_id': self.product1.id, 'quantity': 2},
            {'product_id': self.product2.id, 'quantity': 1}
        ]
        session.save()
        
        # Access page
        response = self.client.get(reverse('core:selected_products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "محصولات انتخاب‌شده")
        self.assertContains(response, "TEST001")
        self.assertContains(response, "TEST002")
    
    def test_process_order_cash_only(self):
        """💰 تست پردازش سفارش نقدی"""
        self.client.login(username="testuser", password="testpass123")
        
        # Submit order with cash items
        data = {
            f'product_id_{self.product1.id}': self.product1.id,
            f'quantity_{self.product1.id}': 2,
            f'payment_method_{self.product1.id}': 'Cash',
        }
        
        response = self.client.post(reverse('core:process_order'), data)
        self.assertEqual(response.status_code, 200)
        
        # Check response
        import json
        result = json.loads(response.content)
        self.assertTrue(result['success'])
        self.assertIn('سفارش نقدی', result['message'])
        
        # Check order created
        orders = Order.objects.filter(customer=self.customer)
        self.assertEqual(orders.count(), 1)
        order = orders.first()
        self.assertEqual(order.payment_method, 'Cash')
        self.assertEqual(order.status, 'Pending')
        
        # Check order items
        items = order.order_items.all()
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.payment_method, 'Cash')
    
    def test_process_order_terms_only(self):
        """📅 تست پردازش سفارش قسطی"""
        self.client.login(username="testuser", password="testpass123")
        
        # Submit order with terms items
        data = {
            f'product_id_{self.product2.id}': self.product2.id,
            f'quantity_{self.product2.id}': 1,
            f'payment_method_{self.product2.id}': 'Terms',
        }
        
        response = self.client.post(reverse('core:process_order'), data)
        self.assertEqual(response.status_code, 200)
        
        # Check response
        import json
        result = json.loads(response.content)
        self.assertTrue(result['success'])
        self.assertIn('سفارش قسطی', result['message'])
        
        # Check order created
        orders = Order.objects.filter(customer=self.customer)
        self.assertEqual(orders.count(), 1)
        order = orders.first()
        self.assertEqual(order.payment_method, 'Terms')
        self.assertEqual(order.status, 'Pending')
    
    def test_process_order_mixed_payment(self):
        """🔄 تست پردازش سفارش با پرداخت ترکیبی"""
        self.client.login(username="testuser", password="testpass123")
        
        # Submit order with mixed payment methods
        data = {
            f'product_id_{self.product1.id}': self.product1.id,
            f'quantity_{self.product1.id}': 2,
            f'payment_method_{self.product1.id}': 'Cash',
            f'product_id_{self.product2.id}': self.product2.id,
            f'quantity_{self.product2.id}': 1,
            f'payment_method_{self.product2.id}': 'Terms',
        }
        
        response = self.client.post(reverse('core:process_order'), data)
        self.assertEqual(response.status_code, 200)
        
        # Check response
        import json
        result = json.loads(response.content)
        self.assertTrue(result['success'])
        self.assertIn('سفارش نقدی', result['message'])
        self.assertIn('سفارش قسطی', result['message'])
        
        # Check orders created (should be 2 separate orders)
        orders = Order.objects.filter(customer=self.customer)
        self.assertEqual(orders.count(), 2)
        
        cash_order = orders.filter(payment_method='Cash').first()
        terms_order = orders.filter(payment_method='Terms').first()
        
        self.assertIsNotNone(cash_order)
        self.assertIsNotNone(terms_order)
    
    def test_inactive_customer_restriction(self):
        """🚫 تست محدودیت مشتری غیرفعال"""
        # Set customer as inactive
        self.customer.status = 'Inactive'
        self.customer.save()
        
        self.client.login(username="testuser", password="testpass123")
        
        # Try to submit order
        data = {
            f'product_id_{self.product1.id}': self.product1.id,
            f'quantity_{self.product1.id}': 1,
            f'payment_method_{self.product1.id}': 'Cash',
        }
        
        response = self.client.post(reverse('core:process_order'), data)
        self.assertEqual(response.status_code, 200)
        
        # Should be allowed for inactive customers
        import json
        result = json.loads(response.content)
        self.assertTrue(result['success'])
    
    def test_blocked_customer_restriction(self):
        """🚫 تست محدودیت مشتری مسدود"""
        # Set customer as blocked
        self.customer.status = 'Blocked'
        self.customer.save()
        
        self.client.login(username="testuser", password="testpass123")
        
        # Try to submit order
        data = {
            f'product_id_{self.product1.id}': self.product1.id,
            f'quantity_{self.product1.id}': 1,
            f'payment_method_{self.product1.id}': 'Cash',
        }
        
        response = self.client.post(reverse('core:process_order'), data)
        self.assertEqual(response.status_code, 200)
        
        # Should be blocked
        import json
        result = json.loads(response.content)
        self.assertFalse(result['success'])
        self.assertIn('فعال نیست', result['error'])

if __name__ == '__main__':
    print("🧪 شروع تست‌های صفحه محصولات انتخاب‌شده...")
    
    # Run tests
    import unittest
    unittest.main(argv=[''], exit=False, verbosity=2) 