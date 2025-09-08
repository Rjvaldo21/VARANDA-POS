from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, FileResponse

from datetime import datetime
from io import BytesIO
import os
import csv
import base64

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

import barcode  # type: ignore
from barcode.writer import ImageWriter  # type: ignore

# ===== Matplotlib backend aman headless =====
import matplotlib # type: ignore
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # type: ignore

from django.db.models import Sum, F

from .models import (
    Customer, Supplier, Product, Profile, StoreProfile,
    Transaction, TransactionItem, Category, Unit,
    ProductReturn, Purchase, PurchaseItem, PurchaseReturn,
    Warehouse, Stock, StockMovement, StockTransfer,
    PointsEarningRule, PointsRedemptionRule, PointsLedger,
    Bank, BankPayment, BackupUpload, StockAdjustment
)


class CustomAdminSite(admin.AdminSite):
    site_header = "VARANDA POS Admin"
    site_title = "VARANDA POS Panel"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        today = datetime.today().date()
        month = today.month
        year = today.year

        daily_sales = Transaction.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total'))['total'] or 0

        monthly_sales = Transaction.objects.filter(
            created_at__year=year, created_at__month=month
        ).aggregate(total=Sum('total'))['total'] or 0

        top_products = (
            TransactionItem.objects
            .values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )

        low_stock_products = Product.objects.filter(stock__lt=F('min_stock'))

        chart_html = generate_chart(top_products)

        context = {
            'daily_sales': daily_sales,
            'monthly_sales': monthly_sales,
            'top_products': top_products,
            'low_stock_products': low_stock_products, 
            'chart': chart_html,
        }

        if extra_context:
            extra_context.update(context)
        else:
            extra_context = context

        return super().index(request, extra_context=extra_context)


admin_site = CustomAdminSite(name='custom_admin')


# ========== CATEGORY ==========
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
admin_site.register(Category, CategoryAdmin)


# ========== PRODUCT ==========
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_barcode(self):
        code = self.cleaned_data.get('barcode')
        if code:
            if len(code) < 8:
                raise forms.ValidationError("Barcode tenki iha karakter minimum 8.")
            if not code.isdigit():
                raise forms.ValidationError("Barcode tenki numeriku de'it (numeru deit).")
            qs = Product.objects.filter(barcode=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Barcode ne'e existe tiha ona iha produtu seluk.")
        return code

    def clean(self):
        cleaned_data = super().clean()
        sku = cleaned_data.get('sku')
        barcode_val = cleaned_data.get('barcode')
        if not sku and barcode_val:
            cleaned_data['sku'] = barcode_val
        return cleaned_data


@admin.action(description="🖨️ Print Label Barcode")
def print_barcode_labels(modeladmin, request, queryset):
    buffer = BytesIO()
    label_width_mm = 50
    label_height_mm = 30
    c = canvas.Canvas(buffer, pagesize=(label_width_mm * mm, label_height_mm * mm))

    x = 5 * mm
    y = 5 * mm

    for product in queryset:
        code = product.barcode or product.sku
        if not code:
            continue

        c.setFont("Helvetica-Bold", 6)
        c.drawString(x, y + 20 * mm, product.name[:20])
        c.setFont("Helvetica", 5)
        c.drawString(x, y + 17 * mm, f"SKU: {product.sku or ''}")

        barcode_class = barcode.get_barcode_class('code128')
        barcode_img = barcode_class(code, writer=ImageWriter())
        barcode_buffer = BytesIO()
        barcode_img.write(barcode_buffer)
        barcode_buffer.seek(0)
        barcode_image = ImageReader(barcode_buffer)
        c.drawImage(barcode_image, x, y, width=40 * mm, height=10 * mm)

        c.showPage()

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='barcode_labels.pdf')


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = [
        'name', 'sku', 'barcode', 'category', 'variant', 'unit',
        'price', 'cost_price', 'discount', 'stock', 'min_stock', 'supplier'
    ]
    actions = [print_barcode_labels]
    list_filter = ['category', 'supplier']
    search_fields = ['name', 'sku', 'barcode']
    ordering = ['name']
    fieldsets = (
        (None, {
            'fields': (
                'name', 'sku', 'barcode', 'category', 'variant', 'unit',
                'price', 'cost_price', 'discount',
                'stock', 'min_stock', 'supplier'
            )
        }),
    )

admin_site.register(Product, ProductAdmin)
admin_site.register(Unit)  # cukup sekali


