# 🧪 تست‌های HomayOMS - مستندات کامل

## 📋 نمای کلی

پروژه HomayOMS شامل مجموعه کاملی از تست‌های خودکار است که برای دستیابی به **90% پوشش کد** طراحی شده‌اند. این تست‌ها تمام جنبه‌های اصلی سیستم را پوشش می‌دهند:

## 🎯 اهداف تست

- ✅ **ایجاد کاربران** با نقش‌های مختلف
- ✅ **خرید کاربران** و فرآیند سفارش‌دهی
- ✅ **ایجاد Super Admin** و تنظیمات مدیریتی
- ✅ **مجوزهای Super Admin** و کنترل دسترسی
- ✅ **مجوزهای Admin** و محدودیت‌ها
- ✅ **مجوزهای Finance** و مدیریت مالی
- ✅ **مجوزهای Customer** و محدودیت‌ها
- ✅ **ایجاد پرداخت** و درگاه‌های مختلف
- ✅ **پرداخت موفق** و پردازش تراکنش‌ها
- ✅ **پرداخت ناموفق** و مدیریت خطاها

## 📁 ساختار فایل‌های تست

```
v1/
├── tests/
│   ├── __init__.py
│   ├── test_basic.py              # تست‌های پایه
│   ├── test_user_creation.py      # تست‌های ایجاد کاربر
│   ├── test_user_purchase.py      # تست‌های خرید کاربران
│   ├── test_permissions.py        # تست‌های مجوزها
│   └── test_payments.py           # تست‌های پرداخت
├── conftest.py                    # فیکسچرهای pytest
├── pytest.ini                    # تنظیمات pytest
├── run_tests.py                   # اجراکننده تست‌ها
└── README_TESTS.md               # این فایل
```

## 🧪 انواع تست‌ها

### 1. تست‌های ایجاد کاربر (`test_user_creation.py`)

- **TestUserCreation**: تست‌های unittest برای ایجاد کاربران
  - ایجاد Super Admin
  - ایجاد Admin
  - ایجاد Finance
  - ایجاد Customer
  - اعتبارسنجی شماره تلفن
  - یکتایی نام کاربری و شماره تلفن
  - تعیین گروه‌های کاربر
  - ایجاد خودکار پروفایل مشتری

- **TestUserCreationIntegration**: تست‌های یکپارچگی
  - ایجاد چندین کاربر همزمان
  - تعیین مجوزها
  - ایجاد همزمان کاربران

- **TestUserCreationPytest**: تست‌های pytest
  - استفاده از فیکسچرها
  - تست‌های پارامتری
  - Factory Pattern

### 2. تست‌های خرید کاربران (`test_user_purchase.py`)

- **TestUserPurchaseProcess**: فرآیند کامل خرید
  - ایجاد سفارش
  - افزودن آیتم‌ها
  - محاسبه قیمت و تخفیف
  - انواع روش‌های پرداخت
  - بررسی موجودی محصولات
  - تغییر وضعیت سفارش

- **TestCustomerPurchasePermissions**: کنترل دسترسی
  - مجوزهای مشتری فعال/غیرفعال
  - محدودیت دسترسی به سفارشات

### 3. تست‌های مجوزها (`test_permissions.py`)

- **TestRoleBasedPermissions**: مجوزهای مبتنی بر نقش
  - تست مجوزهای هر نقش
  - کنترل دسترسی‌های مختلف

- **TestPermissionDecorators**: دکوریتورهای مجوز
  - `@super_admin_required`
  - `@admin_required`
  - `@role_required`
  - `@check_user_permission`

- **TestPermissionMixins**: میکسین‌های مجوز
  - `SuperAdminRequiredMixin`
  - `AdminRequiredMixin`
  - `RoleRequiredMixin`

### 4. تست‌های پرداخت (`test_payments.py`)

- **TestPaymentCreation**: ایجاد پرداخت
  - ایجاد پرداخت پایه
  - تولید کد پیگیری
  - تغییر وضعیت پرداخت
  - علامت‌گذاری موفق/ناموفق

- **TestPaymentGateways**: درگاه‌های پرداخت
  - زرین‌پال
  - شاپرک
  - Mock درگاه‌ها

