from django.urls import path
from . import views

app_name = 'inventory_sync'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.sync_dashboard, name='sync_dashboard'),
    
    # Product import
    path('import/', views.import_products_view, name='import_products'),
    path('import/perform/', views.perform_import, name='perform_import'),
    
    # Full synchronization
    path('sync/full/', views.perform_full_sync, name='perform_full_sync'),
    
    # Logs and mappings
    path('logs/', views.sync_logs_view, name='sync_logs'),
    path('mappings/', views.product_mappings_view, name='product_mappings'),
    path('field-mappings/', views.field_mappings_view, name='field_mappings'),
    
    # Configuration
    path('config/', views.sync_config_view, name='sync_config'),
    
    # AJAX endpoints
    path('status/', views.get_sync_status, name='get_sync_status'),
    path('test-connection/', views.test_sqlite_connection, name='test_sqlite_connection'),
] 