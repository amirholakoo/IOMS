"""
🔍 Middleware برای ردیابی کاربر فعلی در لاگ‌های فعالیت
"""

import threading
from django.utils.deprecation import MiddlewareMixin


class CurrentUserMiddleware(MiddlewareMixin):
    """
    🔍 میدلور ردیابی کاربر فعلی
    
    این میدلور کاربر فعلی را در thread-local storage ذخیره می‌کند
    تا مدل‌ها بتوانند در زمان save/delete به آن دسترسی داشته باشند
    """
    
    def process_request(self, request):
        """
        🔍 پردازش درخواست و ذخیره کاربر فعلی
        """
        # ذخیره کاربر فعلی در thread-local storage
        _thread_locals.user = getattr(request, 'user', None)
    
    def process_response(self, request, response):
        """
        🔍 پاکسازی thread-local storage پس از پردازش درخواست
        """
        # پاکسازی thread-local storage
        if hasattr(_thread_locals, 'user'):
            delattr(_thread_locals, 'user')
        return response


# Thread-local storage برای ذخیره کاربر فعلی
_thread_locals = threading.local()


def get_current_user():
    """
    👤 دریافت کاربر فعلی از thread-local storage
    """
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """
    👤 تنظیم کاربر فعلی در thread-local storage
    """
    _thread_locals.user = user 