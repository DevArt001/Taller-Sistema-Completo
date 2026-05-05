from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
 
 
# ─────────────────────────────────────────
# USUARIOS Y PERMISOS
# ─────────────────────────────────────────
 
class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin',      'Administrador'),
        ('tecnico',    'Técnico'),
        ('recepcion',  'Recepción'),
        ('contador',   'Contador'),
    ]
    rol          = models.CharField(max_length=20, choices=ROL_CHOICES, default='recepcion')
    telefono     = models.CharField(max_length=20, blank=True)
    foto         = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    activo       = models.BooleanField(default=True)
    creado_en    = models.DateTimeField(auto_now_add=True)
    groups       = models.ManyToManyField('auth.Group', related_name='usuario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='usuario_set', blank=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def is_staff(self):
        return self.activo

    def has_module_perms(self, app_label):
        if self.rol == 'admin':
            return True
        if self.rol in ('tecnico', 'contador') and app_label == 'taller':
            return True
        return False

    def has_perm(self, perm, obj=None):
        if self.rol == 'admin':
            return True
        if self.rol == 'tecnico':
            permitidos = ['ordentrabajo', 'vehiculo', 'cliente',
                          'ordenservicio', 'ordenproducto',
                          'agrandamiento', 'etapaagrandamiento']
            return any(p in perm for p in permitidos)
        if self.rol == 'contador':
            permitidos = ['factura', 'pago', 'transaccion',
                          'categoriacontable', 'cotizacion', 'itemcotizacion']
            return any(p in perm for p in permitidos)
        return False
 
 
# ─────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────
 
class Cliente(models.Model):
    TIPO_DOCUMENTO = [
        ('cc',  'Cédula de ciudadanía'),
        ('nit', 'NIT'),
        ('ce',  'Cédula extranjería'),
        ('pas', 'Pasaporte'),
    ]
    tipo_documento    = models.CharField(max_length=5, choices=TIPO_DOCUMENTO, default='cc')
    numero_documento  = models.CharField(max_length=20, unique=True)
    nombre            = models.CharField(max_length=100)
    apellido          = models.CharField(max_length=100)
    telefono          = models.CharField(max_length=20)
    telefono_alt      = models.CharField(max_length=20, blank=True)
    email             = models.EmailField(blank=True)
    direccion         = models.TextField(blank=True)
    ciudad            = models.CharField(max_length=80, blank=True)
    fecha_nacimiento  = models.DateField(null=True, blank=True)
    notas             = models.TextField(blank=True, help_text='Notas internas sobre el cliente')
    activo            = models.BooleanField(default=True)
    creado_en         = models.DateTimeField(auto_now_add=True)
    actualizado_en    = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre', 'apellido']
 
    def __str__(self):
        return f"{self.nombre} {self.apellido} — {self.numero_documento}"
 
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
 
 
# ─────────────────────────────────────────
# VEHÍCULOS
# ─────────────────────────────────────────
 
class Vehiculo(models.Model):
    TIPO_CHOICES = [
        ('moto',   'Moto'),
        ('carro',  'Carro'),
        ('camion', 'Camión'),
        ('otro',   'Otro'),
    ]
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='vehiculos')
    tipo            = models.CharField(max_length=10, choices=TIPO_CHOICES)
    marca           = models.CharField(max_length=60)
    modelo          = models.CharField(max_length=60)
    anio            = models.PositiveSmallIntegerField(verbose_name='Año')
    placa           = models.CharField(max_length=10, unique=True)
    color           = models.CharField(max_length=40, blank=True)
    cilindraje      = models.CharField(max_length=20, blank=True, help_text='Ej: 150cc, 2000cc')
    numero_motor    = models.CharField(max_length=50, blank=True)
    numero_chasis   = models.CharField(max_length=50, blank=True)
    kilometraje     = models.PositiveIntegerField(default=0)
    foto            = models.ImageField(upload_to='vehiculos/', null=True, blank=True)
    notas           = models.TextField(blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['placa']
 
    def __str__(self):
        return f"{self.placa} — {self.marca} {self.modelo} {self.anio} ({self.cliente.nombre_completo})"
 
 
# ─────────────────────────────────────────
# SERVICIOS Y PRODUCTOS
# ─────────────────────────────────────────
 
class CategoriaServicio(models.Model):
    nombre      = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
 
    def __str__(self):
        return self.nombre
 
 
class Servicio(models.Model):
    categoria       = models.ForeignKey(CategoriaServicio, on_delete=models.SET_NULL, null=True, blank=True)
    nombre          = models.CharField(max_length=120)
    descripcion     = models.TextField(blank=True)
    precio_base     = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    aplica_moto     = models.BooleanField(default=True)
    aplica_carro    = models.BooleanField(default=True)
    activo          = models.BooleanField(default=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['categoria', 'nombre']
 
    def __str__(self):
        return self.nombre
 
 
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
 
    def __str__(self):
        return self.nombre
 
 
class Producto(models.Model):
    categoria       = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True)
    nombre          = models.CharField(max_length=120)
    referencia      = models.CharField(max_length=60, blank=True)
    descripcion     = models.TextField(blank=True)
    precio_compra   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta    = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    stock           = models.IntegerField(default=0)
    stock_minimo    = models.IntegerField(default=2, help_text='Alerta cuando el stock baje de este número')
    activo          = models.BooleanField(default=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['nombre']
 
    def __str__(self):
        return f"{self.nombre} (stock: {self.stock})"
 
    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo
 
 
# ─────────────────────────────────────────
# ÓRDENES DE TRABAJO
# ─────────────────────────────────────────
 
class OrdenTrabajo(models.Model):
    ESTADO_CHOICES = [
        ('recibido',     'Recibido'),
        ('diagnostico',  'En diagnóstico'),
        ('aprobado',     'Aprobado por cliente'),
        ('en_proceso',   'En proceso'),
        ('pausado',      'Pausado / espera repuesto'),
        ('terminado',    'Terminado'),
        ('entregado',    'Entregado'),
        ('cancelado',    'Cancelado'),
    ]
    PRIORIDAD_CHOICES = [
        ('baja',   'Baja'),
        ('normal', 'Normal'),
        ('alta',   'Alta'),
        ('urgente','Urgente'),
    ]
 
    numero          = models.CharField(max_length=20, unique=True, editable=False)
    vehiculo        = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='ordenes')
    tecnico         = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                        limit_choices_to={'rol': 'tecnico'}, related_name='ordenes_asignadas')
    recepcionado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='ordenes_recibidas')
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recibido')
    prioridad       = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='normal')
 
    # Entrada del vehículo
    km_entrada      = models.PositiveIntegerField(default=0, verbose_name='Kilometraje entrada')
    descripcion_cliente = models.TextField(verbose_name='Descripción del problema según el cliente')
    diagnostico     = models.TextField(blank=True, verbose_name='Diagnóstico técnico')
 
    # Fechas
    fecha_entrada   = models.DateTimeField(auto_now_add=True)
    fecha_prometida = models.DateTimeField(null=True, blank=True, verbose_name='Fecha prometida de entrega')
    fecha_terminado = models.DateTimeField(null=True, blank=True)
    fecha_entregado = models.DateTimeField(null=True, blank=True)
 
    # Observaciones
    observaciones_internas = models.TextField(blank=True)
    notas_entrega   = models.TextField(blank=True)
 
    # Fotos de entrada
    foto_entrada_1  = models.ImageField(upload_to='ordenes/entrada/', null=True, blank=True)
    foto_entrada_2  = models.ImageField(upload_to='ordenes/entrada/', null=True, blank=True)
    foto_entrada_3  = models.ImageField(upload_to='ordenes/entrada/', null=True, blank=True)
 
    creado_en       = models.DateTimeField(auto_now_add=True)
    actualizado_en  = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name = 'Orden de trabajo'
        verbose_name_plural = 'Órdenes de trabajo'
        ordering = ['-creado_en']
 
    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = OrdenTrabajo.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            self.numero = f"OT-{siguiente:05d}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.numero} — {self.vehiculo.placa} ({self.get_estado_display()})"
 
 
