# 🤖 راهنمای تست سیستم خودکار لغو سفارشات

## 🎯 **سیستم کاملاً خودکار - بدون نیاز به cron jobs**

سیستم جدید به صورت **کاملاً خودکار و machine-driven** کار می‌کند:
- 🤖 **Thread جداگانه** برای بررسی مداوم
- ⏰ **شروع خودکار** هنگام بارگذاری Django
- 🔄 **بررسی هر 60 ثانیه** (قابل تنظیم)
- 🚫 **بدون نیاز به cron jobs**

---

## 🧪 **مراحل تست با Workflow واقعی**

### **مرحله 1: راه‌اندازی سیستم**

```bash
# 1. راه‌اندازی سرور Django
cd v200
python manage.py runserver

# 2. بررسی لاگ‌های راه‌اندازی
# در ترمینال باید این پیام را ببینید:
# "🤖 سیستم خودکار آماده است" یا "🤖 سیستم خودکار شروع شد"
```

### **مرحله 2: تنظیم زمان انقضا کوتاه برای تست**

```python
# در فایل v200/HomayOMS/settings/base.py
ORDER_CANCELLATION_TIMEOUT = 1  # فقط 1 دقیقه برای تست
```

### **مرحله 3: ایجاد سفارش Processing**

#### **3.1 ورود به سیستم**
1. به `http://localhost:8000/accounts/customer/sms-login/` بروید
2. با شماره تلفن مشتری وارد شوید
3. کد تایید را وارد کنید

#### **3.2 انتخاب محصولات**
1. به صفحه اصلی بروید
2. چند محصول انتخاب کنید
3. روی "Proceed" کلیک کنید

#### **3.3 ایجاد سفارش Processing**
1. در صفحه `selected-products`، سفارش به صورت خودکار ایجاد می‌شود
2. وضعیت سفارش: `Processing`
3. محصولات: `Pre-order` (رزرو شده)

### **مرحله 4: انتظار برای لغو خودکار**

#### **4.1 بررسی وضعیت اولیه**
```bash
# در Django shell یا از طریق admin panel
python manage.py shell

>>> from core.models import Order
>>> Order.objects.filter(status='Processing').count()
# باید > 0 باشد
```

#### **4.2 انتظار 1 دقیقه**
- **نکته مهم**: صفحه را رها کنید و کاری نکنید
- سیستم خودکار هر 60 ثانیه بررسی می‌کند
- پس از 1 دقیقه، سفارش باید لغو شود

#### **4.3 بررسی نتیجه**
```bash
python manage.py shell

>>> from core.models import Order
>>> Order.objects.filter(status='Processing').count()
# باید 0 باشد

>>> Order.objects.filter(status='Cancelled').count()
# باید > 0 باشد
```

### **مرحله 5: بررسی لاگ‌ها**

```bash
python manage.py shell

>>> from core.models import ActivityLog
>>> recent_logs = ActivityLog.objects.filter(action='CANCEL').order_by('-created_at')[:3]
>>> for log in recent_logs:
...     print(f"{log.created_at}: {log.description}")
```

---

## 🔧 **کنترل سیستم خودکار**

### **بررسی وضعیت سیستم**

```bash
# GET request
curl http://localhost:8000/core/api/automation-control/
```

**پاسخ نمونه:**
```json
{
    "success": true,
    "automation_running": true,
    "processing_orders": 0,
    "cancelled_orders": 1,
    "recent_automated_actions": [
        {
            "time": "2025-01-16 14:30:15",
            "action": "CANCEL",
            "description": "سفارش ORD-20250116-ABC123 به صورت خودکار لغو شد"
        }
    ]
}
```

### **شروع/توقف سیستم**

```bash
# شروع سیستم
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# توقف سیستم
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# تنظیم فاصله بررسی (30 ثانیه)
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "set_interval", "interval": 30}'
```

---

## 📊 **نشانه‌های موفقیت**

### **✅ نشانه‌های سیستم کار می‌کند:**

