from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Usuario, Cliente, Vehiculo,
    Servicio, Producto,
    OrdenTrabajo, Agrandamiento, EtapaAgrandamiento,
    Cotizacion, Factura, Pago,
    Transaccion, Recordatorio,
)
from .serializers import (
    UsuarioSerializer, ClienteSerializer, VehiculoSerializer,
    ServicioSerializer, ProductoSerializer,
    OrdenTrabajoSerializer, AgrandamientoSerializer, EtapaAgrandamientoSerializer,
    CotizacionSerializer, FacturaSerializer, PagoSerializer,
    TransaccionSerializer, RecordatorioSerializer,
)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset         = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['username', 'first_name', 'last_name']


class ClienteViewSet(viewsets.ModelViewSet):
    queryset         = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['nombre', 'apellido', 'numero_documento', 'telefono']
    filterset_fields = ['activo', 'ciudad']

    @action(detail=True, methods=['get'])
    def vehiculos(self, request, pk=None):
        cliente  = self.get_object()
        vehiculos = cliente.vehiculos.all()
        serializer = VehiculoSerializer(vehiculos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        cliente = self.get_object()
        ordenes = OrdenTrabajo.objects.filter(vehiculo__cliente=cliente).order_by('-fecha_entrada')
        serializer = OrdenTrabajoSerializer(ordenes, many=True)
        return Response(serializer.data)


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset         = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['placa', 'marca', 'modelo']
    filterset_fields = ['tipo', 'marca']

    @action(detail=True, methods=['get'])
    def ordenes(self, request, pk=None):
        vehiculo = self.get_object()
        ordenes  = vehiculo.ordenes.all().order_by('-fecha_entrada')
        serializer = OrdenTrabajoSerializer(ordenes, many=True)
        return Response(serializer.data)


class ServicioViewSet(viewsets.ModelViewSet):
    queryset         = Servicio.objects.filter(activo=True)
    serializer_class = ServicioSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['nombre']
    filterset_fields = ['aplica_moto', 'aplica_carro', 'categoria']


class ProductoViewSet(viewsets.ModelViewSet):
    queryset         = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['nombre', 'referencia']

    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        productos = [p for p in Producto.objects.all() if p.bajo_stock]
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)


class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset         = OrdenTrabajo.objects.all()
    serializer_class = OrdenTrabajoSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['numero', 'vehiculo__placa', 'vehiculo__cliente__nombre']
    filterset_fields = ['estado', 'prioridad', 'tecnico']

    @action(detail=False, methods=['get'])
    def activas(self, request):
        ordenes = OrdenTrabajo.objects.exclude(estado__in=['entregado', 'cancelado'])
        serializer = OrdenTrabajoSerializer(ordenes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def urgentes(self, request):
        ordenes = OrdenTrabajo.objects.filter(prioridad='urgente').exclude(estado='entregado')
        serializer = OrdenTrabajoSerializer(ordenes, many=True)
        return Response(serializer.data)


class AgrandamientoViewSet(viewsets.ModelViewSet):
    queryset         = Agrandamiento.objects.all()
    serializer_class = AgrandamientoSerializer
    filterset_fields = ['tipo']


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset         = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['numero', 'cliente__nombre', 'cliente__apellido']
    filterset_fields = ['estado']

    def create(self, request, *args, **kwargs):
        items_data = request.data.pop('items', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cotizacion = serializer.save()
        for item in items_data:
            ItemCotizacion.objects.create(
                cotizacion   = cotizacion,
                tipo         = item.get('tipo', 'servicio'),
                descripcion  = item.get('descripcion', ''),
                cantidad     = item.get('cantidad', 1),
                precio_unit  = item.get('precio_unitario', item.get('precio_unit', 0)),
                descuento    = item.get('descuento', 0),
            )
        return Response(self.get_serializer(cotizacion).data, status=201)

    def update(self, request, *args, **kwargs):
        items_data = request.data.pop('items', None)
        instance   = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        cotizacion = serializer.save()
        if items_data is not None:
            cotizacion.items.all().delete()
            for item in items_data:
                ItemCotizacion.objects.create(
                    cotizacion   = cotizacion,
                    tipo         = item.get('tipo', 'servicio'),
                    descripcion  = item.get('descripcion', ''),
                    cantidad     = item.get('cantidad', 1),
                    precio_unit  = item.get('precio_unitario', item.get('precio_unit', 0)),
                    descuento    = item.get('descuento', 0),
                )
        return Response(self.get_serializer(cotizacion).data)

    @action(detail=True, methods=['post'])
    def convertir_factura(self, request, pk=None):
        from decimal import Decimal
        cot = self.get_object()
        if cot.estado != 'aprobada':
            return Response({'error': 'Solo se pueden convertir cotizaciones aprobadas'}, status=400)
        subtotal = sum(i.subtotal for i in cot.items.all())
        factura  = Factura.objects.create(
            cliente      = cot.cliente,
            cotizacion   = cot,
            subtotal     = subtotal,
            total        = subtotal,
            estado       = 'pendiente',
        )
        return Response(FacturaSerializer(factura).data, status=201)

class FacturaViewSet(viewsets.ModelViewSet):
    queryset         = Factura.objects.all()
    serializer_class = FacturaSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['numero', 'cliente__nombre', 'cliente__apellido']
    filterset_fields = ['estado', 'metodo_pago']

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        facturas = Factura.objects.filter(estado__in=['pendiente', 'parcial'])
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data)


class PagoViewSet(viewsets.ModelViewSet):
    queryset         = Pago.objects.all()
    serializer_class = PagoSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset         = Transaccion.objects.all()
    serializer_class = TransaccionSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['descripcion', 'proveedor']
    filterset_fields = ['tipo', 'categoria', 'fecha']

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        from django.db.models import Sum
        ingresos = Transaccion.objects.filter(tipo='ingreso').aggregate(total=Sum('monto'))['total'] or 0
        gastos   = Transaccion.objects.filter(tipo='gasto').aggregate(total=Sum('monto'))['total'] or 0
        return Response({
            'ingresos': ingresos,
            'gastos':   gastos,
            'utilidad': ingresos - gastos,
        })


class RecordatorioViewSet(viewsets.ModelViewSet):
    queryset         = Recordatorio.objects.all()
    serializer_class = RecordatorioSerializer
    filter_backends  = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['cliente__nombre', 'cliente__apellido']
    filterset_fields = ['tipo', 'canal', 'estado']

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        from django.utils import timezone
        recordatorios = Recordatorio.objects.filter(
            estado='pendiente',
            programado_para__lte=timezone.now()
        )
        serializer = RecordatorioSerializer(recordatorios, many=True)
        return Response(serializer.data)