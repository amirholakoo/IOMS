"""
🧪 تنظیمات و فیکسچرهای pytest برای HomayOMS
📋 شامل فیکسچرهای مشترک برای تست تمام بخش‌های سیستم
🎯 پشتیبانی از تست‌های کاربران، مجوزها، پرداخت‌ها و عملیات کسب‌وکار
"""

import os
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

import pytest
import factory
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from django.db import transaction
from accounts.models import User
from core.models import Customer, Product, Order, OrderItem, ActivityLog, WorkingHours
from payments.models import Payment, PaymentCallback, PaymentRefund

User = get_user_model()


# =============================================================================
# Database and Transaction Fixtures
# =============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """تنظیمات پایگاه داده برای تست"""
    pass


@pytest.fixture
def enable_db_access():
    """فعال‌سازی دسترسی به پایگاه داده"""
    pass


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def super_admin_user(db):
    """👑 کاربر Super Admin"""
    return User.objects.create_user(
        username='super_admin',
        email='super@test.com',
        password='test123',
        first_name='Super',
        last_name='Admin',
        phone='09101234567',
        role=User.UserRole.SUPER_ADMIN,
        status=User.UserStatus.ACTIVE
    )


@pytest.fixture
def admin_user(db):
    """🟡 کاربر Admin"""
    return User.objects.create_user(
        username='admin_user',
        email='admin@test.com',
        password='test123',
        first_name='Test',
        last_name='Admin',
        phone='09101234568',
        role=User.UserRole.ADMIN,
        status=User.UserStatus.ACTIVE
    )


@pytest.fixture
def finance_user(db):
    """🟢 کاربر Finance"""
    return User.objects.create_user(
        username='finance_user',
        email='finance@test.com',
        password='test123',
        first_name='Test',
        last_name='Finance',
        phone='09101234569',
        role=User.UserRole.FINANCE,
        status=User.UserStatus.ACTIVE
    )


@pytest.fixture
def customer_user(db):
    """🔵 کاربر Customer"""
    return User.objects.create_user(
        username='customer_user',
        email='customer@test.com',
        password='test123',
        first_name='Test',
        last_name='Customer',
        phone='09101234570',
        role=User.UserRole.CUSTOMER,
        status=User.UserStatus.ACTIVE
    )


@pytest.fixture
def inactive_user(db):
    """❌ کاربر غیرفعال"""
    return User.objects.create_user(
        username='inactive_user',
        email='inactive@test.com',
        password='test123',
        first_name='Inactive',
        last_name='User',
        phone='09101234571',
        role=User.UserRole.CUSTOMER,
        status=User.UserStatus.INACTIVE
    )


# =============================================================================
# Customer Fixtures
# =============================================================================

@pytest.fixture
def customer(db):
    """👤 مشتری تست"""
    return Customer.objects.create(
        customer_name='شرکت تست',
        phone='02112345678',
        address='تهران، خیابان تست',
        status='Active',
        economic_code='123456789',
        postcode='1234567890',
        national_id='1234567890'
    )


@pytest.fixture
def inactive_customer(db):
    """👤 مشتری غیرفعال"""
    return Customer.objects.create(
        customer_name='شرکت غیرفعال',
        phone='02112345679',
        address='تهران، خیابان غیرفعال',
        status='Inactive'
    )


# =============================================================================
# Product Fixtures
# =============================================================================

@pytest.fixture
def product(db):
    """📦 محصول تست"""
    return Product.objects.create(
        reel_number='TEST-001',
        location='Anbar_Akhal',
        status='In-stock',
        width=1000,
        gsm=80,
        length=1500,
        grade='A',
        breaks=0,
        price=Decimal('150000.00'),
        qr_code='QR-TEST-001'
    )


@pytest.fixture
def sold_product(db):
    """📦 محصول فروخته شده"""
    return Product.objects.create(
        reel_number='SOLD-001',
        location='Anbar_Akhal',
        status='Sold',
        width=800,
        gsm=70,
        length=1200,
        grade='B',
        breaks=1,
        price=Decimal('120000.00'),
        qr_code='QR-SOLD-001'
    )


