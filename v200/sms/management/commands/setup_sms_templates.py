"""
📝 Management command to set up default SMS templates
"""

from django.core.management.base import BaseCommand
from sms.models import SMSTemplate


class Command(BaseCommand):
    help = '📝 ایجاد قالب‌های پیش‌فرض SMS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 شروع ایجاد قالب‌های SMS...'))
        
        templates_data = [
            {
                'name': 'کد تایید ورود',
                'template_type': 'VERIFICATION',
                'content': 'کد تایید شما: {code}\nمعتبر تا {expires_at}\n\nHomayOMS',
                'variables': {'code': 'کد 6 رقمی', 'expires_at': 'زمان انقضا'}
            },
            {
                'name': 'تایید سفارش',
                'template_type': 'ORDER_STATUS',
                'content': 'سفارش {order_number} شما تایید شد.\nمبلغ: {amount} تومان\n\nHomayOMS',
                'variables': {'order_number': 'شماره سفارش', 'amount': 'مبلغ'}
            },
            {
                'name': 'آماده تحویل',
                'template_type': 'ORDER_STATUS',
                'content': 'سفارش {order_number} شما آماده تحویل است.\nلطفاً برای دریافت مراجعه کنید.\n\nHomayOMS',
                'variables': {'order_number': 'شماره سفارش'}
            },
            {
                'name': 'تحویل شده',
                'template_type': 'ORDER_STATUS',
                'content': 'سفارش {order_number} شما تحویل داده شد.\nاز خرید شما متشکریم.\n\nHomayOMS',
                'variables': {'order_number': 'شماره سفارش'}
            },
            {
                'name': 'پرداخت موفق',
                'template_type': 'PAYMENT',
                'content': 'پرداخت سفارش {order_number} با موفقیت انجام شد.\nمبلغ: {amount} تومان\n\nHomayOMS',
                'variables': {'order_number': 'شماره سفارش', 'amount': 'مبلغ'}
            },
            {
                'name': 'پرداخت ناموفق',
                'template_type': 'PAYMENT',
                'content': 'پرداخت سفارش {order_number} ناموفق بود.\nلطفاً مجدداً تلاش کنید.\n\nHomayOMS',
                'variables': {'order_number': 'شماره سفارش'}
            },
            {
                'name': 'خوش‌آمدگویی',
                'template_type': 'NOTIFICATION',
                'content': 'به HomayOMS خوش آمدید!\nحساب کاربری شما با موفقیت ایجاد شد.\n\nHomayOMS',
                'variables': {}
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates_data:
            template, created = SMSTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'template_type': template_data['template_type'],
                    'content': template_data['content'],
                    'variables': template_data['variables'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ قالب "{template.name}" ایجاد شد')
                )
                created_count += 1
            else:
                # به‌روزرسانی قالب موجود
                template.template_type = template_data['template_type']
                template.content = template_data['content']
                template.variables = template_data['variables']
                template.is_active = True
                template.save()
                
                self.stdout.write(
                    self.style.WARNING(f'🔄 قالب "{template.name}" به‌روزرسانی شد')
                )
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'🎉 عملیات تکمیل شد:\n'
            f'   ✅ {created_count} قالب جدید ایجاد شد\n'
            f'   🔄 {updated_count} قالب به‌روزرسانی شد'
        )) 