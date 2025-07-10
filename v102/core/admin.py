"""
🎛️ پنل مدیریت اپلیکیشن Core - HomayOMS
📋 تنظیمات پنل مدیریت جنگو برای مدل‌های اصلی کسب‌وکار
👥 رابط کاربری فارسی برای مدیریت مشتریان، محصولات و لاگ‌های سیستم
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html
from .models import Customer, Product, ActivityLog, Order, OrderItem, WorkingHours


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    🎛️ پنل مدیریت مشتریان
    📊 رابط کاربری کامل برای مدیریت اطلاعات مشتریان
    """
    
    # 📋 فیلدهای نمایش داده شده در لیست مشتریان
    list_display = [
        'customer_name',       # 👤 نام مشتری
        'phone',              # 📞 تلفن
        'status',             # 📊 وضعیت
        'national_id',        # 🆔 شناسه ملی
        'postcode',           # 📮 کد پستی
        'created_at',         # 📅 تاریخ ایجاد
        'is_active',          # ✅ فعال/غیرفعال
    ]
    
    # 🔍 فیلدهای قابل جستجو
    search_fields = [
        'customer_name',      # جستجو در نام
        'phone',              # جستجو در تلفن
        'national_id',        # جستجو در شناسه ملی
        'economic_code',      # جستجو در کد اقتصادی
    ]
    
    # 🔽 فیلترهای کناری
    list_filter = [
        'status',             # فیلتر بر اساس وضعیت
        'created_at',         # فیلتر بر اساس تاریخ ایجاد
        'updated_at',         # فیلتر بر اساس تاریخ به‌روزرسانی
    ]
    
    # 📝 ترتیب فیلدها در فرم ویرایش
    fieldsets = (
        ('👤 اطلاعات اصلی مشتری', {
            'fields': ('customer_name', 'status')
        }),
        ('📞 اطلاعات تماس', {
            'fields': ('phone', 'address', 'postcode'),
            'classes': ('collapse',)  # قابل جمع شدن
        }),
        ('🆔 کدهای قانونی', {
            'fields': ('national_id', 'economic_code'),
            'classes': ('collapse',)  # قابل جمع شدن
        }),
        ('💬 توضیحات اضافی', {
            'fields': ('comments',),
            'classes': ('collapse',)  # قابل جمع شدن
        }),
    )
    
    # 📅 فیلدهای فقط خواندنی (از BaseModel)
    readonly_fields = ['created_at', 'updated_at']
    
    # 🔢 تعداد آیتم‌ها در هر صفحه
    list_per_page = 25
    
    # ⚡ بهینه‌سازی کوئری‌ها
    list_select_related = []  # در صورت داشتن ForeignKey اضافه می‌شود
    
    # 🎯 اکشن‌های سفارشی
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """
        ✅ فعال کردن مشتریان انتخاب شده
        """
        updated = queryset.update(status='Active')
        self.message_user(
            request, 
            f'✅ {updated} مشتری فعال شدند.'
        )
    make_active.short_description = "✅ فعال کردن مشتریان انتخاب شده"
    
    def make_inactive(self, request, queryset):
        """
        ❌ غیرفعال کردن مشتریان انتخاب شده
        """
        updated = queryset.update(status='Inactive')
        self.message_user(
            request, 
            f'❌ {updated} مشتری غیرفعال شدند.'
        )
    make_inactive.short_description = "❌ غیرفعال کردن مشتریان انتخاب شده"
    
    def is_active(self, obj):
        """
        ✅ نمایش وضعیت فعال/غیرفعال با آیکون
        """
        return obj.is_active()  # Return boolean value for Django admin
    is_active.short_description = "📊 وضعیت فعال"
    is_active.boolean = True  # نمایش به صورت آیکون بولین
    
    def has_add_permission(self, request):
        """➕ مجوز اضافه کردن مشتری"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.add_customer')
    
    def has_change_permission(self, request, obj=None):
        """✏️ مجوز تغییر مشتری"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.change_customer')
    
    def has_delete_permission(self, request, obj=None):
        """🗑️ مجوز حذف مشتری"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.delete_customer')
    
    def has_view_permission(self, request, obj=None):
        """👁️ مجوز مشاهده مشتری"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.view_customer')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    📦 پنل مدیریت محصولات
    🎛️ رابط کاربری کامل برای مدیریت محصولات انبار
    """
    
    # 📋 فیلدهای نمایش داده شده در لیست محصولات
    list_display = [
        'reel_number',        # 🏷️ شماره ریل
        'location_display',   # 📍 مکان انبار
        'status_display',     # 📊 وضعیت محصول
        'price_display',      # 💰 قیمت
        'width',              # 📏 عرض
        'gsm',                # ⚖️ GSM
        'length',             # 📐 طول
        'grade',              # 🏆 درجه کیفیت
        'breaks',             # 💔 شکستگی
        'total_area_display', # 📐 مساحت کل
        'total_weight_display',  # ⚖️ وزن کل
        'is_available_display',  # ✅ در دسترس
        'created_at',         # 📅 تاریخ ایجاد
    ]
    
    # 🔍 فیلدهای قابل جستجو
    search_fields = [
        'reel_number',        # جستجو در شماره ریل
        'grade',              # جستجو در درجه کیفیت
        'qr_code',            # جستجو در کد QR
    ]
    
    # 🔽 فیلترهای کناری
    list_filter = [
        'location',           # فیلتر بر اساس مکان انبار
        'status',             # فیلتر بر اساس وضعیت محصول
        'gsm',                # فیلتر بر اساس GSM
        'width',              # فیلتر بر اساس عرض
        'grade',              # فیلتر بر اساس درجه کیفیت
        'created_at',         # فیلتر بر اساس تاریخ ایجاد
        'updated_at',         # فیلتر بر اساس تاریخ به‌روزرسانی
    ]
    
    # 📝 ترتیب فیلدها در فرم ویرایش
    def get_fieldsets(self, request, obj=None):
        """
        📝 تنظیم فیلدها بر اساس نقش کاربر
        💰 فقط Super Admin می‌تواند قیمت را ببیند و تغییر دهد
        """
        base_fieldsets = [
            ('🏷️ اطلاعات اصلی محصول', {
                'fields': ('reel_number', 'location', 'grade')
            }),
            ('📊 وضعیت محصول', {
                'fields': ('status',),
            }),
            ('📏 مشخصات فنی', {
                'fields': ('width', 'length', 'gsm', 'breaks'),
                'description': 'ابعاد و مشخصات فنی محصول'
            }),
            ('📱 اطلاعات اضافی', {
                'fields': ('qr_code',),
                'classes': ('collapse',)  # قابل جمع شدن
            }),
        ]
        
        # اضافه کردن بخش قیمت فقط برای Super Admin
        if request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()):
            price_fieldset = ('💰 مدیریت قیمت (فقط Super Admin)', {
                'fields': ('price', 'price_updated_at', 'price_updated_by'),
                'classes': ('collapse',),
                'description': '⚠️ فقط Super Admin می‌تواند قیمت را تغییر دهد'
            })
            base_fieldsets.insert(-1, price_fieldset)  # قبل از اطلاعات اضافی
        
        return base_fieldsets
    
    # 📅 فیلدهای فقط خواندنی
    def get_readonly_fields(self, request, obj=None):
        """
        📅 تنظیم فیلدهای فقط خواندنی بر اساس نقش کاربر
        """
        readonly = ['created_at', 'updated_at']
        
        # اگر کاربر Super Admin نیست، قیمت را فقط خواندنی کن
        if not (request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin())):
            readonly.extend(['price', 'price_updated_at', 'price_updated_by'])
        else:
            # برای Super Admin هم فیلدهای تاریخ و کاربر قیمت فقط خواندنی است
            readonly.extend(['price_updated_at', 'price_updated_by'])
        
        return readonly
    
    # 🔢 تعداد آیتم‌ها در هر صفحه
    list_per_page = 50
    
    # 🎯 اکشن‌های سفارشی
    actions = ['mark_as_sold', 'mark_as_in_stock', 'mark_as_pre_order', 'export_products']
    
    def location_display(self, obj):
        """📍 نمایش مکان انبار با آیکون رنگی"""
        colors = {
            'Anbar_Akhal': '#FF6B6B',
            'Anbar_Muhvateh_Kordan': '#4ECDC4',
            'Anbar_Khamir_Kordan': '#45B7D1',
            'Anbar_Khamir_Ghadim': '#96CEB4',
            'Anbar_Koochak': '#FFEAA7',
            'Anbar_Salon_Tolid': '#DDA0DD',
            'Anbar_Sangin': '#98D8C8',
        }
        color = colors.get(obj.location, '#BDC3C7')
        return format_html(
            '<span style="color: {}; font-weight: bold;">📍 {}</span>',
            color,
            obj.get_location_display()
        )
    location_display.short_description = "📍 مکان انبار"
    
    def status_display(self, obj):
        """📊 نمایش وضعیت محصول با رنگ"""
        colors = {
            'In-stock': 'green',
            'Sold': 'red',
            'Pre-order': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "📊 وضعیت"
    

    
    def total_area_display(self, obj):
        """📐 نمایش مساحت کل"""
        return f"{obj.get_total_area():.2f} m²"
    total_area_display.short_description = "📐 مساحت کل"
    
    def total_weight_display(self, obj):
        """⚖️ نمایش وزن کل"""
        return f"{obj.get_total_weight():.2f} kg"
    total_weight_display.short_description = "⚖️ وزن کل"
    
    def is_available_display(self, obj):
        """✅ نمایش در دسترس بودن"""
        if obj.is_available():
            return format_html('<span style="color: green;">✅ موجود</span>')
        return format_html('<span style="color: red;">❌ ناموجود</span>')
    is_available_display.short_description = "✅ موجودی"
    
    def price_display(self, obj):
        """💰 نمایش قیمت با فرمت زیبا"""
        if obj.price > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">💰 {} تومان</span>',
                f"{int(obj.price):,}"
            )
        return format_html('<span style="color: red;">💰 قیمت تعیین نشده</span>')
    price_display.short_description = "💰 قیمت"
    
    # 🎯 اکشن‌های سفارشی
    def mark_as_sold(self, request, queryset):
        """💰 علامت‌گذاری به عنوان فروخته شده"""
        updated = queryset.update(status='Sold')
        self.message_user(
            request,
            f'💰 {updated} محصول به عنوان فروخته شده علامت‌گذاری شدند.'
        )
    mark_as_sold.short_description = "💰 علامت‌گذاری به عنوان فروخته شده"
    
    def mark_as_in_stock(self, request, queryset):
        """📦 علامت‌گذاری به عنوان موجود در انبار"""
        updated = queryset.update(status='In-stock')
        self.message_user(
            request,
            f'📦 {updated} محصول به عنوان موجود در انبار علامت‌گذاری شدند.'
        )
    mark_as_in_stock.short_description = "📦 علامت‌گذاری به عنوان موجود در انبار"
    
    def mark_as_pre_order(self, request, queryset):
        """⏳ علامت‌گذاری به عنوان پیش‌سفارش"""
        updated = queryset.update(status='Pre-order')
        self.message_user(
            request,
            f'⏳ {updated} محصول به عنوان پیش‌سفارش علامت‌گذاری شدند.'
        )
    mark_as_pre_order.short_description = "⏳ علامت‌گذاری به عنوان پیش‌سفارش"
    
    def save_model(self, request, obj, form, change):
        """
        💾 ذخیره محصول با ردیابی تغییرات قیمت
        """
        # بررسی تغییر قیمت
        if change:  # اگر در حال ویرایش است
            try:
                old_obj = Product.objects.get(pk=obj.pk)
                if old_obj.price != obj.price:
                    # قیمت تغییر کرده است
                    from django.utils import timezone
                    obj.price_updated_at = timezone.now()
                    obj.price_updated_by = request.user
                    
                    # ثبت لاگ تغییر قیمت
                    ActivityLog.log_activity(
                        user=request.user,
                        action='UPDATE',
                        description=f'قیمت محصول {obj.reel_number} از {old_obj.price:,} به {obj.price:,} تومان تغییر یافت',
                        content_object=obj,
                        severity='HIGH',
                        old_price=float(old_obj.price),
                        new_price=float(obj.price),
                        price_change=float(obj.price - old_obj.price)
                    )
            except Product.DoesNotExist:
                pass
        else:
            # محصول جدید - اگر قیمت تنظیم شده، اطلاعات قیمت را ثبت کن
            if obj.price > 0:
                from django.utils import timezone
                obj.price_updated_at = timezone.now()
                obj.price_updated_by = request.user
                
                # ثبت لاگ ایجاد محصول با قیمت
                ActivityLog.log_activity(
                    user=request.user,
                    action='CREATE',
                    description=f'محصول جدید {obj.reel_number} با قیمت {obj.price:,} تومان ایجاد شد',
                    content_object=obj,
                    severity='MEDIUM',
                    initial_price=float(obj.price)
                )
        
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        👑 Super Admin می‌تواند همه محصولات را ببیند
        """
        queryset = super().get_queryset(request)
        
        # 👑 Super Admin دسترسی کامل دارد
        if request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()):
            return queryset
        
        # برای سایر کاربران محدودیت اعمال می‌شود (در صورت نیاز)
        return queryset
    
    def has_add_permission(self, request):
        """➕ مجوز اضافه کردن محصول"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.add_product')
    
    def has_change_permission(self, request, obj=None):
        """✏️ مجوز تغییر محصول"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.change_product')
    
    def has_delete_permission(self, request, obj=None):
        """🗑️ مجوز حذف محصول"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.delete_product')
    
    def has_view_permission(self, request, obj=None):
        """👁️ مجوز مشاهده محصول"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.view_product')


