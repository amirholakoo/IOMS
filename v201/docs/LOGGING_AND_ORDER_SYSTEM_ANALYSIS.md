# 🔍 تحلیل سیستم لاگ‌گیری و بخش سفارشات HomayOMS

## 📋 خلاصه اجرایی

این سند تحلیل کامل سیستم لاگ‌گیری و بخش سفارشات HomayOMS را ارائه می‌دهد و پیشنهادات بهبود را برای بهینه‌سازی عملکرد و تجربه کاربری ارائه می‌کند.

## 🏗️ معماری فعلی سیستم

### 📜 سیستم لاگ‌گیری (ActivityLog)

#### ✅ نقاط قوت:
- **مدل جامع**: ActivityLog با GenericForeignKey قابلیت اتصال به هر مدلی
- **سطوح اهمیت**: 4 سطح (LOW, MEDIUM, HIGH, CRITICAL)
- **انواع عملیات**: 20 نوع مختلف عملیات تعریف شده
- **اطلاعات کامل**: IP، User Agent، Extra Data (JSON)
- **ایندکس‌گذاری**: بهینه‌سازی برای جستجو و فیلتر

#### 🔧 پیاده‌سازی فعلی:
```python
# ثبت لاگ در تمام عملیات مهم
ActivityLog.log_activity(
    user=request.user,
    action='CREATE',
    description='ایجاد سفارش جدید',
    content_object=order,
    severity='HIGH',
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT'),
    extra_data={'order_number': order.order_number}
)
```

### 🛒 سیستم سفارشات (Order & OrderItem)

#### ✅ نقاط قوت:
- **وضعیت‌های جامع**: 7 وضعیت مختلف (Pending, Confirmed, Processing, etc.)
- **روش‌های پرداخت**: 4 نوع (Cash, Terms, Bank_Transfer, Check)
- **مدل OrderItem**: امکان پرداخت جداگانه برای هر محصول
- **محاسبات خودکار**: تخفیف، مبلغ نهایی، وزن کل

#### 🔧 جریان فعلی:
1. **انتخاب محصولات** → سبد خرید (Session)
2. **تکمیل سفارش** → ایجاد Order + OrderItems
3. **تایید توسط Admin** → تغییر وضعیت
4. **پرداخت** → سیستم پرداخت (در v1 موجود)

## 🚨 مشکلات شناسایی شده

### 1. 🔄 عدم یکپارچگی سیستم پرداخت
- **مشکل**: در v1.1 سیستم پرداخت موجود نیست
- **تاثیر**: سفارشات نقدی بدون پرداخت ثبت می‌شوند
- **راه‌حل**: انتقال سیستم پرداخت از v1 به v1.1

### 2. 📊 عدم گزارش‌گیری جامع
- **مشکل**: لاگ‌ها فقط در دیتابیس ذخیره می‌شوند
- **تاثیر**: تحلیل داده‌ها دشوار است
- **راه‌حل**: سیستم گزارش‌گیری خودکار

### 3. 🔍 عدم ردیابی کامل سفارشات
- **مشکل**: تغییرات وضعیت سفارشات به درستی لاگ نمی‌شود
- **تاثیر**: عدم شفافیت در فرآیند
- **راه‌حل**: لاگ‌گیری خودکار تغییرات

### 4. ⚡ عملکرد پایین
- **مشکل**: لاگ‌های زیاد روی عملکرد تاثیر می‌گذارند
- **تاثیر**: کندی سیستم
- **راه‌حل**: بهینه‌سازی و کش‌گذاری

## 💡 پیشنهادات بهبود

### 1. 🔄 یکپارچه‌سازی سیستم پرداخت

#### الف) انتقال مدل‌های پرداخت:
```python
# v1.1/payments/models.py
class Payment(BaseModel):
    order = models.ForeignKey('core.Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    tracking_code = models.CharField(max_length=100, unique=True)
    # ... سایر فیلدها
```

#### ب) سرویس پرداخت:
```python
# v1.1/payments/services.py
class PaymentService:
    @classmethod
    def create_payment_from_order(cls, order, gateway_name='zarinpal'):
        # محاسبه مبلغ نقدی
        cash_amount = cls._calculate_cash_payment_amount(order)
        
        if cash_amount > 0:
            payment = Payment.objects.create(
                order=order,
                amount=cash_amount,
                gateway=gateway_name
            )
            return payment
        return None
```

### 2. 📊 سیستم گزارش‌گیری خودکار

