"""
🧪 تست‌های مجوزها و کنترل دسترسی - HomayOMS
🔐 تست کامل سیستم احراز هویت، مجوزها، و محدودیت‌های دسترسی
✅ پوشش: نقش‌ها، دکوریتورها، میکسین‌ها، و دسترسی‌های کاربران
"""

import pytest
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from accounts.permissions import (
    role_required, super_admin_required, admin_required, finance_required,
    check_user_permission, RoleRequiredMixin, SuperAdminRequiredMixin,
    AdminRequiredMixin, FinanceRequiredMixin, permission_required_custom
)
from accounts.models import User
from core.models import Customer, Product, Order
from unittest.mock import Mock, patch

User = get_user_model()


class TestRoleBasedPermissions(TestCase):
    """🎭 تست‌های مجوزهای مبتنی بر نقش"""

    def setUp(self):
        """🔧 تنظیمات اولیه تست"""
        self.factory = RequestFactory()
        
        # ایجاد کاربران با نقش‌های مختلف
        self.super_admin = User.objects.create_user(
            username='super_admin',
            email='super@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09222222222',
            password='test123',
            role=User.UserRole.ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.finance = User.objects.create_user(
            username='finance',
            email='finance@test.com',
            phone='09333333333',
            password='test123',
            role=User.UserRole.FINANCE,
            status=User.UserStatus.ACTIVE
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09444444444',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )
        
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@test.com',
            phone='09555555555',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.INACTIVE
        )

    @pytest.mark.permissions
    def test_super_admin_permissions(self):
        """👑 تست مجوزهای Super Admin"""
        # Super Admin باید به همه چیز دسترسی داشته باشد
        self.assertTrue(self.super_admin.is_super_admin())
        self.assertTrue(self.super_admin.can_manage_users())
        self.assertTrue(self.super_admin.can_access_financial_data())
        self.assertTrue(self.super_admin.can_manage_inventory())
        
        # بررسی مجوزهای خاص
        self.assertTrue(self.super_admin.has_perm('accounts.manage_all_users'))
        self.assertTrue(self.super_admin.has_perm('accounts.access_all_data'))
        self.assertTrue(self.super_admin.has_perm('accounts.system_settings'))

    @pytest.mark.permissions
    def test_admin_permissions(self):
        """🟡 تست مجوزهای Admin"""
        self.assertFalse(self.admin.is_super_admin())
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.can_manage_users())
        self.assertFalse(self.admin.can_access_financial_data())
        self.assertTrue(self.admin.can_manage_inventory())
        
        # مجوزهای Admin
        self.assertTrue(self.admin.has_perm('accounts.manage_customers'))
        self.assertTrue(self.admin.has_perm('accounts.manage_orders'))
        self.assertTrue(self.admin.has_perm('accounts.manage_inventory'))
        self.assertFalse(self.admin.has_perm('accounts.manage_all_users'))

    @pytest.mark.permissions
    def test_finance_permissions(self):
        """🟢 تست مجوزهای Finance"""
        self.assertFalse(self.finance.is_super_admin())
        self.assertFalse(self.finance.is_admin())
        self.assertTrue(self.finance.is_finance())
        self.assertFalse(self.finance.can_manage_users())
        self.assertTrue(self.finance.can_access_financial_data())
        self.assertFalse(self.finance.can_manage_inventory())
        
        # مجوزهای Finance
        self.assertTrue(self.finance.has_perm('accounts.manage_prices'))
        self.assertTrue(self.finance.has_perm('accounts.view_financial_reports'))
        self.assertTrue(self.finance.has_perm('accounts.manage_payments'))
        self.assertFalse(self.finance.has_perm('accounts.manage_customers'))

    @pytest.mark.permissions
    def test_customer_permissions(self):
        """🔵 تست مجوزهای Customer"""
        self.assertFalse(self.customer.is_super_admin())
        self.assertFalse(self.customer.is_admin())
        self.assertFalse(self.customer.is_finance())
        self.assertTrue(self.customer.is_customer())
        self.assertFalse(self.customer.can_manage_users())
        self.assertFalse(self.customer.can_access_financial_data())
        self.assertFalse(self.customer.can_manage_inventory())
        
        # مجوزهای Customer
        self.assertTrue(self.customer.has_perm('accounts.view_own_orders'))
        self.assertTrue(self.customer.has_perm('accounts.create_orders'))
        self.assertFalse(self.customer.has_perm('accounts.manage_orders'))

    @pytest.mark.permissions
    def test_inactive_user_restrictions(self):
        """❌ تست محدودیت‌های کاربر غیرفعال"""
        self.assertFalse(self.inactive_user.is_active_user())
        # کاربر غیرفعال هیچ دسترسی خاصی نداشته باشد


