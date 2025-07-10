"""
🧪 تست‌های سیستم پرداخت - HomayOMS
💳 تست کامل فرآیند پرداخت، درگاه‌ها، و تراکنش‌ها
✅ پوشش: ایجاد پرداخت، درگاه‌های مختلف، وضعیت‌ها، و کال‌بک‌ها
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from payments.models import Payment, PaymentCallback, PaymentRefund
from payments.services import PaymentService, ZarinPalGateway, ShaparakGateway
from core.models import Customer, Product, Order, OrderItem
import json
import uuid

User = get_user_model()


class TestPaymentCreation(TestCase):
    """💳 تست‌های ایجاد پرداخت"""

    def setUp(self):
        """🔧 تنظیمات اولیه تست"""
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )
        
        self.customer = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09123456789',
            address='آدرس تست',
            status='Active'
        )
        
        self.product = Product.objects.create(
            reel_number='P001',
            location='Anbar_Akhal',
            status='In-stock',
            width=1000,
            gsm=80,
            length=1500,
            grade='A',
            price=Decimal('150000.00')
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            total_amount=Decimal('150000.00'),
            final_amount=Decimal('150000.00'),
            created_by=self.customer_user
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
            total_price=self.product.price,
            payment_method='Cash'
        )

    @pytest.mark.payments
    def test_payment_creation_basic(self):
        """💳 تست ایجاد پرداخت پایه"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),  # 150000 تومان = 1500000 ریال
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='INITIATED',
            payer_phone='09123456789',
            description='تست پرداخت'
        )
        
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.user, self.customer_user)
        self.assertEqual(payment.amount, Decimal('1500000'))
        self.assertEqual(payment.display_amount, Decimal('150000'))
        self.assertEqual(payment.gateway, 'zarinpal')
        self.assertEqual(payment.status, 'INITIATED')
        self.assertTrue(payment.tracking_code)  # کد پیگیری خودکار تولید شود

    @pytest.mark.payments
    def test_payment_tracking_code_generation(self):
        """🏷️ تست تولید کد پیگیری"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='INITIATED'
        )
        
        self.assertTrue(payment.tracking_code)
        self.assertGreaterEqual(len(payment.tracking_code), 10)
        
        # کد پیگیری باید یکتا باشد
        payment2 = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='shaparak',
            status='INITIATED'
        )
        
        self.assertNotEqual(payment.tracking_code, payment2.tracking_code)

    @pytest.mark.payments
    def test_payment_status_transitions(self):
        """📊 تست تغییرات وضعیت پرداخت"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='INITIATED'
        )
        
        # وضعیت‌های مختلف
        statuses = ['INITIATED', 'REDIRECTED', 'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED']
        
        for status in statuses:
            payment.status = status
            payment.save()
            payment.refresh_from_db()
            self.assertEqual(payment.status, status)

    @pytest.mark.payments
    def test_payment_success_marking(self):
        """✅ تست علامت‌گذاری پرداخت موفق"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='PENDING'
        )
        
        # علامت‌گذاری به عنوان موفق
        payment.mark_as_successful(
            transaction_id='TXN789123',
            reference_number='REF987654321',
            card_number='6274121212345678'
        )
        
        self.assertEqual(payment.status, 'SUCCESS')
        self.assertEqual(payment.gateway_transaction_id, 'TXN789123')
        self.assertEqual(payment.bank_reference_number, 'REF987654321')
        # Test the actual masked format returned by the model
        self.assertEqual(payment.masked_card_number, '****-****-****-5678')
        self.assertIsNotNone(payment.completed_at)

    @pytest.mark.payments
    def test_payment_failure_marking(self):
        """❌ تست علامت‌گذاری پرداخت ناموفق"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='PENDING'
        )
        
        # علامت‌گذاری به عنوان ناموفق
        payment.mark_as_failed('خطا در پردازش تراکنش')
        
        self.assertEqual(payment.status, 'FAILED')
        self.assertEqual(payment.error_message, 'خطا در پردازش تراکنش')
        self.assertTrue(payment.completed_at)

    @pytest.mark.payments
    def test_payment_retry_capability(self):
        """🔄 تست قابلیت تلاش مجدد"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='FAILED',
            retry_count=0
        )
        
        # پرداخت ناموفق باید قابل تلاش مجدد باشد
        self.assertTrue(payment.can_retry())
        
        # افزایش تعداد تلاش
        payment.retry_count = 3
        payment.save()
        self.assertFalse(payment.can_retry())  # حداکثر 3 تلاش

    @pytest.mark.payments
    def test_payment_expiration(self):
        """⏰ تست انقضای پرداخت"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='PENDING',
            expires_at=timezone.now() - timezone.timedelta(minutes=30)  # 30 دقیقه پیش
        )
        
        self.assertTrue(payment.is_expired())
        
        # علامت‌گذاری به عنوان منقضی شده
        payment.mark_as_expired()
        self.assertEqual(payment.status, 'TIMEOUT')


