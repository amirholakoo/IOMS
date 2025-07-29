from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from inventory_sync.services import InventorySyncService
from inventory_sync.models import SyncConfig


class Command(BaseCommand):
    help = 'Perform manual inventory synchronization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--import-only',
            action='store_true',
            help='Only import products, skip export',
        )
        parser.add_argument(
            '--export-only',
            action='store_true',
            help='Only export sales, skip import',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting inventory synchronization...')
        )
        
        sync_service = InventorySyncService()
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
            
            # Show what would be imported
            importable_products = sync_service.get_importable_products()
            self.stdout.write(
                f'Found {len(importable_products)} products available for import:'
            )
            for product in importable_products[:10]:  # Show first 10
                self.stdout.write(f'  - {product["reel_number"]} ({product["external_data"]["grade"]})')
            if len(importable_products) > 10:
                self.stdout.write(f'  ... and {len(importable_products) - 10} more')
            
            return
        
        try:
            if options['import_only']:
                self.stdout.write('Performing import-only synchronization...')
                importable_products = sync_service.get_importable_products()
                if importable_products:
                    reel_numbers = [p['reel_number'] for p in importable_products]
                    results = sync_service.import_selected_products(reel_numbers)
                    self._display_results(results, 'Import')
                else:
                    self.stdout.write(
                        self.style.WARNING('No products available for import')
                    )
            
            elif options['export_only']:
                self.stdout.write('Performing export-only synchronization...')
                results = sync_service.sync_sales_to_sqlite()
                self._display_results(results, 'Export')
            
            else:
                self.stdout.write('Performing full synchronization...')
                results = sync_service.perform_full_sync()
                self._display_results(results, 'Full Sync')
            
            self.stdout.write(
                self.style.SUCCESS('Synchronization completed successfully!')
            )
            
        except Exception as e:
            raise CommandError(f'Synchronization failed: {str(e)}')
    
    def _display_results(self, results, operation_type):
        """Display synchronization results"""
        self.stdout.write(f'\n{operation_type} Results:')
        self.stdout.write(f'  Products processed: {results.get("products_processed", 0)}')
        self.stdout.write(f'  Products imported: {results.get("imported", 0)}')
        self.stdout.write(f'  Products updated: {results.get("updated", 0)}')
        self.stdout.write(f'  Products exported: {results.get("exported", 0)}')
        
        if results.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'  Errors: {len(results["errors"])}')
            )
            for error in results['errors'][:5]:  # Show first 5 errors
                self.stdout.write(f'    - {error}')
            if len(results['errors']) > 5:
                self.stdout.write(f'    ... and {len(results["errors"]) - 5} more errors')
        
        if results.get('duration_seconds'):
            self.stdout.write(f'  Duration: {results["duration_seconds"]:.2f} seconds') 