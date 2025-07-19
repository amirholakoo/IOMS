# 🚫 سیستم لغو خودکار سفارشات - HomayOMS

## 📋 خلاصه
سیستم لغو خودکار سفارشات Processing که بیش از زمان تعیین شده در این وضعیت مانده‌اند را به صورت خودکار لغو می‌کند و محصولات مربوطه را آزاد می‌کند.

## 🎯 ویژگی‌ها

### ✅ **ویژگی‌های اصلی**
- ⏰ **لغو خودکار**: سفارشات Processing منقضی شده به صورت خودکار لغو می‌شوند
- 🔧 **قابل تنظیم**: زمان انقضا از طریق تنظیمات قابل تغییر است
- 📦 **آزادسازی محصولات**: محصولات مربوطه به انبار بازگردانده می‌شوند
- 📝 **لاگ کامل**: تمام عملیات در ActivityLog ثبت می‌شود
- 🔔 **سیگنال Django**: استفاده از سیگنال‌های Django برای مدیریت خودکار

### 🛠️ **ابزارهای مدیریتی**
- 📋 **دستور مدیریت**: `python manage.py cancel_expired_orders`
- 🌐 **API دستی**: `POST /core/api/cancel-expired-orders/`
- 🧪 **حالت تست**: امکان تست بدون اجرای واقعی
- 📊 **گزارش‌گیری**: نمایش آمار و جزئیات عملیات

## ⚙️ تنظیمات

### 🔧 **تنظیم زمان انقضا**
در فایل `HomayOMS/settings/base.py`:

```python
# ⏰ تنظیمات لغو خودکار سفارشات
ORDER_CANCELLATION_TIMEOUT = 5  # زمان به دقیقه برای لغو خودکار سفارشات Processing
```

### 📊 **مقادیر پیشنهادی**
- **5 دقیقه**: برای تست و توسعه
- **10 دقیقه**: برای محیط تولید با ترافیک کم
- **15 دقیقه**: برای محیط تولید با ترافیک متوسط
- **30 دقیقه**: برای محیط تولید با ترافیک بالا

## 🚀 نحوه استفاده

### 1️⃣ **اجرای دستی (Management Command)**

```bash
# اجرای عادی
python manage.py cancel_expired_orders

# حالت تست (بدون لغو واقعی)
python manage.py cancel_expired_orders --dry-run

# با زمان انقضای سفارشی
python manage.py cancel_expired_orders --timeout 10

# نمایش جزئیات بیشتر
python manage.py cancel_expired_orders --verbose
```

### 2️⃣ **فراخوانی API**

```python
import requests
import json

# حالت تست
response = requests.post('http://localhost:8000/core/api/cancel-expired-orders/', 
    json={'dry_run': True},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

# اجرای واقعی
response = requests.post('http://localhost:8000/core/api/cancel-expired-orders/', 
    json={'timeout_minutes': 10},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

print(json.loads(response.content))
```

### 3️⃣ **فراخوانی مستقیم تابع**

```python
from core.signals import cancel_expired_processing_orders

# اجرای تابع لغو خودکار
cancelled_count = cancel_expired_processing_orders()
print(f"{cancelled_count} سفارش لغو شد")
```

### 4️⃣ **برنامه‌ریزی خودکار (Cron Job)**

```bash
# هر 5 دقیقه بررسی کن
*/5 * * * * cd /path/to/project && python manage.py cancel_expired_orders

# هر ساعت بررسی کن
0 * * * * cd /path/to/project && python manage.py cancel_expired_orders
```

## 📁 ساختار فایل‌ها

### 🔔 **سیگنال‌ها**
- `v200/core/signals.py`: تعریف سیگنال‌ها و توابع لغو خودکار
- `v200/core/apps.py`: ثبت سیگنال‌ها در اپلیکیشن

### 🌐 **API و Views**
- `v200/core/views.py`: `manual_cancel_expired_orders_view`
- `v200/core/urls.py`: مسیر API

### 📋 **دستورات مدیریت**
- `v200/core/management/commands/cancel_expired_orders.py`: دستور مدیریت

### ⚙️ **تنظیمات**
- `v200/HomayOMS/settings/base.py`: تنظیم `ORDER_CANCELLATION_TIMEOUT`

## 🔄 فرآیند کار

### 📊 **مراحل اجرا**

1. **🔍 شناسایی سفارشات منقضی شده**
   ```python
   expiration_time = timezone.now() - timedelta(minutes=timeout)
   expired_orders = Order.objects.filter(
       status='Processing',
       updated_at__lt=expiration_time
   )
   ```

2. **🚫 لغو سفارشات**
   ```python
   order.status = 'Cancelled'
   order.notes = f"لغو خودکار پس از {timeout} دقیقه"
   order.save()
   ```

3. **📦 آزادسازی محصولات**
   ```python
   for order_item in order.order_items.all():
       product = order_item.product
       if product.status == 'Pre-order':
           product.status = 'In-stock'
           product.save()
   ```