#### الف) مدل گزارش‌گیری:
```python
# v1.1/core/models.py
class SystemReport(BaseModel):
    REPORT_TYPES = [
        ('DAILY_SALES', '📊 فروش روزانه'),
        ('CUSTOMER_ACTIVITY', '👥 فعالیت مشتریان'),
        ('INVENTORY_STATUS', '📦 وضعیت انبار'),
        ('PAYMENT_ANALYSIS', '💰 تحلیل پرداخت‌ها'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
```

#### ب) سرویس گزارش‌گیری:
```python
# v1.1/core/services.py
class ReportingService:
    @classmethod
    def generate_daily_sales_report(cls, date=None):
        if not date:
            date = timezone.now().date()
        
        orders = Order.objects.filter(
            created_at__date=date,
            status__in=['Confirmed', 'Delivered']
        )
        
        report_data = {
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(Sum('final_amount')),
            'payment_methods': orders.values('payment_method').annotate(count=Count('id')),
            'top_customers': orders.values('customer__customer_name').annotate(
                total_spent=Sum('final_amount')
            ).order_by('-total_spent')[:10]
        }
        
        return SystemReport.objects.create(
            report_type='DAILY_SALES',
            data=report_data
        )
```

### 3. 🔍 ردیابی کامل سفارشات

#### الف) سیگنال‌های Django:
```python
# v1.1/core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=Order)
def log_order_status_change(sender, instance, created, **kwargs):
    if created:
        # لاگ ایجاد سفارش جدید
        ActivityLog.log_activity(
            user=instance.created_by,
            action='CREATE',
            description=f'ایجاد سفارش جدید {instance.order_number}',
            content_object=instance,
            severity='HIGH'
        )
    else:
        # لاگ تغییر وضعیت
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            ActivityLog.log_activity(
                user=instance.created_by,
                action='UPDATE',
                description=f'تغییر وضعیت سفارش {instance.order_number} از {old_status} به {instance.status}',
                content_object=instance,
                severity='MEDIUM'
            )
```

#### ب) مدل Order با ردیابی تغییرات:
```python
# v1.1/core/models.py
from model_utils import FieldTracker

class Order(BaseModel):
    # ... فیلدهای موجود ...
    tracker = FieldTracker(fields=['status', 'payment_method'])
```

### 4. ⚡ بهینه‌سازی عملکرد

#### الف) کش‌گذاری لاگ‌ها:
```python
# v1.1/core/cache.py
from django.core.cache import cache
from django.conf import settings

class LogCache:
    CACHE_KEY_PREFIX = 'activity_logs'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_recent_logs(cls, user_id=None, action=None, limit=50):
        cache_key = f"{cls.CACHE_KEY_PREFIX}:recent:{user_id}:{action}:{limit}"
        
        logs = cache.get(cache_key)
        if logs is None:
            queryset = ActivityLog.objects.select_related('user', 'content_type')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            if action:
                queryset = queryset.filter(action=action)
            
            logs = list(queryset.order_by('-created_at')[:limit])
            cache.set(cache_key, logs, cls.CACHE_TIMEOUT)
        
        return logs
```

#### ب) لاگ‌گیری غیرهمزمان:
```python
# v1.1/core/tasks.py
from celery import shared_task

@shared_task
def log_activity_async(user_id, action, description, content_type_id=None, 
                      object_id=None, severity='LOW', **extra_data):
    """لاگ‌گیری غیرهمزمان برای بهبود عملکرد"""
    try:
        user = User.objects.get(id=user_id) if user_id else None
        content_object = None
        
        if content_type_id and object_id:
            content_type = ContentType.objects.get(id=content_type_id)
            content_object = content_type.get_object_for_this_type(id=object_id)
        
        ActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            content_object=content_object,
            severity=severity,
            extra_data=extra_data
        )
    except Exception as e:
        logger.error(f"Error in async logging: {e}")
```

### 5. 🎯 بهبود تجربه کاربری

#### الف) داشبورد مدیریتی پیشرفته:
```python
# v1.1/core/views.py
@login_required
@check_user_permission('is_admin')
def advanced_dashboard_view(request):
    """داشبورد پیشرفته با آمار زنده"""
    
    # آمار زنده
    live_stats = {
        'active_orders': Order.objects.filter(status='Pending').count(),
        'today_sales': Order.objects.filter(
            created_at__date=timezone.now().date(),
            status__in=['Confirmed', 'Delivered']
        ).aggregate(total=Sum('final_amount')),
        'recent_activities': ActivityLog.objects.select_related('user')[:10],
        'low_stock_products': Product.objects.filter(
            status='In-stock'
        ).annotate(
            order_count=Count('orderitem')
        ).filter(order_count__gt=0)[:5]
    }
    
    # نمودارها
    charts_data = {
        'daily_sales': get_daily_sales_chart_data(),
        'payment_methods': get_payment_methods_chart_data(),
        'customer_activity': get_customer_activity_chart_data()
    }
    
    context = {
        'live_stats': live_stats,
        'charts_data': charts_data,
        'recent_alerts': get_system_alerts()
    }
    
    return render(request, 'core/advanced_dashboard.html', context)
```