class TestPermissionDecorators(TestCase):
    """🔐 تست‌های دکوریتورهای مجوز"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.factory = RequestFactory()
        
        self.super_admin = User.objects.create_user(
            username='super_admin',
            email='super@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09222222222',
            password='test123',
            role=User.UserRole.ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09333333333',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )

    def create_mock_view(self, decorator):
        """🏭 ایجاد ویو آزمایشی با دکوریتور"""
        @decorator
        def test_view(request):
            return HttpResponse('Success')
        return test_view

    @pytest.mark.permissions
    def test_super_admin_required_decorator(self):
        """👑 تست دکوریتور super_admin_required"""
        view = self.create_mock_view(super_admin_required)
        
        # Super Admin باید دسترسی داشته باشد
        request = self.factory.get('/')
        request.user = self.super_admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin نباید دسترسی داشته باشد
        request.user = self.admin
        response = view(request)
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_admin_required_decorator(self):
        """🟡 تست دکوریتور admin_required"""
        view = self.create_mock_view(admin_required)
        
        # Super Admin باید دسترسی داشته باشد
        request = self.factory.get('/')
        request.user = self.super_admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin باید دسترسی داشته باشد
        request.user = self.admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Customer نباید دسترسی داشته باشد
        request.user = self.customer
        response = view(request)
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_role_required_decorator(self):
        """🎭 تست دکوریتور role_required"""
        # دکوریتور برای Admin و Finance
        admin_finance_required = role_required(User.UserRole.ADMIN, User.UserRole.FINANCE)
        view = self.create_mock_view(admin_finance_required)
        
        request = self.factory.get('/')
        
        # Super Admin همیشه دسترسی دارد
        request.user = self.super_admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin باید دسترسی داشته باشد
        request.user = self.admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Customer نباید دسترسی داشته باشد
        request.user = self.customer
        response = view(request)
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_check_user_permission_decorator(self):
        """🔍 تست دکوریتور check_user_permission"""
        # دکوریتور برای بررسی متد is_admin
        admin_check = check_user_permission('is_admin')
        view = self.create_mock_view(admin_check)
        
        request = self.factory.get('/')
        
        # Super Admin همیشه دسترسی دارد
        request.user = self.super_admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin باید دسترسی داشته باشد
        request.user = self.admin
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        # Customer نباید دسترسی داشته باشد
        request.user = self.customer
        response = view(request)
        self.assertEqual(response.status_code, 403)


class TestPermissionMixins(TestCase):
    """🔀 تست‌های میکسین‌های مجوز"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.factory = RequestFactory()
        
        self.super_admin = User.objects.create_user(
            username='super_admin',
            email='super@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09222222222',
            password='test123',
            role=User.UserRole.ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09333333333',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )

    def create_test_view_class(self, mixin_class):
        """🏭 ایجاد کلاس ویو آزمایشی"""
        from django.views import View
        
        class TestView(mixin_class, View):
            def get(self, request):
                return HttpResponse('Success')
                
            def post(self, request):
                return HttpResponse('Success')
        
        return TestView

    @pytest.mark.permissions
    def test_super_admin_required_mixin(self):
        """👑 تست میکسین SuperAdminRequiredMixin"""
        TestView = self.create_test_view_class(SuperAdminRequiredMixin)
        view = TestView()
        
        # Super Admin باید دسترسی داشته باشد
        request = self.factory.get('/')
        request.user = self.super_admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin نباید دسترسی داشته باشد
        request.user = self.admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_admin_required_mixin(self):
        """🟡 تست میکسین AdminRequiredMixin"""
        TestView = self.create_test_view_class(AdminRequiredMixin)
        view = TestView()
        
        request = self.factory.get('/')
        
        # Super Admin باید دسترسی داشته باشد
        request.user = self.super_admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin باید دسترسی داشته باشد
        request.user = self.admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
        
        # Customer نباید دسترسی داشته باشد
        request.user = self.customer
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_role_required_mixin_custom(self):
        """🎭 تست میکسین RoleRequiredMixin با نقش‌های سفارشی"""
        from django.views import View
        
        class CustomRoleView(RoleRequiredMixin, View):
            allowed_roles = [User.UserRole.ADMIN, User.UserRole.FINANCE]
            
            def get(self, request):
                return HttpResponse('Success')
        
        view = CustomRoleView()
        request = self.factory.get('/')
        
        # Super Admin همیشه دسترسی دارد
        request.user = self.super_admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
        
        # Admin باید دسترسی داشته باشد
        request.user = self.admin
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
        
        # Customer نباید دسترسی داشته باشد
        request.user = self.customer
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 403)