class OrdenServicio(models.Model):
    """Servicios incluidos en una orden de trabajo."""
    orden       = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='servicios')
    servicio    = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    cantidad    = models.PositiveSmallIntegerField(default=1)
    precio_unit = models.DecimalField(max_digits=12, decimal_places=2)
    descuento   = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='% de descuento')
    notas       = models.TextField(blank=True)
 
    @property
    def subtotal(self):
        return self.precio_unit * self.cantidad * (1 - self.descuento / 100)
 
 
class OrdenProducto(models.Model):
    """Productos/repuestos usados en una orden de trabajo."""
    orden       = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='productos')
    producto    = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad    = models.PositiveSmallIntegerField(default=1)
    precio_unit = models.DecimalField(max_digits=12, decimal_places=2)
    descuento   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
 
    @property
    def subtotal(self):
        return self.precio_unit * self.cantidad * (1 - self.descuento / 100)
 
 
# ─────────────────────────────────────────
# AGRANDAMIENTOS (proceso especial por etapas)
# ─────────────────────────────────────────
 
class Agrandamiento(models.Model):
    """Trabajos grandes con múltiples etapas: pintura, restauración, etc."""
    TIPO_CHOICES = [
        ('pintura',      'Pintura completa'),
        ('latoneria',    'Latonería y pintura'),
        ('electricidad', 'Sistema eléctrico'),
        ('motor',        'Reparación de motor'),
        ('mixto',        'Mixto'),
    ]
    orden       = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name='agrandamiento')
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion_general = models.TextField()
    porcentaje_avance   = models.PositiveSmallIntegerField(default=0, help_text='0 a 100')
    creado_en   = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Agrandamiento {self.orden.numero} — {self.get_tipo_display()} ({self.porcentaje_avance}%)"
 
 
