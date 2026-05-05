from rest_framework import serializers
from .models import (
    Usuario, Cliente, Vehiculo,
    CategoriaServicio, Servicio,
    OrdenTrabajo, OrdenServicio, OrdenProducto,
    Agrandamiento, EtapaAgrandamiento,
    Cotizacion, ItemCotizacion,
    Factura, Pago,
    CategoriaContable, Transaccion,
    Recordatorio, Producto,
)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'rol', 'telefono', 'activo']


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    class Meta:
        model  = Cliente
        fields = '__all__'


class VehiculoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    class Meta:
        model  = Vehiculo
        fields = '__all__'


class OrdenServicioSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    subtotal        = serializers.ReadOnlyField()
    class Meta:
        model  = OrdenServicio
        fields = '__all__'


class OrdenProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal        = serializers.ReadOnlyField()
    class Meta:
        model  = OrdenProducto
        fields = '__all__'


class EtapaAgrandamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EtapaAgrandamiento
        fields = '__all__'


class AgrandamientoSerializer(serializers.ModelSerializer):
    etapas = EtapaAgrandamientoSerializer(many=True, read_only=True)
    class Meta:
        model  = Agrandamiento
        fields = '__all__'


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    servicios       = OrdenServicioSerializer(many=True, read_only=True)
    productos       = OrdenProductoSerializer(many=True, read_only=True)
    agrandamiento   = AgrandamientoSerializer(read_only=True)
    cliente_nombre  = serializers.CharField(source='vehiculo.cliente.nombre_completo', read_only=True)
    vehiculo_placa  = serializers.CharField(source='vehiculo.placa', read_only=True)
    tecnico_nombre  = serializers.CharField(source='tecnico.get_full_name', read_only=True)
    class Meta:
        model  = OrdenTrabajo
        fields = '__all__'


class ItemCotizacionSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model  = ItemCotizacion
        fields = '__all__'


class CotizacionSerializer(serializers.ModelSerializer):
    items          = ItemCotizacionSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    class Meta:
        model  = Cotizacion
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pago
        fields = '__all__'


class FacturaSerializer(serializers.ModelSerializer):
    pagos          = PagoSerializer(many=True, read_only=True)
    saldo_pendiente = serializers.ReadOnlyField()
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    class Meta:
        model  = Factura
        fields = '__all__'


class TransaccionSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    class Meta:
        model  = Transaccion
        fields = '__all__'


class RecordatorioSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    class Meta:
        model  = Recordatorio
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    class Meta:
        model  = Servicio
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    bajo_stock = serializers.ReadOnlyField()
    class Meta:
        model  = Producto
        fields = '__all__'