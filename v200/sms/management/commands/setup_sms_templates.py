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
                'name': 'Verification Code',
                'template_type': 'VERIFICATION',
                'content': 'HomayOMS Verification\n\nYour security code: {code}\nValid until: {expires_at}\n\nPlease enter this code to continue.\n\nKeep this code private!\nHomayOMS Security Team',
                'variables': {'code': '6-digit code', 'expires_at': 'expiration time'}
            },
            {
                'name': 'Order Confirmed',
                'template_type': 'ORDER_STATUS',
                'content': 'Order Status Update\n\nOrder: {order_number}\nStatus: Confirmed\nAmount: {amount} Toman\n\nHomayOMS - Your Trusted Partner',
                'variables': {'order_number': 'order number', 'amount': 'amount'}
            },
            {
                'name': 'Ready for Delivery',
                'template_type': 'ORDER_STATUS',
                'content': 'Order Status Update\n\nOrder: {order_number}\nStatus: Ready for Delivery\n\nPlease visit us to collect your order.\n\nHomayOMS - Quality Guaranteed',
                'variables': {'order_number': 'order number'}
            },
            {
                'name': 'Order Delivered',
                'template_type': 'ORDER_STATUS',
                'content': 'Order Status Update\n\nOrder: {order_number}\nStatus: Delivered\n\nThank you for your purchase!\n\nHomayOMS - Your Trusted Partner',
                'variables': {'order_number': 'order number'}
            },
            {
                'name': 'Payment Successful',
                'template_type': 'PAYMENT',
                'content': 'Payment Successful!\n\nOrder: {order_number}\nAmount: {amount} Toman\nPayment completed successfully\n\nThank you for your purchase!\nHomayOMS - Quality Guaranteed',
                'variables': {'order_number': 'order number', 'amount': 'amount'}
            },
            {
                'name': 'Payment Failed',
                'template_type': 'PAYMENT',
                'content': 'Payment Failed\n\nOrder: {order_number}\nPayment was not completed\n\nPlease try again or contact support\nWe\'re here to help!\n\nHomayOMS Support Team',
                'variables': {'order_number': 'order number'}
            },
            {
                'name': 'Welcome Message',
                'template_type': 'NOTIFICATION',
                'content': 'Welcome to HomayOMS!\n\nDear {customer_name},\nYour account has been created successfully.\n\nYou can now access our services\nLogin with your phone number\nBrowse our quality products\nSecure payment options\n\nHomay Paper & Cardboard Factory\nQuality • Trust • Excellence',
                'variables': {'customer_name': 'customer name'}
            },
            {
                'name': 'Account Activated',
                'template_type': 'NOTIFICATION',
                'content': 'Welcome to HomayOMS!\n\nDear {customer_name},\nYour account has been activated successfully by {activated_by}.\n\nYou can now login to your account\nUse your phone number for authentication\nStart shopping with confidence\n\nThank you for choosing HomayOMS!\nHomay Paper & Cardboard Factory',
                'variables': {'customer_name': 'customer name', 'activated_by': 'admin name'}
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