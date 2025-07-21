from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import time


class Command(BaseCommand):
    help = 'بررسی وضعیت سرور SMS و تست اتصال'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-send',
            action='store_true',
            help='تست ارسال پیام آزمایشی',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='شماره تلفن برای تست ارسال',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 بررسی وضعیت سرور SMS'))
        self.stdout.write('=' * 50)
        
        # دریافت تنظیمات SMS
        sms_url = getattr(settings, 'SMS_SERVER_URL', 'http://192.168.221.102:5003')
        sms_api_key = getattr(settings, 'SMS_API_KEY', 'ioms_sms_server_2025')
        sms_timeout = getattr(settings, 'SMS_TIMEOUT', 30)
        sms_fallback = getattr(settings, 'SMS_FALLBACK_TO_FAKE', False)
        
        self.stdout.write(f'📡 آدرس سرور SMS: {sms_url}')
        self.stdout.write(f'🔑 کلید API: {sms_api_key}')
        self.stdout.write(f'⏰ Timeout: {sms_timeout} ثانیه')
        self.stdout.write(f'🔄 Fallback به fake SMS: {"فعال" if sms_fallback else "غیرفعال"}')
        self.stdout.write('')
        
        # تست اتصال به سرور
        self.stdout.write('🌐 تست اتصال به سرور SMS...')
        try:
            health_url = f"{sms_url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.stdout.write(self.style.SUCCESS('✅ سرور SMS در دسترس است'))
                self.stdout.write(f'📊 وضعیت: {health_data.get("status", "نامشخص")}')
                self.stdout.write(f'📶 سیگنال: {health_data.get("signal", "نامشخص")}')
                self.stdout.write(f'🌐 شبکه: {health_data.get("network", "نامشخص")}')
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ سرور پاسخ می‌دهد اما وضعیت نامشخص: {response.status_code}'))
                
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR('❌ خطا در اتصال به سرور SMS'))
            self.stdout.write('💡 راه‌حل‌های ممکن:')
            self.stdout.write('   1. بررسی اتصال شبکه')
            self.stdout.write('   2. بررسی آدرس IP سرور')
            self.stdout.write('   3. بررسی فعال بودن سرویس SMS')
            self.stdout.write('   4. فعال کردن fallback به fake SMS')
            
        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR('⏰ سرور SMS پاسخ نمی‌دهد (timeout)'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطای غیرمنتظره: {str(e)}'))
        
        self.stdout.write('')
        
        # تست ارسال پیام
        if options['test_send'] and options['phone']:
            self.stdout.write('📱 تست ارسال پیام...')
            try:
                test_url = f"{sms_url}/api/v1/verify/send"
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": sms_api_key
                }
                data = {
                    "phone_number": options['phone'],
                    "message": "تست اتصال SMS - HomayOMS"
                }
                
                response = requests.post(test_url, json=data, headers=headers, timeout=sms_timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.stdout.write(self.style.SUCCESS('✅ پیام تست با موفقیت ارسال شد'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠️ خطا در ارسال پیام: {result.get("message", "نامشخص")}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ خطای HTTP {response.status_code}: {response.text}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ خطا در تست ارسال: {str(e)}'))
        
        self.stdout.write('')
        self.stdout.write('🔧 پیشنهادات:')
        if not sms_fallback:
            self.stdout.write('   - فعال کردن SMS_FALLBACK_TO_FAKE=True برای تست')
        self.stdout.write('   - بررسی لاگ‌های سرور SMS')
        self.stdout.write('   - بررسی تنظیمات شبکه')
        self.stdout.write('   - تست دستی سرور SMS با curl') 