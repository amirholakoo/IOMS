# Generated manually for inventory_sync app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from HomayOMS.baseModel import BaseModel


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_sync_interval_minutes', models.IntegerField(default=1440, help_text='Interval in minutes for automatic synchronization')),
                ('last_auto_sync', models.DateTimeField(blank=True, help_text='Last time automatic sync was performed', null=True)),
                ('is_auto_sync_enabled', models.BooleanField(default=True, help_text='Whether automatic synchronization is enabled')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='📅 تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='🔄 تاریخ به‌روزرسانی')),
            ],
            options={
                'verbose_name': 'Sync Configuration',
                'verbose_name_plural': 'Sync Configuration',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_type', models.CharField(choices=[('manual', 'Manual Sync'), ('auto', 'Automatic Sync'), ('import', 'Product Import'), ('export', 'Sales Export')], max_length=20)),
                ('operation', models.CharField(help_text='Description of the operation', max_length=255)),
                ('products_processed', models.IntegerField(default=0)),
                ('products_imported', models.IntegerField(default=0)),
                ('products_updated', models.IntegerField(default=0)),
                ('products_exported', models.IntegerField(default=0)),
                ('errors', models.TextField(blank=True, null=True)),
                ('executed_at', models.DateTimeField(auto_now_add=True)),
                ('duration_seconds', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='📅 تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='🔄 تاریخ به‌روزرسانی')),
                ('executed_by', models.ForeignKey(blank=True, help_text='User who triggered the sync (for manual syncs)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={
                'verbose_name': 'Sync Log',
                'verbose_name_plural': 'Sync Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reel_number', models.CharField(max_length=255, unique=True)),
                ('external_id', models.IntegerField(help_text='ID from external SQLite database')),
                ('django_product_id', models.IntegerField(blank=True, help_text='ID of corresponding product in Django database', null=True)),
                ('last_synced', models.DateTimeField(auto_now=True)),
                ('sync_status', models.CharField(choices=[('imported', 'Imported'), ('updated', 'Updated'), ('exported', 'Exported'), ('error', 'Error')], default='imported', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='📅 تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='🔄 تاریخ به‌روزرسانی')),
            ],
            options={
                'verbose_name': 'Product Mapping',
                'verbose_name_plural': 'Product Mappings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FieldMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_field', models.CharField(help_text='Field name in external SQLite', max_length=255)),
                ('django_field', models.CharField(help_text='Field name in Django model', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this mapping is active')),
                ('mapping_type', models.CharField(choices=[('direct', 'Direct Copy'), ('transform', 'Transform'), ('conditional', 'Conditional')], default='direct', max_length=20)),
                ('transform_function', models.CharField(blank=True, help_text='Python function name for transformation (if needed)', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='📅 تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='🔄 تاریخ به‌روزرسانی')),
            ],
            options={
                'verbose_name': 'Field Mapping',
                'verbose_name_plural': 'Field Mappings',
                'unique_together': {('external_field', 'django_field')},
                'ordering': ['-created_at'],
            },
        ),
    ] 