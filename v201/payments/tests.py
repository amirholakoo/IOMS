from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch

from core.models import Order, Customer, Product, OrderItem
from .models import Payment
from .services import ShaparakGateway, PaymentService

User = get_user_model()


class ShaparakMockGatewayTest(TestCase):
    """Test Shaparak mock gateway functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user with unique phone
        self.user = User.objects.create_user(
            username='testuser_shaparak',
            phone='09123456788',  # Different phone number
            password='testpass123'
        )
        
        # Create test customer with unique phone
        self.customer = Customer.objects.create(
            customer_name='Test Customer Shaparak',
            phone='09123456788'  # Same as user
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product Shaparak',
            price=Decimal('100000'),  # 100,000 Toman
            payment_method='Cash'
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            order_number='TEST-ORDER-SHAPARAK-001',
            status='Pending'
        )
        
        # Create order item
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=Decimal('100000'),
            total_price=Decimal('100000'),
            payment_method='Cash'
        )
        
        self.client = Client()
    
    def test_shaparak_mock_gateway_creation(self):
        """Test that Shaparak mock gateway creates payment correctly"""
        # Create payment using Shaparak gateway
        payment = PaymentService.create_payment_from_order(
            order=self.order,
            gateway_name='shaparak',
            user=self.user
        )
        
        # Verify payment was created correctly
        self.assertEqual(payment.gateway, 'shaparak')
        self.assertEqual(payment.amount, Decimal('1000000'))  # 100,000 Toman * 10 = 1,000,000 Rial
        self.assertEqual(payment.status, 'INITIATED')
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.user, self.user)
    
    def test_shaparak_mock_gateway_url_generation(self):
        """Test that Shaparak mock gateway generates correct URL in sandbox mode"""
        # Create payment
        payment = PaymentService.create_payment_from_order(
            order=self.order,
            gateway_name='shaparak',
            user=self.user
        )
        
        # Test payment initiation with mock gateway (sandbox=True)
        callback_url = 'http://testserver/payments/callback/1/'
        result = PaymentService.initiate_payment(
            payment=payment,
            callback_url=callback_url,
            sandbox=True
        )
        
        # Verify mock gateway URL is generated
        self.assertTrue(result['success'])
        self.assertIn('/payments/mock-gateway/', result['payment_url'])
        self.assertIn('gateway=shaparak', result['payment_url'])
        self.assertIn(f'payment_id={payment.id}', result['payment_url'])
        self.assertIn('token=', result['payment_url'])
    
    def test_shaparak_mock_gateway_template_access(self):
        """Test that mock gateway template is accessible"""
        # Create a test payment
        payment = Payment.objects.create(
            order=self.order,
            user=self.user,
            amount=Decimal('1000000'),
            gateway='shaparak',
            tracking_code='TEST123SHAPARAK'
        )
        
        # Test mock gateway view
        url = f'/payments/mock-gateway/?gateway=shaparak&token=test_token&payment_id={payment.id}'
        response = self.client.get(url)
        
        # Should return 200 and contain payment information
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'شبیه‌ساز درگاه پرداخت')
        self.assertContains(response, '🏦 شاپرک')
        self.assertContains(response, payment.tracking_code)
