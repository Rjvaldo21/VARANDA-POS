from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from .models import *

# Simple admin without external dependencies

# Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Unit
@admin.register(Unit) 
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'address']
    search_fields = ['name', 'phone', 'email']

# Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'barcode', 'cost_price', 'selling_price', 'discount_percent']
    list_filter = ['category', 'unit']
    search_fields = ['name', 'barcode']

# Warehouse
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'description']
    search_fields = ['name', 'location']

# Stock
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'minimum_stock']
    list_filter = ['warehouse', 'product__category']
    search_fields = ['product__name']

# Stock Movement
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'date', 'warehouse']
    list_filter = ['movement_type', 'warehouse', 'date']
    search_fields = ['product__name']

# Stock Adjustment
@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'old_quantity', 'new_quantity', 'reason', 'date', 'adjusted_by']
    list_filter = ['warehouse', 'date']
    search_fields = ['product__name', 'reason']

# Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'customer', 'total_amount', 'amount_paid', 'date', 'user']
    list_filter = ['date', 'user']
    search_fields = ['invoice_id', 'customer__name']

# Transaction Item  
@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'quantity', 'price']
    list_filter = ['transaction__date']
    search_fields = ['transaction__invoice_id', 'product__name']

# Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'is_active_employee', 'date_hired']
    list_filter = ['role', 'is_active_employee', 'preferred_shift']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']

# Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'total_spent', 'total_points']
    search_fields = ['name', 'phone', 'email']

# Store Profile
@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'email']
    search_fields = ['name', 'address']

# Purchase
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'supplier', 'total_amount', 'purchase_date']
    list_filter = ['purchase_date', 'supplier']
    search_fields = ['invoice_id', 'supplier__name']

# Purchase Item
@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'product', 'quantity', 'cost_price']
    search_fields = ['purchase__invoice_id', 'product__name']

# Product Return
@admin.register(ProductReturn)
class ProductReturnAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'quantity', 'return_date', 'status', 'user']
    list_filter = ['status', 'return_date']
    search_fields = ['transaction__invoice_id', 'product__name']

# Purchase Return  
@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'return_date', 'total_amount', 'status', 'user']
    list_filter = ['status', 'return_date']
    search_fields = ['purchase__invoice_id']

# Expense
try:
    @admin.register(Expense)
    class ExpenseAdmin(admin.ModelAdmin):
        list_display = ['description', 'amount', 'date', 'category']
        list_filter = ['date', 'category']
        search_fields = ['description']
except:
    pass

# Bank
try:
    @admin.register(Bank)
    class BankAdmin(admin.ModelAdmin):
        list_display = ['name', 'account_number', 'account_holder']
        search_fields = ['name', 'account_number', 'account_holder']
except:
    pass

# Bank Payment
try:
    @admin.register(BankPayment)
    class BankPaymentAdmin(admin.ModelAdmin):
        list_display = ['transaction', 'bank', 'amount', 'transfer_fee', 'status', 'payment_date']
        list_filter = ['status', 'bank', 'payment_date']
        search_fields = ['transaction__invoice_id', 'bank__name']
except:
    pass

# Points models
try:
    @admin.register(PointsEarningRule)
    class PointsEarningRuleAdmin(admin.ModelAdmin):
        list_display = ['amount_spent', 'points_earned', 'is_active']
        list_filter = ['is_active']

    @admin.register(PointsRedemptionRule) 
    class PointsRedemptionRuleAdmin(admin.ModelAdmin):
        list_display = ['points_required', 'discount_amount', 'is_active']
        list_filter = ['is_active']

    @admin.register(PointsLedger)
    class PointsLedgerAdmin(admin.ModelAdmin):
        list_display = ['customer', 'transaction', 'points_earned', 'points_redeemed', 'date']
        list_filter = ['date']
        search_fields = ['customer__name', 'transaction__invoice_id']
except:
    pass

# Unregister default User/Group admins and re-register
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)