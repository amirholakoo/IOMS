"""
🧹 Management command to clean up empty orders
🎯 Removes orders that have no items (data integrity issue)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Order, OrderItem
from payments.models import Payment
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '🧹 Clean up empty orders that have no items (data integrity issue)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion even if orders have payments',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🧹 Starting cleanup of empty orders...')
        )
        
        # Find all Processing orders
        processing_orders = Order.objects.filter(status='Processing')
        
        self.stdout.write(f'📊 Found {processing_orders.count()} Processing orders')
        
        empty_orders = []
        orders_with_payments = []
        
        for order in processing_orders:
            item_count = order.order_items.count()
            payment_count = Payment.objects.filter(order=order).count()
            
            if item_count == 0:
                if payment_count == 0:
                    empty_orders.append(order)
                    self.stdout.write(
                        self.style.WARNING(f'  ❌ Empty order: {order.order_number} (ID: {order.id})')
                    )
                else:
                    orders_with_payments.append(order)
                    self.stdout.write(
                        self.style.ERROR(f'  ⚠️  Empty order with payments: {order.order_number} (ID: {order.id}) - {payment_count} payments')
                    )
        
        self.stdout.write(f'\n📋 Summary:')
        self.stdout.write(f'  - Empty orders (no items, no payments): {len(empty_orders)}')
        self.stdout.write(f'  - Empty orders with payments: {len(orders_with_payments)}')
        
        if not empty_orders and not orders_with_payments:
            self.stdout.write(
                self.style.SUCCESS('✅ No empty orders found!')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be made')
            )
            if empty_orders:
                self.stdout.write('\n📝 Orders that would be deleted:')
                for order in empty_orders:
                    self.stdout.write(f'  - {order.order_number} (ID: {order.id}) - Customer: {order.customer.customer_name}')
            
            if orders_with_payments and not force:
                self.stdout.write('\n⚠️  Orders with payments (use --force to delete):')
                for order in orders_with_payments:
                    payment_count = Payment.objects.filter(order=order).count()
                    self.stdout.write(f'  - {order.order_number} (ID: {order.id}) - {payment_count} payments')
            
            return
        
        # Actually delete the orders
        deleted_count = 0
        
        with transaction.atomic():
            # Delete empty orders without payments
            for order in empty_orders:
                try:
                    order_number = order.order_number
                    order_id = order.id
                    customer_name = order.customer.customer_name
                    
                    order.delete()
                    deleted_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Deleted empty order: {order_number} (ID: {order_id}) - Customer: {customer_name}')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error deleting order {order.order_number}: {str(e)}')
                    )
            
            # Handle orders with payments if force is enabled
            if force and orders_with_payments:
                self.stdout.write('\n⚠️  Force deleting orders with payments...')
                for order in orders_with_payments:
                    try:
                        order_number = order.order_number
                        order_id = order.id
                        customer_name = order.customer.customer_name
                        payment_count = Payment.objects.filter(order=order).count()
                        
                        # Delete payments first
                        Payment.objects.filter(order=order).delete()
                        order.delete()
                        deleted_count += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Force deleted order with payments: {order_number} (ID: {order_id}) - Customer: {customer_name} - {payment_count} payments deleted')
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Error force deleting order {order.order_number}: {str(e)}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Cleanup completed! Deleted {deleted_count} empty orders.')
        )
        
        if orders_with_payments and not force:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {len(orders_with_payments)} orders with payments remain. Use --force to delete them.')
            ) 