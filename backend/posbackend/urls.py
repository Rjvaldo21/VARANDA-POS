from pos.admin import admin_site 
from django.urls import path, include
from pos import views
from pos.views import check_db 
from django.conf import settings
from django.conf.urls.static import static
from pos.admin import admin_site
from django.urls import path, include
from pos.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView # type: ignore

urlpatterns = [
    path('admin/', admin_site.urls),
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/locations/', views.location_list, name='location-list'),
    path("check-db/", check_db),
    path('api/receipt/<str:invoice_id>/', views.print_receipt, name='print_receipt'),

    path('api/', include('pos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

