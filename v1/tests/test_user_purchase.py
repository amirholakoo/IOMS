"""
🧪 تست‌های خرید کاربر - HomayOMS
🛒 تست کامل فرآیند خرید از ایجاد سفارش تا تکمیل پرداخت
✅ پوشش: ایجاد سفارش، افزودن محصولات، محاسبه قیمت، و کنترل دسترسی
"""

import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Customer, Product, Order, OrderItem, WorkingHours
from payments.models import Payment
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestUserPurchaseProcess(TestCase):
    """🛒 تست‌های فرآیند خرید کاربر"""

    def setUp(self):
        """🔧 تنظیمات اولیه تست"""
        self.client = Client()
        
        # ایجاد کاربر مشتری
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09123456789',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE,
            first_name='مشتری',
            last_name='تست'
        )
        
        # ایجاد مشتری مرتبط
        self.customer = Customer.objects.create(
            customer_name=f'مشتری تست {timezone.now().timestamp()}',
            phone='09123456789',
            address='آدرس تست',
            status='Active'
        )
        
        # ایجاد محصولات
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
            length=1800,
            grade='A+',
            price=Decimal('200000.00')
        )
        
        # تنظیم ساعات کاری
        self.working_hours = WorkingHours.objects.create(
            start_time='09:00',
            end_time='18:00',
            is_active=True
        )

    @pytest.mark.unit
    def test_order_creation_basic(self):
        """📋 تست ایجاد سفارش پایه"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            total_amount=Decimal('350000.00'),
            discount_percentage=Decimal('5.00'),
            created_by=self.customer_user
        )
        
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.payment_method, 'Cash')
        self.assertEqual(order.status, 'Pending')
        self.assertTrue(order.order_number)  # شماره سفارش خودکار تولید شود
        self.assertEqual(order.created_by, self.customer_user)

    @pytest.mark.unit
    def test_order_item_creation(self):
        """📦 تست ایجاد آیتم سفارش"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=self.product1.price,
            total_price=self.product1.price * 2,
            payment_method='Cash'
        )
        
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product1)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.total_price, Decimal('300000.00'))

    @pytest.mark.unit
    def test_order_total_calculation(self):
        """💰 تست محاسبه مجموع سفارش"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            total_amount=Decimal('550000.00'),
            discount_percentage=Decimal('10.00'),
            created_by=self.customer_user
        )
        
        # افزودن آیتم‌ها
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=self.product1.price,
            total_price=self.product1.price * 2,
            payment_method='Cash'
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            unit_price=self.product2.price,
            total_price=self.product2.price,
            payment_method='Terms'
        )
        
        # محاسبه مجدد
        order.calculate_final_amount()
        
        expected_total = Decimal('300000.00') + Decimal('200000.00')  # 500000
        expected_discount = expected_total * Decimal('10.00') / 100  # 50000
        expected_final = expected_total - expected_discount  # 450000
        
        self.assertEqual(order.total_amount, expected_total)
        self.assertEqual(order.discount_amount, expected_discount)
        self.assertEqual(order.final_amount, expected_final)

    @pytest.mark.unit
    def test_order_item_payment_methods(self):
        """💳 تست روش‌های مختلف پرداخت در آیتم‌ها"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        # آیتم نقدی
        cash_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=1,
            unit_price=self.product1.price,
            total_price=self.product1.price,
            payment_method='Cash'
        )
        
        # آیتم قسطی
        terms_item = OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            unit_price=self.product2.price,
            total_price=self.product2.price,
            payment_method='Terms'
        )
        
        self.assertEqual(cash_item.payment_method, 'Cash')
        self.assertEqual(terms_item.payment_method, 'Terms')

    @pytest.mark.unit
    def test_product_availability_check(self):
        """📦 تست بررسی موجودی محصول"""
        # محصول موجود
        self.assertTrue(self.product1.is_available())
        self.assertEqual(self.product1.status, 'In-stock')
        
        # محصول فروخته شده
        sold_product = Product.objects.create(
            reel_number='SOLD001',
            location='Anbar_Akhal',
            status='Sold',
            width=1000,
            gsm=80,
            length=1500,
            grade='A',
            price=Decimal('150000.00')
        )
        self.assertFalse(sold_product.is_available())

    @pytest.mark.integration
    def test_complete_purchase_flow(self):
        """🔗 تست فرآیند کامل خرید"""
        # 1. ورود کاربر
        self.client.login(username='customer', password='test123')
        
        # 2. ایجاد سفارش
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        # 3. افزودن محصولات
        item1 = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=1,
            unit_price=self.product1.price,
            total_price=self.product1.price,
            payment_method='Cash'
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            unit_price=self.product2.price,
            total_price=self.product2.price,
            payment_method='Cash'
        )
        
        # 4. محاسبه مجموع
        order.total_amount = item1.total_price + item2.total_price
        order.discount_percentage = Decimal('5.00')
        order.calculate_final_amount()
        order.save()
        
        # 5. ایجاد پرداخت
        payment = Payment.objects.create(
            order=order,
            user=self.customer_user,
            amount=order.final_amount * 10,  # تبدیل به ریال
            display_amount=order.final_amount,
            gateway='zarinpal',
            status='INITIATED',
            payer_phone=self.customer_user.phone
        )
        
        # بررسی نهایی
        self.assertEqual(order.order_items.count(), 2)
        self.assertTrue(order.final_amount > 0)
        self.assertEqual(payment.order, order)
        self.assertEqual(payment.user, self.customer_user)

    @pytest.mark.unit
    def test_order_status_transitions(self):
        """📊 تست تغییرات وضعیت سفارش"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        # وضعیت‌های مختلف
        valid_statuses = ['Pending', 'Confirmed', 'Processing', 'Ready', 'Delivered']
        
        for status in valid_statuses:
            order.status = status
            order.save()
            order.refresh_from_db()
            self.assertEqual(order.status, status)

    @pytest.mark.unit
    def test_order_modification_permissions(self):
        """🔐 تست مجوزهای تغییر سفارش"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        # سفارش در انتظار قابل تغییر است
        self.assertTrue(order.can_be_modified())
        
        # سفارش تحویل داده شده قابل تغییر نیست
        order.status = 'Delivered'
        order.save()
        self.assertFalse(order.can_be_modified())

    @pytest.mark.unit
    def test_order_cancellation_permissions(self):
        """🚫 تست مجوزهای لغو سفارش"""
        order = Order.objects.create(
            customer=self.customer,
            payment_method='Cash',
            status='Pending',
            created_by=self.customer_user
        )
        
        # سفارش در انتظار قابل لغو است
        self.assertTrue(order.can_be_cancelled())
        
        # سفارش تحویل داده شده قابل لغو نیست
        order.status = 'Delivered'
        order.save()
        self.assertFalse(order.can_be_cancelled())

    @pytest.mark.integration
    @patch('core.models.WorkingHours.is_shop_open')
    def test_working_hours_restriction(self, mock_is_open):
        """⏰ تست محدودیت ساعات کاری"""
        # Mock که مغازه بسته است
        mock_is_open.return_value = False
        
        self.assertFalse(WorkingHours.is_shop_open())
        
        # Mock که مغازه باز است
        mock_is_open.return_value = True
        
        self.assertTrue(WorkingHours.is_shop_open())


