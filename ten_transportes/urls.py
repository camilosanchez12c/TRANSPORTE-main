from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from solicitudes.views import SolicitudViewSet, OfertaViewSet
from documentos.views import DocumentoViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')
router.register(r'ofertas', OfertaViewSet, basename='oferta')
router.register(r'documentos', DocumentoViewSet, basename='documento')
#urls para ingresar con las direcciones en la pagina 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/base/', include('base.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