- **TestPaymentService**: سرویس پرداخت
  - محاسبه مبلغ نقدی
  - ایجاد پرداخت از سفارش
  - تایید پرداخت

## 🔧 نحوه اجرا

### اجرای کامل تست‌ها
```bash
python run_tests.py
```

### اجرای فقط unittest
```bash
python run_tests.py --unittest-only
```

### اجرای فقط pytest
```bash
python run_tests.py --pytest-only
```

### اجرای دسته‌بندی خاص
```bash
python run_tests.py --markers unit
python run_tests.py --markers permissions
python run_tests.py --markers payments
```

### تولید گزارش HTML
```bash
python run_tests.py --html-report
```

## 📊 گزارش پوشش کد

```bash
# اجرای با coverage
coverage run --source='.' manage.py test

# نمایش گزارش
coverage report --show-missing

# تولید گزارش HTML
coverage html
firefox htmlcov/index.html
```

## 🎭 مارکرهای pytest

- `@pytest.mark.unit`: تست‌های واحد
- `@pytest.mark.integration`: تست‌های یکپارچگی
- `@pytest.mark.permissions`: تست‌های مجوزها
- `@pytest.mark.payments`: تست‌های پرداخت
- `@pytest.mark.user_creation`: تست‌های ایجاد کاربر
- `@pytest.mark.slow`: تست‌های کند

## 🏭 فیکسچرهای موجود

### کاربران
- `super_admin_user`
- `admin_user`
- `finance_user`
- `customer_user`
- `inactive_user`

### مشتریان
- `customer`
- `inactive_customer`

### محصولات
- `product`
- `sold_product`
- `multiple_products`

### سفارشات
- `order`
- `order_with_items`

### پرداخت‌ها
- `payment`
- `successful_payment`
- `failed_payment`

### کلاینت‌های احراز هویت شده
- `authenticated_super_admin_client`
- `authenticated_admin_client`
- `authenticated_finance_client`
- `authenticated_customer_client`

## 📈 آمار پوشش فعلی

هدف: **90% پوشش کد**

### بخش‌های تست شده:
- ✅ مدل‌های User
- ✅ مدل‌های Customer
- ✅ مدل‌های Product
- ✅ مدل‌های Order
- ✅ مدل‌های Payment
- ✅ سیستم مجوزها
- ✅ دکوریتورها و میکسین‌ها
- ✅ فرآیند خرید
- ✅ درگاه‌های پرداخت

## 🐛 رفع اشکالات رایج

### خطای UNIQUE constraint
اگر این خطا رخ دهد:
```
IntegrityError: UNIQUE constraint failed
```

باید فیکسچرها را با نام‌های یکتا ایجاد کرد.

### خطای Permission denied
برای رفع مشکلات مجوزها:
```python
# اطمینان از ایجاد گروه‌ها
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_default_groups()
```

## 🚀 افزودن تست جدید

### 1. تست unittest
```python
class TestNewFeature(TestCase):
    def setUp(self):
        # تنظیمات اولیه
        pass
    
    def test_feature(self):
        # تست ویژگی
        self.assertEqual(result, expected)
```

### 2. تست pytest
```python
@pytest.mark.unit
def test_new_feature(fixture_name):
    # تست با فیکسچر
    assert result == expected
```

## 📝 بهترین شیوه‌ها

1. **نام‌گذاری**: نام‌های توصیفی و فارسی برای تست‌ها
2. **مستقل بودن**: هر تست مستقل از دیگران
3. **پاک‌سازی**: استفاده از فیکسچرها برای داده‌های تست
4. **مارکرگذاری**: دسته‌بندی تست‌ها با مارکرهای مناسب
5. **مستندسازی**: کامنت‌های فارسی برای توضیح تست‌ها

## 📞 پشتیبانی

برای مشکلات تست:
1. بررسی لاگ‌های خطا
2. اجرای تست‌های مجزا
3. بررسی فیکسچرها
4. اطمینان از صحت تنظیمات

---

**🎯 هدف: دستیابی به 90% پوشش کد و اطمینان از کیفیت نرم‌افزار** 