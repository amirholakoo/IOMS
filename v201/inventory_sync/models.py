from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from HomayOMS.baseModel import BaseModel

User = get_user_model()


class SyncConfig(BaseModel):
    """
    Configuration for inventory synchronization settings
    """
    auto_sync_interval_minutes = models.IntegerField(
        default=1440,  # 24 hours default
        help_text="Interval in minutes for automatic synchronization"
    )
    last_auto_sync = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last time automatic sync was performed"
    )
    is_auto_sync_enabled = models.BooleanField(
        default=True,
        help_text="Whether automatic synchronization is enabled"
    )

    class Meta:
        verbose_name = "Sync Configuration"
        verbose_name_plural = "Sync Configuration"

    def __str__(self):
        return f"Sync Config (Auto: {self.is_auto_sync_enabled}, Interval: {self.auto_sync_interval_minutes}min)"


class SyncLog(BaseModel):
    """
    Log of all synchronization operations
    """
    SYNC_TYPES = [
        ('manual', 'Manual Sync'),
        ('auto', 'Automatic Sync'),
        ('import', 'Product Import'),
        ('export', 'Sales Export'),
    ]

    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    operation = models.CharField(max_length=255, help_text="Description of the operation")
    products_processed = models.IntegerField(default=0)
    products_imported = models.IntegerField(default=0)
    products_updated = models.IntegerField(default=0)
    products_exported = models.IntegerField(default=0)
    errors = models.TextField(blank=True, null=True)
    executed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who triggered the sync (for manual syncs)"
    )
    executed_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-executed_at']
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"

    def __str__(self):
        return f"{self.sync_type} - {self.operation} ({self.executed_at})"


class ProductMapping(BaseModel):
    """
    Maps products between external SQLite and Django database
    """
    reel_number = models.CharField(max_length=255, unique=True)
    external_id = models.IntegerField(help_text="ID from external SQLite database")
    django_product_id = models.IntegerField(
        null=True, 
        blank=True,
        help_text="ID of corresponding product in Django database"
    )
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('imported', 'Imported'),
            ('updated', 'Updated'),
            ('exported', 'Exported'),
            ('error', 'Error'),
        ],
        default='imported'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Product Mapping"
        verbose_name_plural = "Product Mappings"

    def __str__(self):
        return f"Reel {self.reel_number} (External: {self.external_id})"


class FieldMapping(BaseModel):
    """
    Configurable field mappings between external SQLite and Django models
    """
    external_field = models.CharField(max_length=255, help_text="Field name in external SQLite")
    django_field = models.CharField(max_length=255, help_text="Field name in Django model")
    is_active = models.BooleanField(default=True, help_text="Whether this mapping is active")
    mapping_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Copy'),
            ('transform', 'Transform'),
            ('conditional', 'Conditional'),
        ],
        default='direct'
    )
    transform_function = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Python function name for transformation (if needed)"
    )

    class Meta:
        unique_together = ['external_field', 'django_field']
        verbose_name = "Field Mapping"
        verbose_name_plural = "Field Mappings"

    def __str__(self):
        return f"{self.external_field} → {self.django_field}"