#### ب) سیستم هشدار:
```python
# v1.1/core/models.py
class SystemAlert(BaseModel):
    ALERT_TYPES = [
        ('LOW_STOCK', '📦 موجودی کم'),
        ('PENDING_ORDERS', '⏳ سفارشات در انتظار'),
        ('PAYMENT_ISSUE', '💰 مشکل پرداخت'),
        ('SYSTEM_ERROR', '⚠️ خطای سیستم'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=ActivityLog.SEVERITY_CHOICES)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
```

### 6. 🔐 امنیت و نظارت

#### الف) لاگ‌گیری امنیتی:
```python
# v1.1/core/middleware.py
class SecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # لاگ درخواست‌های مشکوک
        if self._is_suspicious_request(request):
            ActivityLog.log_activity(
                user=None,
                action='WARNING',
                description=f'درخواست مشکوک از IP {get_client_ip(request)}',
                severity='HIGH',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_data={
                    'path': request.path,
                    'method': request.method,
                    'suspicious_reason': self._get_suspicious_reason(request)
                }
            )
        
        response = self.get_response(request)
        return response
    
    def _is_suspicious_request(self, request):
        # بررسی درخواست‌های مشکوک
        suspicious_patterns = [
            '/admin/',  # تلاش دسترسی به admin
            'sql', 'script', 'eval',  # تلاش XSS/SQL Injection
        ]
        
        path = request.path.lower()
        return any(pattern in path for pattern in suspicious_patterns)
```

#### ب) نظارت بر عملکرد:
```python
# v1.1/core/monitoring.py
import time
from functools import wraps

def monitor_performance(func_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # لاگ عملکرد
                if execution_time > 1.0:  # بیش از 1 ثانیه
                    ActivityLog.log_activity(
                        user=None,
                        action='WARNING',
                        description=f'عملکرد کند در {func_name or func.__name__}: {execution_time:.2f}s',
                        severity='MEDIUM',
                        extra_data={
                            'execution_time': execution_time,
                            'function_name': func_name or func.__name__
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # لاگ خطا
                ActivityLog.log_activity(
                    user=None,
                    action='ERROR',
                    description=f'خطا در {func_name or func.__name__}: {str(e)}',
                    severity='HIGH',
                    extra_data={
                        'execution_time': execution_time,
                        'error': str(e),
                        'function_name': func_name or func.__name__
                    }
                )
                raise
        
        return wrapper
    return decorator
```

## 📈 برنامه پیاده‌سازی

### فاز 1: انتقال سیستم پرداخت (1-2 هفته)
1. انتقال مدل‌های Payment از v1 به v1.1
2. یکپارچه‌سازی با سیستم سفارشات فعلی
3. تست عملکرد

### فاز 2: بهبود لاگ‌گیری (1 هفته)
1. پیاده‌سازی سیگنال‌های Django
2. اضافه کردن ردیابی تغییرات
3. بهینه‌سازی عملکرد

### فاز 3: سیستم گزارش‌گیری (2 هفته)
1. ایجاد مدل‌های گزارش
2. پیاده‌سازی سرویس‌های گزارش‌گیری
3. ایجاد داشبورد پیشرفته

### فاز 4: امنیت و نظارت (1 هفته)
1. پیاده‌سازی middleware امنیتی
2. سیستم هشدار
3. نظارت بر عملکرد

## 🎯 نتیجه‌گیری

سیستم فعلی HomayOMS دارای پایه قوی است اما نیاز به بهبودهای زیر دارد:

1. **یکپارچه‌سازی کامل** سیستم پرداخت
2. **گزارش‌گیری خودکار** برای تحلیل بهتر
3. **ردیابی کامل** تغییرات سفارشات
4. **بهینه‌سازی عملکرد** برای مقیاس‌پذیری
5. **امنیت و نظارت** پیشرفته

با پیاده‌سازی این پیشنهادات، سیستم HomayOMS به یک پلتفرم کامل و حرفه‌ای تبدیل خواهد شد که قابلیت مدیریت کسب‌وکارهای بزرگ را خواهد داشت. 