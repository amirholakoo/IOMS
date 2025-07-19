from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
import json

from accounts.permissions import super_admin_required
from .models import SyncConfig, SyncLog, ProductMapping, FieldMapping
from .services import InventorySyncService


@login_required
@super_admin_required
def sync_dashboard(request):
    """
    Main dashboard for inventory synchronization
    """
    sync_service = InventorySyncService()
    
    # Get sync configuration
    config, created = SyncConfig.objects.get_or_create()
    
    # Get recent sync logs
    recent_logs = SyncLog.objects.all()[:10]
    
    # Get importable products count
    importable_products = sync_service.get_importable_products()
    
    # Get sync statistics
    total_mappings = ProductMapping.objects.count()
    imported_mappings = ProductMapping.objects.filter(sync_status='imported').count()
    updated_mappings = ProductMapping.objects.filter(sync_status='updated').count()
    
    context = {
        'config': config,
        'recent_logs': recent_logs,
        'importable_count': len(importable_products),
        'total_mappings': total_mappings,
        'imported_mappings': imported_mappings,
        'updated_mappings': updated_mappings,
        'last_auto_sync': config.last_auto_sync,
        'next_auto_sync': config.last_auto_sync + timezone.timedelta(minutes=config.auto_sync_interval_minutes) if config.last_auto_sync else None,
    }
    
    return render(request, 'inventory_sync/sync_dashboard.html', context)


@login_required
@super_admin_required
def import_products_view(request):
    """
    View for importing products from SQLite
    """
    sync_service = InventorySyncService()
    importable_products = sync_service.get_importable_products()
    
    # Filter by width if specified
    width_filter = request.GET.get('width')
    if width_filter:
        try:
            width_value = int(width_filter)
            filtered_products = []
            for product in importable_products:
                # Check both external_data and django_data for width
                external_width = product.get('external_data', {}).get('width')
                django_width = product.get('django_data', {}).get('width')
                
                if external_width == width_value or django_width == width_value:
                    filtered_products.append(product)
            importable_products = filtered_products
        except (ValueError, TypeError):
            # If width filter is invalid, show all products
            pass
    
    # Pagination
    paginator = Paginator(importable_products, 20)  # 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'total_count': len(importable_products),
        'page_obj': page_obj,
        'current_width': width_filter,
    }
    
    return render(request, 'inventory_sync/import_products.html', context)


@login_required
@super_admin_required
@require_http_methods(["POST"])
def perform_import(request):
    """
    AJAX endpoint for importing selected products
    """
    try:
        data = json.loads(request.body)
        selected_reel_numbers = data.get('selected_reel_numbers', [])
        
        if not selected_reel_numbers:
            return JsonResponse({
                'success': False,
                'message': 'No products selected for import'
            })
        
        sync_service = InventorySyncService()
        results = sync_service.import_selected_products(selected_reel_numbers, request.user)
        
        if results['errors']:
            error_details = '\n'.join(results['errors'][:5])  # Show first 5 errors
            if len(results['errors']) > 5:
                error_details += f"\n... and {len(results['errors']) - 5} more errors"
            
            return JsonResponse({
                'success': False,
                'message': f"Import completed with {len(results['errors'])} errors. Details: {error_details}",
                'results': results
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f"Successfully imported {results['imported']} products and updated {results['updated']} products",
                'results': results
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error during import: {str(e)}'
        })


@login_required
@super_admin_required
@require_http_methods(["POST"])
def perform_full_sync(request):
    """
    AJAX endpoint for performing full synchronization
    """
    try:
        sync_service = InventorySyncService()
        results = sync_service.perform_full_sync(request.user)
        
        # Check if sync was successful
        if results.get('sync_successful', False):
            # Build success message
            message_parts = []
            
            if results['exported'] > 0:
                message_parts.append(f"بروزرسانی {results['exported']} محصول فروخته شده")
            elif results['exported'] == 0 and results.get('warnings'):
                message_parts.append("هیچ محصول فروخته شده‌ای برای بروزرسانی یافت نشد")
            else:
                message_parts.append("همگام‌سازی با موفقیت انجام شد")
            
            if results['importable_count'] > 0:
                message_parts.append(f"{results['importable_count']} محصول قابل وارد کردن")
            
            # Add warnings if any
            if results.get('warnings'):
                warning_count = len(results['warnings'])
                message_parts.append(f"({warning_count} هشدار - محصولات در فایل SQLite یافت نشدند)")
            
            success_message = ". ".join(message_parts)
            
            return JsonResponse({
                'success': True,
                'message': success_message,
                'results': results
            })
        else:
            # Handle critical errors
            if results.get('errors'):
                error_details = '\n'.join(results['errors'][:3])  # Show first 3 errors
                if len(results['errors']) > 3:
                    error_details += f"\n... and {len(results['errors']) - 3} more errors"
                
                return JsonResponse({
                    'success': False,
                    'message': f"خطا در همگام‌سازی: {error_details}",
                    'results': results
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'خطا در همگام‌سازی - جزئیات نامشخص',
                    'results': results
                })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در همگام‌سازی: {str(e)}'
        })