# ========== PURCHASE & PURCHASE ITEMS ==========
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'supplier', 'total', 'created_at')
    inlines = [PurchaseItemInline]

admin_site.register(Purchase, PurchaseAdmin)

class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'product', 'quantity', 'price')
admin_site.register(PurchaseItem, PurchaseItemAdmin)

class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'product', 'quantity', 'refunded_amount', 'status', 'returned_at')
    list_filter = ['status', 'returned_at']
    search_fields = ['product__name', 'purchase__supplier__name', 'reason']
admin_site.register(PurchaseReturn, PurchaseReturnAdmin)


# ========== CUSTOMER / SUPPLIER / PROFILE / STORE ==========
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'points', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('points',)
admin_site.register(Customer, CustomerAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')
admin_site.register(Supplier, SupplierAdmin)

admin_site.register(StoreProfile)
admin_site.register(Profile)


# ========== TRANSACTION ==========
class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

def backup_to_json(modeladmin, request, queryset):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'backup_{timestamp}.json'
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    call_command('dumpdata', stdout=response)
    return response
backup_to_json.short_description = '📦 Backup JSON Data'

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'total', 'payment_method', 'warehouse', 'created_at')
    list_filter = ('payment_method', 'warehouse', 'created_at')
    search_fields = ('invoice_id',)
    inlines = [TransactionItemInline]
    readonly_fields = ('invoice_id', 'total', 'payment_method', 'created_at')
    actions = [backup_to_json, 'export_to_csv', 'export_struk_pdf']

    @admin.action(description='Exporta tranzasaun ba CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=transaksi.csv'
        writer = csv.writer(response)
        writer.writerow(['Invoice', 'Total', 'Metode', 'Data'])
        for t in queryset:
            writer.writerow([t.invoice_id, t.total, t.payment_method, t.created_at])
        return response

    @admin.action(description="Exporta PDF Nota Tranzasaun")
    def export_struk_pdf(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Hili de'it tranzasaun ida atu imprime resibu PDF.", level='error')
            return
        transaction = queryset.first()
        items = TransactionItem.objects.filter(transaction=transaction)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=struk_{transaction.invoice_id}.pdf'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        y = height - 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "NOTA TRANZASAUN")
        y -= 30

        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Invoice: {transaction.invoice_id}")
        y -= 20
        p.drawString(50, y, f"Metode Selu: {transaction.payment_method}")
        y -= 20
        p.drawString(50, y, f"Data: {transaction.created_at.strftime('%d-%m-%Y %H:%M')}")
        y -= 30

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Item:")
        y -= 20

        p.setFont("Helvetica", 11)
        for item in items:
            p.drawString(60, y, f"{item.product.name} x {item.quantity} @ {item.price}")
            y -= 18

        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"Total: ${transaction.total}")
        p.showPage()
        p.save()

        return response

admin_site.register(Transaction, TransactionAdmin)


# ========== PRODUCT RETURN (penjualan) ==========
class ProductReturnAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'quantity', 'refunded_amount', 'status', 'returned_at']
    list_filter = ['status', 'returned_at']
    search_fields = ['transaction__id', 'product__name']
admin_site.register(ProductReturn, ProductReturnAdmin)


# ========== AUTH ==========
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


# ========== WAREHOUSE / STOCK ==========
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'description')
    search_fields = ('name', 'location', 'description')
admin_site.register(Warehouse, WarehouseAdmin)

class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity']
    list_filter = ['warehouse', 'product']
admin_site.register(Stock, StockAdmin)


# ========== STOCK MOVEMENT ==========
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'movement_type', 'note', 'created_at']
    list_filter = ['movement_type', 'warehouse', 'created_at']
    search_fields = ['product__name', 'note']

    def save_model(self, request, obj, form, change):
        stock_obj, created = Stock.objects.get_or_create(
            product=obj.product,
            warehouse=obj.warehouse,
            defaults={'quantity': 0}
        )
        if obj.movement_type == 'in':
            stock_obj.quantity += obj.quantity
        else:
            if stock_obj.quantity < obj.quantity:
                raise ValidationError('❌ Kuantidade iha armazén la suficiente.')
            stock_obj.quantity -= obj.quantity

        stock_obj.save()
        if not change:
            obj.adjusted_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(StockMovement, StockMovementAdmin)


