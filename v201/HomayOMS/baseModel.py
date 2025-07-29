"""
🏗️ مدل پایه برای پروژه HomayOMS
📋 این ماژول شامل کلاس مدل انتزاعی پایه است که فیلدهای مشترک
⏰ مانند created_at و updated_at را به تمام مدل‌هایی که از آن ارث‌بری می‌کنند اضافه می‌کند
"""

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    🏗️ مدل پایه انتزاعی که فیلدهای زمانی خودکار ارائه می‌دهد
    
    🎯 تمام مدل‌های پروژه باید از این مدل پایه ارث‌بری کنند
    ✅ این کار تضمین می‌کند که ردیابی زمان ایجاد و به‌روزرسانی در تمام اپلیکیشن یکسان باشد
    
    📋 فیلدها:
        created_at (DateTimeField): به صورت خودکار هنگام ایجاد اولین بار تنظیم می‌شود
        updated_at (DateTimeField): به صورت خودکار هنگام هر ذخیره‌سازی به‌روزرسانی می‌شود
    
    🔧 نحوه استفاده:
        class YourModel(BaseModel):
            # فیلدهای مدل شما در اینجا
            name = models.CharField(max_length=100)
            
        # مدل به طور خودکار دارای فیلدهای created_at و updated_at خواهد بود
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="📅 تاریخ ایجاد",
        help_text="تاریخ و زمان ایجاد رکورد به صورت خودکار ثبت می‌شود"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="🔄 تاریخ به‌روزرسانی",
        help_text="تاریخ و زمان آخرین به‌روزرسانی رکورد به صورت خودکار ثبت می‌شود"
    )
    
    class Meta:
        abstract = True  # 🏗️ مدل انتزاعی - جدول مستقل ایجاد نمی‌شود
        # 📊 مرتب‌سازی پیش‌فرض بر اساس تاریخ ایجاد (جدیدترین ابتدا)
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """
        🔄 بازنویسی متد save برای اطمینان از به‌روزرسانی درست updated_at
        ⏰ این متد تضمین می‌کند که فیلد updated_at همیشه به زمان جاری تنظیم شود
        """
        # 🕐 به‌روزرسانی دستی فیلد updated_at برای اطمینان از درستی زمان
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_created_at_jalali(self):
        """
        📅 متد برای دریافت created_at در قالب تقویم جلالی (شمسی)
        🔮 این متد بعداً هنگام اضافه کردن پشتیبانی از تاریخ جلالی توسعه خواهد یافت
        """
        # TODO: 🚧 پیاده‌سازی تبدیل تاریخ جلالی هنگام نیاز
        return self.created_at
    
    def get_updated_at_jalali(self):
        """
        📅 متد برای دریافت updated_at در قالب تقویم جلالی (شمسی)
        🔮 این متد بعداً هنگام اضافه کردن پشتیبانی از تاریخ جلالی توسعه خواهد یافت
        """
        # TODO: 🚧 پیاده‌سازی تبدیل تاریخ جلالی هنگام نیاز
        return self.updated_at
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای شیء که تاریخ ایجاد را نشان می‌دهد
        ⚠️ این متد باید در کلاس‌های فرزند برای نمایش معنادارتر بازنویسی شود
        """
        return f"📅 ایجاد شده در: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}" 