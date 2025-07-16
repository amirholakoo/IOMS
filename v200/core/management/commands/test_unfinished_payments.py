from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Order, OrderItem, Product, Customer
from payments.models import Payment
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the unfinished payment orders feature'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for unfinished payments',
        )
        parser.add_argument(
            '--check-unfinished',
            action='store_true',
            help='Check for unfinished payment orders',
        )

    def handle(self, *args, **options):
        if options['create_test_data']:
            self.create_test_data()
        elif options['check_unfinished']:
            self.check_unfinished_orders()
        else:
            self.stdout.write(
                self.style.WARNING('Please specify --create-test-data or --check-unfinished')
            )

    def create_test_data(self):
        """Create test data for unfinished payment orders"""
        self.stdout.write('Creating test data for unfinished payments...')
        
        # Create a test customer
        customer, created = Customer.objects.get_or_create(
            phone='09123456789',
            defaults={
                'customer_name': 'Test Customer',
                'status': 'Active',
                'address': 'Test Address',
            }
        )
        
        if created:
            self.stdout.write(f'Created customer: {customer.customer_name}')
        
        # Create test products
        products = []
        for i in range(3):
            product, created = Product.objects.get_or_create(
                reel_number=f'TEST-REEL-{i+1}',
                defaults={
                    'width': 1000 + (i * 100),
                    'gsm': 80 + (i * 10),
                    'length': 1000 + (i * 100),
                    'grade': 'A',
                    'price': Decimal('50000') + (i * 10000),
                    'status': 'In-stock',
                    'location': 'A1',
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.reel_number}')
        
        # Create a test order with cash items
        order, created = Order.objects.get_or_create(
            order_number='TEST-ORDER-001',
            defaults={
                'customer': customer,
                'status': 'Pending',
                'payment_method': 'Cash',
                'final_amount': Decimal('150000'),
            }
        )
        
        if created:
            self.stdout.write(f'Created order: {order.order_number}')
            
            # Create order items
            for i, product in enumerate(products):
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    unit_price=product.price,
                    total_price=product.price,
                    payment_method='Cash'
                )
                self.stdout.write(f'Created order item: {order_item.product.reel_number}')
        
        self.stdout.write(
            self.style.SUCCESS('Test data created successfully!')
        )

    def check_unfinished_orders(self):
        """Check for unfinished payment orders"""
        self.stdout.write('Checking for unfinished payment orders...')
        
        # Find orders that are in 'Pending' or 'Processing' status with cash items but no successful payments
        unfinished_orders = Order.objects.filter(
            status__in=['Pending', 'Processing'],
            payment_method='Cash'
        ).prefetch_related('order_items', 'order_items__product')
        
        self.stdout.write(f'Found {unfinished_orders.count()} orders with Pending/Processing status')
        
        for order in unfinished_orders:
            # Check if order has cash items
            cash_items = order.order_items.filter(payment_method='Cash')
            if cash_items.exists():
                # Calculate total cash amount
                total_cash_amount = sum(item.total_price for item in cash_items)
                
                # Check if there are no successful payments for this order
                successful_payments = Payment.objects.filter(
                    order=order,
                    status='SUCCESS'
                ).exists()
                
                if not successful_payments and total_cash_amount > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Unfinished order found: {order.order_number} - '
                            f'Amount: {total_cash_amount} - '
                            f'Items: {cash_items.count()}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Order {order.order_number} has successful payments or no cash amount'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Order {order.order_number} has no cash items'
                    )
                ) 