4. **📝 ثبت لاگ**
   ```python
   ActivityLog.log_activity(
       user=None,  # سیستم
       action='CANCEL',
       description=f'سفارش {order.order_number} لغو شد',
       content_object=order,
       severity='HIGH'
   )
   ```

### 🎯 **شرایط لغو**
- ✅ وضعیت سفارش: `Processing`
- ⏰ زمان بروزرسانی: بیش از `ORDER_CANCELLATION_TIMEOUT` دقیقه قبل
- 🔒 دسترسی: فقط Super Admin برای اجرای دستی

## 📊 خروجی و گزارش‌گیری

### 📋 **اطلاعات خروجی**

```json
{
    "success": true,
    "message": "✅ 3 سفارش Processing به صورت خودکار لغو شد",
    "cancelled_count": 3,
    "timeout_minutes": 5
}
```

### 📝 **لاگ‌های ثبت شده**

1. **لاگ لغو سفارش**:
   - `action`: `CANCEL`
   - `description`: توضیح لغو سفارش
   - `severity`: `HIGH`

2. **لاگ آزادسازی محصول**:
   - `action`: `UPDATE`
   - `description`: آزادسازی محصول
   - `severity`: `MEDIUM`

3. **لاگ عملیات دستی**:
   - `action`: `INFO` یا `CANCEL`
   - `description`: عملیات دستی
   - `severity`: `MEDIUM` یا `HIGH`

## 🧪 تست و عیب‌یابی

### 🧪 **تست دستی**

```bash
# اجرای تست
python v200/test_order_cancellation.py
```

### 🔍 **بررسی لاگ‌ها**

```python
from core.models import ActivityLog

# لاگ‌های اخیر لغو
recent_cancellations = ActivityLog.objects.filter(
    action='CANCEL'
).order_by('-created_at')[:10]

for log in recent_cancellations:
    print(f"{log.created_at}: {log.description}")
```

### 📊 **بررسی آمار**

```python
from core.models import Order

# آمار سفارشات
processing_count = Order.objects.filter(status='Processing').count()
cancelled_count = Order.objects.filter(status='Cancelled').count()

print(f"Processing: {processing_count}")
print(f"Cancelled: {cancelled_count}")
```

## ⚠️ نکات مهم

### 🔒 **امنیت**
- فقط Super Admin می‌تواند عملیات دستی را انجام دهد
- تمام عملیات لاگ می‌شوند
- بررسی دسترسی در تمام نقاط

### ⚡ **عملکرد**
- استفاده از `select_related` برای بهینه‌سازی کوئری‌ها
- اجرای عملیات در تراکنش‌های اتمیک
- مدیریت خطا و rollback در صورت نیاز

### 🔄 **نگهداری**
- بررسی منظم لاگ‌ها
- تنظیم زمان انقضا مناسب
- مانیتورینگ عملکرد سیستم

## 🚨 عیب‌یابی

### ❌ **مشکلات رایج**

1. **سفارشات لغو نمی‌شوند**:
   - بررسی تنظیم `ORDER_CANCELLATION_TIMEOUT`
   - بررسی وضعیت سفارشات
   - بررسی لاگ‌های خطا

2. **محصولات آزاد نمی‌شوند**:
   - بررسی وضعیت محصولات
   - بررسی ارتباط سفارش-محصول
   - بررسی لاگ‌های عملیات

3. **خطا در اجرای دستور**:
   - بررسی دسترسی‌ها
   - بررسی تنظیمات Django
   - بررسی لاگ‌های سیستم

### 🔧 **راه‌حل‌ها**

```bash
# بررسی تنظیمات
python manage.py shell
>>> from django.conf import settings
>>> print(settings.ORDER_CANCELLATION_TIMEOUT)

# بررسی سفارشات Processing
python manage.py shell
>>> from core.models import Order
>>> Order.objects.filter(status='Processing').count()

# اجرای تست
python manage.py cancel_expired_orders --dry-run --verbose
```

## 📈 توسعه آینده

### 🚀 **ویژگی‌های پیشنهادی**
- 📧 **اعلان ایمیل**: ارسال اعلان به مدیران
- 📱 **اعلان پیامک**: ارسال پیامک به مشتریان
- 📊 **داشبورد**: نمایش آمار لغو خودکار
- ⏰ **زمان‌بندی پیشرفته**: زمان‌های مختلف برای انواع مختلف سفارش
- 🔄 **بازگردانی**: امکان بازگردانی سفارشات لغو شده

### 🔧 **بهینه‌سازی**
- 🗄️ **ایندکس‌گذاری**: بهینه‌سازی کوئری‌های پایگاه داده
- ⚡ **کش**: استفاده از کش برای بهبود عملکرد
- 📊 **مانیتورینگ**: نظارت بر عملکرد سیستم

---

**📅 آخرین بروزرسانی**: ژانویه 2025  
**👨‍💻 توسعه‌دهنده**: HomayOMS Team  
**📄 نسخه**: 1.0.0 