@pytest.fixture
def multiple_products(db):
    """📦 چندین محصول برای تست"""
    products = []
    for i in range(5):
        product = Product.objects.create(
            reel_number=f'MULTI-{i+1:03d}',
            location='Anbar_Akhal',
            status='In-stock',
            width=800 + i * 100,
            gsm=70 + i * 10,
            length=1000 + i * 200,
            grade=['A', 'B', 'C', 'A+', 'B+'][i],
            breaks=i,
            price=Decimal(f'{100000 + i * 25000}.00'),
            qr_code=f'QR-MULTI-{i+1:03d}'
        )
        products.append(product)
    return products


# =============================================================================
# Order Fixtures
# =============================================================================

@pytest.fixture
def order(db, customer, super_admin_user):
    """🛒 سفارش تست"""
    return Order.objects.create(
        customer=customer,
        payment_method='Cash',
        status='Pending',
        total_amount=Decimal('300000.00'),
        discount_percentage=Decimal('10.00'),
        discount_amount=Decimal('30000.00'),
        final_amount=Decimal('270000.00'),
        notes='سفارش تست',
        created_by=super_admin_user
    )


@pytest.fixture
def order_with_items(db, order, product, sold_product):
    """🛒 سفارش با آیتم‌ها"""
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=product.price,
        total_price=product.price * 2,
        payment_method='Cash'
    )
    OrderItem.objects.create(
        order=order,
        product=sold_product,
        quantity=1,
        unit_price=sold_product.price,
        total_price=sold_product.price,
        payment_method='Terms'
    )
    return order


# =============================================================================
# Payment Fixtures
# =============================================================================

@pytest.fixture
def payment(db, order, customer_user):
    """💳 پرداخت تست"""
    return Payment.objects.create(
        order=order,
        user=customer_user,
        amount=Decimal('2700000'),  # 270000 تومان = 2700000 ریال
        display_amount=Decimal('270000'),
        gateway='zarinpal',
        status='INITIATED',
        payer_phone='09101234570',
        description='تست پرداخت'
    )


@pytest.fixture
def successful_payment(db, order, customer_user):
    """💳 پرداخت موفق"""
    payment = Payment.objects.create(
        order=order,
        user=customer_user,
        amount=Decimal('2700000'),
        display_amount=Decimal('270000'),
        gateway='zarinpal',
        status='SUCCESS',
        payer_phone='09101234570',
        gateway_transaction_id='TXN123456789',
        bank_reference_number='REF987654321',
        masked_card_number='6274-****-****-1234',
        completed_at=timezone.now()
    )
    return payment


@pytest.fixture
def failed_payment(db, order, customer_user):
    """💳 پرداخت ناموفق"""
    return Payment.objects.create(
        order=order,
        user=customer_user,
        amount=Decimal('2700000'),
        display_amount=Decimal('270000'),
        gateway='shaparak',
        status='FAILED',
        payer_phone='09101234570',
        error_message='تراکنش ناموفق',
        completed_at=timezone.now()
    )


# =============================================================================
# Working Hours Fixtures
# =============================================================================

@pytest.fixture
def working_hours(db, super_admin_user):
    """⏰ ساعات کاری"""
    return WorkingHours.objects.create(
        start_time='09:00',
        end_time='18:00',
        description='ساعات کاری عادی',
        is_active=True,
        set_by=super_admin_user
    )


# =============================================================================
# Client Fixtures
# =============================================================================

@pytest.fixture
def client():
    """🌐 کلاینت Django"""
    return Client()


@pytest.fixture
def authenticated_super_admin_client(client, super_admin_user):
    """🌐 کلاینت وارد شده با Super Admin"""
    client.force_login(super_admin_user)
    return client


@pytest.fixture
def authenticated_admin_client(client, admin_user):
    """🌐 کلاینت وارد شده با Admin"""
    client.force_login(admin_user)
    return client


@pytest.fixture
def authenticated_finance_client(client, finance_user):
    """🌐 کلاینت وارد شده با Finance"""
    client.force_login(finance_user)
    return client


