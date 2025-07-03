"""
🌐 URL patterns برای اپلیکیشن accounts
🔗 مسیریابی احراز هویت و مدیریت کاربران
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 🔐 احراز هویت
    path('login/', views.login_view, name='login'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 🔵 ورود مخصوص مشتریان
    path('customer/login/', views.customer_login_view, name='customer_login'),
    path('customer/sms-login/', views.customer_sms_login_view, name='customer_sms_login'),
    path('customer/sms-verify/', views.customer_sms_verify_view, name='customer_sms_verify'),
    path('customer/resend-sms/', views.resend_sms_code_view, name='resend_sms_code'),
    path('customer/dashboard/', views.customer_dashboard_view, name='customer_dashboard'),

    # 🔵 ثبت نام مشتریان
    path('customer/registration/', views.customer_registration_view, name='customer_registration'),
    
    # 📊 داشبورد
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # 👤 پروفایل کاربر
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # 👥 مدیریت کاربران (Super Admin فقط)
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('users/<int:user_id>/update-status/', views.update_user_status, name='update_user_status'),
    
    # 🔗 API endpoints
    path('api/permissions/', views.user_permissions_api, name='user_permissions_api'),
    path('api/check-password/', views.check_password_strength, name='check_password_strength'),
    path('customer/terms/', views.terms_and_request_view, name='terms_and_request'),
] 