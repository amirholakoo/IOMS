"""
🧪 تست‌های پایه - HomayOMS
📋 تست‌های ابتدایی برای اطمینان از صحت تنظیمات
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class TestBasicSetup(TestCase):
    """🔧 تست‌های تنظیمات پایه"""

    def test_user_model_exists(self):
        """👤 تست وجود مدل User"""
        self.assertTrue(User)
        self.assertEqual(User.__name__, 'User')

    def test_create_simple_user(self):
        """👤 تست ایجاد کاربر ساده"""
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            phone='09123456789',
            password='test123'
        )
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone, '09123456789')

    def test_user_roles(self):
        """🎭 تست نقش‌های کاربر"""
        roles = [choice[0] for choice in User.UserRole.choices]
        expected_roles = ['super_admin', 'admin', 'finance', 'customer']
        
        for role in expected_roles:
            self.assertIn(role, roles)


@pytest.mark.unit
def test_pytest_working():
    """🧪 تست عملکرد pytest"""
    assert True


@pytest.mark.unit  
def test_django_integration():
    """🔗 تست یکپارچگی Django"""
    from django.conf import settings
    assert settings.configured 