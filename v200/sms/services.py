"""
📱 SMS Services for HomayOMS
سرویس‌های سیستم پیامک برای ارتباط با سرور SIM800C
"""

import requests
import logging
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
import string
from .models import SMSMessage, SMSVerification, SMSTemplate, SMSSettings

logger = logging.getLogger(__name__)


class SMSService:
    """
    📱 سرویس اصلی ارسال پیامک
    """
    
    def __init__(self):
        # Initialize with environment variables first, database settings will be loaded lazily
        self._settings = None
        self.base_url = getattr(settings, 'SMS_SERVER_URL', 'http://192.168.1.60:5003').rstrip('/')
        self.api_key = getattr(settings, 'SMS_API_KEY', 'ioms_sms_server_2025')
        self.timeout = getattr(settings, 'SMS_TIMEOUT', 30)
        self.retry_attempts = getattr(settings, 'SMS_RETRY_ATTEMPTS', 3)
        self.fallback_to_fake = getattr(settings, 'SMS_FALLBACK_TO_FAKE', True)
    
    @property
    def settings(self):
        """Lazy loading of SMS settings from database"""
        if self._settings is None:
            try:
                self._settings = SMSSettings.get_settings()
                # Update instance variables with database settings if available
                self.base_url = getattr(settings, 'SMS_SERVER_URL', self._settings.sms_server_url).rstrip('/')
                self.api_key = getattr(settings, 'SMS_API_KEY', self._settings.api_key)
                self.timeout = getattr(settings, 'SMS_TIMEOUT', self._settings.timeout_seconds)
                self.retry_attempts = getattr(settings, 'SMS_RETRY_ATTEMPTS', self._settings.retry_attempts)
            except Exception as e:
                logger.warning(f"Could not load SMS settings from database: {e}")
                # Use default values if database is not available
                self._settings = type('MockSettings', (), {
                    'sms_server_url': self.base_url,
                    'api_key': self.api_key,
                    'timeout_seconds': self.timeout,
                    'retry_attempts': self.retry_attempts,
                    'verification_code_expiry': 10,
                    'max_verification_attempts': 3,
                    'enable_order_notifications': True,
                    'enable_payment_notifications': True,
                })()
        return self._settings
    
    def format_phone_number(self, phone_number):
        """
        فرمت کردن شماره تلفن برای استفاده بین‌المللی
        """
        # حذف کاراکترهای غیر عددی
        phone = ''.join(filter(str.isdigit, str(phone_number)))
        
        # تبدیل فرمت محلی ایران به بین‌المللی
        if phone.startswith('09'):
            phone = '+98' + phone[1:]
        elif phone.startswith('9') and len(phone) == 10:
            phone = '+98' + phone
        elif not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def check_server_health(self):
        """
        بررسی سلامت سرور SMS
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"Server returned status code: {response.status_code}"
                
        except requests.RequestException as e:
            logger.error(f"SMS server health check failed: {e}")
            return False, f"Connection error: {str(e)}"
    
    def send_sms(self, phone_number, message, message_type='NOTIFICATION', user=None, template=None, extra_data=None):
        """
        ارسال پیامک
        """
        # فرمت کردن شماره تلفن
        formatted_phone = self.format_phone_number(phone_number)
        
        # ایجاد رکورد پیام
        sms_message = SMSMessage.objects.create(
            phone_number=formatted_phone,
            message_content=message,
            message_type=message_type,
            user=user,
            template=template,
            extra_data=extra_data or {},
            status='PENDING'
        )
        
        # آماده‌سازی درخواست
        url = f"{self.base_url}/api/v1/verify/send"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        data = {
            "phone_number": formatted_phone,
            "message": message
        }
        
        # ارسال با تلاش‌های مجدد
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending SMS attempt {attempt + 1}/{self.retry_attempts} to {formatted_phone}")
                
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if response_data.get('success'):
                        # موفقیت
                        sms_message.mark_as_sent(response_data)
                        logger.info(f"SMS sent successfully to {formatted_phone}")
                        return True, sms_message, "SMS sent successfully"
                    else:
                        # خطای API
                        error_msg = response_data.get('error', 'Unknown API error')
                        sms_message.mark_as_failed(error_msg, response_data)
                        logger.error(f"SMS API error for {formatted_phone}: {error_msg}")
                        return False, sms_message, error_msg
                        
                else:
                    # خطای HTTP
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    sms_message.mark_as_failed(error_msg, {'status_code': response.status_code})
                    logger.error(f"SMS HTTP error for {formatted_phone}: {error_msg}")
                    
                    if attempt < self.retry_attempts - 1:
                        logger.info(f"Retrying SMS send to {formatted_phone} in 3 seconds...")
                        import time
                        time.sleep(3)
                        continue
                    else:
                        return False, sms_message, error_msg
                        
            except requests.RequestException as e:
                # خطای اتصال
                error_msg = f"Connection error: {str(e)}"
                sms_message.mark_as_failed(error_msg)
                logger.error(f"SMS connection error for {formatted_phone}: {error_msg}")
                
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying SMS send to {formatted_phone} in 3 seconds...")
                    import time
                    time.sleep(3)
                    continue
                else:
                    return False, sms_message, error_msg
        
        return False, sms_message, "All retry attempts failed"
    
    def send_verification_code(self, phone_number, user=None):
        """
        ارسال کد تایید
        """
        # تولید کد تایید
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # محاسبه زمان انقضا
        expires_at = timezone.now() + timedelta(minutes=self.settings.verification_code_expiry)
        
        # ایجاد رکورد کد تایید
        verification = SMSVerification.objects.create(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        # آماده‌سازی پیام
        message = f"""کد تایید HomayOMS

