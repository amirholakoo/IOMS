import csv
import os
from django.core.management.base import BaseCommand
from payments.models import Payment

class Command(BaseCommand):
    help = 'Export payment logs to CSV file'

    def handle(self, *args, **options):
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'csv_logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Path to payments logs CSV file
        csv_file_path = os.path.join(logs_dir, 'payments_logs.csv')
        
        try:
            # Get all payments with logs
            payments = Payment.objects.exclude(logs='').order_by('created_at')
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['payment_id', 'order_id', 'order_number', 'log_line'])
                for payment in payments:
                    log_line = ' | '.join([line.strip() for line in payment.logs.split(',') if line.strip()])
                    writer.writerow([
                        payment.id,
                        payment.order.id if payment.order else '',
                        payment.order.order_number if payment.order else '',
                        log_line
                    ])
            self.stdout.write(self.style.SUCCESS(f'✅ Exported payment logs to {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error exporting payment logs: {e}')) 