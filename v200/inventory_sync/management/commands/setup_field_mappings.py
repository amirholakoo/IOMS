from django.core.management.base import BaseCommand
from inventory_sync.models import FieldMapping


class Command(BaseCommand):
    help = 'Set up default field mappings for inventory sync'

    def handle(self, *args, **options):
        # Get Django Product model fields
        try:
            from core.models import Product
            django_fields = [field.name for field in Product._meta.get_fields()]
            self.stdout.write(f"Django Product model fields: {django_fields}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting Django model fields: {e}')
            )
            return

        # Default field mappings - only include fields that exist in Django model
        all_mappings = [
            ('reel_number', 'reel_number'),
            ('width', 'width'),
            ('gsm', 'gsm'),
            ('length', 'length'),
            ('grade', 'grade'),
            ('breaks', 'breaks'),
            ('comments', 'comments'),
            ('qr_code', 'qr_code'),
            ('profile_name', 'profile_name'),
            ('location', 'location'),
            ('status', 'status'),
            ('receive_date', 'receive_date'),
            ('last_date', 'last_date'),
            ('username', 'username'),
            ('logs', 'logs'),
        ]
        
        # Filter mappings to only include fields that exist in Django model
        default_mappings = [
            (external_field, django_field) 
            for external_field, django_field in all_mappings 
            if django_field in django_fields
        ]
        
        self.stdout.write(f"Creating {len(default_mappings)} field mappings...")

        created_count = 0
        updated_count = 0

        for external_field, django_field in default_mappings:
            mapping, created = FieldMapping.objects.get_or_create(
                external_field=external_field,
                django_field=django_field,
                defaults={'is_active': True}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created mapping: {external_field} -> {django_field}')
                )
            else:
                # Ensure existing mappings are active
                if not mapping.is_active:
                    mapping.is_active = True
                    mapping.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Activated mapping: {external_field} -> {django_field}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Field mappings setup complete. Created: {created_count}, Updated: {updated_count}'
            )
        ) 