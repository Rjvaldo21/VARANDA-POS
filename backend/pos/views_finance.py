from datetime import datetime, timedelta
from decimal import Decimal
from itertools import chain

from django.db.models import Sum, F, Value as V, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Transaction, Purchase, Expense, ProductReturn, PurchaseReturn


def parse_date(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '').split('.')[0])
    except Exception:
        return None

def normalize_end(s: str | None):
    if not s:
        return None
    dt = parse_date(s)
    if not dt:
        return None
    is_date_only = len(s.strip()) == 10
    return dt + timedelta(days=1) if is_date_only else dt

def coalesce_sum(qs, field: str):
    return qs.aggregate(
        v=Coalesce(Sum(field, output_field=DecimalField(max_digits=18, decimal_places=2)),
                   V(Decimal('0.00')),
                   output_field=DecimalField(max_digits=18, decimal_places=2))
    )['v'] or Decimal('0.00')

def signed_amount(field_name: str, sign: int):
    return ExpressionWrapper(
        F(field_name) * V(sign),
        output_field=DecimalField(max_digits=18, decimal_places=2)
    )


class FinanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        p = request.query_params
        start = parse_date(p.get('date_from'))
        end   = normalize_end(p.get('date_to'))

        qs_sales = Transaction.objects.all()
        if start: qs_sales = qs_sales.filter(created_at__gte=start)
        if end:   qs_sales = qs_sales.filter(created_at__lt=end)
        sales_total = coalesce_sum(qs_sales, 'amount_paid')

        qs_pr = PurchaseReturn.objects.all()
        if start: qs_pr = qs_pr.filter(returned_at__gte=start)
        if end:   qs_pr = qs_pr.filter(returned_at__lt=end)
        purchase_return_total = coalesce_sum(qs_pr, 'refunded_amount')

        qs_exp = Expense.objects.all()
        if start: qs_exp = qs_exp.filter(date__gte=(start.date()))
        if end:   qs_exp = qs_exp.filter(date__lt=(end.date()))
        expense_total = coalesce_sum(qs_exp, 'amount')

        qs_pur = Purchase.objects.all()
        if start: qs_pur = qs_pur.filter(created_at__gte=start)
        if end:   qs_pur = qs_pur.filter(created_at__lt=end)
        purchase_total = coalesce_sum(qs_pur, 'total')

        qs_ret = ProductReturn.objects.all()
        if start: qs_ret = qs_ret.filter(returned_at__gte=start)
        if end:   qs_ret = qs_ret.filter(returned_at__lt=end)
        refund_customer_total = coalesce_sum(qs_ret, 'refunded_amount')

        income_sum  = sales_total + purchase_return_total
        outflow_sum = expense_total + purchase_total + refund_customer_total
        net_total   = income_sum - outflow_sum

        def s(x: Decimal) -> str: return f"{x:.2f}"

        return Response({
            "period": {"date_from": p.get('date_from'), "date_to": p.get('date_to')},
            "breakdown": {
                "income": {
                    "sales_paid": s(sales_total),
                    "purchase_return": s(purchase_return_total),
                    "total_income": s(income_sum),
                },
                "outflow": {
                    "expense": s(expense_total),
                    "purchase": s(purchase_total),
                    "customer_refund": s(refund_customer_total),
                    "total_outflow": s(outflow_sum),
                }
            },
            "total_net": s(net_total)
        })


class FinanceEntriesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class FinanceEntriesView(APIView, FinanceEntriesPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        start = parse_date(p.get('date_from'))
        end   = normalize_end(p.get('date_to'))
        typ   = p.get('type')

        def to_values(qs, date_field: str, typelabel: str, sign: int, fields: dict):
            qs = qs.annotate(
                entry_date=F(date_field),
                entry_type=V(typelabel),
                amount_signed=signed_amount(fields['amount'], sign),
            ).values(
                'entry_date', 'entry_type', 'amount_signed', 'id'
            )
            
            if fields.get('number'):
                qs = qs.annotate(number=F(fields['number'])).values('number', *qs.query.values_select)
            if fields.get('note'):
                qs = qs.annotate(note=F(fields['note'])).values(*qs.query.values_select + ['note'])
            return qs

        rows = []

        qs = Transaction.objects.all()
        if start: qs = qs.filter(created_at__gte=start)
        if end:   qs = qs.filter(created_at__lt=end)
        rows.append(to_values(qs, 'created_at', 'sales', +1, {
            'amount': 'amount_paid', 'number': 'invoice_id', 'note': None
        }))

        qs = Purchase.objects.all()
        if start: qs = qs.filter(created_at__gte=start)
        if end:   qs = qs.filter(created_at__lt=end)
        rows.append(to_values(qs, 'created_at', 'purchase', -1, {
            'amount': 'total', 'number': 'invoice_id', 'note': None
        }))

        qs = Expense.objects.all()
        if start: qs = qs.filter(date__gte=(start.date()))
        if end:   qs = qs.filter(date__lt=(end.date()))
        rows.append(to_values(qs, 'date', 'expense', -1, {
            'amount': 'amount', 'number': None, 'note': 'name'
        }))

        qs = ProductReturn.objects.all()
        if start: qs = qs.filter(returned_at__gte=start)
        if end:   qs = qs.filter(returned_at__lt=end)
        rows.append(to_values(qs, 'returned_at', 'customer_refund', -1, {
            'amount': 'refunded_amount', 'number': None, 'note': 'reason'
        }))

        qs = PurchaseReturn.objects.all()
        if start: qs = qs.filter(returned_at__gte=start)
        if end:   qs = qs.filter(returned_at__lt=end)
        rows.append(to_values(qs, 'returned_at', 'purchase_return', +1, {
            'amount': 'refunded_amount', 'number': None, 'note': 'reason'
        }))

        data = list(chain.from_iterable([list(q) for q in rows]))

        if typ:
            data = [x for x in data if x['entry_type'] == typ]

        data.sort(key=lambda x: x['entry_date'] or datetime.min, reverse=True)

        page = self.paginate_queryset(data, request, view=self)
        return self.get_paginated_response(page)