class EtapaAgrandamiento(models.Model):
    """Cada etapa del proceso de agrandamiento."""
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('en_proceso',  'En proceso'),
        ('completada',  'Completada'),
        ('pausada',     'Pausada'),
    ]
    agrandamiento   = models.ForeignKey(Agrandamiento, on_delete=models.CASCADE, related_name='etapas')
    nombre          = models.CharField(max_length=100, help_text='Ej: Despiece, Masillado, Pintura, Brillado')
    descripcion     = models.TextField(blank=True)
    orden_ejecucion = models.PositiveSmallIntegerField(default=1)
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    pauta           = models.TextField(blank=True, help_text='Instrucciones paso a paso para esta etapa')
    tecnico         = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='etapas_realizadas')
    fecha_inicio    = models.DateTimeField(null=True, blank=True)
    fecha_fin       = models.DateTimeField(null=True, blank=True)
    foto_antes      = models.ImageField(upload_to='agrandamientos/antes/', null=True, blank=True)
    foto_despues    = models.ImageField(upload_to='agrandamientos/despues/', null=True, blank=True)
    notas           = models.TextField(blank=True)
 
    class Meta:
        ordering = ['orden_ejecucion']
 
    def __str__(self):
        return f"{self.nombre} — {self.get_estado_display()}"
 
 
# ─────────────────────────────────────────
# COTIZACIONES
# ─────────────────────────────────────────
 