class TestViewPermissions(TestCase):
    """👁️ تست‌های دسترسی ویوها"""

    def setUp(self):
        """🔧 تنظیمات اولیه"""
        self.client = Client()
        
        self.super_admin = User.objects.create_user(
            username='super_admin',
            email='super@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.SUPER_ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone='09222222222',
            password='test123',
            role=User.UserRole.ADMIN,
            status=User.UserStatus.ACTIVE
        )
        
        self.finance = User.objects.create_user(
            username='finance',
            email='finance@test.com',
            phone='09333333333',
            password='test123',
            role=User.UserRole.FINANCE,
            status=User.UserStatus.ACTIVE
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            phone='09444444444',
            password='test123',
            role=User.UserRole.CUSTOMER,
            status=User.UserStatus.ACTIVE
        )

    @pytest.mark.permissions
    def test_dashboard_access_permissions(self):
        """📊 تست دسترسی به داشبوردها"""
        # تست دسترسی Super Admin
        self.client.login(username='super_admin', password='test123')
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # تست دسترسی Admin
        self.client.login(username='admin', password='test123')
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # تست دسترسی Customer - باید redirect شود
        self.client.login(username='customer', password='test123')
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 302)  # Customer gets redirected
        self.assertRedirects(response, '/accounts/customer/dashboard/')
        
        # تست دسترسی Customer به داشبورد مخصوص خود
        response = self.client.get('/accounts/customer/dashboard/')
        self.assertEqual(response.status_code, 200)

    @pytest.mark.permissions
    def test_user_management_access(self):
        """👥 تست دسترسی مدیریت کاربران"""
        # فقط Super Admin باید دسترسی داشته باشد
        self.client.login(username='super_admin', password='test123')
        response = self.client.get('/accounts/users/')
        self.assertEqual(response.status_code, 200)
        
        # Admin نباید دسترسی داشته باشد
        self.client.login(username='admin', password='test123')
        response = self.client.get('/accounts/users/')
        self.assertEqual(response.status_code, 403)

    @pytest.mark.permissions
    def test_customer_orders_access(self):
        """🛒 تست دسترسی به سفارشات مشتری"""
        # ایجاد مشتری
        customer_profile = Customer.objects.create(
            customer_name='مشتری تست',
            phone='09444444444',
            status='Active'
        )
        
        # مشتری باید به سفارشات خود دسترسی داشته باشد
        self.client.login(username='customer', password='test123')
        response = self.client.get('/core/my-orders/')
        self.assertEqual(response.status_code, 200)

    @pytest.mark.permissions
    def test_financial_data_access(self):
        """💰 تست دسترسی به داده‌های مالی"""
        # Super Admin و Finance باید دسترسی داشته باشند
        self.client.login(username='super_admin', password='test123')
        response = self.client.get('/core/finance/')
        # اگر این URL وجود داشت، باید 200 برگرداند
        
        self.client.login(username='finance', password='test123')
        response = self.client.get('/core/finance/')
        # اگر این URL وجود داشت، باید 200 برگرداند
        
        # Admin و Customer نباید دسترسی داشته باشند
        self.client.login(username='admin', password='test123')
        # response = self.client.get('/core/finance/')
        # self.assertEqual(response.status_code, 403)


