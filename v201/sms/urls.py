"""
📱 URL patterns for SMS app
"""

from django.urls import path
from . import views

app_name = 'sms'

urlpatterns = [
    # 📊 Dashboard
    path('dashboard/', views.sms_dashboard_view, name='dashboard'),
    
    # 📱 Messages
    path('messages/', views.message_list_view, name='message_list'),
    path('messages/<uuid:tracking_id>/', views.message_detail_view, name='message_detail'),
    
    # 📝 Templates
    path('templates/', views.template_list_view, name='template_list'),
    path('templates/add/', views.template_add_view, name='template_add'),
    path('templates/<int:template_id>/edit/', views.template_edit_view, name='template_edit'),
    path('templates/<int:template_id>/delete/', views.template_delete_view, name='template_delete'),
    
    # 🔐 Verifications
    path('verifications/', views.verification_list_view, name='verification_list'),
    
    # ⚙️ Settings
    path('settings/', views.settings_view, name='settings'),
    
    # 📊 Statistics
    path('statistics/', views.statistics_view, name='statistics'),
    
    # 🔔 Notifications
    path('notifications/', views.notification_list_view, name='notification_list'),
    
    # 🧪 Test
    path('test/', views.test_sms_view, name='test_sms'),
    
    # 🔍 Health Check
    path('health/', views.health_check_view, name='health_check'),
] 