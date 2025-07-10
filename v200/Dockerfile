# 🐳 Dockerfile برای HomayOMS Django Application (v200)
# 🏗️ Multi-stage build برای بهینه‌سازی اندازه image

# 📦 Stage 1: Base Python Image
FROM python:3.11-slim

# 🏷️ Metadata
LABEL maintainer="امیرحسین دربندی <darbandidr99@gmail.com>"
LABEL description="HomayOMS v200 - سیستم مدیریت سفارشات هوما"
LABEL version="v2.0"

# 🔧 تنظیم متغیرهای محیط
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=HomayOMS.settings.production

# 📁 ایجاد دایرکتوری کاری
WORKDIR /app

# 🔧 نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 📦 کپی requirements.txt و نصب وابستگی‌های Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 📁 کپی کد پروژه
COPY . .

# 🎯 Entrypoint script (copy before user change)
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 👤 ایجاد کاربر غیر root برای امنیت
RUN adduser --disabled-password --gecos '' django && \
    chown -R django:django /app
USER django

# 🔧 جمع‌آوری فایل‌های استاتیک
RUN python manage.py collectstatic --noinput --settings=HomayOMS.settings.production

# 🌐 Expose پورت
EXPOSE 8000

# 🚀 Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "HomayOMS.wsgi:application"] 