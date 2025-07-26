#!/bin/bash
# 🐳 Docker Entrypoint Script برای HomayOMS v200 - Raspberry Pi Production
# 🔧 راه‌اندازی خودکار پایگاه داده و مایگریشن‌ها برای محیط تولید

set -e

echo "🚀 شروع راه‌اندازی HomayOMS v200 - Raspberry Pi Production..."

# ⏰ انتظار برای آماده شدن PostgreSQL
echo "⏳ انتظار برای آماده شدن PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "⏳ PostgreSQL هنوز آماده نیست... انتظار..."
    sleep 5
done
echo "✅ PostgreSQL آماده است!"

# 🔧 اجرای مایگریشن‌ها
echo "🔄 اجرای مایگریشن‌های پایگاه داده..."
python manage.py migrate --noinput

# 🎭 راه‌اندازی نقش‌ها و مجوزها (فقط اگر وجود نداشته باشند)
echo "🔐 بررسی و راه‌اندازی نقش‌ها و مجوزهای سیستم..."
python manage.py setup_roles --create-superuser --username admin --password admin123 --phone 09123456789

# 📦 جمع‌آوری فایل‌های استاتیک
echo "📦 جمع‌آوری فایل‌های استاتیک..."
python manage.py collectstatic --noinput

# 🔍 بررسی سلامت سیستم
echo "🔍 بررسی سلامت سیستم..."
python manage.py check --deploy

# 📊 راه‌اندازی تنظیمات اولیه (فقط اگر وجود نداشته باشند)
echo "📊 راه‌اندازی تنظیمات اولیه سیستم..."

# بررسی وجود محصولات
PRODUCT_COUNT=$(python manage.py shell -c "from core.models import Product; print(Product.objects.count())" 2>/dev/null || echo "0")
if [ "$PRODUCT_COUNT" -eq "0" ]; then
    echo "📦 ایجاد محصولات تست..."
    python manage.py create_test_products
fi

# بررسی وجود مشتریان
CUSTOMER_COUNT=$(python manage.py shell -c "from core.models import Customer; print(Customer.objects.count())" 2>/dev/null || echo "0")
if [ "$CUSTOMER_COUNT" -eq "0" ]; then
    echo "👤 ایجاد مشتریان تست..."
    python manage.py create_test_customer
fi

# بررسی وجود کاربران تست
USER_COUNT=$(python manage.py shell -c "from accounts.models import User; print(User.objects.count())" 2>/dev/null || echo "0")
if [ "$USER_COUNT" -eq "1" ]; then  # فقط admin وجود دارد
    echo "👥 ایجاد کاربران تست..."
    python manage.py create_test_users
fi

# بررسی تنظیمات ساعات کاری
WORKING_HOURS_COUNT=$(python manage.py shell -c "from core.models import WorkingHours; print(WorkingHours.objects.count())" 2>/dev/null || echo "0")
if [ "$WORKING_HOURS_COUNT" -eq "0" ]; then
    echo "⏰ راه‌اندازی تنظیمات ساعات کاری..."
    python manage.py setup_working_hours
fi

# 🔧 راه‌اندازی تنظیمات SMS
echo "📱 بررسی تنظیمات SMS..."
python manage.py setup_sms_templates

# 🔧 راه‌اندازی تنظیمات Inventory Sync
echo "🔄 راه‌اندازی تنظیمات Inventory Sync..."
python manage.py setup_field_mappings

# ✅ راه‌اندازی کامل
echo "✅ راه‌اندازی HomayOMS v200 - Raspberry Pi Production کامل شد!"
echo ""
echo "🌐 دسترسی به سیستم:"
echo "🔗 سرور اصلی: http://localhost:${WEB_PORT:-8000}"
echo "🎛️ پنل مدیریت: http://localhost:${WEB_PORT:-8000}/admin/"
echo "🐘 pgAdmin: http://localhost:${PGADMIN_PORT:-5050} (با --profile admin)"
echo ""
echo "👤 اطلاعات ورود کاربران:"
echo "🔑 Super Admin: admin / admin123"
echo "👨‍💼 Admin: admin_user / admin123"
echo "💰 Finance: finance_user / finance123"
echo "👤 Customer: customer_user / customer123"
echo ""
echo "📱 برای تست SMS، از شماره: 09123456789 استفاده کنید"
echo "🔗 کد تایید SMS: 123456"
echo ""
echo "⚙️ ویژگی‌های Production:"
echo "🔒 امنیت پیشرفته فعال"
echo "📊 لاگ‌گیری کامل"
echo "🔄 SMS واقعی با SIM800C"
echo "📦 Inventory Sync فعال"
echo "⚡ بهینه‌سازی برای Raspberry Pi"
echo ""
echo "🔧 مدیریت سیستم:"
echo "📊 مشاهده لاگ‌ها: docker logs homayoms_v200_web"
echo "🗄️ پشتیبان‌گیری: docker exec homayoms_v200_db pg_dump -U homayoms_user homayoms_v200_db > backup.sql"
echo "🔄 راه‌اندازی مجدد: docker-compose -f docker-compose.raspberry.yml restart"
echo "🛑 توقف سیستم: docker-compose -f docker-compose.raspberry.yml down"

# 🚀 اجرای دستور اصلی
exec "$@" 