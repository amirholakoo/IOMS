# 🔍 راهنمای عیب‌یابی سیستم خودکار لغو سفارشات

## 🚨 **مشکل: تغییر وضعیت سفارشات دیده نمی‌شود**

### **مراحل عیب‌یابی:**

## 1️⃣ **بررسی تنظیمات**

### **الف) بررسی فایل تنظیمات**
```bash
# فایل: v200/HomayOMS/settings/base.py
# خط 157 باید این باشد:
ORDER_CANCELLATION_TIMEOUT = 1  # 1 دقیقه برای تست
```

### **ب) بررسی لاگ‌های Django**
```bash
# هنگام راه‌اندازی سرور، این پیام‌ها را باید ببینید:
🤖 سیستم خودکار آماده است
# یا
🤖 سیستم خودکار شروع شد
```

## 2️⃣ **بررسی وضعیت فعلی**

### **الف) بررسی سفارشات Processing**
```bash
# در Django shell یا admin panel
python manage.py shell

>>> from core.models import Order
>>> from django.utils import timezone
>>> from datetime import timedelta

# تعداد سفارشات Processing
>>> Order.objects.filter(status='Processing').count()

# جزئیات سفارشات Processing
>>> for order in Order.objects.filter(status='Processing'):
...     time_diff = timezone.now() - order.updated_at
...     print(f"{order.order_number}: {time_diff.total_seconds()/60:.1f} دقیقه")
```

### **ب) بررسی لاگ‌های اخیر**
```bash
>>> from core.models import ActivityLog
>>> recent_logs = ActivityLog.objects.filter(action='CANCEL').order_by('-created_at')[:5]
>>> for log in recent_logs:
...     print(f"{log.created_at}: {log.description}")
```

## 3️⃣ **مشکلات احتمالی و راه‌حل‌ها**

### **مشکل 1: سیستم خودکار شروع نشده**

**نشانه‌ها:**
- لاگ‌های راه‌اندازی نشان نمی‌دهد "سیستم خودکار شروع شد"
- هیچ لاگ لغو خودکار وجود ندارد

**راه‌حل:**
```bash
# راه‌اندازی دستی سیستم
python manage.py shell

>>> from core.signals import start_automated_cancellation
>>> start_automated_cancellation()
```

### **مشکل 2: سفارشات Processing وجود ندارند**

**نشانه‌ها:**
- `Order.objects.filter(status='Processing').count()` برابر 0 است

**راه‌حل:**
1. یک سفارش Processing ایجاد کنید:
   - وارد سیستم شوید
   - محصولات انتخاب کنید
   - روی "Proceed" کلیک کنید
   - صفحه را رها کنید

### **مشکل 3: سفارشات هنوز منقضی نشده‌اند**

**نشانه‌ها:**
- سفارشات Processing وجود دارند اما کمتر از 1 دقیقه قدیمی هستند

**راه‌حل:**
```bash
# بررسی زمان سفارشات
>>> for order in Order.objects.filter(status='Processing'):
...     time_diff = timezone.now() - order.updated_at
...     print(f"{order.order_number}: {time_diff.total_seconds()/60:.1f} دقیقه")
...     if time_diff.total_seconds() < 60:
...         print("  ⏰ هنوز منقضی نشده")
...     else:
...         print("  ✅ منقضی شده")
```

### **مشکل 4: سیگنال‌ها ثبت نشده‌اند**

**نشانه‌ها:**
- تغییرات وضعیت لاگ نمی‌شوند

**راه‌حل:**
```bash
# بررسی ثبت سیگنال‌ها
python manage.py shell

>>> from django.db.models.signals import post_save
>>> from core.models import Order
>>> from core.signals import handle_order_status_change

# بررسی اینکه آیا سیگنال ثبت شده
>>> receivers = post_save._live_receivers
>>> for receiver in receivers:
...     if 'handle_order_status_change' in str(receiver):
...         print("✅ سیگنال ثبت شده")
...         break
... else:
...     print("❌ سیگنال ثبت نشده")
```

## 4️⃣ **تست سریع**

### **تست 1: اجرای دستی تابع لغو**
```bash
python manage.py shell

>>> from core.signals import cancel_expired_processing_orders
>>> cancelled_count = cancel_expired_processing_orders()
>>> print(f"{cancelled_count} سفارش لغو شد")
```

### **تست 2: بررسی وضعیت سیستم خودکار**
```bash
python manage.py shell

>>> from core.signals import is_automation_running
>>> status = is_automation_running()
>>> print(f"سیستم خودکار: {'در حال اجرا' if status else 'متوقف'}")
```

### **تست 3: شروع دستی سیستم**
```bash
python manage.py shell

>>> from core.signals import start_automated_cancellation
>>> thread = start_automated_cancellation()
>>> print(f"Thread ID: {thread.ident}")
```

## 5️⃣ **بررسی از طریق Admin Panel**

### **الف) بررسی سفارشات**
1. به `http://localhost:8000/admin/` بروید
2. روی "Orders" کلیک کنید
3. فیلتر بر اساس Status = "Processing"
4. زمان "Updated at" را بررسی کنید

### **ب) بررسی لاگ‌ها**
1. در Admin Panel، روی "Activity logs" کلیک کنید
2. فیلتر بر اساس Action = "CANCEL"
3. لاگ‌های اخیر را بررسی کنید

## 6️⃣ **تست با اسکریپت سریع**

```bash
# اجرای اسکریپت تست
python test_automation_quick.py
```

این اسکریپت:
- وضعیت سیستم را بررسی می‌کند
- سفارشات Processing را لیست می‌کند
- تابع لغو خودکار را اجرا می‌کند
- نتایج را نمایش می‌دهد

## 7️⃣ **نشانه‌های موفقیت**

### **✅ سیستم کار می‌کند اگر:**
1. لاگ‌های راه‌اندازی نشان می‌دهد "سیستم خودکار شروع شد"
2. لاگ‌های لغو خودکار وجود دارند
3. سفارشات از `Processing` به `Cancelled` تغییر کرده‌اند
4. محصولات از `Pre-order` به `In-stock` تغییر کرده‌اند

### **❌ سیستم کار نمی‌کند اگر:**
1. لاگ‌های راه‌اندازی وجود ندارند
2. سفارشات Processing باقی مانده‌اند
3. هیچ لاگ لغو خودکار وجود ندارد

## 8️⃣ **درخواست کمک**

اگر مشکل حل نشد، این اطلاعات را ارائه دهید:

1. **خروجی لاگ‌های Django**
2. **نتیجه `Order.objects.filter(status='Processing').count()`**
3. **نتیجه `ActivityLog.objects.filter(action='CANCEL').count()`**
4. **مقدار `ORDER_CANCELLATION_TIMEOUT` در تنظیمات**
5. **زمان ایجاد آخرین سفارش Processing** 