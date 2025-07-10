from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Customer, Order, Product
import json
import random
from datetime import timedelta
import string
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create comprehensive test customers and orders with logs.'

    def random_timestamp(self):
        days = random.randint(1, 30)
        hours = random.randint(1, 24)
        minutes = random.randint(1, 60)
        return (timezone.now() - timedelta(days=days, hours=hours, minutes=minutes)).isoformat()

    def handle(self, *args, **options):
        # Define test customer names
        customer_names = ["Ali Mohammadi", "Sara Ahmadi", "Reza Karimi", "Mina Hosseini", "Amir Tehrani", "LOG_TEST_12345"]
        # Delete all test customers first
        self.stdout.write(self.style.WARNING('Deleting old test customers...'))
        Customer.objects.filter(customer_name__in=customer_names).delete()
        self.stdout.write(self.style.SUCCESS('Old test customers deleted.'))

        # Create new test customers and show logs
        customers = []
        for name in customer_names:
            customer = Customer.objects.create(
                customer_name=name,
                phone=f"0912{random.randint(1000000, 9999999)}",
                status=random.choice(["Active", "Inactive", "Suspended", "Blocked"]),
                address=f"Tehran, District {random.randint(1, 22)}",
                comments="Initial creation by test",
                economic_code=str(random.randint(100000, 999999)),
                postcode=str(random.randint(1000000000, 9999999999)),
                national_id=str(random.randint(1000000000, 9999999999)),
            )
            self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.customer_name}'))
            self.stdout.write(f'Logs after creation: {customer.logs}')
            # Update comments and status to test log append
            customer.comments = "Updated by test (edit)"
            customer.status = random.choice(["Active", "Inactive", "Suspended", "Blocked"])
            customer.save()
            self.stdout.write(self.style.SUCCESS(f'Updated customer: {customer.customer_name}'))
            self.stdout.write(f'Logs after update: {customer.logs}')
            customers.append(customer)

        # Create test products if not exist
        if not Product.objects.exists():
            for i in range(10):
                Product.objects.create(
                    reel_number=f"TEST-{i+1:04d}",
                    location="Anbar_Akhal",
                    status="In-stock",
                    width=random.randint(800, 1600),
                    gsm=random.choice([70, 80, 90, 100, 120, 140, 160]),
                    length=random.randint(500, 2000),
                    grade=random.choice(['A', 'B', 'C', 'A+', 'B+']),
                    breaks=random.randint(0, 5),
                    price=Decimal(random.randint(100000, 500000)),
                    qr_code=f"QR-{i+1:04d}"
                )

        # Create test orders for each customer
        for customer in customers:
            for i in range(2):
                order = Order(
                    customer=customer,
                    payment_method=random.choice(["Cash", "Terms", "Bank_Transfer", "Check"]),
                    status=random.choice(["Pending", "Confirmed", "Processing", "Ready", "Delivered", "Cancelled", "Returned"]),
                    total_amount=Decimal(random.randint(1000000, 5000000)),
                    discount_percentage=Decimal(random.choice([0, 5, 10, 15, 20])),
                    discount_amount=Decimal(0),  # Will be calculated
                    final_amount=Decimal(0),     # Will be calculated
                    notes=f"Test order {i+1} for {customer.customer_name}",
                    delivery_address=f"Delivery address {i+1} for {customer.customer_name}",
                    expected_delivery_date=timezone.now(),
                    actual_delivery_date=timezone.now(),
                )
                order.save()
                self.stdout.write(self.style.SUCCESS(f'Created order: {order.order_number} for {customer.customer_name}'))
                self.stdout.write(f'Order logs: {order.logs}')
                # Update status and payment method to test log append
                order.status = random.choice(["Pending", "Confirmed", "Processing", "Ready", "Delivered", "Cancelled", "Returned"])
                order.payment_method = random.choice(["Cash", "Terms", "Bank_Transfer", "Check"])
                order.final_amount = order.total_amount - (order.total_amount * order.discount_percentage / 100)
                order.save()
                self.stdout.write(self.style.SUCCESS(f'Updated order: {order.order_number}'))
                self.stdout.write(f'Order logs after update: {order.logs}')

        # Export logs to CSV
        from django.core.management import call_command
        call_command('export_logs_to_csv')
        self.stdout.write(self.style.SUCCESS('✅ All logs exported to CSV files')) 