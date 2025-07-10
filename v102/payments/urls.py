from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment flow URLs
    path('summary/<int:order_id>/', views.payment_summary, name='payment_summary'),
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('callback/<int:payment_id>/', views.payment_callback, name='payment_callback'),
    
    # Payment status URLs
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    
    # Payment management URLs
    path('history/', views.payment_history, name='payment_history'),
    path('retry/<int:payment_id>/', views.retry_payment, name='retry_payment'),
    
    # Test/Mock URLs (for development)
    path('mock-gateway/', views.mock_payment_gateway, name='mock_gateway'),
    
    # API URLs
    path('api/status/<int:payment_id>/', views.payment_status_api, name='payment_status_api'),
] 