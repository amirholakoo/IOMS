#!/bin/bash
# 🚀 اسکریپت راه‌اندازی خودکار HomayOMS
# 📋 این اسکریپت پروژه را به صورت خودکار راه‌اندازی می‌کند

echo "🚀 شروع راه‌اندازی خودکار HomayOMS..."
echo ""

# 🔍 بررسی وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker نصب نشده است!"
    echo "📥 لطفاً Docker Desktop را از https://www.docker.com/products/docker-desktop دانلود و نصب کنید"
    exit 1
fi

# 🔍 بررسی وجود Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose نصب نشده است!"
    echo "📥 لطفاً Docker Compose را نصب کنید"
    exit 1
fi

echo "✅ Docker و Docker Compose موجود هستند"
echo ""

# 🛑 توقف سرویس‌های قبلی (در صورت وجود)
echo "🛑 توقف سرویس‌های قبلی..."
docker-compose down -v 2>/dev/null || true
echo ""

# 🏗️ ساخت و راه‌اندازی سرویس‌ها
echo "🏗️ ساخت و راه‌اندازی سرویس‌ها..."
docker-compose up -d --build

# ⏰ انتظار برای آماده شدن سرویس‌ها
echo ""
echo "⏳ انتظار برای آماده شدن سرویس‌ها..."
sleep 30

# 🔍 بررسی وضعیت سرویس‌ها
echo ""
echo "🔍 بررسی وضعیت سرویس‌ها..."
docker-compose ps

echo ""
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
echo "📱 برای تست SMS، از شماره: 09123456789 و کد: 123456 استفاده کنید"
echo ""
echo "📊 برای مشاهده لاگ‌ها: docker-compose logs -f"
echo "🛑 برای توقف: docker-compose down"
echo ""
echo "🎉 پروژه آماده استفاده است!" 