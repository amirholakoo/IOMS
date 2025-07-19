import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import SyncConfig, SyncLog, ProductMapping, FieldMapping


class SQLiteInventoryService:
    """
    Service for handling SQLite inventory database operations
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize with SQLite database path
        """
        if db_path is None:
            # Default path in inventory_sync directory
            db_path = os.path.join(
                os.path.dirname(__file__), 
                'db.sqlite3'
            )
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish connection to SQLite database"""
        try:
            # Check if database file exists
            import os
            if not os.path.exists(self.db_path):
                print(f"SQLite database file not found: {self.db_path}")
                return False
            
            # Check if file is readable
            if not os.access(self.db_path, os.R_OK):
                print(f"SQLite database file not readable: {self.db_path}")
                return False
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            return True
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
            return False
    
    def disconnect(self):
        """Close SQLite connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_available_products(self, status_filter: str = 'In-stock') -> List[Dict]:
        """
        Get all available products from SQLite database
        Only returns products with specified status (default: In-stock)
        """
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT * FROM Products 
                WHERE status = ? 
                ORDER BY date DESC
            """
            cursor.execute(query, (status_filter,))
            products = [dict(row) for row in cursor.fetchall()]
            return products
        except Exception as e:
            print(f"Error fetching products from SQLite: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_product_by_reel_number(self, reel_number: str) -> Optional[Dict]:
        """Get a specific product by reel number"""
        if not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM Products WHERE reel_number = ?"
            cursor.execute(query, (reel_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error fetching product by reel number: {e}")
            return None
        finally:
            self.disconnect()
    
    def update_product_status(self, reel_number: str, new_status: str) -> bool:
        """
        Update product status in SQLite database
        Used for syncing sales/cancellations back to SQLite
        """
        if not self.connect():
            print(f"Failed to connect to SQLite database for product {reel_number}")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # First check if product exists
            check_query = "SELECT COUNT(*) FROM Products WHERE reel_number = ?"
            cursor.execute(check_query, (reel_number,))
            product_exists = cursor.fetchone()[0] > 0
            
            if not product_exists:
                print(f"Product {reel_number} not found in SQLite database")
                return False
            
            # Update the product status
            update_query = """
                UPDATE Products 
                SET status = ?, last_date = ? 
                WHERE reel_number = ?
            """
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(update_query, (new_status, current_time, reel_number))
            self.connection.commit()
            
            rows_updated = cursor.rowcount
            if rows_updated > 0:
                print(f"Successfully updated product {reel_number} status to {new_status}")
                return True
            else:
                print(f"No rows updated for product {reel_number}")
                return False
                
        except Exception as e:
            print(f"Error updating product {reel_number} status in SQLite: {e}")
            return False
        finally:
            self.disconnect()
    
    def test_connection(self) -> Dict:
        """
        Test SQLite connection and basic operations
        """
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            # Test file existence
            import os
            if not os.path.exists(self.db_path):
                result['message'] = f"Database file not found: {self.db_path}"
                return result
            
            # Test file permissions
            if not os.access(self.db_path, os.R_OK):
                result['message'] = f"Database file not readable: {self.db_path}"
                return result
            
            # Test connection
            if not self.connect():
                result['message'] = "Failed to connect to database"
                return result
            
            # Test table existence
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Products'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                result['message'] = "Products table not found in database"
                return result
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM Products")
            product_count = cursor.fetchone()[0]
            
            result['success'] = True
            result['message'] = f"Connection successful. Found {product_count} products in database."
            result['details'] = {
                'file_path': self.db_path,
                'file_size': os.path.getsize(self.db_path),
                'product_count': product_count
            }
            
        except Exception as e:
            result['message'] = f"Connection test failed: {str(e)}"
        finally:
            self.disconnect()
        
        return result


class InventorySyncService:
    """
    Main service for handling inventory synchronization
    """
    
    def __init__(self):
        self.sqlite_service = SQLiteInventoryService()
        self.field_mappings = self._load_field_mappings()
    
    def _load_field_mappings(self) -> Dict[str, str]:
        """Load field mappings from database"""
        mappings = {}
        try:
            active_mappings = FieldMapping.objects.filter(is_active=True)
            
            for mapping in active_mappings:
                mappings[mapping.external_field] = mapping.django_field
            
            # If no mappings found, use defaults
            if not mappings:
                mappings = {
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
        except Exception as e:
            # Default mappings based on provided schema
            mappings = {
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
        
        return mappings
    
    def _map_external_to_django(self, external_data: Dict) -> Dict:
        """Map external SQLite data to Django model fields"""
        django_data = {}
        
        # Default values for required fields
        defaults = {
            'width': 0,
            'gsm': 0,
            'length': 0,
            'breaks': 0,
            'grade': 'Unknown',
            'location': 'Anbar_Akhal',
            'status': 'In-stock',
        }
        
        # Get Django Product model fields to filter out non-existent fields
        try:
            from core.models import Product
            django_fields = [field.name for field in Product._meta.get_fields()]
        except Exception as e:
            django_fields = ['reel_number', 'width', 'gsm', 'length', 'grade', 'breaks', 'qr_code', 'location', 'status', 'price']
        
        for external_field, value in external_data.items():
            if external_field in self.field_mappings:
                django_field = self.field_mappings[external_field]
                
                # Skip fields that don't exist in Django model
                if django_field not in django_fields:
                    continue
                
                # Handle NULL values and provide defaults for required fields
                if value is None or value == '':
                    if django_field in defaults:
                        django_data[django_field] = defaults[django_field]
                    else:
                        # Skip NULL values for optional fields
                        continue
                else:
                    # Convert numeric fields to proper types
                    if django_field in ['width', 'gsm', 'length', 'breaks']:
                        try:
                            django_data[django_field] = int(float(value))
                        except (ValueError, TypeError):
                            django_data[django_field] = defaults[django_field]
                    else:
                        django_data[django_field] = value
        
        # Ensure all required fields have values
        for field, default_value in defaults.items():
            if field not in django_data and field in django_fields:
                django_data[field] = default_value
        
        return django_data
    
    def _should_import_product(self, external_product: Dict) -> bool:
        """
        Check if product should be imported based on business rules
        """
        # Only import In-stock products
        if external_product.get('status') != 'In-stock':
            return False
        
        # Ensure reel number exists
        if not external_product.get('reel_number'):
            return False
        
        return True
    
    def get_importable_products(self) -> List[Dict]:
        """
        Get list of products that can be imported from SQLite
        """
        external_products = self.sqlite_service.get_available_products('In-stock')
        importable_products = []
        
        # Get all existing reel numbers in Django for efficient filtering
        try:
            from core.models import Product
            existing_reel_numbers = set(Product.objects.values_list('reel_number', flat=True))
        except Exception as e:
            print(f"Error getting existing reel numbers: {e}")
            existing_reel_numbers = set()
        
        for product in external_products:
            reel_number = product.get('reel_number')
            if not reel_number:
                continue
                
            # Skip if product already exists in Django (unless it was sold/delivered)
            if reel_number in existing_reel_numbers:
                try:
                    existing_product = Product.objects.filter(reel_number=reel_number).first()
                    if existing_product and existing_product.status not in ['Sold', 'Delivered']:
                        continue  # Skip already imported products that are still in stock
                except Exception as e:
                    print(f"Error checking product status: {e}")
                    continue
            
            # Check other import criteria
            if self._should_import_product(product):
                # Add mapped data
                mapped_data = self._map_external_to_django(product)
                importable_products.append({
                    'external_data': product,
                    'django_data': mapped_data,
                    'reel_number': reel_number,
                    'external_id': product.get('id'),
                })
        
        return importable_products
    
    def import_selected_products(self, selected_reel_numbers: List[str], user=None) -> Dict:
        """
        Import selected products from SQLite to Django database
        """
        start_time = timezone.now()
        results = {
            'imported': 0,
            'updated': 0,
            'errors': [],
            'products_processed': len(selected_reel_numbers)
        }
        
        try:
            from core.models import Product
            
            with transaction.atomic():
                for reel_number in selected_reel_numbers:
                    try:
                        # Get product from SQLite
                        external_product = self.sqlite_service.get_product_by_reel_number(reel_number)
                        if not external_product:
                            results['errors'].append(f"Product {reel_number} not found in SQLite")
                            continue
                        
                        # Map data
                        django_data = self._map_external_to_django(external_product)
                        
                        # Validate required fields
                        required_fields = ['reel_number', 'width', 'gsm', 'length', 'grade']
                        missing_fields = [field for field in required_fields if not django_data.get(field)]
                        
                        if missing_fields:
                            results['errors'].append(f"Product {reel_number} missing required fields: {', '.join(missing_fields)}")
                            continue
                        
                        # Check if product exists
                        existing_product = Product.objects.filter(reel_number=reel_number).first()
                        
                        if existing_product:
                            # Update existing product
                            for field, value in django_data.items():
                                if hasattr(existing_product, field):
                                    setattr(existing_product, field, value)
                            existing_product.save()
                            results['updated'] += 1
                        else:
                            # Create new product
                            try:
                                new_product = Product.objects.create(**django_data)
                                results['imported'] += 1
                            except Exception as create_error:
                                results['errors'].append(f"Error creating product {reel_number}: {str(create_error)}")
                                continue
                        
                        # Create or update mapping
                        try:
                            mapping, created = ProductMapping.objects.get_or_create(
                                reel_number=reel_number,
                                defaults={
                                    'external_id': external_product.get('id'),
                                    'django_product_id': existing_product.id if existing_product else new_product.id,
                                    'sync_status': 'imported'
                                }
                            )
                            if not created:
                                mapping.django_product_id = existing_product.id if existing_product else new_product.id
                                mapping.sync_status = 'updated'
                                mapping.save()
                        except Exception as mapping_error:
                            results['errors'].append(f"Error creating mapping for product {reel_number}: {str(mapping_error)}")
                            continue
                    
                    except Exception as e:
                        error_msg = f"Error importing product {reel_number}: {str(e)}"
                        results['errors'].append(error_msg)
                        print(error_msg)
        
        except Exception as e:
            error_msg = f"Transaction error during import: {str(e)}"
            results['errors'].append(error_msg)
            print(error_msg)
        
        # Log the operation
        duration = (timezone.now() - start_time).total_seconds()
        SyncLog.objects.create(
            sync_type='import',
            operation=f"Import {len(selected_reel_numbers)} products",
            products_processed=results['products_processed'],
            products_imported=results['imported'],
            products_updated=results['updated'],
            errors='\n'.join(results['errors']) if results['errors'] else None,
            executed_by=user,
            duration_seconds=duration
        )
        
        return results
    
    def sync_sales_to_sqlite(self, user=None) -> Dict:
        """
        Sync sales/cancellations from Django back to SQLite
        """
        start_time = timezone.now()
        results = {
            'exported': 0,
            'errors': [],
            'products_processed': 0
        }
        
        try:
            from core.models import Product
            
            # Get products that have been sold/delivered since last sync
            sold_products = Product.objects.filter(
                status__in=['Sold', 'Delivered'],
                reel_number__isnull=False
            ).exclude(reel_number='')
            
            results['products_processed'] = sold_products.count()
            
            if results['products_processed'] == 0:
                print("No sold products found to sync")
                return results
            
            print(f"Found {results['products_processed']} sold products to sync")
            
            for product in sold_products:
                try:
                    print(f"Attempting to sync product {product.reel_number} with status {product.status}")
                    
                    # Update status in SQLite
                    success = self.sqlite_service.update_product_status(
                        product.reel_number, 
                        product.status
                    )
                    
                    if success:
                        results['exported'] += 1
                        print(f"Successfully synced product {product.reel_number}")
                        
                        # Update mapping
                        try:
                            mapping, created = ProductMapping.objects.get_or_create(
                                reel_number=product.reel_number,
                                defaults={
                                    'external_id': 0,  # Will be updated when we know the external ID
                                    'django_product_id': product.id,
                                    'sync_status': 'exported'
                                }
                            )
                            if not created:
                                mapping.sync_status = 'exported'
                                mapping.save()
                        except Exception as mapping_error:
                            print(f"Error updating mapping for {product.reel_number}: {mapping_error}")
                            # Don't add to errors as the main sync was successful
                    else:
                        error_msg = f"Failed to update {product.reel_number} in SQLite - product may not exist in SQLite database"
                        results['errors'].append(error_msg)
                        print(error_msg)
                
                except Exception as e:
                    error_msg = f"Error syncing product {product.reel_number}: {str(e)}"
                    results['errors'].append(error_msg)
                    print(error_msg)
        
        except Exception as e:
            error_msg = f"Error during sales sync: {str(e)}"
            results['errors'].append(error_msg)
            print(error_msg)
        
        # Log the operation
        duration = (timezone.now() - start_time).total_seconds()
        try:
            SyncLog.objects.create(
                sync_type='export',
                operation=f"Export {results['exported']} sales to SQLite",
                products_processed=results['products_processed'],
                products_exported=results['exported'],
                errors='\n'.join(results['errors']) if results['errors'] else None,
                executed_by=user,
                duration_seconds=duration
            )
        except Exception as log_error:
            print(f"Error creating sync log: {log_error}")
        
        return results
    
    def perform_full_sync(self, user=None) -> Dict:
        """
        Perform full synchronization (import + export)
        """
        start_time = timezone.now()
        
        # First sync sales to SQLite
        export_results = self.sync_sales_to_sqlite(user)
        
        # Then get importable products (this will exclude newly sold ones)
        importable_products = self.get_importable_products()
        
        # Determine if sync was successful
        sync_successful = export_results['exported'] > 0 or export_results['products_processed'] == 0
        
        # Filter out non-critical errors (like products not found in SQLite)
        critical_errors = []
        non_critical_errors = []
        
        for error in export_results.get('errors', []):
            if 'not found in SQLite database' in error or 'Failed to update' in error:
                non_critical_errors.append(error)
            else:
                critical_errors.append(error)
        
        results = {
            'exported': export_results['exported'],
            'importable_count': len(importable_products),
            'errors': critical_errors,  # Only include critical errors
            'warnings': non_critical_errors,  # Non-critical issues as warnings
            'sync_successful': sync_successful,
            'duration_seconds': (timezone.now() - start_time).total_seconds()
        }
        
        # Log the operation
        try:
            SyncLog.objects.create(
                sync_type='manual',
                operation="Full inventory synchronization",
                products_processed=export_results['products_processed'],
                products_exported=export_results['exported'],
                errors='\n'.join(critical_errors) if critical_errors else None,
                executed_by=user,
                duration_seconds=results['duration_seconds']
            )
        except Exception as log_error:
            print(f"Error creating sync log: {log_error}")
        
        return results
    
    def should_run_auto_sync(self) -> bool:
        """
        Check if automatic sync should run based on configuration
        """
        try:
            config = SyncConfig.objects.first()
            if not config:
                # Create default config
                config = SyncConfig.objects.create()
            
            if not config.is_auto_sync_enabled:
                return False
            
            if not config.last_auto_sync:
                return True
            
            # Check if enough time has passed
            next_sync_time = config.last_auto_sync + timedelta(minutes=config.auto_sync_interval_minutes)
            return timezone.now() >= next_sync_time
            
        except Exception as e:
            print(f"Error checking auto sync: {e}")
            return False
    
    def run_auto_sync(self) -> Dict:
        """
        Run automatic synchronization
        """
        try:
            config = SyncConfig.objects.first()
            if not config:
                config = SyncConfig.objects.create()
            
            results = self.perform_full_sync()
            
            # Update last auto sync time
            config.last_auto_sync = timezone.now()
            config.save()
            
            return results
            
        except Exception as e:
            print(f"Error in auto sync: {e}")
            return {'errors': [str(e)]} 