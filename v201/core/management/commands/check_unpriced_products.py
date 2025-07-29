from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Check for un-priced products in the database'

    def handle(self, *args, **options):
        # Check for products without prices (price = 0)
        un_priced_products = Product.objects.filter(
            status='In-stock',
            price=0
        )
        
        # Check for products with price = 0
        zero_priced_products = Product.objects.filter(
            status='In-stock',
            price=0
        )
        
        # Check for products with price = None (shouldn't exist with default=0.00)
        null_priced_products = Product.objects.filter(
            status='In-stock',
            price__isnull=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'🔍 Database Check Results:'))
        self.stdout.write(f'📦 Total products in stock: {Product.objects.filter(status="In-stock").count()}')
        self.stdout.write(f'💰 Products with prices: {Product.objects.filter(status="In-stock", price__isnull=False, price__gt=0).count()}')
        self.stdout.write(f'❌ Products with price = 0: {zero_priced_products.count()}')
        self.stdout.write(f'❌ Products with price = None: {null_priced_products.count()}')
        self.stdout.write(f'🚨 Total un-priced products: {un_priced_products.count()}')
        
        if un_priced_products.exists():
            self.stdout.write(self.style.WARNING('\n📋 Un-priced products list:'))
            for product in un_priced_products[:10]:  # Show first 10
                self.stdout.write(f'  - {product.reel_number} (ID: {product.id}) - Price: {product.price}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No un-priced products found!'))
            
        # Check if we need to create test data
        if not un_priced_products.exists():
            self.stdout.write(self.style.WARNING('\n💡 To test the feature, you can create a product without price:'))
            self.stdout.write('   python manage.py shell')
            self.stdout.write('   from core.models import Product')
            self.stdout.write('   Product.objects.create(reel_number="TEST-001", width=200, gsm=80, length=100, grade="A", status="In-stock", price=None)') 