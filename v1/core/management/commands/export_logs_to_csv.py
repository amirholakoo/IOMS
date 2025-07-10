from django.core.management.base import BaseCommand
from core.models import Customer, Order
import os
import csv

class Command(BaseCommand):
    help = 'Export all customer and order logs to csv_logs directory.'

    def handle(self, *args, **options):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
        logs_dir = os.path.join(base_dir, 'csv_logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Export customer logs
        customers_csv = os.path.join(logs_dir, 'customers_logs.csv')
        with open(customers_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['customer_id', 'customer_name', 'log_line'])
            for customer in Customer.objects.all():
                if customer.logs:
                    for line in customer.logs.strip().split('\n'):
                        if line.strip():
                            writer.writerow([customer.id, customer.customer_name, line.strip()])
        self.stdout.write(self.style.SUCCESS(f'✅ Exported customer logs to {customers_csv}'))

        # Export order logs
        orders_csv = os.path.join(logs_dir, 'orders_logs.csv')
        with open(orders_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['order_id', 'order_number', 'log_line'])
            for order in Order.objects.all():
                if order.logs:
                    for line in order.logs.strip().split('\n'):
                        if line.strip():
                            writer.writerow([order.id, order.order_number, line.strip()])
        self.stdout.write(self.style.SUCCESS(f'✅ Exported order logs to {orders_csv}')) 