from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from inventory_sync.services import InventorySyncService
from inventory_sync.models import SyncConfig


class Command(BaseCommand):
    help = 'Run automatic inventory synchronization based on configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if not due',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        sync_service = InventorySyncService()
        
        if options['verbose']:
            self.stdout.write('Checking auto-sync configuration...')
        
        # Check if auto-sync should run
        if not options['force'] and not sync_service.should_run_auto_sync():
            if options['verbose']:
                self.stdout.write(
                    self.style.WARNING('Auto-sync not due yet. Use --force to override.')
                )
            return
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS('Starting automatic inventory synchronization...')
            )
        
        try:
            # Perform auto-sync
            results = sync_service.run_auto_sync()
            
            if options['verbose']:
                self._display_results(results)
            
            if results.get('errors'):
                self.stdout.write(
                    self.style.WARNING(
                        f'Auto-sync completed with {len(results["errors"])} errors'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Automatic synchronization completed successfully!')
                )
                
        except Exception as e:
            error_msg = f'Automatic synchronization failed: {str(e)}'
            if options['verbose']:
                raise CommandError(error_msg)
            else:
                self.stdout.write(self.style.ERROR(error_msg))
    
    def _display_results(self, results):
        """Display synchronization results"""
        self.stdout.write(f'\nAuto-Sync Results:')
        self.stdout.write(f'  Products exported: {results.get("exported", 0)}')
        self.stdout.write(f'  Products available for import: {results.get("importable_count", 0)}')
        
        if results.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'  Errors: {len(results["errors"])}')
            )
            for error in results['errors'][:3]:  # Show first 3 errors
                self.stdout.write(f'    - {error}')
            if len(results['errors']) > 3:
                self.stdout.write(f'    ... and {len(results["errors"]) - 3} more errors')
        
        if results.get('duration_seconds'):
            self.stdout.write(f'  Duration: {results["duration_seconds"]:.2f} seconds') 