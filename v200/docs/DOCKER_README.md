# 🐳 راهنمای کامل Docker برای HomayOMS

## 📋 خلاصه پروژه
**HomayOMS** یک سیستم مدیریت سفارشات و انبار هوشمند است که با Django و PostgreSQL ساخته شده است. این سیستم شامل مدیریت کاربران، محصولات، سفارشات و سیستم لاگ‌گیری کامل است.

## 🚀 راه‌اندازی سریع

### پیش‌نیازها
- Docker Desktop نصب شده
- Docker Compose نصب شده
- حداقل 4GB RAM آزاد

### 1️⃣ کلون کردن پروژه
```bash
git clone <repository-url>
cd HomayOMS-main
```

### 2️⃣ اجرای Docker Compose
```bash
docker-compose up -d
```

### 3️⃣ بررسی وضعیت سرویس‌ها
```bash
docker-compose ps
```

## 🌐 دسترسی به سرویس‌ها

### 🐍 Django Application
- **URL اصلی:** http://localhost:8000
- **پنل مدیریت:** http://localhost:8000/admin/
- **داشبورد Admin:** http://localhost:8000/core/admin-dashboard/
- **داشبورد Finance:** http://localhost:8000/core/finance-dashboard/

### 🐘 PostgreSQL Database
- **Host:** localhost
- **Port:** 5432
- **Database:** homayoms_db
- **Username:** homayoms_user
- **Password:** homayoms_password

### 🐘 pgAdmin (مدیریت پایگاه داده)
- **URL:** http://localhost:5050
- **Email:** admin@homayoms.com
- **Password:** admin123

## 👤 اطلاعات ورود کاربران تست

### 🔑 Super Admin (دسترسی کامل)
- **Username:** admin
- **Password:** admin123
- **Phone:** 09123456789
- **دسترسی:** مدیریت کامل سیستم، تغییر قیمت‌ها، تنظیم ساعات کاری

### 👨‍💼 Admin (مدیر)
- **Username:** admin_user
- **Password:** admin123
- **دسترسی:** مدیریت محصولات، مشتریان، سفارشات

### 💰 Finance (مالی)
- **Username:** finance_user
- **Password:** finance123
- **دسترسی:** مشاهده گزارشات مالی، مدیریت سفارشات

### 👤 Customer (مشتری)
- **Username:** customer_user
- **Password:** customer123
- **Phone:** 09123456789
- **دسترسی:** مشاهده محصولات، ثبت سفارش

## 📱 تست سیستم SMS

### 🔗 ورود با SMS
1. به آدرس http://localhost:8000/accounts/customer-sms-login/ بروید
2. شماره تلفن `09123456789` را وارد کنید
3. کد تایید `123456` را وارد کنید
4. وارد سیستم شوید

### 📋 کدهای تایید تست
- **شماره:** 09123456789
- **کد تایید:** 123456

## 🧪 تست نقش‌های مختلف

### 🔑 تست Super Admin
1. با `admin / admin123` وارد شوید
2. به پنل مدیریت بروید: http://localhost:8000/admin/
3. محصولات را مشاهده کنید و قیمت‌ها را تغییر دهید
4. ساعات کاری را تنظیم کنید: http://localhost:8000/core/working-hours/
5. لاگ‌های فعالیت را مشاهده کنید: http://localhost:8000/core/activity-logs/

### 👨‍💼 تست Admin
1. با `admin_user / admin123` وارد شوید
2. محصولات را مدیریت کنید
3. مشتریان را مشاهده کنید
4. سفارشات را بررسی کنید

### 💰 تست Finance
1. با `finance_user / finance123` وارد شوید
2. گزارشات مالی را مشاهده کنید
3. سفارشات را بررسی کنید

### 👤 تست Customer
1. با `customer_user / customer123` وارد شوید
2. محصولات را مشاهده کنید
3. به سبد خرید اضافه کنید
4. سفارش ثبت کنید

## 🔧 دستورات مفید

### 📊 مشاهده لاگ‌ها
```bash
# تمام سرویس‌ها
docker-compose logs

# سرویس خاص
docker-compose logs web
docker-compose logs db
docker-compose logs pgadmin

# لاگ‌های زنده (real-time)
docker-compose logs -f web
```

### 🛑 توقف سرویس‌ها
```bash
# توقف کامل
docker-compose down

# توقف و حذف volumes (داده‌ها)
docker-compose down -v
```

### 🔄 راه‌اندازی مجدد
```bash
# راه‌اندازی مجدد تمام سرویس‌ها
docker-compose restart

# راه‌اندازی مجدد سرویس خاص
docker-compose restart web
```

### 🧹 پاکسازی
```bash
# حذف کامل (شامل داده‌ها)
docker-compose down -v --remove-orphans

# پاکسازی Docker cache
docker system prune -a
```

### 📦 به‌روزرسانی
```bash
# کشیدن آخرین تغییرات
git pull

# بازسازی image ها
docker-compose build --no-cache

# راه‌اندازی مجدد
docker-compose up -d
```

