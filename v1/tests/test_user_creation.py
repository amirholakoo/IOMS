"""
🧪 تست‌های ایجاد کاربر - HomayOMS
👥 تست کامل عملیات ایجاد کاربران با نقش‌های مختلف
✅ پوشش: ایجاد، اعتبارسنجی، مجوزها، و تعیین گروه‌ها
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError, transaction
from accounts.models import User
from core.models import Customer

User = get_user_model()


class TestUserCreation(TestCase):
    """🧪 تست‌های ایجاد کاربر"""

    def setUp(self):
        """🔧 تنظیمات اولیه تست"""
        self.valid_user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '09123456789',
            'password': 'secure123'
        }

    @pytest.mark.unit
    def test_create_super_admin_user(self):
        """👑 تست ایجاد Super Admin"""
        user = User.objects.create_user(
            role=User.UserRole.SUPER_ADMIN,
            **self.valid_user_data
        )
        
        self.assertEqual(user.role, User.UserRole.SUPER_ADMIN)
        self.assertTrue(user.is_super_admin())
        self.assertFalse(user.is_admin())
        self.assertFalse(user.is_finance())
        self.assertFalse(user.is_customer())
        self.assertTrue(user.can_manage_users())
        self.assertTrue(user.can_access_financial_data())
        self.assertTrue(user.can_manage_inventory())

    @pytest.mark.unit
    def test_create_admin_user(self):
        """🟡 تست ایجاد Admin"""
        user = User.objects.create_user(
            role=User.UserRole.ADMIN,
            **self.valid_user_data
        )
        
        self.assertEqual(user.role, User.UserRole.ADMIN)
        self.assertFalse(user.is_super_admin())
        self.assertTrue(user.is_admin())
        self.assertFalse(user.is_finance())
        self.assertFalse(user.is_customer())
        self.assertFalse(user.can_manage_users())
        self.assertFalse(user.can_access_financial_data())
        self.assertTrue(user.can_manage_inventory())

    @pytest.mark.unit
    def test_create_finance_user(self):
        """🟢 تست ایجاد Finance"""
        user = User.objects.create_user(
            role=User.UserRole.FINANCE,
            **self.valid_user_data
        )
        
        self.assertEqual(user.role, User.UserRole.FINANCE)
        self.assertFalse(user.is_super_admin())
        self.assertFalse(user.is_admin())
        self.assertTrue(user.is_finance())
        self.assertFalse(user.is_customer())
        self.assertFalse(user.can_manage_users())
        self.assertTrue(user.can_access_financial_data())
        self.assertFalse(user.can_manage_inventory())

    @pytest.mark.unit
    def test_create_customer_user(self):
        """🔵 تست ایجاد Customer"""
        user = User.objects.create_user(
            role=User.UserRole.CUSTOMER,
            **self.valid_user_data
        )
        
        self.assertEqual(user.role, User.UserRole.CUSTOMER)
        self.assertFalse(user.is_super_admin())
        self.assertFalse(user.is_admin())
        self.assertFalse(user.is_finance())
        self.assertTrue(user.is_customer())
        self.assertFalse(user.can_manage_users())
        self.assertFalse(user.can_access_financial_data())
        self.assertFalse(user.can_manage_inventory())

    @pytest.mark.unit
    def test_user_phone_validation(self):
        """📞 تست اعتبارسنجی شماره تلفن"""
        # شماره معتبر
        user = User.objects.create_user(
            phone='09123456789',
            **{k: v for k, v in self.valid_user_data.items() if k != 'phone'}
        )
        self.assertEqual(user.phone, '09123456789')

        # شماره نامعتبر
        invalid_user_data = self.valid_user_data.copy()
        invalid_user_data['phone'] = '0812345678'  # شروع نمی‌شود با 09
        invalid_user_data['username'] = 'invalid_user'
        
        user = User(**invalid_user_data)
        with self.assertRaises(ValidationError):
            user.clean()

    @pytest.mark.unit
    def test_unique_phone_constraint(self):
        """📞 تست یکتایی شماره تلفن"""
        # ایجاد کاربر اول
        User.objects.create_user(**self.valid_user_data)
        
        # تلاش برای ایجاد کاربر دوم با همان شماره تلفن
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'duplicate_user'
        duplicate_data['email'] = 'duplicate@example.com'
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**duplicate_data)

    @pytest.mark.unit
    def test_unique_username_constraint(self):
        """👤 تست یکتایی نام کاربری"""
        User.objects.create_user(**self.valid_user_data)
        
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['phone'] = '09987654321'
        duplicate_data['email'] = 'duplicate@example.com'
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**duplicate_data)

    @pytest.mark.unit
    def test_user_group_assignment(self):
        """🎭 تست تعیین خودکار گروه کاربر"""
        user = User.objects.create_user(
            role=User.UserRole.ADMIN,
            **self.valid_user_data
        )
        
        # بررسی تعیین گروه
        group_name = f"{user.role}_group"
        self.assertTrue(user.groups.filter(name=group_name).exists())

    @pytest.mark.unit
    def test_customer_profile_creation_for_customer_role(self):
        """👤 تست ایجاد خودکار پروفایل مشتری"""
        customer_data = self.valid_user_data.copy()
        customer_data['role'] = User.UserRole.CUSTOMER
        
        user = User.objects.create_user(**customer_data)
        
        # بررسی ایجاد Customer مرتبط
        customer_exists = Customer.objects.filter(
            customer_name=user.get_full_name(),
            phone=user.phone
        ).exists()
        self.assertTrue(customer_exists)

    @pytest.mark.unit
    def test_user_status_validation(self):
        """📊 تست اعتبارسنجی وضعیت کاربر"""
        for status in User.UserStatus.choices:
            user_data = self.valid_user_data.copy()
            user_data['username'] = f'user_{status[0]}'
            user_data['phone'] = f'0912345{len(status[0]):04d}'
            user_data['email'] = f'{status[0]}@example.com'
            user_data['status'] = status[0]
            
            user = User.objects.create_user(**user_data)
            self.assertEqual(user.status, status[0])

    @pytest.mark.unit
    def test_is_active_user_method(self):
        """✅ تست متد is_active_user"""
        # کاربر فعال
        active_user = User.objects.create_user(
            status=User.UserStatus.ACTIVE,
            **self.valid_user_data
        )
        self.assertTrue(active_user.is_active_user())

        # کاربر غیرفعال
        inactive_data = self.valid_user_data.copy()
        inactive_data['username'] = 'inactive_user'
        inactive_data['phone'] = '09987654321'
        inactive_data['email'] = 'inactive@example.com'
        inactive_data['status'] = User.UserStatus.INACTIVE
        
        inactive_user = User.objects.create_user(**inactive_data)
        self.assertFalse(inactive_user.is_active_user())

    @pytest.mark.unit
    def test_password_hashing(self):
        """🔐 تست هش شدن رمز عبور"""
        user = User.objects.create_user(**self.valid_user_data)
        
        # رمز عبور نباید به صورت خام ذخیره شود
        self.assertNotEqual(user.password, 'secure123')
        self.assertTrue(user.check_password('secure123'))
        self.assertFalse(user.check_password('wrong_password'))

    @pytest.mark.unit
    def test_get_accessible_features(self):
        """🎯 تست دریافت ویژگی‌های قابل دسترسی"""
        # Super Admin
        super_admin = User.objects.create_user(
            role=User.UserRole.SUPER_ADMIN,
            username='super_admin',
            phone='09111111111',
            email='super@example.com',
            password='secure123'
        )
        super_features = super_admin.get_accessible_features()
        self.assertIn('👥 مدیریت کاربران', super_features)
        self.assertIn('💰 مدیریت مالی', super_features)
        self.assertIn('📦 مدیریت موجودی', super_features)

        # Customer
        customer = User.objects.create_user(
            role=User.UserRole.CUSTOMER,
            username='customer',
            phone='09222222222',
            email='customer@example.com',
            password='secure123'
        )
        customer_features = customer.get_accessible_features()
        self.assertIn('📋 مشاهده سفارشات من', customer_features)
        self.assertNotIn('👥 مدیریت کاربران', customer_features)

    @pytest.mark.unit
    def test_user_string_representation(self):
        """📄 تست نمایش رشته‌ای کاربر"""
        user = User.objects.create_user(**self.valid_user_data)
        # Expected format: "🔵 Test User" for Customer role
        expected_str = f"🔵 {user.first_name} {user.last_name}"
        self.assertEqual(str(user), expected_str)

    @pytest.mark.unit
    def test_role_display_with_emoji(self):
        """😀 تست نمایش نقش با ایموجی"""
        user = User.objects.create_user(
            role=User.UserRole.SUPER_ADMIN,
            **self.valid_user_data
        )
        role_display = user.get_role_display_with_emoji()
        self.assertIn('🔴', role_display)
        self.assertIn('Super Admin', role_display)


class TestUserCreationIntegration(TestCase):
    """🔗 تست‌های یکپارچگی ایجاد کاربر"""

    @pytest.mark.integration
    def test_multiple_users_creation(self):
        """👥 تست ایجاد چندین کاربر همزمان"""
        users_data = [
            {
                'username': f'user_{i}',
                'email': f'user{i}@example.com',
                'phone': f'091234567{i:02d}',
                'first_name': f'User{i}',
                'last_name': 'Test',
                'role': [
                    User.UserRole.SUPER_ADMIN,
                    User.UserRole.ADMIN,
                    User.UserRole.FINANCE,
                    User.UserRole.CUSTOMER
                ][i % 4],
                'password': 'secure123'
            }
            for i in range(10)
        ]

        created_users = []
        for user_data in users_data:
            user = User.objects.create_user(**user_data)
            created_users.append(user)

        self.assertEqual(len(created_users), 10)
        
        # بررسی توزیع نقش‌ها
        roles_count = {}
        for user in created_users:
            roles_count[user.role] = roles_count.get(user.role, 0) + 1
        
        # هر نقش باید 2-3 کاربر داشته باشد (10/4 ≈ 2.5)
        for role, count in roles_count.items():
            self.assertGreaterEqual(count, 2)
            self.assertLessEqual(count, 3)

    @pytest.mark.integration
    def test_user_creation_with_permissions(self):
        """🔐 تست ایجاد کاربر و تعیین مجوزها"""
        user = User.objects.create_user(
            role=User.UserRole.FINANCE,
            username='finance_test',
            email='finance@example.com',
            phone='09123456789',
            password='secure123'
        )

        # بررسی مجوزهای Finance
        self.assertTrue(user.has_perm('accounts.manage_prices'))
        self.assertTrue(user.has_perm('accounts.view_financial_reports'))
        self.assertFalse(user.has_perm('accounts.manage_all_users'))

    @pytest.mark.integration
    def test_concurrent_user_creation(self):
        """⚡ تست ایجاد همزمان کاربران"""
        def create_user(index):
            return User.objects.create_user(
                username=f'concurrent_user_{index}',
                email=f'concurrent{index}@example.com',
                phone=f'091111111{index:02d}',
                password='secure123',
                role=User.UserRole.CUSTOMER
            )

        # ایجاد 5 کاربر همزمان
        with transaction.atomic():
            users = [create_user(i) for i in range(5)]

        self.assertEqual(len(users), 5)
        for user in users:
            self.assertTrue(user.pk is not None)
            self.assertEqual(user.role, User.UserRole.CUSTOMER)


@pytest.mark.user_creation
class TestUserCreationPytest:
    """🧪 تست‌های pytest برای ایجاد کاربر"""

    def test_create_user_with_factory(self, user_factory):
        """🏭 تست ایجاد کاربر با Factory"""
        user = user_factory()
        assert user.pk is not None
        assert user.role == User.UserRole.CUSTOMER
        assert user.status == User.UserStatus.ACTIVE

    def test_create_multiple_users_with_factory(self, user_factory):
        """🏭 تست ایجاد چندین کاربر با Factory"""
        users = user_factory.create_batch(5)
        assert len(users) == 5
        
        usernames = [user.username for user in users]
        assert len(set(usernames)) == 5  # همه نام‌های کاربری یکتا باشند

    def test_super_admin_fixture(self, super_admin_user):
        """👑 تست فیکسچر Super Admin"""
        assert super_admin_user.is_super_admin()
        assert super_admin_user.role == User.UserRole.SUPER_ADMIN
        assert super_admin_user.status == User.UserStatus.ACTIVE

    def test_all_user_role_fixtures(self, super_admin_user, admin_user, finance_user, customer_user):
        """🎭 تست همه فیکسچرهای نقش‌ها"""
        users = [super_admin_user, admin_user, finance_user, customer_user]
        roles = [user.role for user in users]
        
        expected_roles = [
            User.UserRole.SUPER_ADMIN,
            User.UserRole.ADMIN,
            User.UserRole.FINANCE,
            User.UserRole.CUSTOMER
        ]
        
        assert roles == expected_roles

    def test_user_phone_uniqueness(self, db):
        """📞 تست یکتایی شماره تلفن با pytest"""
        # ایجاد کاربر اول
        User.objects.create_user(
            username='user1',
            email='user1@test.com',
            phone='09123456789',
            password='test123'
        )
        
        # تلاش برای ایجاد کاربر دوم با همان شماره
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='user2@test.com',
                phone='09123456789',  # شماره تکراری
                password='test123'
            )

    def test_customer_profile_auto_creation(self, db):
        """👤 تست ایجاد خودکار پروفایل Customer"""
        user = User.objects.create_user(
            username='auto_customer',
            email='auto@test.com',
            phone='09111111111',
            password='test123',
            role=User.UserRole.CUSTOMER,
            first_name='Auto',
            last_name='Customer'
        )
        
        # بررسی ایجاد Customer
        customer = Customer.objects.filter(
            customer_name=user.get_full_name(),
            phone=user.phone
        ).first()
        
        assert customer is not None
        assert customer.customer_name == 'Auto Customer'
        assert customer.phone == '09111111111'

    @pytest.mark.parametrize("role,expected_permissions", [
        (User.UserRole.SUPER_ADMIN, ['manage_all_users', 'access_all_data', 'system_settings']),
        (User.UserRole.ADMIN, ['manage_customers', 'manage_orders', 'manage_inventory']),
        (User.UserRole.FINANCE, ['manage_prices', 'view_financial_reports', 'manage_payments']),
        (User.UserRole.CUSTOMER, ['view_own_orders', 'create_orders', 'view_own_profile']),
    ])
    def test_role_permissions(self, db, role, expected_permissions):
        """🔐 تست مجوزهای نقش‌ها"""
        user = User.objects.create_user(
            username=f'test_{role}',
            email=f'{role}@test.com',
            phone=f'091{hash(role) % 100000000:08d}',
            password='test123',
            role=role
        )
        
        for permission in expected_permissions:
            assert user.has_perm(f'accounts.{permission}'), f'User with role {role} should have {permission}' 