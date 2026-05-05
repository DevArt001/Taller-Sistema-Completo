from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, ClienteViewSet, VehiculoViewSet,
    ServicioViewSet, ProductoViewSet,
    OrdenTrabajoViewSet, AgrandamientoViewSet,
    CotizacionViewSet, FacturaViewSet, PagoViewSet,
    TransaccionViewSet, RecordatorioViewSet,
)

router = DefaultRouter()
router.register(r'usuarios',      UsuarioViewSet)
router.register(r'clientes',      ClienteViewSet)
router.register(r'vehiculos',     VehiculoViewSet)
router.register(r'servicios',     ServicioViewSet)
router.register(r'productos',     ProductoViewSet)
router.register(r'ordenes',       OrdenTrabajoViewSet)
router.register(r'agrandamientos',AgrandamientoViewSet)
router.register(r'cotizaciones',  CotizacionViewSet)
router.register(r'facturas',      FacturaViewSet)
router.register(r'pagos',         PagoViewSet)
router.register(r'transacciones', TransaccionViewSet)
router.register(r'recordatorios', RecordatorioViewSet)

urlpatterns = router.urls