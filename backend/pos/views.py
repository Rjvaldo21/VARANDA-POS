from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .serializers import ProductReturnSerializer
from .models import Bank, BankPayment
from .serializers import BankSerializer, BankPaymentSerializer
from .models import ProductReturn
from datetime import datetime, date, timedelta
from django.db.models import Sum, F, DecimalField, Count, ExpressionWrapper
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models.functions import Coalesce
from .models import Stock
from .models import Purchase
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.viewsets import ModelViewSet
from .serializers import PurchaseSerializer
from .serializers import StockSerializer
from pos.models import StockMovement
from pos.serializers import StockMovementSerializer
from rest_framework import serializers
from rest_framework import viewsets, permissions
from .models import PurchaseReturn
from .serializers import PurchaseReturnSerializer
from .models import Transaction, TransactionItem 
from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper, Q
from .models import Warehouse
from .serializers import WarehouseSerializer
from .models import Category
from .models import Unit
from django.http import JsonResponse
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from .models import StockAdjustment
from .serializers import StockAdjustmentSerializer
from .models import StockTransfer, Stock
from .serializers import StockTransferSerializer
from .serializers import TransactionSummarySerializer
from .serializers import UnitSerializer
from .serializers import CategorySerializer
from .serializers import InvoiceSerializer
from datetime import datetime
import os
from django.core.files import File
from .models import StoreProfile
from django.db.models import Sum, Q
from .models import Transaction, TransactionItem
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.db import transaction as db_transaction
from .models import Transaction, TransactionItem, Expense
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command
from io import StringIO, BytesIO
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Transaction, TransactionItem
from django.utils.timezone import now

from .models import (
    Product, Transaction, TransactionItem, StoreProfile,
    Customer, Supplier
)
from .serializers import (
    ProductSerializer, TransactionSerializer,
    StoreProfileSerializer, CustomerSerializer, SupplierSerializer
)

from rest_framework.views import APIView


@csrf_exempt
def create_superuser(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User sudah existe'}, status=400)

        user = User.objects.create_superuser(username=username, password=password)
        return JsonResponse({'message': 'Superuser kria ho susesu!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def check_db(request):
    return JsonResponse({"status": "ok"})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_summary_detail(request, transaction_id: int):
    """Ringkasan untuk 1 transaksi tertentu (pakai serializer)."""
    try:
        tx = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'detail': 'Transaksaun la hetan.'}, status=404)

    serializer = TransactionSummarySerializer(tx)
    return Response(serializer.data)


class PurchaseReturnViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturn.objects.select_related('purchase', 'product', 'user').all()
    serializer_class = PurchaseReturnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)    
    
    
@staff_member_required
def backup_json_view(request):
    string_io = StringIO()
    call_command('dumpdata', stdout=string_io)
    
    byte_content = string_io.getvalue().encode('utf-8')
    buffer = BytesIO(byte_content)

    filename = f'backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    response = HttpResponse(buffer.getvalue(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all().order_by('-id')
    serializer_class = PurchaseSerializer  


@staff_member_required
def sales_report_admin(request):
    today = now().date()
    month = today.month
    year = today.year

    daily_transactions = Transaction.objects.filter(created_at__date=today)
    monthly_transactions = Transaction.objects.filter(created_at__year=year, created_at__month=month)
    daily_sales = sum(t.total - t.return_total for t in daily_transactions)
    monthly_sales = sum(t.total - t.return_total for t in monthly_transactions)
    daily_returns = sum(t.return_total for t in daily_transactions)
    monthly_returns = sum(t.return_total for t in monthly_transactions)
    top_products = TransactionItem.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]

    context = {
    'daily_sales': daily_sales,
    'monthly_sales': monthly_sales,
    'daily_returns': daily_returns,
    'monthly_returns': monthly_returns,
    'top_products': top_products,
    }
    return render(request, 'admin/sales_report.html', context)