class OrderItemInline(admin.TabularInline):
    """
    📦 Inline برای آیتم‌های سفارش
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'unit_price', 'payment_method', 'total_price', 'notes']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    🛒 مدیریت سفارشات در پنل ادمین
    """
    
    list_display = [
        'order_number',
        'customer_display',
        'status_display',
        'payment_method_display',
        'items_count',
        'final_amount_display',
        'created_at_display',
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'created_at',
        'customer',
    ]
    
    search_fields = [
        'order_number',
        'customer__customer_name',
        'customer__phone',
        'notes',
    ]
    
    readonly_fields = [
        'order_number',
        'total_amount',
        'discount_amount',
        'final_amount',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('🏷️ اطلاعات اصلی سفارش', {
            'fields': ('order_number', 'customer', 'status', 'created_by')
        }),
        ('💳 اطلاعات پرداخت', {
            'fields': ('payment_method', 'total_amount', 'discount_percentage', 'discount_amount', 'final_amount'),
        }),
        ('🚚 اطلاعات تحویل', {
            'fields': ('delivery_address', 'expected_delivery_date', 'actual_delivery_date'),
            'classes': ('collapse',)
        }),
        ('📝 توضیحات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('📅 اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    def customer_display(self, obj):
        """👤 نمایش مشتری"""
        return f"👤 {obj.customer.customer_name}"
    customer_display.short_description = "👤 مشتری"
    
    def status_display(self, obj):
        """📊 نمایش وضعیت با رنگ"""
        colors = {
            'Pending': 'orange',
            'Confirmed': 'blue',
            'Processing': 'purple',
            'Ready': 'green',
            'Delivered': 'darkgreen',
            'Cancelled': 'red',
            'Returned': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = "📊 وضعیت"
    
    def payment_method_display(self, obj):
        """💳 نمایش روش پرداخت"""
        return f"💳 {obj.get_payment_method_display()}"
    payment_method_display.short_description = "💳 روش پرداخت"
    
    def items_count(self, obj):
        """📦 تعداد اقلام"""
        count = obj.get_order_items_count()
        return f"📦 {count} قلم"
    items_count.short_description = "📦 تعداد اقلام"
    
    def final_amount_display(self, obj):
        """💰 مبلغ نهایی"""
        return format_html(
            '<span style="color: green; font-weight: bold;">💰 {} تومان</span>',
            f"{int(obj.final_amount):,}"
        )
    final_amount_display.short_description = "💰 مبلغ نهایی"
    
    def created_at_display(self, obj):
        """📅 تاریخ ایجاد"""
        return obj.created_at.strftime('%Y/%m/%d %H:%M')
    created_at_display.short_description = "📅 تاریخ ایجاد"
    
    def save_model(self, request, obj, form, change):
        """
        💾 ذخیره سفارش با ثبت لاگ
        """
        if not change:  # سفارش جدید
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # ثبت لاگ
        action = 'UPDATE' if change else 'CREATE'
        action_text = 'ویرایش' if change else 'ایجاد'
        description = f'{action_text} سفارش {obj.order_number}'
        
        ActivityLog.log_activity(
            user=request.user,
            action=action,
            description=description,
            content_object=obj,
            severity='MEDIUM' if change else 'HIGH',
            order_number=obj.order_number,
            order_status=obj.status,
            final_amount=float(obj.final_amount)
        )

    def has_add_permission(self, request):
        """➕ مجوز اضافه کردن سفارش"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.add_order')
    
    def has_change_permission(self, request, obj=None):
        """✏️ مجوز تغییر سفارش"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.change_order')
    
    def has_delete_permission(self, request, obj=None):
        """🗑️ مجوز حذف سفارش"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.delete_order')
    
    def has_view_permission(self, request, obj=None):
        """👁️ مجوز مشاهده سفارش"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('core.view_order')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    📦 مدیریت آیتم‌های سفارش در پنل ادمین
    """
    
    list_display = [
        'order_number',
        'product_display',
        'quantity',
        'unit_price_display',
        'payment_method_display',
        'total_price_display',
    ]
    
    list_filter = [
        'order__status',
        'payment_method',
        'product__location',
        'created_at',
    ]
    
    search_fields = [
        'order__order_number',
        'product__reel_number',
        'order__customer__customer_name',
    ]
    
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    
    def order_number(self, obj):
        """🏷️ شماره سفارش"""
        return obj.order.order_number
    order_number.short_description = "🏷️ شماره سفارش"
    
    def product_display(self, obj):
        """📦 نمایش محصول"""
        return f"📦 {obj.product.reel_number}"
    product_display.short_description = "📦 محصول"
    
    def unit_price_display(self, obj):
        """💰 قیمت واحد"""
        return f"💰 {obj.unit_price:,.0f} تومان"
    unit_price_display.short_description = "💰 قیمت واحد"
    
    def payment_method_display(self, obj):
        """💳 نمایش روش پرداخت"""
        return f"💳 {obj.payment_method}"
    payment_method_display.short_description = "💳 روش پرداخت"
    
    def total_price_display(self, obj):
        """💵 قیمت کل"""
        return format_html(
            '<span style="color: green; font-weight: bold;">💵 {} تومان</span>',
            f"{int(obj.total_price):,}"
        )
    total_price_display.short_description = "💵 قیمت کل"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """
    📜 پنل مدیریت لاگ‌های فعالیت
    🎛️ رابط کاربری برای مشاهده و تحلیل فعالیت‌های سیستم
    """
    
    # 📋 فیلدهای نمایش داده شده در لیست لاگ‌ها
    list_display = [
        'action_icon_display',    # 🎭 آیکون عملیات
        'user_display',           # 👤 کاربر
        'action',                 # 🎭 نوع عملیات
        'description_short',      # 📝 توضیحات کوتاه
        'severity_display',       # ⚠️ سطح اهمیت
        'related_object_display', # 🔗 آبجکت مرتبط
        'ip_address',             # 🌐 IP
        'created_at',             # 📅 زمان
    ]
    
    # 🔍 فیلدهای قابل جستجو
    search_fields = [
        'description',            # جستجو در توضیحات
        'user__username',         # جستجو در نام کاربری
        'user__first_name',       # جستجو در نام
        'user__last_name',        # جستجو در نام خانوادگی
        'ip_address',             # جستجو در IP
    ]
    
    # 🔽 فیلترهای کناری
    list_filter = [
        'action',                 # فیلتر بر اساس نوع عملیات
        'severity',               # فیلتر بر اساس سطح اهمیت
        'content_type',           # فیلتر بر اساس نوع محتوا
        'created_at',             # فیلتر بر اساس تاریخ
        'user',                   # فیلتر بر اساس کاربر
    ]
    
    # 📝 ترتیب فیلدها در فرم مشاهده (فقط خواندنی)
    fieldsets = (
        ('🎭 اطلاعات عملیات', {
            'fields': ('user', 'action', 'description', 'severity')
        }),
        ('🔗 آبجکت مرتبط', {
            'fields': ('content_type', 'object_id', 'content_object_info'),
            'classes': ('collapse',)
        }),
        ('🌐 اطلاعات فنی', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('📄 اطلاعات اضافی', {
            'fields': ('extra_data_display',),
            'classes': ('collapse',)
        }),
        ('⏰ اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    # 📅 تمام فیلدها فقط خواندنی (لاگ‌ها قابل ویرایش نیستند)
    readonly_fields = [
        'user', 'action', 'description', 'severity', 'content_type', 
        'object_id', 'content_object_info', 'ip_address', 'user_agent',
        'extra_data_display', 'created_at', 'updated_at'
    ]
    
    # 🔢 تعداد آیتم‌ها در هر صفحه
    list_per_page = 100
    
    # ⚡ بهینه‌سازی کوئری‌ها
    list_select_related = ['user', 'content_type']
    
    # 🚫 غیرفعال کردن اکشن‌های حذف (لاگ‌ها نباید حذف شوند)
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request):
        return False  # لاگ‌ها فقط از طریق سیستم ایجاد می‌شوند
    
    def has_change_permission(self, request, obj=None):
        return False  # لاگ‌ها قابل ویرایش نیستند
    
    # 📊 متدهای نمایش سفارشی
    def action_icon_display(self, obj):
        """🎭 نمایش آیکون عملیات"""
        return format_html(
            '<span style="font-size: 18px;">{}</span>',
            obj.get_action_icon()
        )
    action_icon_display.short_description = "🎭"
    
    def user_display(self, obj):
        """👤 نمایش کاربر با لینک"""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.pk])
            return format_html(
                '<a href="{}" style="color: #007cba;">👤 {}</a>',
                url,
                obj.user.get_full_name() or obj.user.username
            )
        return "🤖 سیستم"
    user_display.short_description = "👤 کاربر"
    
    def description_short(self, obj):
        """📝 نمایش توضیحات کوتاه"""
        if len(obj.description) > 50:
            return f"{obj.description[:47]}..."
        return obj.description
    description_short.short_description = "📝 توضیحات"
    
    def severity_display(self, obj):
        """⚠️ نمایش سطح اهمیت با رنگ"""
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_display.short_description = "⚠️ اهمیت"
    
    def related_object_display(self, obj):
        """🔗 نمایش آبجکت مرتبط با لینک"""
        if obj.content_object:
            try:
                # سعی در ایجاد لینک به آبجکت در ادمین
                app_label = obj.content_type.app_label
                model_name = obj.content_type.model
                url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.object_id])
                return format_html(
                    '<a href="{}" style="color: #007cba;">🔗 {}</a>',
                    url,
                    str(obj.content_object)[:30]
                )
            except:
                return f"🔗 {str(obj.content_object)[:30]}"
        return "➖"
    related_object_display.short_description = "🔗 آبجکت مرتبط"
    
    def content_object_info(self, obj):
        """🔗 اطلاعات کامل آبجکت مرتبط"""
        info = obj.get_related_object_info()
        if info:
            return format_html(
                '<strong>مدل:</strong> {}<br>'
                '<strong>شناسه:</strong> {}<br>'
                '<strong>آبجکت:</strong> {}',
                info['model'],
                info['object_id'],
                info['object_str']
            )
        return "اطلاعاتی موجود نیست"
    content_object_info.short_description = "🔗 اطلاعات آبجکت"
    
    def extra_data_display(self, obj):
        """📄 نمایش اطلاعات اضافی JSON"""
        if obj.extra_data:
            import json
            return format_html(
                '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
                json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
            )
        return "اطلاعات اضافی موجود نیست"
    extra_data_display.short_description = "📄 اطلاعات اضافی"


@admin.register(WorkingHours)
class WorkingHoursAdmin(ModelAdmin):
    """
    ⏰ پنل مدیریت ساعات کاری فروشگاه
    
    👑 تنها Super Admin می‌تواند ساعات کاری را مدیریت کند
    🕐 امکان تنظیم زمان‌های شروع و پایان کار
    🔧 کنترل فعال/غیرفعال کردن ساعات کاری
    """
    
    list_display = [
        'working_hours_display', 
        'status_display',
        'duration_display',
        'set_by_display',
        'created_at_display',
        'actions_display'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'start_time',
        'end_time'
    ]
    
    search_fields = [
        'description',
        'set_by__username',
        'set_by__first_name',
        'set_by__last_name'
    ]
    
    fieldsets = (
        ('⏰ تنظیمات ساعات کاری', {
            'fields': (
                'start_time',
                'end_time',
                'is_active',
                'description'
            ),
            'classes': ('wide',),
            'description': '⏰ ساعات کاری فروشگاه را تنظیم کنید'
        }),
        ('📋 اطلاعات سیستم', {
            'fields': (
                'set_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',),
            'description': '📋 اطلاعات سیستمی و تاریخچه تغییرات'
        }),
    )
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'set_by'
    ]
    
    ordering = ['-is_active', '-created_at']
    
    def get_queryset(self, request):
        """
        👑 محدود کردن دسترسی فقط به Super Admin
        """
        queryset = super().get_queryset(request)
        
        # 👑 فقط Super Admin می‌تواند ساعات کاری را ببیند
        if not (request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin())):
            return queryset.none()  # هیچ رکوردی نشان نده
        
        return queryset
    
    def has_add_permission(self, request):
        """
        ➕ مجوز اضافه کردن ساعات کاری جدید
        """
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin())
    
    def has_change_permission(self, request, obj=None):
        """
        ✏️ مجوز تغییر ساعات کاری
        """
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin())
    
    def has_delete_permission(self, request, obj=None):
        """
        🗑️ مجوز حذف ساعات کاری
        """
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin())
    
    def save_model(self, request, obj, form, change):
        """
        💾 ذخیره مدل ساعات کاری با ثبت کاربر تنظیم‌کننده
        """
        if not change:  # اگر رکورد جدیدی ساخته می‌شود
            obj.set_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # پیام موفقیت
        if change:
            messages.success(request, f"⏰ ساعات کاری با موفقیت به‌روزرسانی شد: {obj}")
        else:
            messages.success(request, f"✅ ساعات کاری جدید با موفقیت ایجاد شد: {obj}")
    
    def working_hours_display(self, obj):
        """
        ⏰ نمایش ساعات کاری
        """
        return format_html(
            '<span style="font-weight: bold; color: #2196F3;">⏰ {} - {}</span>',
            obj.start_time.strftime('%H:%M'),
            obj.end_time.strftime('%H:%M')
        )
    working_hours_display.short_description = "⏰ ساعات کاری"
    working_hours_display.admin_order_field = 'start_time'
    
    def status_display(self, obj):
        """
        🔄 نمایش وضعیت ساعات کاری
        """
        if obj.is_active:
            status_color = '#4CAF50'
            status_icon = '🟢'
            status_text = 'فعال'
            
            # بررسی وضعیت فعلی فروشگاه
            if obj.is_currently_open():
                extra_info = '<br><small style="color: #2196F3;">🏪 فروشگاه باز است</small>'
            else:
                time_until = obj.time_until_open()
                if time_until:
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    extra_info = f'<br><small style="color: #FF9800;">⏳ باز می‌شود در: {hours}:{minutes:02d}</small>'
                else:
                    extra_info = '<br><small style="color: #F44336;">🔒 فروشگاه بسته است</small>'
        else:
            status_color = '#F44336'
            status_icon = '🔴'
            status_text = 'غیرفعال'
            extra_info = ''
        
        return format_html(
            '<span style="color: {};">{} {}</span>{}',
            status_color, status_icon, status_text, extra_info
        )
    status_display.short_description = "🔄 وضعیت"
    status_display.admin_order_field = 'is_active'
    
    def duration_display(self, obj):
        """
        ⏱️ نمایش مدت زمان کاری
        """
        duration = obj.get_duration_hours()
        return format_html(
            '<span style="color: #9C27B0;">⏱️ {:.1f} ساعت</span>',
            duration
        )
    duration_display.short_description = "⏱️ مدت زمان"
    
    def set_by_display(self, obj):
        """
        👑 نمایش کاربر تنظیم‌کننده
        """
        if obj.set_by:
            return format_html(
                '<span style="color: #FF5722;">👑 {}</span>',
                obj.set_by.get_full_name() or obj.set_by.username
            )
        return format_html('<span style="color: #757575;">➖ تعیین نشده</span>')
    set_by_display.short_description = "👑 تنظیم شده توسط"
    set_by_display.admin_order_field = 'set_by'
    
    def created_at_display(self, obj):
        """
        📅 نمایش تاریخ ایجاد
        """
        from django.utils import timezone
        import jdatetime
        
        # تبدیل به تاریخ شمسی
        jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        
        return format_html(
            '<span style="color: #607D8B;">📅 {}</span><br>'
            '<small style="color: #9E9E9E;">🕐 {}</small>',
            jalali_date.strftime('%Y/%m/%d'),
            obj.created_at.strftime('%H:%M')
        )
    created_at_display.short_description = "📅 تاریخ ایجاد"
    created_at_display.admin_order_field = 'created_at'
    
    def actions_display(self, obj):
        """
        🔧 نمایش عملیات
        """
        actions = []
        
        if obj.is_active:
            actions.append('<span style="color: #F44336;">🔴 غیرفعال کردن</span>')
        else:
            actions.append('<span style="color: #4CAF50;">🟢 فعال کردن</span>')
        
        actions.append('<span style="color: #2196F3;">✏️ ویرایش</span>')
        actions.append('<span style="color: #FF9800;">👁️ مشاهده</span>')
        
        return format_html(' | '.join(actions))
    actions_display.short_description = "🔧 عملیات"
    
    def get_form(self, request, obj=None, **kwargs):
        """
        📝 تنظیم فرم ساعات کاری
        """
        form = super().get_form(request, obj, **kwargs)
        
        # تنظیم مقادیر پیش‌فرض برای فرم جدید
        if not obj:
            form.base_fields['start_time'].initial = '09:00'
            form.base_fields['end_time'].initial = '18:00'
            form.base_fields['is_active'].initial = True
        
        return form