# ========== STOCK TRANSFER ==========
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['product', 'from_warehouse', 'to_warehouse', 'quantity', 'note', 'transferred_at']
    list_filter = ['from_warehouse', 'to_warehouse', 'transferred_at']
    search_fields = ['product__name', 'note']
    actions = ['export_transfer_csv']

    @admin.action(description="📤 Exporta Transfer Armazén ba CSV")
    def export_transfer_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=transfer_gudang.csv'
        writer = csv.writer(response)
        writer.writerow(['Produk', 'Husi Armazén', 'Ba Armazén', 'Total', 'Deskirsaun', 'Data'])
        for transfer in queryset:
            writer.writerow([
                transfer.product.name,
                transfer.from_warehouse.name,
                transfer.to_warehouse.name,
                transfer.quantity,
                transfer.note,
                transfer.transferred_at.strftime('%d-%m-%Y %H:%M')
            ])
        return response

    def save_model(self, request, obj, form, change):
        stock_from, _ = Stock.objects.get_or_create(
            product=obj.product,
            warehouse=obj.from_warehouse,
            defaults={'quantity': 0}
        )
        stock_to, _ = Stock.objects.get_or_create(
            product=obj.product,
            warehouse=obj.to_warehouse,
            defaults={'quantity': 0}
        )
        if stock_from.quantity < obj.quantity:
            messages.error(request, "❌ Stok iha armazén origen la suficiente.")
            return
        stock_from.quantity -= obj.quantity
        stock_from.save()
        stock_to.quantity += obj.quantity
        stock_to.save()
        messages.success(request, "✅ Transferénsia stok ho susesu!")
        super().save_model(request, obj, form, change)

admin_site.register(StockTransfer, StockTransferAdmin)


# ========== STOCK ADJUSTMENT ==========
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_stock', 'new_stock', 'reason', 'adjusted_by', 'adjusted_at')
    readonly_fields = ('old_stock', 'adjusted_by', 'adjusted_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.adjusted_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(StockAdjustment, StockAdjustmentAdmin)


# ========== BACKUP / RESTORE ==========
class BackupUploadAdmin(admin.ModelAdmin):
    list_display = ['file', 'uploaded_at']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        backup_path = os.path.join(settings.MEDIA_ROOT, str(obj.file))
        try:
            # loaddata harus pakai path, bukan file-like
            call_command('loaddata', backup_path, verbosity=0)
            self.message_user(request, "✅ Restore susesu!", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"❌ Restore falha: {e}", messages.ERROR)

admin_site.register(BackupUpload, BackupUploadAdmin)


# ========== BANK ==========
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "account_name", "account_number", "is_active")
    search_fields = ("name", "code", "account_number")
    list_filter = ("is_active",)

class BankPaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction", "bank", "gross_amount", "fee_amount", "net_amount", "status", "created_at")
    list_filter = ("status", "bank")
    search_fields = ("transaction__invoice_id",)

admin_site.register(Bank, BankAdmin)
admin_site.register(BankPayment, BankPaymentAdmin)


# ========== POINTS ==========
class PointsEarningRuleAdmin(admin.ModelAdmin):
    list_display = ("min_total", "points_awarded", "is_active")
    list_editable = ("points_awarded", "is_active")
    search_fields = ("min_total",)
    ordering = ("min_total",)
    list_filter = ("is_active",)

class PointsRedemptionRuleAdmin(admin.ModelAdmin):
    list_display = ("points_required", "detail", "discount_amount", "is_active")
    list_editable = ("detail", "discount_amount", "is_active")
    search_fields = ("detail",)
    ordering = ("points_required",)
    list_filter = ("is_active",)

class PointsLedgerAdmin(admin.ModelAdmin):
    list_display = ("customer", "change", "balance_after", "transaction", "note", "created_at")
    search_fields = ("customer__name", "transaction__invoice_id", "note")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("customer", "change", "balance_after", "transaction", "note", "created_at")

admin_site.register(PointsEarningRule, PointsEarningRuleAdmin)
admin_site.register(PointsRedemptionRule, PointsRedemptionRuleAdmin)
admin_site.register(PointsLedger, PointsLedgerAdmin)


# ========== UTIL ==========
def generate_chart(top_products):
    names = [p["product__name"] for p in top_products]
    sales = [p["total_sold"] for p in top_products]
    plt.figure(figsize=(6, 3))
    plt.bar(names, sales)  
    plt.title("Produtu sira ne'ebé fa'an barak liu")
    plt.xlabel("Produtu")
    plt.ylabel("Total Fa'an")
    plt.xticks(rotation=15)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'<img src="data:image/png;base64,{image_base64}" style="max-width:100%; height:auto; border:1px solid #ccc; padding:5px; border-radius:4px;" />'
