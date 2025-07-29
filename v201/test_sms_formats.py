#!/usr/bin/env python3
"""
🧪 تست فرمت‌های جدید پیام SMS
📱 نمایش نمونه‌های مختلف پیام‌های SMS با کدگذاری صحیح
"""

from datetime import datetime, timedelta


def format_standard_message(phone_number, verification_code, expires_at):
    """فرمت استاندارد پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    
    message = f"""Verification Code: {verification_code}
Valid until: {time_str}
HomayOMS"""
    
    return message


def format_compact_message(phone_number, verification_code, expires_at):
    """فرمت فشرده پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    
    message = f"""Code: {verification_code}
Until: {time_str}
HomayOMS"""
    
    return message


def format_detailed_message(phone_number, verification_code, expires_at):
    """فرمت تفصیلی پیام SMS"""
    time_str = expires_at.strftime('%H:%M')
    date_str = expires_at.strftime('%Y/%m/%d')
    
    message = f"""Verification Code HomayOMS

Phone: {phone_number}
Code: {verification_code}
Date: {date_str}
Time: {time_str}

Enter this code in login page
HomayOMS"""
    
    return message


def format_persian_simple(phone_number, verification_code, expires_at):
    """فرمت ساده فارسی"""
    time_str = expires_at.strftime('%H:%M')
    
    message = f"""کد: {verification_code}
تا: {time_str}
HomayOMS"""
    
    return message


def main():
    """تابع اصلی برای نمایش فرمت‌های مختلف"""
    
    # داده‌های تست
    phone_number = "+989109462034"
    verification_code = "123456"
    expires_at = datetime.now() + timedelta(minutes=10)
    
    print("🧪 تست فرمت‌های جدید پیام SMS")
    print("=" * 60)
    print()
    
    # فرمت استاندارد (انگلیسی)
    print("📱 فرمت استاندارد (English):")
    print("-" * 40)
    print(format_standard_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_standard_message(phone_number, verification_code, expires_at)))
    print()
    
    # فرمت فشرده (انگلیسی)
    print("📱 فرمت فشرده (English):")
    print("-" * 40)
    print(format_compact_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_compact_message(phone_number, verification_code, expires_at)))
    print()
    
    # فرمت تفصیلی (انگلیسی)
    print("📱 فرمت تفصیلی (English):")
    print("-" * 40)
    print(format_detailed_message(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_detailed_message(phone_number, verification_code, expires_at)))
    print()
    
    # فرمت ساده فارسی
    print("📱 فرمت ساده فارسی:")
    print("-" * 40)
    print(format_persian_simple(phone_number, verification_code, expires_at))
    print()
    print("📊 تعداد کاراکتر: ", len(format_persian_simple(phone_number, verification_code, expires_at)))
    print()
    
    print("=" * 60)
    print("💡 نکات:")
    print("• فرمت‌های انگلیسی: اطمینان از نمایش صحیح")
    print("• فرمت ساده فارسی: حداقل کاراکترهای فارسی")
    print("• همه فرمت‌ها: قابل خواندن و حرفه‌ای")
    print()
    print("🔧 تنظیم فرمت در env.local:")
    print("SMS_MESSAGE_FORMAT=standard  # یا compact یا detailed")
    print()
    print("🎯 توصیه: فرمت استاندارد (English) برای اطمینان از نمایش صحیح")


if __name__ == "__main__":
    main() 