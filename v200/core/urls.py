"""
🌐 URL patterns برای اپلیکیشن core
🏢 مسیریابی عملیات اصلی کسب‌وکار
📦 شامل مدیریت محصولات، مشتریان و سیستم لاگ‌گیری
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    
    path('', views.index_view, name='products_landing'),
    
    # 📊 داشبوردهای مخصوص هر نقش
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('finance-dashboard/', views.finance_dashboard_view, name='finance_dashboard'),
    
    # 📦 مدیریت موجودی
    path('inventory/', views.inventory_list_view, name='inventory_list'),
    path('inventory/add/', views.add_product_view, name='add_product'),
    path('inventory/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    
    # 📋 مدیریت سفارشات
    path('orders/', views.orders_list_view, name='orders_list'),
    path('my-orders/', views.customer_orders_view, name='customer_orders'),
    path('orders/<int:order_id>/confirm/', views.confirm_order_view, name='confirm_order'),
    path('orders/<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('orders/<int:order_id>/update-status/', views.update_order_status_view, name='update_order_status'),
    
    # 👥 مدیریت مشتریان
    path('customers/', views.customers_list_view, name='customers_list'),
    path('customers/create/', views.create_customer_view, name='create_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer_view, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer_view, name='delete_customer'),
    path('customers/<int:customer_id>/create-order/', views.create_order_for_customer_view, name='create_order_for_customer'),
    path('customers/<int:customer_id>/view/', views.customer_detail_modal_view, name='customer_detail_modal'),
    path('customers/<int:customer_id>/edit-modal/', views.customer_edit_modal_view, name='customer_edit_modal'),
    
    # 💰 مدیریت مالی
    path('finance/', views.finance_overview_view, name='finance_overview'),
    
    # 📦 مدیریت محصولات
    path('products/', views.products_list_view, name='products_list'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('products/<int:product_id>/modal/', views.product_detail_modal_view, name='product_detail_modal'),
    
    # 📜 مدیریت لاگ‌های فعالیت
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    
    
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
    path('api/delete-product/', views.product_delete_api, name='product_delete_api'),
    
    # ⏰ مدیریت ساعات کاری - فقط Super Admin
    path('working-hours/', views.working_hours_management_view, name='working_hours_management'),
    path('api/set-working-hours/', views.set_working_hours_view, name='set_working_hours'),
    path('api/working-hours-config/', views.get_working_hours_config_api, name='get_working_hours_config'),
    
    path('save-selected-products/', views.save_selected_products_view, name='save_selected_products'),
    path('selected-products/', views.selected_products_view, name='selected_products'),
    path('process-order/', views.process_order_view, name='process_order'),
] 