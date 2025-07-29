#!/usr/bin/env python3
"""
🧪 تست فرمت‌های مختلف پیام فارسی SMS
📱 نمایش نمونه‌های مختلف پیام‌های SMS
"""

from datetime import datetime, timedelta


def format_standard_message(phone_number, verification_code, expires_at):
    """فرمت استاندارد پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    
    message = f"""کد تایید HomayOMS

شماره: {phone_number}
کد: {verification_code}
معتبر تا: {time_str}

این کد را در صفحه ورود وارد کنید
کد را با کسی به اشتراک نگذارید

با تشکر از انتخاب شما"""
    
    return message


def format_compact_message(phone_number, verification_code, expires_at):
    """فرمت فشرده پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    
    message = f"""کد تایید: {verification_code}
معتبر تا: {time_str}
HomayOMS"""
    
    return message


def format_detailed_message(phone_number, verification_code, expires_at):
    """فرمت تفصیلی پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    date_str = expires_at.strftime('%Y/%m/%d')
    
    message = f"""کد تایید HomayOMS

شماره تلفن: {phone_number}
کد تایید: {verification_code}
تاریخ انقضا: {date_str}
ساعت انقضا: {time_str}

لطفاً این کد را در صفحه ورود وارد کنید
⚠️ این کد را با هیچ شخص دیگری به اشتراک نگذارید

با تشکر از انتخاب شما
سیستم HomayOMS"""
    
    return message


def main():
    """تابع اصلی برای نمایش فرمت‌های مختلف"""
    
    # داده‌های تست
    phone_number = "+989109462034"
    verification_code = "123456"
    expires_at = datetime.now() + timedelta(minutes=10)
    
    print("🧪 تست فرمت‌های مختلف پیام فارسی SMS")
    print("=" * 60)
    print()
    
    # فرمت استاندارد
    print("📱 فرمت استاندارد:")
    print("-" * 30)
    print(format_standard_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_standard_message(phone_number, verification_code, expires_at)))
    print()
    
    # فرمت فشرده
    print("📱 فرمت فشرده:")
    print("-" * 30)
    print(format_compact_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_compact_message(phone_number, verification_code, expires_at)))
    print()
    
    # فرمت تفصیلی
    print("📱 فرمت تفصیلی:")
    print("-" * 30)
    print(format_detailed_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_detailed_message(phone_number, verification_code, expires_at)))
    print()
    
    print("=" * 60)
    print("💡 نکات:")
    print("• فرمت استاندارد: مناسب برای اکثر دستگاه‌ها")
    print("• فرمت فشرده: مناسب برای دستگاه‌های قدیمی")
    print("• فرمت تفصیلی: مناسب برای اطلاعات کامل‌تر")
    print()
    print("🔧 تنظیم فرمت در env.local:")
    print("SMS_MESSAGE_FORMAT=standard  # یا compact یا detailed")


if __name__ == "__main__":
    main() 