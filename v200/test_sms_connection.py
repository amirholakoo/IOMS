#!/usr/bin/env python3
"""
🔍 تست اتصال سرور SMS
📱 بررسی وضعیت سرور SMS و تست ارسال پیام
"""

import requests
import json
import sys
from datetime import datetime


def test_sms_connection():
    """تست اتصال به سرور SMS"""
    
    # تنظیمات
    sms_url = "http://192.168.221.102:5003"
    api_key = "ioms_sms_server_2025"
    timeout = 30
    
    print("🔍 تست اتصال سرور SMS")
    print("=" * 50)
    print(f"📡 آدرس سرور: {sms_url}")
    print(f"🔑 کلید API: {api_key}")
    print(f"⏰ Timeout: {timeout} ثانیه")
    print(f"🕐 زمان تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # تست 1: بررسی سلامت سرور
    print("1️⃣ تست سلامت سرور...")
    try:
        health_url = f"{sms_url}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ سرور SMS در دسترس است")
            print(f"   📊 وضعیت: {health_data.get('status', 'نامشخص')}")
            print(f"   📶 سیگنال: {health_data.get('signal', 'نامشخص')}")
            print(f"   🌐 شبکه: {health_data.get('network', 'نامشخص')}")
            print(f"   🕐 زمان: {health_data.get('timestamp', 'نامشخص')}")
        else:
            print(f"⚠️ سرور پاسخ می‌دهد اما وضعیت نامشخص: {response.status_code}")
            print(f"   پاسخ: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print("❌ خطا در اتصال به سرور SMS")
        print(f"   خطا: {str(e)}")
        print()
        print("💡 راه‌حل‌های ممکن:")
        print("   1. بررسی اتصال شبکه")
        print("   2. بررسی آدرس IP سرور")
        print("   3. بررسی فعال بودن سرویس SMS")
        print("   4. بررسی firewall")
        return False
        
    except requests.exceptions.Timeout as e:
        print("⏰ سرور SMS پاسخ نمی‌دهد (timeout)")
        print(f"   خطا: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {str(e)}")
        return False
    
    print()
    
    # تست 2: ارسال پیام آزمایشی
    print("2️⃣ تست ارسال پیام...")
    test_phone = "+989123456789"  # شماره تست
    test_message = "تست اتصال SMS - HomayOMS"
    
    try:
        send_url = f"{sms_url}/api/v1/verify/send"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        data = {
            "phone_number": test_phone,
            "message": test_message
        }
        
        print(f"   📱 شماره: {test_phone}")
        print(f"   📝 پیام: {test_message}")
        
        response = requests.post(send_url, json=data, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست ارسال موفق")
            print(f"   📊 پاسخ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ پیام با موفقیت ارسال شد")
                return True
            else:
                print(f"⚠️ خطا در ارسال پیام: {result.get('message', 'نامشخص')}")
                return False
        else:
            print(f"❌ خطای HTTP {response.status_code}")
            print(f"   پاسخ: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print("❌ خطا در اتصال برای ارسال پیام")
        print(f"   خطا: {str(e)}")
        return False
        
    except requests.exceptions.Timeout as e:
        print("⏰ timeout در ارسال پیام")
        print(f"   خطا: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره در ارسال: {str(e)}")
        return False


def main():
    """تابع اصلی"""
    print("🚀 شروع تست اتصال سرور SMS")
    print()
    
    success = test_sms_connection()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 تست اتصال موفق بود!")
        print("✅ سرور SMS آماده استفاده است")
    else:
        print("❌ تست اتصال ناموفق بود")
        print("🔧 لطفاً مشکلات را برطرف کنید")
    
    print()
    print("🔧 دستورات مفید:")
    print("   # بررسی وضعیت سرویس SMS")
    print("   ssh admin@192.168.221.102 'sudo systemctl status sms-server'")
    print()
    print("   # راه‌اندازی مجدد سرویس SMS")
    print("   ssh admin@192.168.221.102 'sudo systemctl restart sms-server'")
    print()
    print("   # بررسی لاگ‌های سرویس")
    print("   ssh admin@192.168.221.102 'sudo journalctl -u sms-server -f'")


if __name__ == "__main__":
    main() 