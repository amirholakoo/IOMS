import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from payments.models import Payment


class Command(BaseCommand):
    help = 'Export payment logs to CSV file'

    def handle(self, *args, **options):
        # Create CSV logs directory if it doesn't exist
        csv_dir = os.path.join(settings.BASE_DIR, '..', 'csv_logs')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Path to payments logs CSV file
        csv_file_path = os.path.join(csv_dir, 'payments_logs.csv')
        
        try:
            # Get all payments with logs
            payments = Payment.objects.exclude(logs='').order_by('created_at')
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Payment ID',
                    'Tracking Code', 
                    'Order Number',
                    'Customer Name',
                    'Gateway',
                    'Amount (Toman)',
                    'Status',
                    'Logs',
                    'Created At'
                ])
                
                # Write payment logs
                for payment in payments:
                    if payment.logs:
                        writer.writerow([
                            payment.id,
                            payment.tracking_code,
                            payment.order.order_number,
                            payment.order.customer.customer_name,
                            payment.get_gateway_display_persian(),
                            f"{payment.display_amount:,.0f}",
                            payment.get_status_display_persian(),
                            payment.logs,
                            payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        ])
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Exported payment logs to {csv_file_path}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error exporting payment logs: {str(e)}')
            ) 