@login_required
@super_admin_required
def sync_logs_view(request):
    """
    View for displaying sync logs
    """
    logs = SyncLog.objects.all()
    
    # Filtering
    sync_type = request.GET.get('sync_type')
    if sync_type:
        logs = logs.filter(sync_type=sync_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        logs = logs.filter(
            Q(operation__icontains=search) |
            Q(errors__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(logs, 50)  # 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'sync_types': SyncLog.SYNC_TYPES,
        'current_sync_type': sync_type,
        'search': search,
    }
    
    return render(request, 'inventory_sync/sync_logs.html', context)


@login_required
@super_admin_required
def product_mappings_view(request):
    """
    View for displaying product mappings
    """
    mappings = ProductMapping.objects.all()
    
    # Filtering
    sync_status = request.GET.get('sync_status')
    if sync_status:
        mappings = mappings.filter(sync_status=sync_status)
    
    # Search
    search = request.GET.get('search')
    if search:
        mappings = mappings.filter(
            Q(reel_number__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(mappings, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mappings': page_obj,
        'sync_statuses': ProductMapping._meta.get_field('sync_status').choices,
        'current_sync_status': sync_status,
        'search': search,
    }
    
    return render(request, 'inventory_sync/product_mappings.html', context)


@login_required
@super_admin_required
def field_mappings_view(request):
    """
    View for managing field mappings
    """
    if request.method == 'POST':
        # Handle field mapping updates
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'update_mapping':
                mapping_id = data.get('mapping_id')
                is_active = data.get('is_active')
                
                mapping = get_object_or_404(FieldMapping, id=mapping_id)
                mapping.is_active = is_active
                mapping.save()
                
                return JsonResponse({'success': True})
            
            elif action == 'add_mapping':
                external_field = data.get('external_field')
                django_field = data.get('django_field')
                
                if external_field and django_field:
                    mapping, created = FieldMapping.objects.get_or_create(
                        external_field=external_field,
                        django_field=django_field,
                        defaults={'is_active': True}
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'created': created,
                        'mapping_id': mapping.id
                    })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    # GET request - display mappings
    mappings = FieldMapping.objects.all().order_by('external_field')
    
    context = {
        'mappings': mappings,
    }
    
    return render(request, 'inventory_sync/field_mappings.html', context)


@login_required
@super_admin_required
def sync_config_view(request):
    """
    View for managing sync configuration
    """
    config, created = SyncConfig.objects.get_or_create()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            config.auto_sync_interval_minutes = data.get('auto_sync_interval_minutes', 1440)
            config.is_auto_sync_enabled = data.get('is_auto_sync_enabled', True)
            config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'تنظیمات با موفقیت بروزرسانی شد'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    context = {
        'config': config,
    }
    
    return render(request, 'inventory_sync/sync_config.html', context)


@login_required
@super_admin_required
def get_sync_status(request):
    """
    AJAX endpoint for getting current sync status
    """
    try:
        sync_service = InventorySyncService()
        config = SyncConfig.objects.first()
        
        if not config:
            config = SyncConfig.objects.create()
        
        try:
            importable_products = sync_service.get_importable_products()
            should_auto_sync = sync_service.should_run_auto_sync()
        except Exception as sync_error:
            return JsonResponse({
                'success': False,
                'message': f'Error getting sync status: {str(sync_error)}'
            })
        
        status = {
            'importable_count': len(importable_products),
            'auto_sync_enabled': config.is_auto_sync_enabled,
            'auto_sync_interval': config.auto_sync_interval_minutes,
            'last_auto_sync': config.last_auto_sync.isoformat() if config.last_auto_sync else None,
            'should_auto_sync': should_auto_sync,
            'next_auto_sync': None
        }
        
        if config.last_auto_sync:
            from django.utils import timezone
            from datetime import timedelta
            next_sync = config.last_auto_sync + timedelta(minutes=config.auto_sync_interval_minutes)
            status['next_auto_sync'] = next_sync.isoformat()
        
        return JsonResponse({
            'success': True,
            'status': status
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting sync status: {str(e)}'
        })


@login_required
@super_admin_required
def test_sqlite_connection(request):
    """
    Test SQLite database connection
    """
    try:
        from .services import SQLiteInventoryService
        
        sqlite_service = SQLiteInventoryService()
        test_result = sqlite_service.test_connection()
        
        return JsonResponse({
            'success': test_result['success'],
            'message': test_result['message'],
            'details': test_result.get('details', {})
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error testing connection: {str(e)}'
        })
