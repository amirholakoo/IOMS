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
                # ZarinPal payment request - Generate exactly 36 character authority starting with 'S'
                authority = 'S' + (uuid.uuid4().hex + uuid.uuid4().hex)[:35]  # 1 + 35 = 36
                return {
                    'data': {
                        'code': 100,
                        'message': 'Success',
                        'authority': authority,
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
                # Shaparak payment request - Generate 32 character token
                token = uuid.uuid4().hex  # Exactly 32 characters
                
                return {
                    'status': 'success',
                    'message': 'Payment request created successfully',
                    'data': {
                        'token': token,
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
            self.merchant_id = 'a9b1b6c2-1c5b-11e8-b7f2-005056a205be'  # Official Zarinpal sandbox merchant ID
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
        💳 ایجاد درخواست پرداخت در زرین‌پال
        """
        try:
            # آماده‌سازی داده‌های درخواست
            request_data = {
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),  # مبلغ به ریال
                'description': f'پرداخت سفارش {payment.order.order_number}',
                'callback_url': callback_url,
                'metadata': {
                    'order_id': payment.order.id,
                    'payment_id': payment.id,
                    'tracking_code': payment.tracking_code
                }
            }
            
            # ارسال درخواست به زرین‌پال
            response = self._make_request(self.request_url, request_data)
            
            # بررسی پاسخ
            if response.get('data', {}).get('code') == 100:
                # موفقیت
                authority = response['data']['authority']
                
                # Use mock gateway in sandbox mode (like v1)
                if self.sandbox:
                    payment_url = f"/payments/mock-gateway/?gateway=zarinpal&authority={authority}&payment_id={payment.id}"
                else:
                    payment_url = f"{self.payment_url}/{authority}"
                
                # به‌روزرسانی پرداخت
                payment.gateway_transaction_id = authority
                payment.status = 'REDIRECTED'
                payment.gateway_data.update({
                    'request_response': response,
                    'authority': authority
                })
                payment.save()
                
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'authority': authority,
                    'gateway_response': response
                }
            else:
                # خطا
                error_message = self._get_zarinpal_error_message(response.get('errors', []))
                raise GatewayValidationError(f"خطا در ایجاد درخواست پرداخت: {error_message}")
                
        except Exception as e:
            logger.error(f"ZarinPal payment creation error: {e}")
            payment.mark_as_failed(str(e))
            raise
    
    @transaction.atomic
    def verify_payment(self, payment: Payment, verification_data: Dict) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت در زرین‌پال
        """
        try:
            # بررسی پارامترهای مختلف authority
            authority = (
                verification_data.get('Authority') or 
                verification_data.get('authority') or 
                verification_data.get('AuthorityCode') or
                verification_data.get('authority_code')
            )
            status = (
                verification_data.get('Status') or 
                verification_data.get('status') or
                verification_data.get('ResultCode') or
                verification_data.get('result_code')
            )
            
            logger.info(f"ZarinPal verification - Authority: {authority}, Status: {status}")
            
            if not authority:
                raise PaymentVerificationError("پارامتر Authority یافت نشد")
            
            # بررسی وضعیت - OK یا 100 برای موفقیت
            if status not in ['OK', '100', 'ok']:
                payment.mark_as_failed("کاربر پرداخت را لغو کرد")
                return False, {'error': 'پرداخت لغو شد'}
            
            # آماده‌سازی داده‌های تایید
            verify_data = {
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),
                'authority': authority
            }
            
            # ارسال درخواست تایید
            response = self._make_request(self.verify_url, verify_data)
            
            # بررسی پاسخ
            if response.get('data', {}).get('code') == 100:
                # تایید موفق
                verify_data = response['data']
                
                # به‌روزرسانی پرداخت
                payment.status = 'SUCCESS'
                payment.completed_at = timezone.now()
                payment.bank_reference_number = str(verify_data.get('ref_id', ''))
                payment.masked_card_number = verify_data.get('card_pan', '')
                payment.gateway_data.update({
                    'verification_response': response,
                    'ref_id': verify_data.get('ref_id'),
                    'card_pan': verify_data.get('card_pan'),
                    'card_hash': verify_data.get('card_hash')
                })
                payment.save()
                
                # به‌روزرسانی سفارش
                order = payment.order
                order.status = 'Confirmed'
                order.save()
                
                return True, {
                    'success': True,
                    'ref_id': verify_data.get('ref_id'),
                    'card_pan': verify_data.get('card_pan'),
                    'gateway_response': response
                }
            else:
                # خطا در تایید
                error_message = self._get_zarinpal_error_message(response.get('errors', []))
                payment.mark_as_failed(f"خطا در تایید پرداخت: {error_message}")
                return False, {'error': error_message}
                
        except Exception as e:
            logger.error(f"ZarinPal payment verification error: {e}")
            payment.mark_as_failed(str(e))
            return False, {'error': str(e)}
    
    def _get_zarinpal_error_message(self, errors: list) -> str:
        """
        📝 استخراج پیام خطا از پاسخ زرین‌پال
        """
        if not errors:
            return "خطای نامشخص"
        
        error_codes = {
            '-1': 'اطلاعات ارسال شده ناقص است',
            '-2': 'IP یا مرچنت کد پذیرنده صحیح نیست',
            '-3': 'رقم تراکنش باید بین 1000 تا 500000000 ریال باشد',
            '-4': 'سطح تایید پذیرنده پایین تر از سطح نقره ای است',
            '-11': 'درخواست مورد نظر یافت نشد',
            '-12': 'امکان ویرایش درخواست وجود ندارد',
            '-21': 'هیچ نوع عملیات مالی برای این تراکنش یافت نشد',
            '-22': 'تراکنش ناموفق می باشد',
            '-33': 'رقم تراکنش با رقم پرداخت شده مطابقت ندارد',
            '-34': 'سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است',
            '-40': 'اجازه دسترسی به متد مربوطه وجود ندارد',
            '-41': 'اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می باشد',
            '-42': 'مدت زمان معتبر طول عمر شناسه پرداخت باید بین 30 دقیقه تا 45 روز می باشد',
            '-54': 'درخواست مورد نظر آرشیو شده است',
            '-101': 'عملیات پرداخت ناموفق بوده است',
        }
        
        error_messages = []
        for error in errors:
            code = str(error.get('code', ''))
            message = error_codes.get(code, error.get('message', 'خطای نامشخص'))
            error_messages.append(f"{code}: {message}")
        
        return ' | '.join(error_messages)


class ShaparakGateway(BasePaymentGateway):
    """
    🏦 درگاه شاپرک
    🔗 مستندات: https://docs.shaparak.ir/
    """
    
    def __init__(self, sandbox=True):
        super().__init__(sandbox)
        
        # تنظیمات sandbox و production
        if sandbox:
            self.merchant_id = 'test_merchant_id'
            self.base_url = 'https://sandbox.shaparak.ir'
        else:
            self.merchant_id = getattr(settings, 'SHAPARAK_MERCHANT_ID', '')
            self.base_url = 'https://api.shaparak.ir'
        
        self.request_url = f"{self.base_url}/api/v1/payment/request"
        self.verify_url = f"{self.base_url}/api/v1/payment/verify"
        self.payment_url = f"{self.base_url}/payment"
    
    @transaction.atomic
    def create_payment(self, payment: Payment, callback_url: str) -> Dict[str, Any]:
        """
        💳 ایجاد درخواست پرداخت در شاپرک
        """
        try:
            # آماده‌سازی داده‌های درخواست
            request_data = {
                'merchant_id': self.merchant_id,
                'amount': int(payment.amount),
                'order_id': payment.order.order_number,
                'callback_url': callback_url,
                'description': f'پرداخت سفارش {payment.order.order_number}',
                'metadata': {
                    'payment_id': payment.id,
                    'tracking_code': payment.tracking_code
                }
            }
            
            # ارسال درخواست به شاپرک
            response = self._make_request(self.request_url, request_data)
            
            # بررسی پاسخ
            if response.get('status') == 'success':
                # موفقیت
                token = response['data']['token']
                
                # به‌روزرسانی پرداخت
                payment.gateway_transaction_id = token
                payment.status = 'REDIRECTED'
                payment.gateway_data.update({
                    'request_response': response,
                    'token': token
                })
                payment.save()
                
                # تولید URL پرداخت
                payment_url = f"{self.payment_url}?token={token}"
                
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'token': token,
                    'gateway_response': response
                }
            else:
                # خطا
                error_message = response.get('message', 'خطا در ایجاد درخواست پرداخت')
                raise GatewayValidationError(error_message)
                
        except Exception as e:
            logger.error(f"Shaparak payment creation error: {e}")
            payment.mark_as_failed(str(e))
            raise
    
    @transaction.atomic
    def verify_payment(self, payment: Payment, verification_data: Dict) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت در شاپرک
        """
        try:
            # بررسی پارامترهای مختلف token
            token = (
                verification_data.get('token') or 
                verification_data.get('Token') or
                verification_data.get('payment_token') or
                verification_data.get('PaymentToken')
            )
            status = (
                verification_data.get('status') or 
                verification_data.get('Status') or
                verification_data.get('result') or
                verification_data.get('Result')
            )
            
            logger.info(f"Shaparak verification - Token: {token}, Status: {status}")
            
            if not token:
                raise PaymentVerificationError("پارامتر token یافت نشد")
            
            # بررسی وضعیت - success یا OK برای موفقیت
            if status not in ['success', 'Success', 'OK', 'ok']:
                payment.mark_as_failed("پرداخت ناموفق بود")
                return False, {'error': 'پرداخت ناموفق'}
            
            # آماده‌سازی داده‌های تایید
            verify_data = {
                'merchant_id': self.merchant_id,
                'token': token,
                'amount': int(payment.amount)
            }
            
            # ارسال درخواست تایید
            response = self._make_request(self.verify_url, verify_data)
            
            # بررسی پاسخ
            if response.get('status') == 'success':
                # تایید موفق
                verify_data = response['data']
                
                # به‌روزرسانی پرداخت
                payment.status = 'SUCCESS'
                payment.completed_at = timezone.now()
                payment.bank_reference_number = str(verify_data.get('reference_id', ''))
                payment.masked_card_number = verify_data.get('card_number', '')
                payment.gateway_data.update({
                    'verification_response': response,
                    'reference_id': verify_data.get('reference_id'),
                    'transaction_id': verify_data.get('transaction_id'),
                    'card_number': verify_data.get('card_number')
                })
                payment.save()
                
                # به‌روزرسانی سفارش
                order = payment.order
                order.status = 'Confirmed'
                order.save()
                
                return True, {
                    'success': True,
                    'reference_id': verify_data.get('reference_id'),
                    'transaction_id': verify_data.get('transaction_id'),
                    'card_number': verify_data.get('card_number'),
                    'gateway_response': response
                }
            else:
                # خطا در تایید
                error_message = response.get('message', 'خطا در تایید پرداخت')
                payment.mark_as_failed(error_message)
                return False, {'error': error_message}
                
        except Exception as e:
            logger.error(f"Shaparak payment verification error: {e}")
            payment.mark_as_failed(str(e))
            return False, {'error': str(e)}


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
        💳 ایجاد پرداخت از سفارش
        """
        # محاسبه مبلغ قابل پرداخت (فقط اقلام نقدی)
        cash_amount = cls._calculate_cash_payment_amount(order)
        
        if cash_amount <= 0:
            raise ValueError("مبلغ قابل پرداخت باید بیشتر از صفر باشد")
        
        # ایجاد پرداخت
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=cash_amount * 10,  # تبدیل تومان به ریال
            gateway=gateway_name,
            description=f"پرداخت سفارش {order.order_number}",
            payer_phone=user.phone if user else None
        )
        
        return payment
    
    @classmethod
    def _calculate_cash_payment_amount(cls, order) -> Decimal:
        """
        💰 محاسبه مبلغ قابل پرداخت (فقط اقلام نقدی)
        """
        cash_items = order.order_items.filter(payment_method='Cash')
        total_amount = sum(item.total_price for item in cash_items)
        return total_amount
    
    @classmethod
    def initiate_payment(cls, payment: Payment, callback_url: str, sandbox: bool = True) -> Dict:
        """
        🚀 شروع فرآیند پرداخت
        """
        try:
            gateway = cls.get_gateway(payment.gateway, sandbox)
            result = gateway.create_payment(payment, callback_url)
            
            # ثبت لاگ
            payment.log_activity('INITIATE', f'فرآیند پرداخت شروع شد - درگاه: {payment.gateway}')
            
            return result
            
        except Exception as e:
            logger.error(f"Payment initiation error: {e}")
            payment.mark_as_failed(str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def verify_payment(cls, payment: Payment, verification_data: Dict, sandbox: bool = True) -> Tuple[bool, Dict]:
        """
        ✅ تایید پرداخت
        """
        try:
            gateway = cls.get_gateway(payment.gateway, sandbox)
            success, result = gateway.verify_payment(payment, verification_data)
            
            if success:
                payment.log_activity('VERIFY_SUCCESS', f'پرداخت تایید شد - {result.get("reference_id", "N/A")}')
            else:
                payment.log_activity('VERIFY_FAILED', f'تایید پرداخت ناموفق - {result.get("error", "N/A")}')
            
            return success, result
            
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            payment.mark_as_failed(str(e))
            return False, {'error': str(e)}
    
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
            payment.status = 'TIMEOUT'
            payment.completed_at = timezone.now()
            payment.error_message = 'پرداخت منقضی شد'
            payment.save()
            
            payment.log_activity('TIMEOUT', 'پرداخت منقضی شد')
        
        return expired_payments.count() 