1. **در لاگ‌های Django:**
   ```
   🤖 سیستم خودکار لغو سفارشات شروع شد
   🔄 لغو خودکار سفارش ORD-XXX - منقضی شده پس از 1 دقیقه
   ✅ 1 سفارش Processing به صورت خودکار لغو شد
   ```

2. **در ActivityLog:**
   - `action`: `CANCEL`
   - `description`: شامل "به صورت خودکار لغو شد"
   - `extra_data`: `"automated": true`

3. **در پایگاه داده:**
   - سفارش: `status` از `Processing` به `Cancelled` تغییر کرده
   - محصولات: `status` از `Pre-order` به `In-stock` تغییر کرده

### **❌ نشانه‌های مشکل:**

1. **سیستم شروع نشده:**
   ```
   ❌ خطا در راه‌اندازی سیستم خودکار
   ```

2. **سفارش لغو نشده:**
   - سفارش هنوز `Processing` است
   - لاگ‌های لغو وجود ندارد

---

## 🚨 **عیب‌یابی**

### **مشکل 1: سیستم خودکار شروع نشده**

```bash
# بررسی لاگ‌های Django
tail -f v200/logs/django.log

# راه‌اندازی دستی
python manage.py shell
>>> from core.signals import start_automated_cancellation
>>> start_automated_cancellation()
```

### **مشکل 2: سفارش لغو نمی‌شود**

```bash
# بررسی تنظیمات
python manage.py shell
>>> from django.conf import settings
>>> print(settings.ORDER_CANCELLATION_TIMEOUT)

# بررسی سفارشات
>>> from core.models import Order
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> 
>>> # سفارشات Processing
>>> processing_orders = Order.objects.filter(status='Processing')
>>> for order in processing_orders:
...     time_diff = timezone.now() - order.updated_at
...     print(f"{order.order_number}: {time_diff.total_seconds()/60:.1f} دقیقه")
```

### **مشکل 3: محصولات آزاد نمی‌شوند**

```bash
python manage.py shell
>>> from core.models import Product
>>> Product.objects.filter(status='Pre-order').count()
>>> Product.objects.filter(status='In-stock').count()
```

---

## 🎯 **تست‌های پیشرفته**

### **تست 1: چندین سفارش همزمان**

1. چندین مرورگر باز کنید
2. با حساب‌های مختلف وارد شوید
3. سفارشات مختلف ایجاد کنید
4. همه را رها کنید
5. منتظر لغو خودکار بمانید

### **تست 2: تغییر فاصله بررسی**

```bash
# تنظیم بررسی هر 30 ثانیه
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "set_interval", "interval": 30}'
```

### **تست 3: توقف و شروع مجدد**

```bash
# توقف سیستم
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# ایجاد سفارش Processing
# (سفارش لغو نمی‌شود چون سیستم متوقف است)

# شروع مجدد
curl -X POST http://localhost:8000/core/api/automation-control/ \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# (سفارش باید لغو شود)
```

---

## 📋 **چک‌لیست تست**

### **قبل از تست:**
- [ ] سرور Django راه‌اندازی شده
- [ ] `ORDER_CANCELLATION_TIMEOUT = 1` تنظیم شده
- [ ] لاگ‌های راه‌اندازی بررسی شده

### **حین تست:**
- [ ] سفارش Processing ایجاد شده
- [ ] 1 دقیقه انتظار شده
- [ ] وضعیت سفارش بررسی شده

### **بعد از تست:**
- [ ] سفارش لغو شده (`Cancelled`)
- [ ] محصولات آزاد شده (`In-stock`)
- [ ] لاگ‌های خودکار ثبت شده
- [ ] ActivityLog بررسی شده

---

## 🎉 **نتیجه نهایی**

اگر همه مراحل موفقیت‌آمیز باشد:

✅ **سیستم کاملاً خودکار کار می‌کند!**
- 🤖 Thread جداگانه در حال اجرا
- ⏰ بررسی مداوم هر 60 ثانیه
- 🚫 لغو خودکار سفارشات منقضی
- 📦 آزادسازی خودکار محصولات
- 📝 لاگ کامل تمام عملیات

**هیچ cron job یا تنظیم دستی نیاز نیست!** 