class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('borrador',  'Borrador'),
        ('enviada',   'Enviada al cliente'),
        ('aprobada',  'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('vencida',   'Vencida'),
    ]
    numero          = models.CharField(max_length=20, unique=True, editable=False)
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cotizaciones')
    vehiculo        = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    orden           = models.ForeignKey(OrdenTrabajo, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='cotizaciones')
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='borrador')
    validez_dias    = models.PositiveSmallIntegerField(default=7, help_text='Días de validez')
    notas           = models.TextField(blank=True)
    creado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Cotizacion.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            self.numero = f"COT-{siguiente:05d}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.numero} — {self.cliente.nombre_completo}"
 
 
class ItemCotizacion(models.Model):
    TIPO_CHOICES = [('servicio', 'Servicio'), ('producto', 'Producto')]
    cotizacion  = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='items')
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200)
    cantidad    = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    precio_unit = models.DecimalField(max_digits=12, decimal_places=2)
    descuento   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
 
    @property
    def subtotal(self):
        return self.precio_unit * self.cantidad * (1 - self.descuento / 100)
 
 
# ─────────────────────────────────────────
# FACTURAS
# ─────────────────────────────────────────
 
class Factura(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('parcial',   'Pago parcial'),
        ('pagada',    'Pagada'),
        ('anulada',   'Anulada'),
    ]
    METODO_PAGO = [
        ('efectivo',     'Efectivo'),
        ('transferencia','Transferencia'),
        ('nequi',        'Nequi'),
        ('daviplata',    'Daviplata'),
        ('tarjeta',      'Tarjeta'),
        ('credito',      'Crédito / fiado'),
    ]
    numero          = models.CharField(max_length=20, unique=True, editable=False)
    orden           = models.OneToOneField(OrdenTrabajo, on_delete=models.PROTECT,
                                           null=True, blank=True, related_name='factura')
    cotizacion      = models.ForeignKey(Cotizacion, on_delete=models.SET_NULL, null=True, blank=True)
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas')
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago     = models.CharField(max_length=20, choices=METODO_PAGO, blank=True)
    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descuento_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    impuesto        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_pagado    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notas           = models.TextField(blank=True)
    creado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Factura.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            self.numero = f"FAC-{siguiente:05d}"
        super().save(*args, **kwargs)
 
    @property
    def saldo_pendiente(self):
        return self.total - self.total_pagado
 
    def __str__(self):
        return f"{self.numero} — {self.cliente.nombre_completo} — ${self.total:,.0f}"
 
 
class Pago(models.Model):
    """Registro de cada pago recibido sobre una factura."""
    METODO_PAGO = Factura.METODO_PAGO
    factura     = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    monto       = models.DecimalField(max_digits=14, decimal_places=2)
    metodo      = models.CharField(max_length=20, choices=METODO_PAGO)
    referencia  = models.CharField(max_length=100, blank=True, help_text='Número de transferencia, etc.')
    fecha       = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    notas       = models.TextField(blank=True)
 
    def __str__(self):
        return f"Pago ${self.monto:,.0f} — {self.factura.numero}"
 
 
# ─────────────────────────────────────────
# CONTABILIDAD
# ─────────────────────────────────────────
 
class CategoriaContable(models.Model):
    TIPO_CHOICES = [('ingreso', 'Ingreso'), ('gasto', 'Gasto')]
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
 
    class Meta:
        ordering = ['tipo', 'nombre']
 
    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nombre}"
 
 
class Transaccion(models.Model):
    TIPO_CHOICES = [('ingreso', 'Ingreso'), ('gasto', 'Gasto')]
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria   = models.ForeignKey(CategoriaContable, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=200)
    monto       = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    factura     = models.ForeignKey(Factura, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='transacciones')
    proveedor   = models.CharField(max_length=100, blank=True)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    fecha       = models.DateField()
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en   = models.DateTimeField(auto_now_add=True)
    notas       = models.TextField(blank=True)
 
    class Meta:
        ordering = ['-fecha']
 
    def __str__(self):
        return f"{self.get_tipo_display()} ${self.monto:,.0f} — {self.descripcion[:50]}"
 
 