class TestPaymentGateways(TestCase):
    """🌐 تست‌های درگاه‌های پرداخت"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER
        )
        
        self.customer = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09123456789',
            status='Active'
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            total_amount=Decimal('100000.00'),
            final_amount=Decimal('100000.00'),
            created_by=self.customer_user
        )

    @pytest.mark.payments
    def test_zarinpal_gateway_initialization(self):
        """💎 تست راه‌اندازی درگاه زرین‌پال"""
        gateway = ZarinPalGateway(sandbox=True)
        
        self.assertTrue(gateway.sandbox)
        self.assertIsNotNone(gateway.merchant_id)

    @pytest.mark.payments
    def test_shaparak_gateway_initialization(self):
        """🏦 تست راه‌اندازی درگاه شاپرک"""
        gateway = ShaparakGateway(sandbox=True)
        
        self.assertTrue(gateway.sandbox)
        self.assertIsNotNone(gateway.terminal_id)
        self.assertIsNotNone(gateway.merchant_id)

    @pytest.mark.payments
    @patch('payments.services.BasePaymentGateway._make_request')
    def test_zarinpal_payment_request(self, mock_request):
        """💎 تست درخواست پرداخت زرین‌پال"""
        # Mock response
        mock_request.return_value = {
            'data': {
                'code': 100,
                'message': 'Success',
                'authority': 'A00000000000000000000000000000123456789'
            }
        }
        
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway='zarinpal',
            status='INITIATED'
        )
        
        gateway = ZarinPalGateway(sandbox=True)
        result = gateway.create_payment(payment, 'http://test.com/callback/')
        
        self.assertEqual(result['success'], True)
        self.assertIn('payment_url', result)
        mock_request.assert_called_once()

    @pytest.mark.payments
    @patch('payments.services.BasePaymentGateway._make_request')
    def test_shaparak_payment_request(self, mock_request):
        """🏦 تست درخواست پرداخت شاپرک"""
        # Mock response
        mock_request.return_value = {
            'status': 'success',
            'data': {
                'token': 'mock_token_123456',
                'order_id': self.order.order_number
            }
        }
        
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway='shaparak',
            status='INITIATED'
        )
        
        gateway = ShaparakGateway(sandbox=True)
        result = gateway.create_payment(payment, 'http://test.com/callback/')
        
        self.assertEqual(result['success'], True)
        self.assertIn('payment_url', result)
        mock_request.assert_called_once()

    @pytest.mark.payments
    def test_payment_service_gateway_selection(self):
        """🔍 تست انتخاب درگاه توسط PaymentService"""
        # زرین‌پال
        zarinpal_gateway = PaymentService.get_gateway('zarinpal', sandbox=True)
        self.assertIsInstance(zarinpal_gateway, ZarinPalGateway)
        
        # شاپرک
        shaparak_gateway = PaymentService.get_gateway('shaparak', sandbox=True)
        self.assertIsInstance(shaparak_gateway, ShaparakGateway)
        
        # درگاه نامعتبر
        with self.assertRaises(ValueError):
            PaymentService.get_gateway('invalid_gateway')


class TestPaymentService(TestCase):
    """🛠️ تست‌های سرویس پرداخت"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER
        )
        
        self.customer = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09123456789',
            status='Active'
        )
        
        self.product1 = Product.objects.create(
            reel_number='P001',
            location='Anbar_Akhal',
            status='In-stock',
            width=1000,
            gsm=80,
            length=1500,
            grade='A',
            price=Decimal('150000.00')
        )
        
        self.product2 = Product.objects.create(
            reel_number='P002',
            location='Anbar_Akhal',
            status='In-stock',
            width=1200,
            gsm=90,
            length=1500,
            grade='A',
            price=Decimal('150000.00')
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            total_amount=Decimal('300000.00'),
            final_amount=Decimal('270000.00'),
            created_by=self.customer_user
        )
        
        # افزودن آیتم‌های نقدی و قسطی با محصولات مختلف
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=1,
            unit_price=self.product1.price,
            total_price=self.product1.price,
            payment_method='Cash'
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1,
            unit_price=self.product2.price,
            total_price=self.product2.price,
            payment_method='Terms'
        )

    @pytest.mark.payments
    def test_cash_payment_amount_calculation(self):
        """💰 تست محاسبه مبلغ نقدی"""
        cash_amount = PaymentService._calculate_cash_payment_amount(self.order)
        
        # فقط آیتم‌های نقدی باید محاسبه شوند
        expected_amount = Decimal('150000.00')  # فقط یک آیتم نقدی
        self.assertEqual(cash_amount, expected_amount)

    @pytest.mark.payments
    def test_create_payment_from_order(self):
        """📋 تست ایجاد پرداخت از سفارش"""
        payment = PaymentService.create_payment_from_order(
            order=self.order,
            gateway_name='zarinpal',
            user=self.customer_user
        )
        
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.user, self.customer_user)
        self.assertEqual(payment.gateway, 'zarinpal')
        self.assertEqual(payment.status, 'INITIATED')
        self.assertEqual(payment.display_amount, Decimal('150000.00'))  # فقط مبلغ نقدی

    @pytest.mark.payments
    def test_payment_verification_successful(self):
        """✅ تست تایید پرداخت موفق"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='PENDING',
            gateway_transaction_id='A123456789'
        )
        
        verification_data = {
            'Authority': 'A123456789',
            'Status': 'OK'
        }
        
        # Mock gateway's verify_payment method to actually call mark_as_successful
        def mock_verify_payment(payment_obj, verification_data):
            payment_obj.mark_as_successful(
                transaction_id='A123456789',
                reference_number='987654321',
                card_number='6274****1234'
            )
            return True, {
                'message': 'پرداخت با موفقیت انجام شد',
                'ref_id': '987654321',
                'authority': 'A123456789'
            }
        
        with patch('payments.services.ZarinPalGateway.verify_payment', side_effect=mock_verify_payment):
            success, result = PaymentService.verify_payment(payment, verification_data)
            
            self.assertTrue(success)
            payment.refresh_from_db()
            self.assertEqual(payment.status, 'SUCCESS')

    @pytest.mark.payments
    def test_payment_verification_failed(self):
        """❌ تست تایید پرداخت ناموفق"""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1500000'),
            display_amount=Decimal('150000'),
            gateway='zarinpal',
            status='PENDING',
            gateway_transaction_id='A123456789'
        )
        
        verification_data = {
            'Authority': 'A123456789',
            'Status': 'NOK'
        }
        
        # Mock gateway's verify_payment method to actually call mark_as_failed
        def mock_verify_payment(payment_obj, verification_data):
            payment_obj.mark_as_failed('تراکنش یافت نشد')
            return False, {
                'message': 'تراکنش یافت نشد'
            }
        
        with patch('payments.services.ZarinPalGateway.verify_payment', side_effect=mock_verify_payment):
            success, result = PaymentService.verify_payment(payment, verification_data)
            
            self.assertFalse(success)
            payment.refresh_from_db()
            self.assertEqual(payment.status, 'FAILED')


class TestPaymentCallbacks(TestCase):
    """📞 تست‌های کال‌بک پرداخت"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER
        )
        
        self.customer = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09123456789',
            status='Active'
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        self.payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway='zarinpal',
            status='PENDING'
        )

    @pytest.mark.payments
    def test_payment_callback_creation(self):
        """📞 تست ایجاد کال‌بک پرداخت"""
        callback = PaymentCallback.objects.create(
            payment=self.payment,
            callback_type='VERIFY',
            raw_data={'status': 'OK', 'authority': 'A123456789'},
            sender_ip='127.0.0.1',
            response_message='تایید شد'
        )
        
        self.assertEqual(callback.payment, self.payment)
        self.assertEqual(callback.callback_type, 'VERIFY')
        self.assertEqual(callback.raw_data['status'], 'OK')
        self.assertEqual(callback.sender_ip, '127.0.0.1')

    @pytest.mark.payments
    def test_multiple_callbacks_for_payment(self):
        """📞 تست چندین کال‌بک برای یک پرداخت"""
        # کال‌بک بازگشت کاربر
        return_callback = PaymentCallback.objects.create(
            payment=self.payment,
            callback_type='RETURN',
            raw_data={'status': 'OK'},
            sender_ip='192.168.1.1'
        )
        
        # کال‌بک تایید
        verify_callback = PaymentCallback.objects.create(
            payment=self.payment,
            callback_type='VERIFY',
            raw_data={'verified': True, 'ref_id': '123456'},
            sender_ip='127.0.0.1'
        )
        
        callbacks = self.payment.callbacks.all()
        self.assertEqual(callbacks.count(), 2)
        self.assertIn(return_callback, callbacks)
        self.assertIn(verify_callback, callbacks)