def print_receipt(request, invoice_id):
    transaction = get_object_or_404(Transaction, invoice_id=invoice_id)
    items = TransactionItem.objects.filter(transaction=transaction)

    data = {
        "invoice_id": transaction.invoice_id,
        "date": transaction.created_at.strftime('%Y-%m-%d %H:%M'),
        "payment_method": transaction.payment_method,
        "total": transaction.total,
        "items": [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.quantity * item.price
            }
            for item in items
        ]
    }

    return JsonResponse(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):
    today = now().date()
    month = today.month
    year = today.year

    daily_transactions = Transaction.objects.filter(created_at__date=today)
    monthly_transactions = Transaction.objects.filter(created_at__year=year, created_at__month=month)

    daily_sales_total = sum(t.total - t.return_total for t in daily_transactions)
    monthly_sales_total = sum(t.total - t.return_total for t in monthly_transactions)

    top_products = TransactionItem.objects.values('product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    return JsonResponse({
    "daily_sales": daily_sales_total,
    "monthly_sales": monthly_sales_total,
    "top_products": list(top_products),
    }) 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        barcode = request.query_params.get('barcode')
        if barcode:
            try:
                product = Product.objects.get(Q(barcode=barcode) | Q(sku=barcode))
                serializer = self.get_serializer(product)
                return Response(serializer.data)
            except Product.DoesNotExist:
                return Response({"detail": "Produtu la hetan."}, status=404)
        return super().list(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer 


class TransactionViewSet(viewsets.ModelViewSet): 
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        with db_transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        
class InvoiceViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
        
    
class TransactionReceiptView(APIView):
    def get(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        items = TransactionItem.objects.filter(transaction=transaction)
        html = render_to_string('receipt.html', {
            'transaction': transaction,
            'items': items,
        })
        return HttpResponse(html)
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-id')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer    


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-id')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    
class ProductReturnViewSet(viewsets.ModelViewSet):
    queryset = ProductReturn.objects.all().order_by('-returned_at')
    serializer_class = ProductReturnSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}    
    
    
class StoreProfileViewSet(viewsets.ModelViewSet):
    queryset = StoreProfile.objects.all()
    serializer_class = StoreProfileSerializer

    def list(self, request, *args, **kwargs):
        try:
            profile = StoreProfile.objects.first()

            if not profile:
                print("📌 La iha perfil, kria default...")

                default_logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', 'default.jpg')
                logo_file = None

                if os.path.exists(default_logo_path):
                    print("✅ Logo hetan ona")
                    with open(default_logo_path, 'rb') as f:
                        logo_file = File(f)
                        profile = StoreProfile(
                            name='Varanda Store',
                            address='Bemori Centro',
                            location='Dili Timor-Leste',
                            version='Versaun 1.0'
                        )
                        profile.logo.save('default.jpg', logo_file, save=True)
                else:
                    profile = StoreProfile.objects.create(
                        name='Varanda Store',
                        address='',
                        location='Dili Timor-Leste',
                        version='Versaun 1.0'
                    )

            serializer = self.get_serializer(profile)
            return Response([serializer.data])

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("🔥 Falha foti/kria StoreProfile:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def location_list(request):
    from .models import StoreProfile
    locations = [{"id": i + 1, "name": loc[0]} for i, loc in enumerate(StoreProfile.LOCATION_CHOICES)]
    return Response(locations)
    
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def store_profile_list(request):
    queryset = StoreProfile.objects.all()
    serializer = StoreProfileSerializer(queryset, many=True, context={'request': request})
    return JsonResponse(serializer.data, safe=False)
            
            
class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.all().order_by('-adjusted_at')
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    
class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(adjusted_by=self.request.user)    
    
 
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('product', 'warehouse', 'product__category', 'product__unit')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    
    
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('name')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    

class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all().order_by('-transferred_at')
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        transfer = serializer.save()

        stock_from, _ = Stock.objects.get_or_create(
            product=transfer.product,
            warehouse=transfer.from_warehouse,
            defaults={'quantity': 0}
        )

        if stock_from.quantity < transfer.quantity:
            raise serializers.ValidationError("❌ Stok iha gudang origen la suficiente.")

        stock_to, _ = Stock.objects.get_or_create(
            product=transfer.product,
            warehouse=transfer.to_warehouse,
            defaults={'quantity': 0}
        )

        stock_from.quantity -= transfer.quantity
        stock_from.save()

        stock_to.quantity += transfer.quantity
        stock_to.save()                    
        

@api_view(['GET'])
def transaction_summary(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    try:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
    except Exception:
        return Response({'error': 'Invalid date format'}, status=400)

    gross_income = Transaction.objects.filter(created_at__range=[start_date, end_date]).aggregate(
        total=Sum('total'))['total'] or 0

    expenses = Expense.objects.filter(date__range=[start_date, end_date]).aggregate(
        total=Sum('amount'))['total'] or 0

    items = TransactionItem.objects.filter(transaction__created_at__range=[start_date, end_date])
    total_cost = sum(item.quantity * item.product.cost_price for item in items)

    net_income = gross_income - total_cost

    profit_or_loss = net_income - expenses

    return Response({
        'gross_income': gross_income,
        'expenses': expenses,
        'gross_minus_expenses': gross_income - expenses,
        'net_income': net_income,
        'profit_or_loss': profit_or_loss,
    })


class SalesTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def _fmt(self, x: Decimal) -> str:
        return (x.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP) if isinstance(x, Decimal)
                else Decimal(str(x or 0)).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)).to_eng_string()

    def _range_for(self, period: str, date_from: str | None, date_to: str | None):
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()

        alias = (period or '').lower()
        if alias in ('today', 'day'):
            start = timezone.make_aware(datetime.combine(today, datetime.min.time()), now_local.tzinfo)
            end   = start + timedelta(days=1)
            return start, end
        if alias == 'yesterday':
            start = timezone.make_aware(datetime.combine(today - timedelta(days=1), datetime.min.time()), now_local.tzinfo)
            end   = start + timedelta(days=1)
            return start, end
        if alias in ('this_month', 'month'):
            start = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()), now_local.tzinfo)
            if start.month == 12:
                end_date = date(start.year + 1, 1, 1)
            else:
                end_date = date(start.year, start.month + 1, 1)
            end = timezone.make_aware(datetime.combine(end_date, datetime.min.time()), now_local.tzinfo)
            return start, end
        if alias in ('this_year', 'year'):
            start = timezone.make_aware(datetime.combine(date(today.year, 1, 1), datetime.min.time()), now_local.tzinfo)
            end   = timezone.make_aware(datetime.combine(date(today.year + 1, 1, 1), datetime.min.time()), now_local.tzinfo)
            return start, end

        fmt = '%Y-%m-%d'
        if date_from:
            df = datetime.strptime(date_from, fmt)
        else:
            df = datetime(today.year, 1, 1)
        if date_to:
            dt_ = datetime.strptime(date_to, fmt)
        else:
            dt_ = datetime.combine(today, datetime.max.time())
        start = timezone.make_aware(datetime.combine(df.date(), datetime.min.time()), now_local.tzinfo)
        end   = timezone.make_aware(datetime.combine(dt_.date() + timedelta(days=1), datetime.min.time()), now_local.tzinfo)
        return start, end

    def get(self, request):
        period    = request.query_params.get('period')
        date_from = request.query_params.get('date_from')
        date_to   = request.query_params.get('date_to')
        start, end = self._range_for(period, date_from, date_to)

        qs = Transaction.objects.filter(created_at__gte=start, created_at__lt=end)

        agg_tx = qs.aggregate(
            total_sales=Coalesce(Sum('total'), Decimal('0')),
            count_transactions=Count('id'),
        )
        total_sales = agg_tx['total_sales'] or Decimal('0')
        net_revenue = total_sales

        items_qs = TransactionItem.objects.filter(transaction__in=qs)
        money = DecimalField(max_digits=18, decimal_places=2)
        subtotal_expr = ExpressionWrapper(F('quantity') * F('price'), output_field=money)
        cost_expr     = ExpressionWrapper(F('quantity') * F('product__cost_price'), output_field=money)

        agg_items = items_qs.aggregate(
            gross_revenue_items=Coalesce(Sum(subtotal_expr), Decimal('0')),
            cogs=Coalesce(Sum(cost_expr), Decimal('0')),
            total_qty=Coalesce(Sum('quantity'), 0),
        )
        cogs = agg_items['cogs'] or Decimal('0')
        margin = net_revenue - cogs
        margin_rate = ( (margin / net_revenue) * Decimal('100') ).quantize(Decimal('1.00')) if net_revenue > 0 else Decimal('0.00')

        return Response({
            "totals": {
                "total_sales": self._fmt(total_sales),
                "net_revenue": self._fmt(net_revenue),
            },
            "costs": {"cogs": self._fmt(cogs)},
            "margin": {
                "gross_profit": self._fmt(margin),
                "margin_rate_percent": self._fmt(margin_rate),
            },
            "counts": {
                "transactions": agg_tx['count_transactions'],
                "items_qty": agg_items.get('total_qty') or 0,
            },
            "filters": {
                "period": (period or '').lower() or 'custom',
                "date_from": date_from,
                "date_to": date_to,
                "range": {
                    "start": start.isoformat(),
                    "end_exclusive": end.isoformat()
                }
            },
        })
        
        
