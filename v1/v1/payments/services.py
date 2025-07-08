import requests
import json
import logging
import random
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from typing import Dict, Any, Optional, Tuple
from .models import Payment, PaymentCallback

logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """Base exception for payment gateway errors"""
    pass


class GatewayConnectionError(PaymentGatewayError):
    """Connection error with payment gateway"""
    pass


class GatewayValidationError(PaymentGatewayError):
    """Validation error from payment gateway"""
    pass


class PaymentVerificationError(PaymentGatewayError):
    """Payment verification error"""
    pass


class BasePaymentGateway:
    """
    🏦 کلاس پایه برای درگاه‌های پرداخت
    🔐 شامل متدهای مشترک و مدیریت خطا
    """
    
    def __init__(self, sandbox=True):
        self.sandbox = sandbox
        self.timeout = 30  # seconds
        self.max_retries = 3
    
    def _make_request(self, url: str, data: Dict, headers: Dict = None, method: str = 'POST') -> Dict:
        """
        🌐 ارسال درخواست HTTP با مدیریت خطا و حالت تست
        """
        # اگر در حالت sandbox هستیم، پاسخ mock برگردان
        if self.sandbox:
            return self._get_mock_response(url, data, method)
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'POST':
                    response = requests.post(
                        url, 
                        json=data, 
                        headers=headers, 
                        timeout=self.timeout
                    )
                else:
                    response = requests.get(
                        url, 
                        params=data, 
                        headers=headers, 
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout error for {url} (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise GatewayConnectionError("درگاه پرداخت در دسترس نیست - تایم‌اوت")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error for {url} (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise GatewayConnectionError("عدم دسترسی به درگاه پرداخت")
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error for {url}: {e}")
                raise GatewayConnectionError(f"خطا در ارتباط با درگاه پرداخت: {e}")
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from {url}")
                raise GatewayConnectionError("پاسخ نامعتبر از درگاه پرداخت")
    
    def _get_mock_response(self, url: str, data: Dict, method: str) -> Dict:
        """
        🧪 ایجاد پاسخ شبیه‌سازی شده برای حالت تست
        """
        logger.info(f"Mock response for {method} {url} with data: {data}")
        
        if 'zarinpal' in url.lower():
            if 'request' in url:
                # ZarinPal payment request
                return {
                    'data': {
                        'code': 100,
                        'message': 'Success',
                        'authority': f"A{random.randint(100000000000000000, 999999999999999999)}",
                        'fee_type': 'Merchant',
                        'fee': 0
                    },
                    'errors': []
                }
            elif 'verify' in url:
                # ZarinPal payment verification
                return {
                    'data': {
                        'code': 100,
                        'message': 'Verified',
                        'card_hash': f"hash_{uuid.uuid4().hex[:16]}",
                        'card_pan': f"6274****{random.randint(1000, 9999)}",
                        'ref_id': random.randint(100000000, 999999999),
                        'fee_type': 'Merchant',
                        'fee': 0
                    },
                    'errors': []
                }
        
        elif 'shaparak' in url.lower():
            if 'request' in url:
                # Shaparak payment request
                return {
                    'status': 'success',
                    'message': 'Payment request created successfully',
                    'data': {
                        'token': f"mock_token_{uuid.uuid4().hex[:16]}",
                        'order_id': data.get('order_id'),
                        'amount': data.get('amount')
                    }
                }
            elif 'verify' in url:
                # Shaparak payment verification - Consistent field names
                return {
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'data': {
                        'transaction_id': f"TXN{random.randint(100000000, 999999999)}",
                        'reference_id': f"REF{random.randint(100000000, 999999999)}",
                        'reference_number': f"REF{random.randint(100000000, 999999999)}",
                        'trace_number': f"TRC{random.randint(100000000, 999999999)}",
                        'card_number': f"6274****{random.randint(1000, 9999)}",
                        'amount': data.get('amount')
                    }
                }
        
        # Default mock response
        return {
            'status': 'success',
            'message': 'Mock response for test mode',
            'data': {
                'mock': True,
                'url': url,
                'method': method
            }
        }
    
    def create_payment(self, payment: Payment, callback_url: str) -> Dict[str, Any]:
        """ایجاد پرداخت - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError
    
    def verify_payment(self, payment: Payment, verification_data: Dict) -> Tuple[bool, Dict]:
        """تایید پرداخت - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError


class ZarinPalGateway(BasePaymentGateway):
    """
    💎 درگاه زرین‌پال
    🔗 مستندات: https://docs.zarinpal.com/
    """
    
    def __init__(self, sandbox=True):
        super().__init__(sandbox)
        
        # تنظیمات sandbox و production
        if sandbox:
            self.merchant_id = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'  # Sandbox Merchant ID
            self.base_url = 'https://sandbox.zarinpal.com'
            self.payment_url = 'https://sandbox.zarinpal.com/pg/StartPay'
        else:
            self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
            self.base_url = 'https://api.zarinpal.com'
            self.payment_url = 'https://www.zarinpal.com/pg/StartPay'
        
        self.request_url = f"{self.base_url}/pg/v4/payment/request.json"
        self.verify_url = f"{self.base_url}/pg/v4/payment/verify.json"
    
    @transaction.atomic
    def create_payment(self, payment: Payment, callback_url: str) -> Dict[str, Any]:
        """
        💎 ایجاد درخواست پرداخت زرین‌پال
        """
        try:
            # آماده‌سازی داده‌های درخواست
            request_data = {
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),  # ZarinPal expects amount in Rials
                'description': f"پرداخت سفارش شماره {payment.order.order_number}",
                'callback_url': callback_url,
                'metadata': {
                    'mobile': payment.payer_phone or payment.order.customer.phone,
                    'email': payment.payer_email or '',
                    'order_id': str(payment.order.id)
                }
            }
            
            logger.info(f"Creating ZarinPal payment for {payment.tracking_code}")
            
            # ارسال درخواست به زرین‌پال
            response = self._make_request(self.request_url, request_data)
            
            # بررسی پاسخ
            if response.get('data', {}).get('code') == 100:
                authority = response['data']['authority']
                
                # اگر در حالت sandbox هستیم، URL mock درست کن
                if self.sandbox:
                    payment_url = f"/payments/mock-gateway/?gateway=zarinpal&authority={authority}&payment_id={payment.id}"
                else:
                    payment_url = f"{self.payment_url}/{authority}"
                
                # ذخیره اطلاعات در پرداخت
                payment.gateway_transaction_id = authority
                payment.status = 'REDIRECTED'
                payment.gateway_data = response
                payment.save()
                
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'authority': authority,
                    'message': 'درخواست پرداخت با موفقیت ایجاد شد'
                }
            else:
                error_message = self._get_zarinpal_error_message(response.get('errors', []))
                payment.status = 'FAILED'
                payment.error_message = error_message
                payment.gateway_data = response
                payment.save()
                
                return {
                    'success': False,
                    'error': error_message,
                    'gateway_response': response
                }
                
        except Exception as e:
            logger.error(f"ZarinPal payment creation error: {e}")
            payment.status = 'ERROR'
            payment.error_message = str(e)
            payment.save()
            
            return {
                'success': False,
                'error': 'خطا در ایجاد درخواست پرداخت',
                'exception': str(e)
            }
    
    @transaction.atomic
    def verify_payment(self, payment: Payment, verification_data: Dict) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت زرین‌پال
        """
        try:
            authority = verification_data.get('Authority')
            status = verification_data.get('Status')
            
            if not authority or status != 'OK':
                payment.status = 'CANCELLED'
                payment.error_message = 'کاربر از پرداخت انصراف داد'
                payment.save()
                
                return False, {
                    'message': 'پرداخت لغو شد',
                    'status': 'cancelled'
                }
            
            # آماده‌سازی داده‌های تایید
            verify_data = {
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),
                'authority': authority
            }
            
            logger.info(f"Verifying ZarinPal payment {payment.tracking_code}")
            
            # تغییر وضعیت به در حال تایید
            payment.status = 'VERIFYING'
            payment.save()
            
            # ارسال درخواست تایید
            response = self._make_request(self.verify_url, verify_data)
            
            # ثبت کال‌بک
            PaymentCallback.objects.create(
                payment=payment,
                callback_type='VERIFY',
                raw_data=response,
                sender_ip=verification_data.get('ip_address'),
                is_processed=True
            )
            
            # بررسی پاسخ تایید
            if response.get('data', {}).get('code') == 100:
                ref_id = response['data']['ref_id']
                card_hash = response['data'].get('card_hash', '')
                card_pan = response['data'].get('card_pan', '')
                
                # علامت‌گذاری پرداخت به عنوان موفق
                payment.mark_as_successful(
                    transaction_id=authority,
                    reference_number=str(ref_id),
                    card_number=card_pan
                )
                
                payment.gateway_data.update(response)
                payment.save()
                
                return True, {
                    'message': 'پرداخت با موفقیت انجام شد',
                    'ref_id': ref_id,
                    'authority': authority,
                    'card_pan': card_pan
                }
            else:
                error_message = self._get_zarinpal_error_message(response.get('errors', []))
                payment.mark_as_failed(error_message)
                
                return False, {
                    'message': error_message,
                    'gateway_response': response
                }
                
        except Exception as e:
            logger.error(f"ZarinPal verification error: {e}")
            payment.mark_as_failed(f"خطا در تایید پرداخت: {str(e)}")
            
            return False, {
                'message': 'خطا در تایید پرداخت',
                'exception': str(e)
            }
    
    def _get_zarinpal_error_message(self, errors: list) -> str:
        """
        ⚠️ تبدیل کدهای خطای زرین‌پال به پیام فارسی
        """
        error_messages = {
            -1: "اطلاعات ارسال شده ناقص است",
            -2: "IP یا مرچنت کد پذیرنده صحیح نیست",
            -3: "مبلغ کمتر از حداقل مبلغ مجاز است",
            -4: "سطح تایید پذیرنده پایین‌تر از سطح نقره‌ای است",
            -11: "درخواست مورد نظر یافت نشد",
            -12: "امکان ویرایش درخواست میسر نمی‌باشد",
            -21: "هیچ نوع عملیات مالی برای این تراکنش یافت نشد",
            -22: "تراکنش ناموفق می‌باشد",
            -33: "رقم تراکنش با رقم پرداخت شده مطابقت ندارد",
            -34: "سقف تقسیم تراکنش از لحاظ تعداد یا مبلغ عبور کرده است",
            -40: "اجازه دسترسی به متد مربوطه وجود ندارد",
            -41: "اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می‌باشد",
            -42: "مدت زمان معتبر طول عمر شناسه پرداخت باید بین 30 دقیقه تا 45 روز مشخص گردد",
            -54: "درخواست مورد نظر آرشیو شده است",
            101: "عملیات پرداخت موفق بوده و قبلا PaymentVerification تراکنش انجام شده است"
        }
        
        if not errors:
            return "خطای نامشخص"
        
        # اگر errors لیستی از کدها باشد
        if isinstance(errors, list) and errors:
            error_code = errors[0].get('code') if isinstance(errors[0], dict) else errors[0]
            return error_messages.get(error_code, f"خطای ناشناخته: {error_code}")
        
        return "خطای نامشخص در درگاه پرداخت"


class ShaparakGateway(BasePaymentGateway):
    """
    🏦 درگاه شاپرک (ملی)
    🔗 مستندات: https://www.shaparak.ir/
    """
    
    def __init__(self, sandbox=True):
        super().__init__(sandbox)
        
        # تنظیمات sandbox و production
        if sandbox:
            self.terminal_id = 'TEST_TERMINAL'
            self.merchant_id = 'TEST_MERCHANT'
            self.base_url = 'https://sandbox.shaparak.ir'
        else:
            self.terminal_id = getattr(settings, 'SHAPARAK_TERMINAL_ID', '')
            self.merchant_id = getattr(settings, 'SHAPARAK_MERCHANT_ID', '')
            self.base_url = 'https://api.shaparak.ir'
        
        self.request_url = f"{self.base_url}/v1/payment/request"
        self.verify_url = f"{self.base_url}/v1/payment/verify"
        self.payment_url = f"{self.base_url}/payment/gateway"
    
    @transaction.atomic
    def create_payment(self, payment: Payment, callback_url: str) -> Dict[str, Any]:
        """
        🏦 ایجاد درخواست پرداخت شاپرک
        """
        try:
            # آماده‌سازی داده‌های درخواست
            request_data = {
                'terminal_id': self.terminal_id,
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),  # Shaparak expects amount in Rials
                'order_id': payment.tracking_code,
                'description': f"پرداخت سفارش {payment.order.order_number}",
                'callback_url': callback_url,
                'payer_mobile': payment.payer_phone or payment.order.customer.phone,
                'additional_data': {
                    'customer_name': payment.order.customer.customer_name,
                    'order_number': payment.order.order_number
                }
            }
            
            logger.info(f"Creating Shaparak payment for {payment.tracking_code}")
            
            # ارسال درخواست به شاپرک
            response = self._make_request(self.request_url, request_data)
            
            # بررسی پاسخ
            if response.get('status') == 'success':
                token = response['data']['token']
                
                # اگر در حالت sandbox هستیم، URL mock درست کن
                if self.sandbox:
                    payment_url = f"/payments/mock-gateway/?gateway=shaparak&token={token}&payment_id={payment.id}"
                else:
                    payment_url = f"{self.payment_url}?token={token}"
                
                # ذخیره اطلاعات در پرداخت
                payment.gateway_transaction_id = token
                payment.status = 'REDIRECTED'
                payment.gateway_data = response
                payment.save()
                
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'token': token,
                    'message': 'درخواست پرداخت با موفقیت ایجاد شد'
                }
            else:
                error_message = response.get('message', 'خطا در ایجاد درخواست پرداخت')
                payment.status = 'FAILED'
                payment.error_message = error_message
                payment.gateway_data = response
                payment.save()
                
                return {
                    'success': False,
                    'error': error_message,
                    'gateway_response': response
                }
                
        except Exception as e:
            logger.error(f"Shaparak payment creation error: {e}")
            payment.status = 'ERROR'
            payment.error_message = str(e)
            payment.save()
            
            return {
                'success': False,
                'error': 'خطا در ایجاد درخواست پرداخت',
                'exception': str(e)
            }
    
    @transaction.atomic
    def verify_payment(self, payment: Payment, verification_data: Dict) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت شاپرک
        """
        try:
            token = verification_data.get('token')
            status = verification_data.get('status')
            
            logger.info(f"Shaparak verification attempt: {verification_data}")
            
            if not token or status != 'success':
                payment.status = 'CANCELLED'
                payment.error_message = 'کاربر از پرداخت انصراف داد یا پرداخت ناموفق بود'
                payment.save()
                
                return False, {
                    'message': 'پرداخت لغو شد یا ناموفق بود',
                    'status': 'cancelled'
                }
            
            # آماده‌سازی داده‌های تایید
            verify_data = {
                'terminal_id': self.terminal_id,
                'merchant_id': self.merchant_id,
                'token': token,
                'amount': int(payment.amount)
            }
            
            logger.info(f"Verifying Shaparak payment {payment.tracking_code}")
            
            # تغییر وضعیت به در حال تایید
            payment.status = 'VERIFYING'
            payment.save()
            
            # ارسال درخواست تایید
            response = self._make_request(self.verify_url, verify_data)
            
            # ثبت کال‌بک
            PaymentCallback.objects.create(
                payment=payment,
                callback_type='VERIFY',
                raw_data=response,
                sender_ip=verification_data.get('ip_address'),
                is_processed=True
            )
            
            # بررسی پاسخ تایید
            if response.get('status') == 'success':
                data = response.get('data', {})
                
                # Fix: Use correct field names from mock response
                ref_number = data.get('reference_id', data.get('reference_number', f"REF{random.randint(100000000, 999999999)}"))
                trace_number = data.get('trace_number', data.get('transaction_id', f"TRC{random.randint(100000000, 999999999)}"))
                card_number = data.get('card_number', f"6274****{random.randint(1000, 9999)}")
                
                # علامت‌گذاری پرداخت به عنوان موفق
                payment.mark_as_successful(
                    transaction_id=token,
                    reference_number=ref_number,
                    card_number=card_number
                )
                
                payment.gateway_data.update(response)
                payment.save()
                
                logger.info(f"Shaparak payment {payment.tracking_code} verified successfully")
                
                return True, {
                    'message': 'پرداخت با موفقیت انجام شد',
                    'reference_number': ref_number,
                    'trace_number': trace_number,
                    'token': token
                }
            else:
                error_message = response.get('message', 'خطا در تایید پرداخت')
                payment.mark_as_failed(error_message)
                
                logger.error(f"Shaparak verification failed: {error_message}")
                
                return False, {
                    'message': error_message,
                    'gateway_response': response
                }
                
        except Exception as e:
            logger.error(f"Shaparak verification error: {e}")
            payment.mark_as_failed(f"خطا در تایید پرداخت: {str(e)}")
            
            return False, {
                'message': 'خطا در تایید پرداخت',
                'exception': str(e)
            }


class PaymentService:
    """
    💳 سرویس مدیریت پرداخت‌ها
    🎯 مدیریت کامل فرآیند پرداخت با درگاه‌های مختلف
    """
    
    GATEWAY_CLASSES = {
        'zarinpal': ZarinPalGateway,
        'shaparak': ShaparakGateway,
    }
    
    @classmethod
    def get_gateway(cls, gateway_name: str, sandbox: bool = True):
        """
        🌐 دریافت نمونه درگاه پرداخت
        """
        gateway_class = cls.GATEWAY_CLASSES.get(gateway_name)
        if not gateway_class:
            raise ValueError(f"درگاه پرداخت {gateway_name} پشتیبانی نمی‌شود")
        
        return gateway_class(sandbox=sandbox)
    
    @classmethod
    @transaction.atomic
    def create_payment_from_order(cls, order, gateway_name: str, user=None) -> Payment:
        """
        🛒 ایجاد پرداخت از سفارش
        """
        # محاسبه مبلغ قابل پرداخت (فقط پرداخت نقدی)
        cash_amount = cls._calculate_cash_payment_amount(order)
        
        if cash_amount <= 0:
            raise ValueError("مبلغ قابل پرداخت نقدی وجود ندارد")
        
        # ایجاد پرداخت
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=cash_amount * 10,  # تبدیل تومان به ریال
            gateway=gateway_name,
            payer_phone=order.customer.phone,
            description=f"پرداخت سفارش {order.order_number}"
        )
        
        return payment
    
    @classmethod
    def _calculate_cash_payment_amount(cls, order) -> Decimal:
        """
        💰 محاسبه مبلغ قابل پرداخت نقدی
        """
        # دریافت آیتم‌های با روش پرداخت نقدی
        cash_items = order.order_items.filter(payment_method='Cash')
        total_cash_amount = sum(item.total_price for item in cash_items)
        
        return Decimal(total_cash_amount)
    
    @classmethod
    def initiate_payment(cls, payment: Payment, callback_url: str, sandbox: bool = True) -> Dict:
        """
        🚀 شروع فرآیند پرداخت
        """
        try:
            gateway = cls.get_gateway(payment.gateway, sandbox=sandbox)
            result = gateway.create_payment(payment, callback_url)
            
            return result
            
        except Exception as e:
            logger.error(f"Payment initiation error: {e}")
            payment.status = 'ERROR'
            payment.error_message = str(e)
            payment.save()
            
            return {
                'success': False,
                'error': 'خطا در شروع فرآیند پرداخت',
                'exception': str(e)
            }
    
    @classmethod
    def verify_payment(cls, payment: Payment, verification_data: Dict, sandbox: bool = True) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت
        """
        try:
            gateway = cls.get_gateway(payment.gateway, sandbox=sandbox)
            success, result = gateway.verify_payment(payment, verification_data)
            
            # اگر پرداخت موفق بود، وضعیت سفارش را به تایید شده تغییر دهید
            if success:
                order = payment.order
                order.status = 'Confirmed'
                order.save()
            
            return success, result
            
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            payment.mark_as_failed(f"خطا در تایید پرداخت: {str(e)}")
            
            return False, {
                'message': 'خطا در تایید پرداخت',
                'exception': str(e)
            }
    
    @classmethod
    def check_expired_payments(cls):
        """
        ⏰ بررسی و علامت‌گذاری پرداخت‌های منقضی شده
        """
        expired_payments = Payment.objects.filter(
            status__in=['INITIATED', 'REDIRECTED', 'PENDING'],
            expires_at__lt=timezone.now()
        )
        
        for payment in expired_payments:
            payment.mark_as_expired()
            logger.info(f"Marked payment {payment.tracking_code} as expired")
        
        return expired_payments.count() 
        
        return expired_payments.count() 