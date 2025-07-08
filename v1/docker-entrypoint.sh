#!/bin/bash
# 🐳 Docker Entrypoint Script برای HomayOMS
# 🔧 راه‌اندازی خودکار پایگاه داده و مایگریشن‌ها

set -e

echo "🚀 شروع راه‌اندازی HomayOMS..."

# ⏰ انتظار برای آماده شدن PostgreSQL
echo "⏳ انتظار برای آماده شدن PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "⏳ PostgreSQL هنوز آماده نیست... انتظار..."
    sleep 2
done
echo "✅ PostgreSQL آماده است!"

# 🔧 اجرای مایگریشن‌ها
echo "🔄 اجرای مایگریشن‌های پایگاه داده..."
python manage.py migrate --noinput

# 🎭 راه‌اندازی نقش‌ها و مجوزها
echo "🔐 راه‌اندازی نقش‌ها و مجوزهای سیستم..."
python manage.py setup_roles --create-superuser --username admin --password admin123 --phone 09123456789

# 👥 ایجاد کاربران تست
echo "👥 ایجاد کاربران تست برای تمام نقش‌ها..."
python manage.py create_test_users

# 👤 ایجاد مشتریان تست
echo "👤 ایجاد مشتریان تست..."
python manage.py create_test_customer

# 📦 ایجاد محصولات تست
echo "📦 ایجاد محصولات تست..."
python manage.py create_test_products

# 📦 جمع‌آوری فایل‌های استاتیک
echo "📦 جمع‌آوری فایل‌های استاتیک..."
python manage.py collectstatic --noinput

# ✅ راه‌اندازی کامل
echo "✅ راه‌اندازی HomayOMS کامل شد!"
echo ""
echo "🌐 دسترسی به سیستم:"
echo "🔗 سرور اصلی: http://localhost:8000"
echo "🎛️ پنل مدیریت: http://localhost:8000/admin/"
echo "🐘 pgAdmin: http://localhost:5050"
echo ""
echo "👤 اطلاعات ورود کاربران تست:"
echo "🔑 Super Admin: admin / admin123"
echo "👨‍💼 Admin: admin_user / admin123"
echo "💰 Finance: finance_user / finance123"
echo "👤 Customer: customer_user / customer123"
echo ""
echo "📱 برای تست SMS، از شماره: 09123456789 استفاده کنید"
echo "🔗 کد تایید SMS: 123456"

# 🚀 اجرای دستور اصلی
exec "$@" 