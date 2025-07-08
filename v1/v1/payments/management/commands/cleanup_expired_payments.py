from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.services import PaymentService


class Command(BaseCommand):
    help = 'Cleanup expired payments and mark them as timeout'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 DRY RUN MODE - No actual changes will be made')
            )
        
        try:
            # Check and cleanup expired payments
            expired_count = PaymentService.check_expired_payments()
            
            if dry_run:
                # In dry run, just show what would be expired
                from payments.models import Payment
                expired_payments = Payment.objects.filter(
                    status__in=['INITIATED', 'REDIRECTED', 'PENDING'],
                    expires_at__lt=timezone.now()
                )
                
                self.stdout.write(f"🔍 Found {expired_payments.count()} expired payments:")
                for payment in expired_payments:
                    self.stdout.write(
                        f"  - {payment.tracking_code} (Expired: {payment.expires_at})"
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Cleaned up {expired_count} expired payments')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error cleaning up expired payments: {str(e)}')
            ) 