from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Create a test product with price=0 for testing un-priced products feature'

    def handle(self, *args, **options):
        try:
            # Create a test product with price=0
            product = Product.objects.create(
                reel_number="TEST-UNPRICED-001",
                location="Anbar_Akhal",
                width=200,
                gsm=80,
                length=100,
                grade="A",
                status="In-stock",
                price=0.00  # This makes it un-priced
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Test un-priced product created successfully!\n'
                    f'📦 Reel Number: {product.reel_number}\n'
                    f'💰 Price: {product.price} تومان\n'
                    f'📊 Status: {product.get_status_display()}\n'
                    f'📍 Location: {product.get_location_display()}'
                )
            )
            
            # Also create a product with price for comparison
            priced_product = Product.objects.create(
                reel_number="TEST-PRICED-001",
                location="Anbar_Akhal",
                width=210,
                gsm=85,
                length=120,
                grade="A",
                status="In-stock",
                price=2500000.00  # This makes it priced
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Test priced product created successfully!\n'
                    f'📦 Reel Number: {priced_product.reel_number}\n'
                    f'💰 Price: {priced_product.price:,.0f} تومان\n'
                    f'📊 Status: {priced_product.get_status_display()}\n'
                    f'📍 Location: {priced_product.get_location_display()}'
                )
            )
            
            self.stdout.write(
                self.style.WARNING(
                    f'\n💡 Now you can test the feature:\n'
                    f'   1. Visit the main page as a customer\n'
                    f'   2. Visit the admin dashboard as a super admin\n'
                    f'   3. Run: python manage.py check_unpriced_products'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating test product: {e}')
            ) 