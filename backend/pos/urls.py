from django.urls import path, include
from . import views
from .views import create_superuser
from .views import InvoiceViewSet
from pos.views import backup_json_view
from .views import CategoryViewSet
from .views import StoreProfileViewSet
from .views import ProductReturnViewSet
from .views import StockTransferViewSet
from .views import WarehouseViewSet
from .views import StockAdjustmentViewSet
from .views import PurchaseViewSet
from .views import transaction_summary
from .views import SalesTotalView
from .views import PurchaseReturnViewSet
from pos.views import StockMovementViewSet
from .views import BankViewSet, BankPaymentViewSet
from .views_reports import ItemSalesReportView # type: ignore
from .views import StockViewSet
from .views import UnitViewSet
from .views import CustomerViewSet
from rest_framework.routers import DefaultRouter
from .views_finance import FinanceSummaryView, FinanceEntriesView
from .views import CustomTokenObtainPairView
from .views import (
    ProductViewSet, TransactionViewSet, CustomerViewSet,
    SupplierViewSet, TransactionReceiptView, sales_report,
    StoreProfileViewSet, UserViewSet,
)
from .views import (
    PointsEarningRuleViewSet, PointsRedemptionRuleViewSet, PointsLedgerViewSet,
    points_preview, points_redeem
)


router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'purchase-returns', PurchaseReturnViewSet, basename='purchase-return')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'product-returns', ProductReturnViewSet, basename='product-return')
router.register(r'store', StoreProfileViewSet)
router.register(r'store-profile', StoreProfileViewSet, basename='store-profile')
router.register(r'customers', CustomerViewSet)
router.register(r'stock-adjustments', StockAdjustmentViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'users', UserViewSet)
router.register(r'units', UnitViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'stock-transfers', StockTransferViewSet)
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')
router.register(r'stocks', StockViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'banks', BankViewSet, basename='bank')
router.register(r'bank-payments', BankPaymentViewSet, basename='bank-payment')
router.register(r'points/earning-rules', PointsEarningRuleViewSet, basename='points-earning-rules')
router.register(r'points/redemption-rules', PointsRedemptionRuleViewSet, basename='points-redemption-rules')
router.register(r'points/ledger', PointsLedgerViewSet, basename='points-ledger')

urlpatterns = [
    path('', include(router.urls)),
    path('create-superuser/', create_superuser, name='create_superuser'),
    path('report/sales/', sales_report, name='sales-report'),
    path('reports/sales/', sales_report, name='sales-report'),
    path('transaction-summary/', transaction_summary),
    path('finance/summary/', FinanceSummaryView.as_view(), name='finance-summary'),
    path('finance/entries/', FinanceEntriesView.as_view(), name='finance-entries'),
    path('reports/item-sales/', ItemSalesReportView.as_view(), name='item-sales-report'),
    path('sales/total/', SalesTotalView.as_view(), name='sales-total'),
    path('store-profile/', views.store_profile_list, name='store_profile_list'),
    path('api/locations/', views.location_list, name='location-list'),
    path('admin/backup-data/', backup_json_view, name='backup_data'),
    path('receipt/html/<int:pk>/', TransactionReceiptView.as_view(), name='receipt-html'),
    path('transaction/<int:transaction_id>/summary/', transaction_summary),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin/sales-report/', views.sales_report_admin, name='sales_report_admin'),
    path('transactions/<int:pk>/receipt/', TransactionReceiptView.as_view(), name='transaction-receipt'),
    path('api/points/preview/', points_preview, name='points-preview'),
    path('api/points/redeem/', points_redeem, name='points-redeem'),
]