## 🗄️ مدیریت پایگاه داده

### 🔗 اتصال به PostgreSQL
```bash
# اتصال مستقیم
docker-compose exec db psql -U homayoms_user -d homayoms_db

# مشاهده جداول
\dt

# خروج
\q
```

### 💾 Backup پایگاه داده
```bash
# ایجاد backup
docker-compose exec db pg_dump -U homayoms_user homayoms_db > backup.sql

# Restore از backup
docker-compose exec -T db psql -U homayoms_user -d homayoms_db < backup.sql
```

### 📊 مشاهده داده‌ها
```bash
# مشاهده کاربران
docker-compose exec db psql -U homayoms_user -d homayoms_db -c "SELECT username, role FROM accounts_user;"

# مشاهده محصولات
docker-compose exec db psql -U homayoms_user -d homayoms_db -c "SELECT reel_number, location, status, price FROM core_product LIMIT 10;"

# مشاهده مشتریان
docker-compose exec db psql -U homayoms_user -d homayoms_db -c "SELECT customer_name, phone, status FROM core_customer;"
```

## 🛠️ عیب‌یابی

### 🔍 مشکل اتصال به پایگاه داده
```bash
# بررسی وضعیت PostgreSQL
docker-compose exec db pg_isready -U homayoms_user

# بررسی لاگ‌های PostgreSQL
docker-compose logs db

# راه‌اندازی مجدد پایگاه داده
docker-compose restart db
```

### 🌐 مشکل Django
```bash
# بررسی لاگ‌های Django
docker-compose logs web

# اجرای دستورات Django
docker-compose exec web python manage.py check

# بررسی وضعیت مایگریشن‌ها
docker-compose exec web python manage.py showmigrations
```

### 🐘 مشکل pgAdmin
```bash
# بررسی لاگ‌های pgAdmin
docker-compose logs pgadmin

# راه‌اندازی مجدد pgAdmin
docker-compose restart pgadmin
```

### 📱 مشکل SMS
```bash
# بررسی لاگ‌های SMS
docker-compose logs web | grep SMS

# تست اتصال SMS
docker-compose exec web python manage.py test accounts.tests.SMSTestCase
```

## 📊 Monitoring و نظارت

### 📈 بررسی وضعیت سرویس‌ها
```bash
# وضعیت کلی
docker-compose ps

# استفاده از منابع
docker stats

# حجم فایل‌ها
docker system df
```

### 🔍 بررسی عملکرد
```bash
# بررسی health check
docker-compose exec web curl -f http://localhost:8000/health/

# بررسی response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/
```

## 🔒 امنیت

### 🔐 تغییر رمزهای عبور
1. فایل `docker-compose.yml` را ویرایش کنید
2. رمزهای عبور را تغییر دهید
3. سرویس‌ها را راه‌اندازی مجدد کنید

### 🌐 تنظیمات محیط
```bash
# کپی فایل env.example
cp env.example .env

# ویرایش متغیرهای محیطی
nano .env
```

## 🚀 Production Deployment

### ⚙️ تنظیمات امنیتی
1. تغییر `SECRET_KEY`
2. تنظیم `DEBUG=False`
3. محدود کردن `ALLOWED_HOSTS`
4. فعال کردن SSL

### 🔧 بهینه‌سازی
```bash
# استفاده از Nginx
docker-compose -f docker-compose.prod.yml up -d

# تنظیم Redis برای cache
docker-compose -f docker-compose.prod.yml up -d redis
```

## 📋 چک‌لیست تست

### ✅ تست‌های ضروری
- [ ] ورود Super Admin
- [ ] ورود Admin
- [ ] ورود Finance
- [ ] ورود Customer
- [ ] ورود با SMS
- [ ] مشاهده محصولات
- [ ] اضافه کردن به سبد خرید
- [ ] ثبت سفارش
- [ ] مشاهده لاگ‌ها
- [ ] تغییر قیمت محصولات
- [ ] تنظیم ساعات کاری

### 🔍 تست‌های پیشرفته
- [ ] Backup پایگاه داده
- [ ] Restore پایگاه داده
- [ ] مشاهده گزارشات مالی
- [ ] مدیریت مشتریان
- [ ] مشاهده activity logs
- [ ] تست pgAdmin

## 📞 پشتیبانی

### 🆘 مشکلات رایج
1. **پورت 8000 در حال استفاده است**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **پایگاه داده متصل نمی‌شود**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. **فایل‌های استاتیک لود نمی‌شوند**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### 📧 تماس با تیم توسعه
- **توسعه‌دهنده:** امیرحسین دربندی
- **ایمیل:** darbandidr99@gmail.com
- **GitHub:** [Amir DarBandi](https://github.com/AmirDarBandi)

---
**نسخه:** v1.0  
**تاریخ:** 2025  
**وضعیت:** آماده برای تست 