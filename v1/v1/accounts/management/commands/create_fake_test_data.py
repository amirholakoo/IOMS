"""
🎭 مدیریت دستور ایجاد داده‌های تست جعلی - HomayOMS
📊 این دستور برای ایجاد داده‌های تست واقع‌گرایانه استفاده می‌شود
🔢 شامل کاربران، مشتریان، محصولات، سفارشات و لاگ‌ها
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker
import random
from datetime import timedelta, datetime
from decimal import Decimal
import json

from accounts.models import User, UserSession
from core.models import Customer, Product, Order, OrderItem, ActivityLog, WorkingHours

User = get_user_model()
fake = Faker(['fa_IR'])  # فارسی برای داده‌های واقع‌گرایانه


class Command(BaseCommand):
    help = '🎭 ایجاد داده‌های تست جعلی برای HomayOMS'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='تعداد کاربران جعلی (پیش‌فرض: 50)'
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=100,
            help='تعداد مشتریان جعلی (پیش‌فرض: 100)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=200,
            help='تعداد محصولات جعلی (پیش‌فرض: 200)'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=150,
            help='تعداد سفارشات جعلی (پیش‌فرض: 150)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='پاک کردن تمام داده‌های موجود قبل از ایجاد'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 شروع ایجاد داده‌های تست جعلی...')
        )
        
        if options['clear']:
            self.clear_existing_data()
        
        with transaction.atomic():
            # ایجاد کاربران
            users = self.create_fake_users(options['users'])
            
            # ایجاد مشتریان
            customers = self.create_fake_customers(options['customers'])
            
            # ایجاد محصولات
            products = self.create_fake_products(options['products'])
            
            # ایجاد سفارشات
            orders = self.create_fake_orders(options['orders'], customers, products, users)
            
            # ایجاد لاگ‌های فعالیت
            self.create_fake_activity_logs(users, products, orders)
            
            # ایجاد نشست‌های کاربر
            self.create_fake_user_sessions(users)
            
            # ایجاد ساعات کاری
            self.create_working_hours()
        
        self.stdout.write(
            self.style.SUCCESS('✅ داده‌های تست جعلی با موفقیت ایجاد شدند!')
        )
    
    def clear_existing_data(self):
        """🗑️ پاک کردن تمام داده‌های موجود"""
        self.stdout.write('🗑️ پاک کردن داده‌های موجود...')
        
        # حفظ Super Admin ها
        super_admins = User.objects.filter(role=User.UserRole.SUPER_ADMIN)
        
        UserSession.objects.all().delete()
        ActivityLog.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        WorkingHours.objects.all().delete()
        
        # حذف کاربران غیر Super Admin
        User.objects.exclude(role=User.UserRole.SUPER_ADMIN).delete()
        
        self.stdout.write(
            self.style.WARNING(f'✅ داده‌ها پاک شدند. {super_admins.count()} Super Admin حفظ شدند.')
        )
    
    def create_fake_users(self, count):
        """👥 ایجاد کاربران جعلی با شماره‌های تلفن واقعی"""
        users = []
        
        # نقش‌های مختلف با توزیع واقع‌گرایانه
        roles_distribution = {
            User.UserRole.SUPER_ADMIN: 2,    # 2 Super Admin
            User.UserRole.ADMIN: 5,          # 5 Admin
            User.UserRole.FINANCE: 3,        # 3 Finance
            User.UserRole.CUSTOMER: count - 10  # بقیه Customer
        }
        
        # وضعیت‌های مختلف
        statuses = [User.UserStatus.ACTIVE, User.UserStatus.INACTIVE, User.UserStatus.SUSPENDED]
        
        # بخش‌های مختلف
        departments = [
            'مدیریت', 'فروش', 'مالی', 'انبار', 'تولید', 
            'کیفیت', 'فنی', 'پشتیبانی', 'بازاریابی'
        ]
        
        user_counter = 0
        
        for role, role_count in roles_distribution.items():
            for i in range(role_count):
                if user_counter >= count:
                    break
                
                # ایجاد شماره تلفن واقعی ایرانی
                phone = self.generate_iranian_phone()
                
                # ایجاد نام کاربری منحصر به فرد
                username = f"{role}_{i+1}_{fake.user_name()}"
                
                user = User.objects.create(
                    username=username,
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=phone,
                    role=role,
                    status=random.choice(statuses),
                    department=random.choice(departments) if role != User.UserRole.CUSTOMER else '',
                    notes=fake.text(max_nb_chars=200),
                    is_active=True,
                    password='testpass123'  # رمز عبور ساده برای تست
                )
                
                users.append(user)
                user_counter += 1
                
                self.stdout.write(f'👤 کاربر ایجاد شد: {user.username} - {phone}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(users)} کاربر جعلی ایجاد شدند')
        )
        return users
    
    def create_fake_customers(self, count):
        """👥 ایجاد مشتریان جعلی"""
        customers = []
        statuses = ['Active', 'Inactive', 'Suspended']
        
        for i in range(count):
            # ایجاد شماره تلفن واقعی
            phone = self.generate_iranian_phone()
            
            # ایجاد شناسه ملی واقعی
            national_id = self.generate_iranian_national_id()
            
            # ایجاد کد اقتصادی
            economic_code = self.generate_economic_code()
            
            customer = Customer.objects.create(
                customer_name=fake.company() if random.choice([True, False]) else fake.name(),
                phone=phone,
                address=fake.address(),
                status=random.choice(statuses),
                comments=fake.text(max_nb_chars=300),
                economic_code=economic_code,
                postcode=fake.numerify(text='##########'),  # 10 رقم
                national_id=national_id
            )
            
            customers.append(customer)
            
            if i % 20 == 0:
                self.stdout.write(f'👤 مشتری {i+1}/{count} ایجاد شد')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(customers)} مشتری جعلی ایجاد شدند')
        )
        return customers
    
    def create_fake_products(self, count):
        """📦 ایجاد محصولات جعلی"""
        products = []
        
        # گزینه‌های واقعی برای محصولات کاغذی
        locations = [choice[0] for choice in Product.LOCATION_CHOICES]
        statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        grades = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D']
        
        for i in range(count):
            # ایجاد شماره ریل منحصر به فرد
            reel_number = f"R{str(i+1).zfill(6)}"
            
            # ابعاد واقعی کاغذ
            width = random.choice([70, 80, 90, 100, 110, 120, 130, 140, 150])
            gsm = random.choice([60, 70, 80, 90, 100, 120, 150, 200, 250, 300])
            length = random.randint(500, 2000)
            
            # قیمت واقعی بر اساس GSM و ابعاد
            base_price = (gsm * width * length) / 1000000  # قیمت پایه
            price = round(base_price * random.uniform(0.8, 1.5), 2)
            
            product = Product.objects.create(
                reel_number=reel_number,
                location=random.choice(locations),
                status=random.choice(statuses),
                width=width,
                gsm=gsm,
                length=length,
                grade=random.choice(grades),
                breaks=random.randint(0, 5),
                qr_code=f"QR_{reel_number}_{fake.uuid4()}",
                price=price
            )
            
            products.append(product)
            
            if i % 50 == 0:
                self.stdout.write(f'📦 محصول {i+1}/{count} ایجاد شد')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(products)} محصول جعلی ایجاد شدند')
        )
        return products
    
    def create_fake_orders(self, count, customers, products, users):
        """🛒 ایجاد سفارشات جعلی"""
        orders = []
        
        # فیلتر کردن محصولات موجود
        available_products = [p for p in products if p.status == 'In-stock']
        
        if not available_products:
            self.stdout.write(
                self.style.WARNING('⚠️ هیچ محصول موجودی برای ایجاد سفارش یافت نشد!')
            )
            return orders
        
        order_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        payment_methods = [choice[0] for choice in Order.PAYMENT_METHOD_CHOICES]
        
        # تاریخ‌های شروع و پایان برای فیکر
        start_date = timezone.now() - timedelta(days=180)  # 6 ماه پیش
        end_date = timezone.now()
        
        for i in range(count):
            # انتخاب تصادفی مشتری و محصولات
            customer = random.choice(customers)
            order_products = random.sample(available_products, random.randint(1, 5))
            
            # ایجاد شماره سفارش
            order_number = f"ORD{str(i+1).zfill(6)}"
            
            # تاریخ‌های واقعی
            created_date = fake.date_time_between(
                start_date=start_date,
                end_date=end_date,
                tzinfo=timezone.get_current_timezone()
            )
            
            order = Order.objects.create(
                customer=customer,
                order_number=order_number,
                status=random.choice(order_statuses),
                payment_method=random.choice(payment_methods),
                total_amount=0,  # محاسبه خواهد شد
                discount_percentage=Decimal(str(round(random.uniform(0, 15), 2))),
                notes=fake.text(max_nb_chars=200),
                delivery_address=fake.address(),
                expected_delivery_date=created_date + timedelta(days=random.randint(1, 14)),
                created_by=random.choice(users),
                created_at=created_date
            )
            
            # ایجاد آیتم‌های سفارش
            total_amount = Decimal('0.00')
            for product in order_products:
                quantity = random.randint(1, 10)
                unit_price = product.price
                total_price = Decimal(str(unit_price * quantity))
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    notes=fake.text(max_nb_chars=100)
                )
                
                total_amount += total_price
            
            # به‌روزرسانی مبلغ کل و محاسبه تخفیف
            order.total_amount = total_amount
            order.discount_amount = (total_amount * order.discount_percentage) / 100
            order.final_amount = total_amount - order.discount_amount
            order.save()
            
            orders.append(order)
            
            if i % 30 == 0:
                self.stdout.write(f'🛒 سفارش {i+1}/{count} ایجاد شد')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(orders)} سفارش جعلی ایجاد شدند')
        )
        return orders
    
    def create_fake_activity_logs(self, users, products, orders):
        """📜 ایجاد لاگ‌های فعالیت جعلی"""
        actions = [choice[0] for choice in ActivityLog.ACTION_CHOICES]
        severities = [choice[0] for choice in ActivityLog.SEVERITY_CHOICES]
        
        # تاریخ‌های شروع و پایان برای فیکر
        start_date = timezone.now() - timedelta(days=30)  # 30 روز پیش
        end_date = timezone.now()
        
        # لاگ‌های ورود و خروج
        for user in users:
            for _ in range(random.randint(5, 20)):
                login_time = fake.date_time_between(
                    start_date=start_date,
                    end_date=end_date,
                    tzinfo=timezone.get_current_timezone()
                )
                
                ActivityLog.objects.create(
                    user=user,
                    action='LOGIN',
                    description=f'ورود کاربر {user.username} به سیستم',
                    ip_address=fake.ipv4(),
                    user_agent=fake.user_agent(),
                    severity=random.choice(severities),
                    created_at=login_time
                )
        
        # لاگ‌های محصولات
        for product in products:
            ActivityLog.objects.create(
                user=random.choice(users),
                action=random.choice(['CREATE', 'UPDATE', 'VIEW']),
                description=f'عملیات روی محصول {product.reel_number}',
                content_object=product,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                severity=random.choice(severities)
            )
        
        # لاگ‌های سفارشات
        for order in orders:
            ActivityLog.objects.create(
                user=order.created_by,
                action=random.choice(['CREATE', 'UPDATE', 'VIEW']),
                description=f'عملیات روی سفارش {order.order_number}',
                content_object=order,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                severity=random.choice(severities)
            )
        
        self.stdout.write(
            self.style.SUCCESS('✅ لاگ‌های فعالیت جعلی ایجاد شدند')
        )
    
    def create_fake_user_sessions(self, users):
        """📱 ایجاد نشست‌های کاربر جعلی"""
        # تاریخ‌های شروع و پایان برای فیکر
        start_date = timezone.now() - timedelta(days=30)  # 30 روز پیش
        end_date = timezone.now()
        
        for user in users:
            for _ in range(random.randint(3, 10)):
                login_time = fake.date_time_between(
                    start_date=start_date,
                    end_date=end_date,
                    tzinfo=timezone.get_current_timezone()
                )
                
                # 80% احتمال خروج
                logout_time = None
                if random.random() < 0.8:
                    logout_time = login_time + timedelta(
                        minutes=random.randint(5, 480)  # 5 دقیقه تا 8 ساعت
                    )
                
                UserSession.objects.create(
                    user=user,
                    login_time=login_time,
                    logout_time=logout_time,
                    ip_address=fake.ipv4(),
                    user_agent=fake.user_agent(),
                    is_active=logout_time is None
                )
        
        self.stdout.write(
            self.style.SUCCESS('✅ نشست‌های کاربر جعلی ایجاد شدند')
        )
    
    def create_working_hours(self):
        """⏰ ایجاد ساعات کاری پیش‌فرض"""
        if not WorkingHours.objects.exists():
            WorkingHours.objects.create(
                start_time="08:00",
                end_time="17:00",
                description="ساعات کاری پیش‌فرض فروشگاه",
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ ساعات کاری پیش‌فرض ایجاد شد')
            )
    
    def generate_iranian_phone(self):
        """📞 تولید شماره تلفن واقعی ایرانی"""
        prefixes = ['912', '913', '914', '915', '916', '917', '918', '919', '930', '931', '932', '933', '934', '935', '936', '937', '938', '939']
        prefix = random.choice(prefixes)
        number = fake.numerify(text='#######')  # 7 رقم
        return f"09{prefix}{number}"
    
    def generate_iranian_national_id(self):
        """🆔 تولید شناسه ملی واقعی ایرانی"""
        # الگوریتم ساده برای تولید شناسه ملی
        digits = [random.randint(0, 9) for _ in range(9)]
        
        # محاسبه رقم کنترل
        sum_digits = sum(digits[i] * (10 - i) for i in range(9))
        remainder = sum_digits % 11
        
        if remainder < 2:
            control_digit = remainder
        else:
            control_digit = 11 - remainder
        
        digits.append(control_digit)
        return ''.join(map(str, digits))
    
    def generate_economic_code(self):
        """💼 تولید کد اقتصادی"""
        return fake.numerify(text='##########')  # 10 رقم 