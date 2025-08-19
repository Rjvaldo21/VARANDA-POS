from datetime import datetime
from decimal import Decimal
from django.db.models import Sum, F, DecimalField, Q
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import TransactionItem  

class ItemSalesReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from   = request.query_params.get('date_from')
        date_to     = request.query_params.get('date_to')
        search      = request.query_params.get('search', '').strip()
        category_id = request.query_params.get('category_id')
        supplier_id = request.query_params.get('supplier_id')
        unit_id     = request.query_params.get('unit_id')
        product_id  = request.query_params.get('product_id')
        cashier_id  = request.query_params.get('cashier_id')
        ordering    = request.query_params.get('ordering', '-total_sales')

        if not date_from and not date_to:
            today = datetime.now().date().isoformat()
            date_from, date_to = today, today

        def to_start(s): return f"{s} 00:00:00"
        def to_end(s):   return f"{s} 23:59:59"

        qs = (TransactionItem.objects
            .select_related('transaction','transaction__user',
            'product','product__category','product__supplier','product__unit'))

        if date_from: qs = qs.filter(transaction__created_at__gte=to_start(date_from))
        if date_to:   qs = qs.filter(transaction__created_at__lte=to_end(date_to))

        if search:
            qs = qs.filter(
                Q(product__name__icontains=search) |
                Q(product__barcode__icontains=search) |
                Q(product__sku__icontains=search)
            )
        if category_id: qs = qs.filter(product__category_id=category_id)
        if supplier_id: qs = qs.filter(product__supplier_id=supplier_id)
        if unit_id:     qs = qs.filter(product__unit_id=unit_id)
        if product_id:  qs = qs.filter(product_id=product_id)
        if cashier_id:  qs = qs.filter(transaction__user_id=cashier_id)

        money = DecimalField(max_digits=18, decimal_places=2)
        subtotal    = F('quantity') * F('price')
        margin_expr = F('quantity') * (F('price') - F('product__cost_price'))

        grouped = (qs.values('product__barcode','product__name','product__category__name',
                    'product__supplier__name','product__unit__name',
                    'transaction__user__username','product__cost_price',
                    'product__price','product__stock')
            .annotate(
            qty_sold=Coalesce(Sum('quantity'), 0),
            total_sales=Coalesce(Sum(subtotal, output_field=money), Decimal('0.00')),
            margin=Coalesce(Sum(margin_expr, output_field=money), Decimal('0.00')),
            ))

        if ordering == 'name':
            grouped = grouped.order_by('product__name')
        elif ordering == '-name':
            grouped = grouped.order_by('-product__name')
        elif ordering in ('qty_sold','-qty_sold','total_sales','-total_sales','margin','-margin'):
            grouped = grouped.order_by(ordering)
        else:
            grouped = grouped.order_by('-total_sales')

        rows = [{
            "barcode":     r['product__barcode'],
            "name":        r['product__name'],
            "category":    r['product__category__name'],
            "supplier":    r['product__supplier__name'],
            "unit":        r['product__unit__name'],
            "cashier":     r['transaction__user__username'] or '-',
            "qty_sold":    r['qty_sold'],
            "buy_price":   r['product__cost_price'] or Decimal('0.00'),
            "sell_price":  r['product__price'] or Decimal('0.00'),
            "total_sales": r['total_sales'],
            "margin":      r['margin'],
            "stock":       r['product__stock'] or 0,
        } for r in grouped]

        return Response({
            "period": {"date_from": date_from, "date_to": date_to},
            "count": len(rows),
            "results": rows
        })