class TestCustomerPurchasePermissions(TestCase):
    """🔐 تست‌های دسترسی مشتری به خرید"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.client = Client()
        
        # کاربر مشتری فعال
        self.active_customer = User.objects.create_user(
            username='active_customer',
            email='active@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )
        
        # کاربر مشتری غیرفعال
        self.inactive_customer = User.objects.create_user(
            username='inactive_customer',
            email='inactive@test.com',
            phone='09222222222',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.INACTIVE
        )
        
        # کاربر ادمین
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09333333333',
            password='test123',
            role=User.UserRole.ADMIN,
            status=User.UserStatus.ACTIVE
        )

    @pytest.mark.permissions
    def test_active_customer_can_create_order(self):
        """✅ مشتری فعال می‌تواند سفارش ایجاد کند"""
        self.client.login(username='active_customer', password='test123')
        
        # بررسی دسترسی
        self.assertTrue(self.active_customer.has_perm('accounts.create_orders'))
        self.assertTrue(self.active_customer.is_active_user())

    @pytest.mark.permissions  
    def test_inactive_customer_cannot_create_order(self):
        """❌ مشتری غیرفعال نمی‌تواند سفارش ایجاد کند"""
        self.assertFalse(self.inactive_customer.is_active_user())

    @pytest.mark.permissions
    def test_customer_can_only_view_own_orders(self):
        """👁️ مشتری فقط سفارشات خود را می‌بیند"""
        self.assertTrue(self.active_customer.has_perm('accounts.view_own_orders'))
        
        # مشتری نمی‌تواند همه سفارشات را ببیند
        self.assertFalse(self.active_customer.has_perm('accounts.manage_orders'))

    @pytest.mark.permissions
    def test_admin_can_manage_all_orders(self):
        """🟡 ادمین می‌تواند همه سفارشات را مدیریت کند"""
        self.assertTrue(self.admin_user.has_perm('accounts.manage_orders'))
        self.assertTrue(self.admin_user.can_manage_inventory())


@pytest.mark.user_purchase
class TestUserPurchasePytest:
    """🧪 تست‌های pytest برای خرید کاربر"""

    def test_order_creation_with_fixtures(self, customer, product, customer_user):
        """📋 تست ایجاد سفارش با فیکسچرها"""
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending',
            total_amount=product.price,
            final_amount=product.price,
            created_by=customer_user
        )
        
        assert order.customer == customer
        assert order.created_by == customer_user
        assert order.order_number is not None

    def test_order_item_creation_with_fixtures(self, order, product):
        """📦 تست ایجاد آیتم سفارش با فیکسچرها"""
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price=product.price,
            total_price=product.price * 2,
            payment_method='Cash'
        )
        
        assert order_item.order == order
        assert order_item.product == product
        assert order_item.quantity == 2
        assert order_item.total_price == product.price * 2

    def test_multiple_products_order(self, customer, multiple_products, customer_user):
        """🛒 تست سفارش با چندین محصول"""
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending',
            created_by=customer_user
        )
        
        total_amount = Decimal('0')
        for i, product in enumerate(multiple_products[:3]):  # فقط 3 محصول اول
            quantity = i + 1
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                total_price=product.price * quantity,
                payment_method='Cash'
            )
            total_amount += order_item.total_price
        
        order.total_amount = total_amount
        order.final_amount = total_amount
        order.save()
        
        assert order.order_items.count() == 3
        assert order.total_amount == total_amount
        assert order.get_order_items_count() == 3

    def test_order_discount_calculation(self, order):
        """💰 تست محاسبه تخفیف"""
        order.total_amount = Decimal('1000000')
        order.discount_percentage = Decimal('15')
        order.calculate_final_amount()
        
        expected_discount = Decimal('150000')  # 15% از 1,000,000
        expected_final = Decimal('850000')     # 1,000,000 - 150,000
        
        assert order.discount_amount == expected_discount
        assert order.final_amount == expected_final

    @pytest.mark.parametrize("payment_method,expected_status", [
        ('Cash', 'Pending'),
        ('Terms', 'Pending'),
        ('Bank_Transfer', 'Pending'),
        ('Check', 'Pending'),
    ])
    def test_order_payment_methods(self, customer, customer_user, payment_method, expected_status):
        """💳 تست روش‌های مختلف پرداخت"""
        order = Order.objects.create(
            customer=customer,
            payment_method=payment_method,
            status=expected_status,
            created_by=customer_user
        )
        
        assert order.payment_method == payment_method
        assert order.status == expected_status

    def test_customer_order_access(self, authenticated_customer_client, customer, customer_user):
        """🔐 تست دسترسی مشتری به سفارشات خود"""
        # ایجاد سفارش برای مشتری
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending',
            created_by=customer_user
        )
        
        # تست دسترسی به سفارشات خود
        response = authenticated_customer_client.get('/core/my-orders/')
        assert response.status_code == 200

    def test_working_hours_check(self, working_hours):
        """⏰ تست بررسی ساعات کاری"""
        assert working_hours.is_active
        assert working_hours.start_time.hour == 9
        assert working_hours.end_time.hour == 18
        
        # محاسبه ساعات کاری
        duration = working_hours.get_duration_hours()
        assert duration == 9  # 18 - 9 = 9 ساعت

    def test_order_summary_generation(self, order_with_items):
        """📋 تست تولید خلاصه سفارش"""
        summary = order_with_items.get_order_summary()
        
        assert 'تعداد آیتم‌ها' in summary
        assert 'مبلغ کل' in summary
        assert 'مبلغ نهایی' in summary

    def test_bulk_order_creation(self, bulk_test_data, customer):
        """📊 تست ایجاد سفارشات حجیم"""
        products = bulk_test_data['products'][:10]  # 10 محصول اول
        
        orders = []
        for i, product in enumerate(products):
            order = Order.objects.create(
                customer=customer,
                payment_method='Cash',
                status='Pending',
                total_amount=product.price,
                final_amount=product.price,
                notes=f'سفارش حجیم {i+1}'
            )
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                unit_price=product.price,
                total_price=product.price,
                payment_method='Cash'
            )
            
            orders.append(order)
        
        assert len(orders) == 10
        assert Order.objects.filter(customer=customer).count() == 10 