from django.core.management.base import BaseCommand
from core.models import Customer
from django.db.models import Count

class Command(BaseCommand):
    help = 'حذف رکوردهای تکراری مشتریان بر اساس شماره موبایل (فقط یکی باقی می‌ماند)'

    def handle(self, *args, **options):
        duplicates = Customer.objects.values('phone').annotate(count=Count('id')).filter(count__gt=1)
        total_deleted = 0
        for item in duplicates:
            phone = item['phone']
            customers = Customer.objects.filter(phone=phone).order_by('id')
            # فقط اولین رکورد را نگه دار، بقیه را حذف کن
            to_delete_ids = list(customers.values_list('id', flat=True))[1:]
            count = len(to_delete_ids)
            if count > 0:
                Customer.objects.filter(id__in=to_delete_ids).delete()
            total_deleted += count
            self.stdout.write(self.style.WARNING(f'شماره {phone}: {count} رکورد تکراری حذف شد'))
        if total_deleted == 0:
            self.stdout.write(self.style.SUCCESS('هیچ رکورد تکراری یافت نشد.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'پاکسازی انجام شد. مجموع {total_deleted} رکورد تکراری حذف شد.')) 