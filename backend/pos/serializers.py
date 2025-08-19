from rest_framework import serializers
from .models import Customer, Supplier
from .models import ProductReturn
from .models import PurchaseReturn
from .models import Unit
from .models import StockAdjustment
from pos.models import StockMovement
from .models import Stock
from .models import StockTransfer
from .models import Warehouse
from .models import Bank, BankPayment
from django.db.models import Sum
from .models import Transaction, ProductReturn
from .models import Purchase, PurchaseItem
from .models import Purchase
from django.core.files.base import ContentFile
from .models import PointsEarningRule, PointsRedemptionRule, PointsLedger, Customer
import base64
import uuid
import os
from .models import StoreProfile
from .models import Category
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore
from .models import (
    Customer, Supplier, ProductReturn, Unit, Category,
    Product, Transaction, TransactionItem, StoreProfile,
    StockAdjustment
)
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code']
        
        
class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']        


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        
        

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = '__all__'

        
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), allow_null=True, required=False)
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), allow_null=True, required=False)

    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    price_after_discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'variant', 'unit', 'unit_name', 'price', 'cost_price',
            'discount', 'stock', 'min_stock', 'supplier', 'supplier_name',
            'price_after_discount',
        ]

    def get_price_after_discount(self, obj):
        if obj.discount:
            return obj.get_price_after_discount()
        return obj.price


class TransactionItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = TransactionItem
        fields = ['product', 'quantity', 'price']

class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.username')
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(),
        allow_null=True,
        required=False)

    class Meta:
        model = Transaction
        
        fields = [
            'id', 'invoice_id', 'total', 'payment_method',
            'created_at', 'items', 'user', 'customer'
        ]
        
        extra_kwargs = {
        'customer': {'allow_null': True, 'required': False}
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer = validated_data.pop('customer', None) 
        request = self.context.get('request') 

        transaction = Transaction.objects.create(user=request.user, customer=customer, **validated_data)

        for item_data in items_data:
            product_data = item_data['product']
            product_id = product_data.id if hasattr(product_data, 'id') else product_data
            product = Product.objects.get(pk=product_id)

            quantity = item_data['quantity']
            if quantity <= 0:
                raise serializers.ValidationError(f"Kuantidade ba produtu '{product.name}' liu husi 0.")

            if product.stock < quantity:
                raise serializers.ValidationError(f"Stok produtu '{product.name}' la sufisiente.")

            price = product.price
            product.stock -= quantity
            product.save()

            TransactionItem.objects.create(
                transaction=transaction,
                product=product,
                quantity=quantity,
                price=price
            )

        return transaction
    

class StockAdjustmentSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    adjusted_by_username = serializers.ReadOnlyField(source='adjusted_by.username')

    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'product', 'product_name', 'old_stock', 'new_stock',
            'reason', 'adjusted_by', 'adjusted_by_username', 'adjusted_at'
        ]
        read_only_fields = ['old_stock', 'adjusted_by', 'adjusted_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['adjusted_by'] = request.user
        return super().create(validated_data)
    
    
class ProductReturnSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    transaction = TransactionSerializer(read_only=True)
    transaction_id = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.all(), source='transaction', write_only=True
    )

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = ProductReturn
        fields = [
            'id', 'transaction', 'transaction_id',
            'product', 'product_id', 'quantity',
            'refunded_amount', 'reason', 'status',
            'returned_at', 'user'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        return ProductReturn.objects.create(user=request.user, **validated_data)
    

class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku']

class SupplierSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']

class PurchaseSimpleSerializer(serializers.ModelSerializer):
    supplier = SupplierSimpleSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'invoice_id', 'supplier']

class PurchaseReturnSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    purchase = PurchaseSimpleSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    purchase_invoice = serializers.CharField(source='purchase.invoice_id', read_only=True)
    purchase_total = serializers.SerializerMethodField()
    purchase_price = serializers.SerializerMethodField()
    total_refund_value = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PurchaseReturn
        fields = [
            'id',
            'purchase',
            'purchase_invoice',
            'purchase_total',
            'purchase_price',
            'total_refund_value',  
            'product',
            'product_name',
            'quantity',
            'refunded_amount',
            'reason',
            'status',
            'returned_at',
            'user',
            'user_name',
        ]
        read_only_fields = ['returned_at', 'user']
        
    def get_purchase_price(self, obj):
        try:
            item = obj.purchase.purchaseitem_set.get(product=obj.product)
            return item.price
        except:
            return None

    def get_total_refund_value(self, obj):
        price = self.get_purchase_price(obj)
        if price:
            return obj.quantity * price
        return None    

    def get_purchase_total(self, obj):
        if obj.purchase and obj.purchase.total is not None:
            return obj.purchase.total
        return None