@pytest.fixture
def authenticated_customer_client(client, customer_user):
    """🌐 کلاینت وارد شده با Customer"""
    client.force_login(customer_user)
    return client


# =============================================================================
# Factory Fixtures
# =============================================================================

class UserFactory(factory.django.DjangoModelFactory):
    """🏭 Factory برای ایجاد کاربران"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Sequence(lambda n: f'091012345{n:02d}')
    role = User.UserRole.CUSTOMER
    status = User.UserStatus.ACTIVE


class CustomerFactory(factory.django.DjangoModelFactory):
    """🏭 Factory برای ایجاد مشتریان"""
    class Meta:
        model = Customer
    
    customer_name = factory.Faker('company')
    phone = factory.Sequence(lambda n: f'021123456{n:02d}')
    address = factory.Faker('address')
    status = 'Active'
    economic_code = factory.Sequence(lambda n: f'{123456789 + n}')
    postcode = factory.Sequence(lambda n: f'{1234567890 + n}')
    national_id = factory.Sequence(lambda n: f'{1234567890 + n}')


class ProductFactory(factory.django.DjangoModelFactory):
    """🏭 Factory برای ایجاد محصولات"""
    class Meta:
        model = Product
    
    reel_number = factory.Sequence(lambda n: f'FACT-{n:04d}')
    location = 'Anbar_Akhal'
    status = 'In-stock'
    width = factory.Faker('random_int', min=800, max=1600)
    gsm = factory.Faker('random_element', elements=[70, 80, 90, 100, 120])
    length = factory.Faker('random_int', min=1000, max=2000)
    grade = factory.Faker('random_element', elements=['A', 'B', 'C', 'A+', 'B+'])
    breaks = factory.Faker('random_int', min=0, max=5)
    price = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    qr_code = factory.LazyAttribute(lambda obj: f'QR-{obj.reel_number}')


@pytest.fixture
def user_factory():
    """🏭 Factory کاربران"""
    return UserFactory


@pytest.fixture
def customer_factory():
    """🏭 Factory مشتریان"""
    return CustomerFactory


@pytest.fixture
def product_factory():
    """🏭 Factory محصولات"""
    return ProductFactory


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_payment_gateway(mocker):
    """🧪 Mock درگاه پرداخت"""
    mock_gateway = mocker.patch('payments.services.BasePaymentGateway._make_request')
    mock_gateway.return_value = {
        'status': 'success',
        'data': {
            'authority': 'A00000000000000000000000000000123456789',
            'code': 100,
            'message': 'Success'
        }
    }
    return mock_gateway


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def sample_request_data():
    """📋 داده‌های نمونه برای درخواست‌ها"""
    return {
        'user_data': {
            'username': 'new_user',
            'email': 'new@test.com',
            'password': 'secure123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '09101111111',
            'role': 'customer'
        },
        'customer_data': {
            'customer_name': 'شرکت جدید',
            'phone': '02199999999',
            'address': 'آدرس جدید',
            'status': 'Active'
        },
        'product_data': {
            'reel_number': 'NEW-001',
            'location': 'Anbar_Akhal',
            'status': 'In-stock',
            'width': 1200,
            'gsm': 90,
            'length': 1800,
            'grade': 'A+',
            'price': '180000.00'
        }
    }


@pytest.fixture
def test_file_content():
    """📄 محتوای فایل تست"""
    return {
        'csv_content': 'name,phone,email\nTest User,09123456789,test@example.com',
        'json_content': '{"test": "data", "number": 123}',
        'image_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    }


# =============================================================================
# Performance Test Fixtures
# =============================================================================

@pytest.fixture
def bulk_test_data(db, user_factory, customer_factory, product_factory):
    """📊 داده‌های حجیم برای تست عملکرد"""
    users = user_factory.create_batch(10)
    customers = customer_factory.create_batch(20)
    products = product_factory.create_batch(50)
    
    return {
        'users': users,
        'customers': customers,
        'products': products
    }


# =============================================================================
# Cleanup Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """🔧 فعال‌سازی خودکار دسترسی پایگاه داده برای همه تست‌ها"""
    pass 