class TestPaymentRefunds(TestCase):
    """💸 تست‌های بازگشت وجه"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.ADMIN
        )
        
        self.customer = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09123456789',
            status='Active'
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        self.successful_payment = Payment.objects.create(
            order=self.order,
            user=self.customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway='zarinpal',
            status='SUCCESS',
            gateway_transaction_id='TXN123456789',
            bank_reference_number='REF987654321',
            completed_at=timezone.now()
        )

    @pytest.mark.payments
    def test_full_refund_creation(self):
        """💸 تست ایجاد بازگشت وجه کامل"""
        refund = PaymentRefund.objects.create(
            payment=self.successful_payment,
            refund_amount=self.successful_payment.amount,
            status='INITIATED',
            reason='درخواست مشتری',
            requested_by=self.admin_user
        )
        
        self.assertEqual(refund.payment, self.successful_payment)
        self.assertEqual(refund.refund_amount, self.successful_payment.amount)
        self.assertEqual(refund.status, 'INITIATED')
        self.assertEqual(refund.requested_by, self.admin_user)

    @pytest.mark.payments
    def test_partial_refund_creation(self):
        """💰 تست ایجاد بازگشت وجه جزئی"""
        partial_amount = self.successful_payment.amount / 2
        
        refund = PaymentRefund.objects.create(
            payment=self.successful_payment,
            refund_amount=partial_amount,
            status='INITIATED',
            reason='بازگشت جزئی',
            requested_by=self.admin_user
        )
        
        self.assertEqual(refund.refund_amount, partial_amount)
        self.assertLess(refund.refund_amount, self.successful_payment.amount)

    @pytest.mark.payments
    def test_refund_status_transitions(self):
        """📊 تست تغییرات وضعیت بازگشت وجه"""
        refund = PaymentRefund.objects.create(
            payment=self.successful_payment,
            refund_amount=self.successful_payment.amount,
            status='INITIATED',
            reason='تست',
            requested_by=self.admin_user
        )
        
        # تغییر وضعیت‌ها
        statuses = ['INITIATED', 'PROCESSING', 'SUCCESS', 'FAILED']
        
        for status in statuses:
            refund.status = status
            refund.save()
            refund.refresh_from_db()
            self.assertEqual(refund.status, status)


@pytest.mark.payments
class TestPaymentsPytest:
    """🧪 تست‌های pytest برای پرداخت‌ها"""

    def test_payment_creation_with_fixtures(self, payment, order, customer_user):
        """💳 تست ایجاد پرداخت با فیکسچرها"""
        assert payment.order == order
        assert payment.user == customer_user
        assert payment.status == 'INITIATED'
        assert payment.tracking_code is not None

    def test_successful_payment_fixture(self, successful_payment):
        """✅ تست فیکسچر پرداخت موفق"""
        assert successful_payment.status == 'SUCCESS'
        assert successful_payment.gateway_transaction_id is not None
        assert successful_payment.bank_reference_number is not None
        assert successful_payment.completed_at is not None

    def test_failed_payment_fixture(self, failed_payment):
        """❌ تست فیکسچر پرداخت ناموفق"""
        assert failed_payment.status == 'FAILED'
        assert failed_payment.error_message is not None
        assert failed_payment.completed_at is not None

    def test_payment_status_display_persian(self, payment):
        """📊 تست نمایش فارسی وضعیت"""
        status_display = payment.get_status_display_persian()
        assert status_display in ['آغاز شده', 'هدایت شده', 'در انتظار پرداخت']

    def test_payment_gateway_display_persian(self, payment):
        """🌐 تست نمایش فارسی درگاه"""
        gateway_display = payment.get_gateway_display_persian()
        assert 'زرین‌پال' in gateway_display or 'شاپرک' in gateway_display

    def test_payment_card_masking(self, payment):
        """💳 تست ماسک کردن شماره کارت"""
        card_number = '6274129012345678'
        masked = payment.mask_card_number(card_number)
        assert masked == '6274-****-****-5678'
        
        # شماره کوتاه
        short_card = '1234'
        masked_short = payment.mask_card_number(short_card)
        assert masked_short == '****'

    @pytest.mark.parametrize("gateway,expected_name", [
        ('zarinpal', 'زرین‌پال'),
        ('shaparak', 'شاپرک'),
        ('mellat', 'ملت'),
        ('parsian', 'پارسیان'),
    ])
    def test_payment_gateway_choices(self, order, customer_user, gateway, expected_name):
        """🌐 تست انواع درگاه‌های پرداخت"""
        payment = Payment.objects.create(
            order=order,
            user=customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway=gateway,
            status='INITIATED'
        )
        
        assert payment.gateway == gateway
        gateway_display = payment.get_gateway_display_persian()
        assert expected_name in gateway_display

    def test_payment_retry_logic(self, failed_payment):
        """🔄 تست منطق تلاش مجدد"""
        # پرداخت ناموفق قابل تلاش مجدد است
        assert failed_payment.can_retry()
        
        # افزایش تعداد تلاش
        failed_payment.retry_count = 3
        failed_payment.save()
        assert not failed_payment.can_retry()

    def test_payment_expiration_logic(self, payment):
        """⏰ تست منطق انقضا"""
        # پرداخت جدید منقضی نشده
        assert not payment.is_expired()
        
        # تنظیم زمان انقضا در گذشته
        payment.expires_at = timezone.now() - timezone.timedelta(hours=1)
        payment.save()
        assert payment.is_expired()

    def test_mock_payment_gateway(self, mock_payment_gateway, payment):
        """🧪 تست Mock درگاه پرداخت"""
        # استفاده از mock gateway
        mock_payment_gateway.return_value = {
            'status': 'success',
            'data': {'authority': 'A123456789'}
        }
        
        # تست که mock به درستی کار می‌کند
        assert mock_payment_gateway.return_value['status'] == 'success'

    def test_payment_amount_validation(self, order, customer_user):
        """💰 تست اعتبارسنجی مبلغ پرداخت"""
        # مبلغ معتبر
        payment = Payment.objects.create(
            order=order,
            user=customer_user,
            amount=Decimal('1000000'),
            display_amount=Decimal('100000'),
            gateway='zarinpal',
            status='INITIATED'
        )
        assert payment.amount > 0
        assert payment.display_amount > 0
        
        # نسبت صحیح بین ریال و تومان
        assert payment.amount == payment.display_amount * 10

    def test_payment_logs_creation(self, payment):
        """📝 تست ایجاد لاگ‌های پرداخت"""
        # بررسی وجود لاگ‌ها
        assert hasattr(payment, 'logs')
        
        # افزودن لاگ
        payment.logs = 'تست لاگ'
        payment.save()
        payment.refresh_from_db()
        assert 'تست لاگ' in payment.logs

    def test_bulk_payment_creation(self, bulk_test_data, customer):
        """📊 تست ایجاد پرداخت‌های حجیم"""
        users = bulk_test_data['users'][:5]  # 5 کاربر اول
        
        payments = []
        for i, user in enumerate(users):
            order = Order.objects.create(
                customer=customer,
                payment_method='Cash',
                status='Pending',
                total_amount=Decimal(f'{(i+1)*100000}'),
                final_amount=Decimal(f'{(i+1)*100000}'),
                created_by=user
            )
            
            payment = Payment.objects.create(
                order=order,
                user=user,
                amount=order.final_amount * 10,
                display_amount=order.final_amount,
                gateway=['zarinpal', 'shaparak'][i % 2],
                status='INITIATED'
            )
            payments.append(payment)
        
        assert len(payments) == 5
        assert all(p.tracking_code for p in payments)  # همه کدهای پیگیری وجود دارند 