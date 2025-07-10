"""
🌐 URL patterns برای اپلیکیشن core
🏢 مسیریابی عملیات اصلی کسب‌وکار
📦 شامل مدیریت محصولات، مشتریان و سیستم لاگ‌گیری
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 📊 داشبوردهای مخصوص هر نقش
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('finance-dashboard/', views.finance_dashboard_view, name='finance_dashboard'),
    
    # 📦 مدیریت موجودی
    path('inventory/', views.inventory_list_view, name='inventory_list'),
    
    # 📋 مدیریت سفارشات
    path('orders/', views.orders_list_view, name='orders_list'),
    path('my-orders/', views.customer_orders_view, name='customer_orders'),
    path('orders/<int:order_id>/confirm/', views.confirm_order_view, name='confirm_order'),
    path('orders/<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('orders/<int:order_id>/update-status/', views.update_order_status_view, name='update_order_status'),
    
    # 👥 مدیریت مشتریان
    path('customers/', views.customers_list_view, name='customers_list'),
    
    # 💰 مدیریت مالی
    path('finance/', views.finance_overview_view, name='finance_overview'),
    
    # 📦 مدیریت محصولات
    path('products/', views.products_list_view, name='products_list'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    
    # 📜 مدیریت لاگ‌های فعالیت
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    
    # 🏠 Main landing page
    path('', views.products_landing_view, name='products_landing'),
    
    # 🛒 Shopping cart and orders
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('update-cart-quantity/', views.update_cart_quantity_view, name='update_cart_quantity'),
    path('update-cart-payment-method/', views.update_cart_payment_method_view, name='update_cart_payment_method'),
    path('remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # 📊 API endpoints
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/product-qr/<str:qr_code>/', views.product_qr_api, name='product_qr_api'),
    path('api/update-price/', views.update_price_api, name='update_price_api'),
    
    # ⏰ مدیریت ساعات کاری - فقط Super Admin
    path('working-hours/', views.working_hours_management_view, name='working_hours_management'),
    path('api/set-working-hours/', views.set_working_hours_view, name='set_working_hours'),
] 