"""
🚨 مدیریت خطاهای سفارشی HomayOMS
📄 این فایل شامل view های مدیریت خطاها برای نمایش صفحات خطای فارسی است
"""

from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError
import logging

# 📊 تنظیم logger برای ثبت خطاها
logger = logging.getLogger(__name__)

def handler404(request, exception=None):
    """
    🔍 مدیریت خطای 404 - صفحه یافت نشد
    
    این تابع هنگام دسترسی به آدرس نامعتبر فراخوانی می‌شود
    و صفحه خطای فارسی زیبا را نمایش می‌دهد
    
    Args:
        request: درخواست HTTP
        exception: استثنای رخ داده (اختیاری)
        
    Returns:
        HttpResponseNotFound: پاسخ 404 با قالب سفارشی
    """
    
    # 📝 ثبت لاگ خطای 404
    logger.warning(f"404 Error: {request.path} - User: {request.user if request.user.is_authenticated else 'Anonymous'}")
    
    # 📋 اطلاعات کنتکست برای قالب
    context = {
        'request_path': request.path,
        'user': request.user if request.user.is_authenticated else None,
        'error_code': '404',
        'error_title': 'صفحه یافت نشد',
        'error_message': 'متأسفانه صفحه‌ای که به دنبال آن هستید در سیستم HomayOMS موجود نیست.',
    }
    
    # 🎨 رندر قالب خطا با کنتکست
    response = render(request, '404.html', context)
    response.status_code = 404
    return response

def handler500(request):
    """
    ⚠️ مدیریت خطای 500 - خطای داخلی سرور
    
    این تابع هنگام بروز خطای داخلی سرور فراخوانی می‌شود
    و صفحه خطای فارسی زیبا را نمایش می‌دهد
    
    Args:
        request: درخواست HTTP
        
    Returns:
        HttpResponseServerError: پاسخ 500 با قالب سفارشی
    """
    
    # 📝 ثبت لاگ خطای 500
    logger.error(f"500 Error: {request.path} - User: {request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'}")
    
    # 📋 اطلاعات کنتکست برای قالب
    context = {
        'request_path': request.path if hasattr(request, 'path') else 'نامشخص',
        'user': request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
        'error_code': '500',
        'error_title': 'خطای داخلی سرور',
        'error_message': 'متأسفانه مشکلی در سرور سیستم HomayOMS رخ داده است.',
    }
    
    try:
        # 🎨 تلاش برای رندر قالب خطا
        response = render(request, '500.html', context)
        response.status_code = 500
        return response
    except Exception as e:
        # 🚨 در صورت عدم امکان رندر قالب، پاسخ ساده برگردان
        logger.critical(f"Critical error in 500 handler: {str(e)}")
        return HttpResponseServerError("""
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطای سرور - HomayOMS</title>
            <style>
                body { font-family: Tahoma; text-align: center; padding: 50px; direction: rtl; }
                .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h1>🚨 خطای داخلی سرور</h1>
                <p>متأسفانه مشکلی در سیستم رخ داده است. لطفاً با مدیر سیستم تماس بگیرید.</p>
                <p><a href="/">🏠 بازگشت به صفحه اصلی</a></p>
            </div>
        </body>
        </html>
        """)

def handler403(request, exception=None):
    """
    🚫 مدیریت خطای 403 - دسترسی ممنوع
    
    این تابع هنگام عدم دسترسی کاربر به منبع فراخوانی می‌شود
    
    Args:
        request: درخواست HTTP
        exception: استثنای رخ داده (اختیاری)
        
    Returns:
        HttpResponse: پاسخ 403 با قالب سفارشی
    """
    
    # 📝 ثبت لاگ خطای 403
    logger.warning(f"403 Error: {request.path} - User: {request.user if request.user.is_authenticated else 'Anonymous'}")
    
    # 📋 اطلاعات کنتکست برای قالب
    context = {
        'request_path': request.path,
        'user': request.user if request.user.is_authenticated else None,
        'error_code': '403',
        'error_title': 'دسترسی ممنوع',
        'error_message': 'شما اجازه دسترسی به این بخش از سیستم را ندارید.',
    }
    
    # 🎨 رندر قالب خطا
    response = render(request, '403.html', context)
    response.status_code = 403
    return response

def handler400(request, exception=None):
    """
    ❌ مدیریت خطای 400 - درخواست نامعتبر
    
    این تابع هنگام ارسال درخواست نامعتبر فراخوانی می‌شود
    
    Args:
        request: درخواست HTTP
        exception: استثنای رخ داده (اختیاری)
        
    Returns:
        HttpResponse: پاسخ 400 با قالب سفارشی
    """
    
    # 📝 ثبت لاگ خطای 400
    logger.warning(f"400 Error: {request.path} - User: {request.user if request.user.is_authenticated else 'Anonymous'}")
    
    # 📋 اطلاعات کنتکست برای قالب
    context = {
        'request_path': request.path,
        'user': request.user if request.user.is_authenticated else None,
        'error_code': '400',
        'error_title': 'درخواست نامعتبر',
        'error_message': 'درخواست ارسال شده نامعتبر است.',
    }
    
    # 🎨 رندر قالب خطا
    response = render(request, '400.html', context)
    response.status_code = 400
    return response 