class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all().order_by('name')
    serializer_class = BankSerializer
    permission_classes = [permissions.IsAuthenticated] 

class BankPaymentViewSet(viewsets.ModelViewSet):
    queryset = BankPayment.objects.all().order_by('-created_at')
    serializer_class = BankPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]        
    
    
from .models import (
    PointsEarningRule, PointsRedemptionRule, PointsLedger, Customer, calculate_points_from_total
)
from .serializers import (
    PointsEarningRuleSerializer, PointsRedemptionRuleSerializer, PointsLedgerSerializer,
    PointsPreviewSerializer, PointsRedeemRequestSerializer, CustomerPointsSerializer
)

# ------ Actions ------

@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def points_preview(request):
    """
    Body: { "total": "150.00" }
    Return: { "points": 5 }
    """
    serializer = PointsPreviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    total = serializer.validated_data["total"]
    pts = calculate_points_from_total(Decimal(total))
    return Response({"points": pts})


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def points_redeem(request):
    """
    Body: { "customer_id": 1, "rule_id": 2 }
    Mengurangi poin customer sesuai rule & kembalikan discount_amount (jika ada).
    Return:
      {
        "ok": true,
        "customer": { "id": 1, "name": "...", "points": 420 },
        "rule": { ... },
        "discount_amount": "5.00"
      }
    """
    req = PointsRedeemRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)

    customer = get_object_or_404(Customer, pk=req.validated_data["customer_id"])
    rule = get_object_or_404(PointsRedemptionRule, pk=req.validated_data["rule_id"], is_active=True)

    if (customer.points or 0) < rule.points_required:
        return Response({"ok": False, "error": "Poin tidak cukup"}, status=status.HTTP_400_BAD_REQUEST)

    # Kurangi poin
    customer.points = customer.points - rule.points_required
    customer.save(update_fields=["points"])

    PointsLedger.objects.create(
        customer=customer,
        change=-int(rule.points_required),
        balance_after=customer.points,
        note=f"Redeem: {rule.detail or ('-$' + str(rule.discount_amount))}",
        transaction=None
    )

    return Response({
        "ok": True,
        "customer": CustomerPointsSerializer(customer).data,
        "rule": PointsRedemptionRuleSerializer(rule).data,
        "discount_amount": str(rule.discount_amount or Decimal("0.00"))
    })
    
    
class PointsEarningRuleViewSet(ModelViewSet):
    queryset = PointsEarningRule.objects.all().order_by('min_total')
    serializer_class = PointsEarningRuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

class PointsRedemptionRuleViewSet(ModelViewSet):
    queryset = PointsRedemptionRule.objects.all().order_by('points_required')
    serializer_class = PointsRedemptionRuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

class PointsLedgerViewSet(ReadOnlyModelViewSet):
    queryset = PointsLedger.objects.select_related('customer','transaction').order_by('-created_at')
    serializer_class = PointsLedgerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]        