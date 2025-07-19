from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SyncConfig, SyncLog, ProductMapping, FieldMapping


@admin.register(SyncConfig)
class SyncConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_auto_sync_enabled', 'auto_sync_interval_minutes', 'last_auto_sync', 'created_at']
    list_display_links = ['id']
    list_editable = ['is_auto_sync_enabled', 'auto_sync_interval_minutes']
    readonly_fields = ['created_at', 'updated_at', 'last_auto_sync']
    
    fieldsets = (
        ('Auto Sync Settings', {
            'fields': ('is_auto_sync_enabled', 'auto_sync_interval_minutes')
        }),
        ('Timestamps', {
            'fields': ('last_auto_sync', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one configuration instance
        return not SyncConfig.objects.exists()


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'sync_type', 'operation', 'products_processed', 'products_imported', 
        'products_updated', 'products_exported', 'executed_by', 'executed_at', 
        'duration_seconds'
    ]
    list_filter = ['sync_type', 'executed_at', 'executed_by']
    search_fields = ['operation', 'errors']
    readonly_fields = [
        'sync_type', 'operation', 'products_processed', 'products_imported',
        'products_updated', 'products_exported', 'errors', 'executed_by',
        'executed_at', 'duration_seconds'
    ]
    ordering = ['-executed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ProductMapping)
class ProductMappingAdmin(admin.ModelAdmin):
    list_display = [
        'reel_number', 'external_id', 'django_product_link', 'sync_status', 
        'last_synced'
    ]
    list_filter = ['sync_status', 'last_synced']
    search_fields = ['reel_number', 'notes']
    readonly_fields = ['reel_number', 'external_id', 'django_product_id', 'last_synced']
    
    def django_product_link(self, obj):
        if obj.django_product_id:
            try:
                from core.models import Product
                product = Product.objects.get(id=obj.django_product_id)
                url = reverse('admin:core_product_change', args=[product.id])
                return format_html('<a href="{}">{}</a>', url, product.reel_number)
            except:
                return f"Product ID: {obj.django_product_id} (Not Found)"
        return "Not mapped"
    
    django_product_link.short_description = "Django Product"
    django_product_link.admin_order_field = 'django_product_id'


@admin.register(FieldMapping)
class FieldMappingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'external_field', 'django_field', 'is_active', 'mapping_type', 
        'created_at'
    ]
    list_display_links = ['id', 'external_field']
    list_filter = ['is_active', 'mapping_type', 'created_at']
    search_fields = ['external_field', 'django_field']
    list_editable = ['is_active', 'mapping_type']
    
    fieldsets = (
        ('Mapping Information', {
            'fields': ('external_field', 'django_field', 'is_active')
        }),
        ('Advanced Settings', {
            'fields': ('mapping_type', 'transform_function'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