شماره: {phone_number}
کد: {verification_code}
معتبر تا: {expires_at.strftime('%H:%M')}

این کد را در صفحه ورود وارد کنید
کد را با کسی به اشتراک نگذارید

با تشکر از انتخاب شما"""
        
        # ارسال پیامک
        success, sms_message, result = self.send_sms(
            phone_number=phone_number,
            message=message,
            message_type='VERIFICATION',
            user=user,
            extra_data={'verification_code': verification_code}
        )
        
        # مرتبط کردن پیامک با کد تایید
        if success:
            verification.sms_message = sms_message
            verification.save()
        
        return success, verification, result
    
    def verify_code(self, phone_number, code):
        """
        تایید کد
        """
        try:
            # جستجوی کد تایید - ابتدا کدهای استفاده نشده و معتبر
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                verification_code=code,
                is_used=False
            ).filter(
                expires_at__gt=timezone.now()  # فقط کدهای منقضی نشده
            ).latest('created_at')
            
            # علامت‌گذاری به عنوان استفاده شده
            verification.mark_as_used()
            
            return True, verification
            
        except SMSVerification.DoesNotExist:
            # اگر کد یافت نشد، بررسی کنیم که آیا کد منقضی شده یا استفاده شده
            try:
                expired_verification = SMSVerification.objects.filter(
                    phone_number=phone_number,
                    verification_code=code
                ).latest('created_at')
                
                if expired_verification.is_used:
                    return False, "کد تایید قبلاً استفاده شده است"
                elif timezone.now() > expired_verification.expires_at:
                    return False, "کد تایید منقضی شده است"
                else:
                    return False, "کد تایید نامعتبر است"
                    
            except SMSVerification.DoesNotExist:
                return False, "کد تایید یافت نشد"
    
    def send_template_message(self, template_name, phone_number, **kwargs):
        """
        ارسال پیام با استفاده از قالب
        """
        try:
            template = SMSTemplate.objects.get(name=template_name, is_active=True)
            message = template.format_message(**kwargs)
            
            return self.send_sms(
                phone_number=phone_number,
                message=message,
                message_type=template.template_type,
                template=template
            )
            
        except SMSTemplate.DoesNotExist:
            logger.error(f"SMS template '{template_name}' not found or inactive")
            return False, None, f"Template '{template_name}' not found"
    
    def get_statistics(self):
        """
        دریافت آمار پیامک‌ها
        """
        total_messages = SMSMessage.objects.count()
        successful_messages = SMSMessage.objects.filter(status='SENT').count()
        delivered_messages = SMSMessage.objects.filter(status='DELIVERED').count()
        failed_messages = SMSMessage.objects.filter(status='FAILED').count()
        
        success_rate = (successful_messages / total_messages * 100) if total_messages > 0 else 0
        delivery_rate = (delivered_messages / successful_messages * 100) if successful_messages > 0 else 0
        
        return {
            'total_messages': total_messages,
            'successful_messages': successful_messages,
            'delivered_messages': delivered_messages,
            'failed_messages': failed_messages,
            'success_rate': round(success_rate, 2),
            'delivery_rate': round(delivery_rate, 2)
        }


class SMSNotificationService:
    """
    🔔 سرویس اعلان‌های خودکار
    """
    
    def __init__(self):
        self.sms_service = SMSService()
        self._settings = None
    
    @property
    def settings(self):
        """Lazy loading of SMS settings from database"""
        if self._settings is None:
            try:
                self._settings = SMSSettings.get_settings()
            except Exception as e:
                logger.warning(f"Could not load SMS settings from database: {e}")
                # Use default values if database is not available
                self._settings = type('MockSettings', (), {
                    'enable_order_notifications': True,
                    'enable_payment_notifications': True,
                })()
        return self._settings
    
    def send_order_status_notification(self, order, new_status):
        """
        ارسال اعلان تغییر وضعیت سفارش
        """
        if not self.settings.enable_order_notifications:
            return False, "Order notifications are disabled"
        
        try:
            # آماده‌سازی اطلاعات
            status_display = dict(order.ORDER_STATUS_CHOICES).get(new_status, new_status)
            customer_phone = order.customer.phone
            
            # ارسال پیام
            message = f"سفارش {order.order_number} شما {status_display} شد.\nمبلغ: {order.final_amount:,.0f} تومان"
            
            success, sms_message, result = self.sms_service.send_sms(
                phone_number=customer_phone,
                message=message,
                message_type='ORDER_STATUS',
                extra_data={
                    'order_number': order.order_number,
                    'order_status': new_status,
                    'order_amount': str(order.final_amount)
                }
            )
            
            return success, result
            
        except Exception as e:
            logger.error(f"Failed to send order status notification: {e}")
            return False, f"Notification error: {str(e)}"
    
    def send_payment_notification(self, payment, status):
        """
        ارسال اعلان وضعیت پرداخت
        """
        if not self.settings.enable_payment_notifications:
            return False, "Payment notifications are disabled"
        
        try:
            # آماده‌سازی اطلاعات
            customer_phone = payment.order.customer.phone
            
            if status == 'SUCCESS':
                message = f"پرداخت سفارش {payment.order.order_number} با موفقیت انجام شد.\nمبلغ: {payment.display_amount:,.0f} تومان"
            else:
                message = f"پرداخت سفارش {payment.order.order_number} ناموفق بود.\nلطفاً مجدداً تلاش کنید."
            
            success, sms_message, result = self.sms_service.send_sms(
                phone_number=customer_phone,
                message=message,
                message_type='PAYMENT',
                extra_data={
                    'order_number': payment.order.order_number,
                    'payment_status': status,
                    'payment_amount': str(payment.display_amount)
                }
            )
            
            return success, result
            
        except Exception as e:
            logger.error(f"Failed to send payment notification: {e}")
            return False, f"Notification error: {str(e)}"


# نمونه‌های جهانی برای استفاده آسان (lazy initialization)
_sms_service = None
_sms_notification_service = None

def get_sms_service():
    """Get global SMS service instance with lazy initialization"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service

def get_sms_notification_service():
    """Get global SMS notification service instance with lazy initialization"""
    global _sms_notification_service
    if _sms_notification_service is None:
        _sms_notification_service = SMSNotificationService()
    return _sms_notification_service

# Legacy compatibility - these will be created when first accessed
def get_legacy_sms_service():
    """Legacy function for backward compatibility"""
    return get_sms_service()

def get_legacy_sms_notification_service():
    """Legacy function for backward compatibility"""
    return get_sms_notification_service() 