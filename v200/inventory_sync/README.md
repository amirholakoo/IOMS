# Inventory Sync Module

A Django module for synchronizing inventory between an external SQLite database and the main Django application.

## 🎯 Features

- **Bidirectional Sync**: Import products from SQLite and export sales back to SQLite
- **Selective Import**: Super admin can choose which products to import
- **Automatic Sync**: Configurable automatic synchronization with interval settings
- **Product Filtering**: Only imports "In-stock" products, excludes sold/delivered items
- **Comprehensive Logging**: Tracks all sync operations with detailed logs
- **Field Mapping**: Flexible field mapping between external and Django models
- **Raspberry Pi Optimized**: Minimal dependencies, lightweight operations

## 🏗️ Architecture

### Models
- **SyncConfig**: Configuration for auto-sync settings (inherits from BaseModel)
- **SyncLog**: Logs of all synchronization operations (inherits from BaseModel)
- **ProductMapping**: Maps products between external SQLite and Django (inherits from BaseModel)
- **FieldMapping**: Configurable field mappings between systems (inherits from BaseModel)

### Services
- **SQLiteInventoryService**: Handles SQLite database operations
- **InventorySyncService**: Main synchronization logic

### Views
- **sync_dashboard**: Main dashboard with overview and actions
- **import_products_view**: Product selection and import interface
- **sync_config_view**: Configuration management
- **sync_logs_view**: View synchronization logs

## 🚀 Installation

1. **Add to Django Settings**
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'inventory_sync',
   ]
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate inventory_sync
   ```

3. **Add URLs to Main URLs**
   ```python
   urlpatterns = [
       # ... other URLs
       path('inventory-sync/', include('inventory_sync.urls')),
   ]
   ```

4. **Place SQLite File**
   - Copy your SQLite database file to `inventory_sync/db.sqlite3`
   - Or modify the path in `services.py` if needed

## 📋 Usage

### Super Admin Interface

1. **Dashboard**: `/inventory-sync/dashboard/`
   - Overview of sync status
   - Quick actions for manual sync
   - Recent sync logs

2. **Import Products**: `/inventory-sync/import/`
   - View available products from SQLite
   - Select products to import
   - Bulk import functionality

3. **Configuration**: `/inventory-sync/config/`
   - Enable/disable auto-sync
   - Set sync interval
   - Test sync functionality

### Management Commands

```bash
# Manual sync
python manage.py sync_inventory

# Auto sync
python manage.py auto_sync

# Import only
python manage.py sync_inventory --import-only

# Export only
python manage.py sync_inventory --export-only

# Dry run (see what would be done)
python manage.py sync_inventory --dry-run
```

## 🔧 Configuration

### Field Mappings

Default field mappings are automatically created based on the provided schema:

```python
DEFAULT_MAPPINGS = {
    'reel_number': 'reel_number',
    'width': 'width',
    'gsm': 'gsm',
    'length': 'length',
    'grade': 'grade',
    'breaks': 'breaks',
    'comments': 'comments',
    'qr_code': 'qr_code',
    'profile_name': 'profile_name',
    'location': 'location',
    'status': 'status',
    'receive_date': 'receive_date',
    'last_date': 'last_date',
    'username': 'username',
    'logs': 'logs',
}
```

### Auto-Sync Settings

- **Interval**: Configurable in minutes (1-10080)
- **Default**: 1440 minutes (24 hours)
- **Enable/Disable**: Toggle via admin interface

## 🔄 Sync Logic

### Import Process
1. Read products from SQLite with "In-stock" status
2. Filter out products already sold/delivered in Django
3. Map fields using FieldMapping configuration
4. Create or update products in Django
5. Create ProductMapping records

### Export Process
1. Find products in Django with "Sold" or "Delivered" status
2. Update corresponding products in SQLite
3. Update ProductMapping status
4. Log the operation

### Business Rules
- **Primary Key**: `reel_number` for product identification
- **Status Filter**: Only import "In-stock" products
- **Conflict Resolution**: Don't re-import sold products
- **Bidirectional**: Sales sync back to SQLite

## 📊 Monitoring

### Sync Logs
- Track all sync operations
- Monitor success/failure rates
- View detailed error messages
- Performance metrics (duration)

### Dashboard Metrics
- Products available for import
- Total mappings
- Auto-sync status
- Last/next sync times

## 🔒 Security

- **Super Admin Only**: All sync operations require super admin permissions
- **CSRF Protection**: All AJAX endpoints protected
- **Input Validation**: Comprehensive validation of all inputs
- **Error Handling**: Graceful error handling and logging

## 🛠️ Customization

### Adding New Fields
1. Add field mapping in admin interface
2. Update field mapping logic if needed
3. Test with dry-run command

### Custom Transformations
1. Add transform function to services
2. Update FieldMapping with function name
3. Set mapping_type to 'transform'

### Scheduling
- Use Django's built-in cron or celery
- Set up system cron for auto_sync command
- Monitor logs for successful execution

## 🐛 Troubleshooting

### Common Issues

1. **SQLite Connection Failed**
   - Check file path in `services.py`
   - Verify file permissions
   - Test connection via admin interface

2. **Import Errors**
   - Check field mappings
   - Verify SQLite table structure
   - Review sync logs for details

3. **Auto-Sync Not Running**
   - Check configuration settings
   - Verify cron job setup
   - Test manually with management command

### Debug Commands

```bash
# Test SQLite connection
python manage.py shell
>>> from inventory_sync.services import SQLiteInventoryService
>>> service = SQLiteInventoryService()
>>> service.connect()

# Check available products
>>> service.get_available_products()

# Test field mappings
>>> from inventory_sync.models import FieldMapping
>>> FieldMapping.objects.all()
```

## 📝 Dependencies

- **Django**: Core framework
- **Python Standard Library**: sqlite3, os, json, datetime
- **No External Libraries**: Optimized for Raspberry Pi

## 🔄 Integration with Core App

The module integrates with the existing `core` app by:
- Using the same Product model
- Following existing permission patterns
- Maintaining data consistency
- Logging operations via ActivityLog

## 📈 Performance

- **Lightweight**: Minimal memory footprint
- **Efficient**: Batch operations where possible
- **Scalable**: Pagination for large datasets
- **Optimized**: Database queries optimized for performance

---

**Note**: This module is designed to be completely separate from existing code and can be easily removed or modified without affecting the core application. 