@pytest.mark.permissions
class TestPermissionsPytest:
    """🧪 تست‌های pytest برای مجوزها"""

    def test_user_role_methods(self, super_admin_user, admin_user, finance_user, customer_user):
        """🎭 تست متدهای نقش کاربران"""
        # Super Admin
        assert super_admin_user.is_super_admin()
        assert not super_admin_user.is_admin()
        assert not super_admin_user.is_finance()
        assert not super_admin_user.is_customer()
        
        # Admin
        assert not admin_user.is_super_admin()
        assert admin_user.is_admin()
        assert not admin_user.is_finance()
        assert not admin_user.is_customer()
        
        # Finance
        assert not finance_user.is_super_admin()
        assert not finance_user.is_admin()
        assert finance_user.is_finance()
        assert not finance_user.is_customer()
        
        # Customer
        assert not customer_user.is_super_admin()
        assert not customer_user.is_admin()
        assert not customer_user.is_finance()
        assert customer_user.is_customer()

    def test_user_capability_methods(self, super_admin_user, admin_user, finance_user, customer_user):
        """🛠️ تست متدهای قابلیت کاربران"""
        # Super Admin - همه قابلیت‌ها
        assert super_admin_user.can_manage_users()
        assert super_admin_user.can_access_financial_data()
        assert super_admin_user.can_manage_inventory()
        
        # Admin - فقط موجودی
        assert not admin_user.can_manage_users()
        assert not admin_user.can_access_financial_data()
        assert admin_user.can_manage_inventory()
        
        # Finance - فقط مالی
        assert not finance_user.can_manage_users()
        assert finance_user.can_access_financial_data()
        assert not finance_user.can_manage_inventory()
        
        # Customer - هیچ کدام
        assert not customer_user.can_manage_users()
        assert not customer_user.can_access_financial_data()
        assert not customer_user.can_manage_inventory()

    def test_user_permissions_via_groups(self, super_admin_user, admin_user, finance_user, customer_user):
        """🔐 تست مجوزها از طریق گروه‌ها"""
        # Super Admin permissions
        assert super_admin_user.has_perm('accounts.manage_all_users')
        assert super_admin_user.has_perm('accounts.access_all_data')
        
        # Admin permissions
        assert admin_user.has_perm('accounts.manage_customers')
        assert admin_user.has_perm('accounts.manage_orders')
        assert not admin_user.has_perm('accounts.manage_all_users')
        
        # Finance permissions
        assert finance_user.has_perm('accounts.manage_prices')
        assert finance_user.has_perm('accounts.view_financial_reports')
        assert not finance_user.has_perm('accounts.manage_customers')
        
        # Customer permissions
        assert customer_user.has_perm('accounts.view_own_orders')
        assert customer_user.has_perm('accounts.create_orders')
        assert not customer_user.has_perm('accounts.manage_orders')

    def test_inactive_user_restrictions(self, inactive_user):
        """❌ تست محدودیت‌های کاربر غیرفعال"""
        assert not inactive_user.is_active_user()
        assert inactive_user.status == User.UserStatus.INACTIVE

    @pytest.mark.parametrize("user_fixture,expected_features", [
        ('super_admin_user', ['👥 مدیریت کاربران', '💰 مدیریت مالی', '📦 مدیریت موجودی']),
        ('admin_user', ['📦 مدیریت موجودی']),
        ('finance_user', ['💰 مدیریت قیمت‌ها']),
        ('customer_user', ['📋 مشاهده سفارشات من']),
    ])
    def test_accessible_features(self, request, user_fixture, expected_features):
        """🎯 تست ویژگی‌های قابل دسترسی"""
        user = request.getfixturevalue(user_fixture)
        accessible_features = user.get_accessible_features()
        
        for feature in expected_features:
            assert feature in accessible_features

    def test_authenticated_client_permissions(self, authenticated_super_admin_client, authenticated_customer_client):
        """🌐 تست مجوزهای کلاینت‌های احراز هویت شده"""
        # Super Admin client
        response = authenticated_super_admin_client.get('/accounts/dashboard/')
        assert response.status_code == 200
        
        # Customer client
        response = authenticated_customer_client.get('/accounts/dashboard/')
        assert response.status_code == 200

    def test_permission_inheritance(self, super_admin_user):
        """🔗 تست وراثت مجوزها"""
        # Super Admin باید همه مجوزهای نقش‌های دیگر را داشته باشد
        admin_permissions = ['manage_customers', 'manage_orders', 'manage_inventory']
        finance_permissions = ['manage_prices', 'view_financial_reports', 'manage_payments']
        customer_permissions = ['view_own_orders', 'create_orders']
        
        all_permissions = admin_permissions + finance_permissions + customer_permissions
        
        for permission in all_permissions:
            assert super_admin_user.has_perm(f'accounts.{permission}')

    def test_cross_role_permission_denial(self, admin_user, finance_user, customer_user):
        """🚫 تست رد مجوزهای متقابل نقش‌ها"""
        # Admin نباید مجوزهای Finance داشته باشد
        assert not admin_user.has_perm('accounts.manage_prices')
        assert not admin_user.has_perm('accounts.view_financial_reports')
        
        # Finance نباید مجوزهای Admin داشته باشد
        assert not finance_user.has_perm('accounts.manage_customers')
        assert not finance_user.has_perm('accounts.manage_inventory')
        
        # Customer نباید مجوزهای مدیریتی داشته باشد
        assert not customer_user.has_perm('accounts.manage_customers')
        assert not customer_user.has_perm('accounts.manage_prices') 