class TransactionSummarySerializer(serializers.Serializer):
    invoice_id = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_due = serializers.SerializerMethodField()
    total_refunded = serializers.SerializerMethodField()
    remaining_due = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.name', default='-')
    refund_excess = serializers.SerializerMethodField()

    def get_amount_due(self, obj):
        return obj.amount_due

    def get_total_refunded(self, obj):
        total = ProductReturn.objects.filter(transaction=obj, status='approved').aggregate(
            total=Sum('refunded_amount')
        )['total'] or 0
        return total

    def get_remaining_due(self, obj):
        total_due = obj.amount_due
        refunded = self.get_total_refunded(obj)
        return max(total_due - refunded, 0)

    def get_refund_excess(self, obj):
        total_due = obj.amount_due
        refunded = self.get_total_refunded(obj)
        excess = refunded - total_due
        return excess if excess > 0 else 0
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['role'] = getattr(user.profile, 'role', 'Unknown')

        return token    


class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.logo and instance.logo.name:
            try:
                from os.path import exists
                if exists(instance.logo.path):
                    data['logo'] = instance.logo.url
                else:
                    data['logo'] = None
            except Exception:
                data['logo'] = None
        else:
            data['logo'] = None

        return data


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction 
        fields = ['id', 'invoice_id', 'total', 'created_at']
        

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    adjusted_by_name = serializers.ReadOnlyField(source='adjusted_by.username')

    class Meta:
        model = StockMovement
        fields = '__all__'
                
        
class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    barcode = serializers.ReadOnlyField(source='product.barcode')
    category = serializers.ReadOnlyField(source='product.category.name')
    unit = serializers.ReadOnlyField(source='product.unit.name')
    min_stock = serializers.ReadOnlyField(source='product.min_stock')

    current_stock = serializers.IntegerField(source='quantity', read_only=True)

    class Meta:
        model = Stock
        fields = [
            'id',
            'product', 'product_name', 'barcode', 'category', 'unit',
            'warehouse', 'warehouse_name',
            'current_stock', 'min_stock',
        ]        
        
        
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'description']        


class StockTransferSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'product', 'product_name',
            'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name',
            'quantity', 'note', 'transferred_at'
        ]
        read_only_fields = ['transferred_at']

    def validate(self, data):
        product = data['product']
        from_warehouse = data['from_warehouse']
        quantity = data['quantity']

        try:
            stock_from = Stock.objects.get(product=product, warehouse=from_warehouse)
        except Stock.DoesNotExist:
            raise serializers.ValidationError("❌ Stok iha armazen origen seidauk existe.")

        if stock_from.quantity < quantity:
            raise serializers.ValidationError("❌ Stok iha armazen origem la suficiente.")

        return data

    def create(self, validated_data):
        transfer = StockTransfer.objects.create(**validated_data)

        stock_from, _ = Stock.objects.get_or_create(
            product=transfer.product,
            warehouse=transfer.from_warehouse,
            defaults={'quantity': 0}
        )
        stock_from.quantity = max(stock_from.quantity - transfer.quantity, 0)
        stock_from.save()

        stock_to, _ = Stock.objects.get_or_create(
            product=transfer.product,
            warehouse=transfer.to_warehouse,
            defaults={'quantity': 0}
        )
        stock_to.quantity += transfer.quantity
        stock_to.save()

        return transfer
    
class ItemSalesRowSerializer(serializers.Serializer):
    barcode     = serializers.CharField(allow_null=True)
    name        = serializers.CharField()
    category    = serializers.CharField(allow_null=True)
    supplier    = serializers.CharField(allow_null=True)
    unit        = serializers.CharField(allow_null=True)
    cashier     = serializers.CharField()  # username kasir
    qty_sold    = serializers.DecimalField(max_digits=18, decimal_places=3)
    buy_price   = serializers.DecimalField(max_digits=18, decimal_places=2)
    sell_price  = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    margin      = serializers.DecimalField(max_digits=18, decimal_places=2)
    stock       = serializers.IntegerField()
    
    

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"

class BankPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankPayment
        fields = "__all__"
        read_only_fields = ("fee_amount", "net_amount")
        
        
class PointsEarningRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsEarningRule
        fields = ["id", "name", "min_total", "points_awarded", "is_active"]


class PointsRedemptionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsRedemptionRule
        fields = ["id", "name", "points_required", "detail", "discount_amount", "is_active"]


class PointsLedgerSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = PointsLedger
        fields = ["id", "customer", "customer_name", "change", "balance_after", "note", "transaction", "created_at"]


class PointsPreviewSerializer(serializers.Serializer):
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class PointsRedeemRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    rule_id = serializers.IntegerField()


class CustomerPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "points"]                