# ─────────────────────────────────────────
# RECORDATORIOS Y COMUNICACIONES
# ─────────────────────────────────────────
 
class Recordatorio(models.Model):
    TIPO_CHOICES = [
        ('vehiculo_listo',      'Vehículo listo para recoger'),
        ('mantenimiento',       'Mantenimiento próximo'),
        ('seguimiento',         'Seguimiento post-servicio'),
        ('pago_pendiente',      'Pago pendiente'),
        ('cita_agendada',       'Cita agendada'),
        ('personalizado',       'Personalizado'),
    ]
    CANAL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms',      'SMS'),
        ('email',    'Correo electrónico'),
        ('llamada',  'Llamada telefónica'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado',   'Enviado'),
        ('fallido',   'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    cliente         = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='recordatorios')
    orden           = models.ForeignKey(OrdenTrabajo, on_delete=models.SET_NULL, null=True, blank=True)
    tipo            = models.CharField(max_length=30, choices=TIPO_CHOICES)
    canal           = models.CharField(max_length=15, choices=CANAL_CHOICES)
    mensaje         = models.TextField()
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    programado_para = models.DateTimeField()
    enviado_en      = models.DateTimeField(null=True, blank=True)
    creado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['programado_para']
 
    def __str__(self):
        return f"{self.get_tipo_display()} → {self.cliente.nombre_completo} ({self.programado_para:%d/%m/%Y})"
 
 
class RegistroLlamada(models.Model):
    RESULTADO_CHOICES = [
        ('contestado',   'Contestado'),
        ('no_contestó',  'No contestó'),
        ('ocupado',      'Ocupado'),
        ('equivocado',   'Número equivocado'),
    ]
    cliente     = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='llamadas')
    orden       = models.ForeignKey(OrdenTrabajo, on_delete=models.SET_NULL, null=True, blank=True)
    resultado   = models.CharField(max_length=20, choices=RESULTADO_CHOICES)
    notas       = models.TextField(blank=True)
    duracion_seg = models.PositiveIntegerField(default=0, verbose_name='Duración (segundos)')
    realizada_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha       = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Llamada a {self.cliente.nombre_completo} — {self.get_resultado_display()}"
 
 
# ─────────────────────────────────────────
# MARKETING Y PUBLICIDAD
# ─────────────────────────────────────────
 
class Promocion(models.Model):
    TIPO_CHOICES = [
        ('descuento_porcentaje', 'Descuento porcentaje'),
        ('descuento_valor',      'Descuento valor fijo'),
        ('combo',                'Combo de servicios'),
        ('regalo',               'Regalo / bonificación'),
    ]
    nombre          = models.CharField(max_length=100)
    tipo            = models.CharField(max_length=25, choices=TIPO_CHOICES)
    valor           = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          help_text='Porcentaje o valor según el tipo')
    descripcion     = models.TextField(blank=True)
    servicios       = models.ManyToManyField(Servicio, blank=True, help_text='Servicios aplicables')
    productos       = models.ManyToManyField(Producto, blank=True, help_text='Productos aplicables')
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField()
    activa          = models.BooleanField(default=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
 
 
class CampanaMarketing(models.Model):
    RED_CHOICES = [
        ('facebook',  'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok',    'TikTok'),
        ('email',     'Email'),
        ('whatsapp',  'WhatsApp'),
    ]
    nombre          = models.CharField(max_length=100)
    red             = models.CharField(max_length=15, choices=RED_CHOICES)
    descripcion     = models.TextField(blank=True)
    promocion       = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)
    presupuesto     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_real      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impresiones     = models.PositiveIntegerField(default=0)
    clics           = models.PositiveIntegerField(default=0)
    conversiones    = models.PositiveIntegerField(default=0)
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField(null=True, blank=True)
    activa          = models.BooleanField(default=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.nombre} — {self.get_red_display()}"