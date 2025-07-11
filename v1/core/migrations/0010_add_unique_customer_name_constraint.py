# Generated by Django 5.2.3 on 2025-06-30 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_workinghours_set_by'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='customer',
            constraint=models.UniqueConstraint(fields=('customer_name',), name='unique_customer_name', violation_error_message='👤 مشتری با این نام قبلاً ثبت شده است'),
        ),
    ]
