"""
🧪 دستور مدیریت ایجاد محصولات تستی - HomayOMS
📦 این دستور برای ایجاد محصولات نمونه و تست سیستم لاگ‌گیری استفاده می‌شود
🎯 هدف: نمایش قابلیت‌های سیستم ثبت محصولات و فعالیت‌ها

🔧 استفاده:
    python manage.py create_test_products
    python manage.py create_test_products --count 10
    python manage.py create_test_products --clear
"""

import random
import string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.models import Product, ActivityLog
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    """
    📦 دستور ایجاد محصولات تستی
    🎛️ کلاس فرماندهی برای ایجاد داده‌های نمونه محصولات
    """
    
    help = '🧪 ایجاد محصولات تستی برای نمایش قابلیت‌های سیستم'
    
    def add_arguments(self, parser):
        """
        ⚙️ اضافه کردن آرگومان‌های خط فرمان
        """
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='تعداد محصولات تستی که باید ایجاد شود'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='🗑️ حذف تمام محصولات موجود قبل از ایجاد محصولات جدید'
        )
        
        parser.add_argument(
            '--no-logs',
            action='store_true',
            help='📜 عدم ایجاد لاگ‌های فعالیت (فقط برای تست)'
        )
    
    def handle(self, *args, **options):
        """
        🚀 اجرای اصلی دستور
        """
        count = options['count']
        clear = options['clear']
        no_logs = options['no_logs']
        
        # 🎨 رنگ‌ها برای خروجی زیبا
        self.style.SUCCESS = self.style.SUCCESS
        self.style.WARNING = self.style.WARNING
        self.style.ERROR = self.style.ERROR
        
        try:
            # 🗑️ حذف محصولات موجود (در صورت درخواست)
            if clear:
                self.stdout.write('🗑️ در حال حذف محصولات موجود...')
                deleted_count = Product.objects.count()
                Product.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f'🗑️ {deleted_count} محصول حذف شد.')
                )
            
            # 👤 پیدا کردن یا ایجاد کاربر سیستم
            admin_user = self._get_or_create_admin_user()
            
            # 📦 ایجاد محصولات تستی
            self.stdout.write(f'📦 در حال ایجاد {count} محصول تستی...')
            
            created_products = []
            for i in range(count):
                product = self._create_test_product(i + 1)
                created_products.append(product)
                
                # 📜 ثبت لاگ فعالیت (در صورت عدم غیرفعال بودن)
                if not no_logs:
                    ActivityLog.log_activity(
                        user=admin_user,
                        action='CREATE',
                        description=f'محصول تستی {product.reel_number} ایجاد شد',
                        content_object=product,
                        severity='LOW',
                        **product.get_product_info()
                    )
                
                # 🎯 نمایش پیشرفت
                if (i + 1) % 10 == 0 or (i + 1) == count:
                    self.stdout.write(f'  ✅ {i + 1}/{count} محصول ایجاد شد')
            
            # 📊 خلاصه نتایج
            self._display_summary(created_products, no_logs)
            
            # 🎉 پیام موفقیت
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 عملیات با موفقیت انجام شد! {len(created_products)} محصول ایجاد شد.'
                )
            )
            
        except Exception as e:
            # ❌ مدیریت خطاها
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در اجرای دستور: {str(e)}')
            )
            raise CommandError(f'❌ خطا در ایجاد محصولات تستی: {str(e)}')
    
    def _get_or_create_admin_user(self):
        """
        👤 پیدا کردن یا ایجاد کاربر مدیر برای ثبت لاگ‌ها
        """
        try:
            # سعی در پیدا کردن سوپر یوزر
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                self.stdout.write(f'👤 استفاده از کاربر مدیر: {admin_user.username}')
                return admin_user
            
            # اگر سوپر یوزر وجود نداشت، از کاربر فعال استفاده کن
            admin_user = User.objects.filter(is_active=True).first()
            if admin_user:
                self.stdout.write(f'👤 استفاده از کاربر فعال: {admin_user.username}')
                return admin_user
            
            # اگر هیچ کاربری وجود نداشت، کاربر سیستمی ایجاد کن
            admin_user = User.objects.create_user(
                username='system_test',
                email='system@homayoms.local',
                password='temp_password_123',
                first_name='سیستم',
                last_name='تست'
            )
            self.stdout.write(
                self.style.WARNING(f'👤 کاربر سیستمی جدید ایجاد شد: {admin_user.username}')
            )
            return admin_user
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ عدم توانایی در پیدا کردن کاربر: {str(e)}')
            )
            return None
    
    def _create_test_product(self, index):
        """
        📦 ایجاد یک محصول تستی
        """
        # 🏷️ ایجاد شماره ریل یکتا
        reel_number = f"TEST-{index:04d}-{self._generate_random_string(4)}"
        
        # 📍 انتخاب تصادفی مکان انبار
        locations = [choice[0] for choice in Product.LOCATION_CHOICES]
        location = random.choice(locations)
        
        # 📊 انتخاب تصادفی وضعیت
        statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        status = random.choice(statuses)
        
        # 📏 مشخصات تصادفی
        width = random.randint(800, 1600)  # میلی‌متر
        gsm = random.choice([70, 80, 90, 100, 120, 140, 160])  # گرم بر متر مربع
        length = random.randint(500, 2000)  # متر
        grade = random.choice(['A', 'B', 'C', 'A+', 'B+'])
        breaks = random.randint(0, 5)
        
        # 📱 ایجاد کد QR نمونه
        qr_code = f"QR-{reel_number}-{random.randint(1000, 9999)}"
        
        # 💰 محاسبه قیمت بر اساس ابعاد و کیفیت
        area = Decimal(width * length) / Decimal('1000.0')  # متر مربع
        weight = area * Decimal(gsm) / Decimal('1000.0')  # کیلوگرم
        
        # قیمت پایه بر اساس کیفیت
        base_price_per_kg = {
            'A+': Decimal('45000'),
            'A': Decimal('40000'),
            'B+': Decimal('38000'),
            'B': Decimal('35000'),
            'C': Decimal('30000'),
        }.get(grade, Decimal('35000'))
        
        # قیمت کل با تغییرات تصادفی
        total_price = weight * base_price_per_kg
        # اضافه کردن تغییرات تصادفی ±15%
        price_variation = Decimal(str(random.uniform(0.85, 1.15)))
        final_price = (total_price * price_variation).quantize(Decimal('1'))
        
        # 🏗️ ایجاد محصول
        product = Product.objects.create(
            reel_number=reel_number,
            location=location,
            status=status,
            width=width,
            gsm=gsm,
            length=length,
            grade=grade,
            breaks=breaks,
            price=final_price,
            qr_code=qr_code
        )
        
        return product
    
    def _generate_random_string(self, length):
        """
        🔤 ایجاد رشته تصادفی
        """
        letters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    def _display_summary(self, products, no_logs):
        """
        📊 نمایش خلاصه محصولات ایجاد شده
        """
        if not products:
            return
        
        self.stdout.write('\n📊 خلاصه محصولات ایجاد شده:')
        self.stdout.write('=' * 50)
        
        # 📈 آمار کلی
        total_area = sum(p.get_total_area() for p in products)
        total_weight = sum(p.get_total_weight() for p in products)
        
        self.stdout.write(f'📦 تعداد کل: {len(products)} محصول')
        self.stdout.write(f'📐 مساحت کل: {total_area:.2f} متر مربع')
        self.stdout.write(f'⚖️ وزن کل: {total_weight:.2f} کیلوگرم')
        
        # 📍 آمار بر اساس مکان
        location_stats = {}
        for product in products:
            location = product.get_location_display()
            location_stats[location] = location_stats.get(location, 0) + 1
        
        self.stdout.write('\n📍 توزیع بر اساس مکان انبار:')
        for location, count in location_stats.items():
            self.stdout.write(f'  • {location}: {count} محصول')
        
        # 📊 آمار بر اساس وضعیت
        status_stats = {}
        for product in products:
            status = product.get_status_display()
            status_stats[status] = status_stats.get(status, 0) + 1
        
        self.stdout.write('\n📊 توزیع بر اساس وضعیت:')
        for status, count in status_stats.items():
            self.stdout.write(f'  • {status}: {count} محصول')
        
        # 📜 آمار لاگ‌ها
        if not no_logs:
            log_count = ActivityLog.objects.filter(action='CREATE').count()
            self.stdout.write(f'\n📜 تعداد لاگ‌های ثبت شده: {log_count}')
        
        self.stdout.write('=' * 50) 