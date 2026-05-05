from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Cliente, Vehiculo,
    CategoriaServicio, Servicio,
    CategoriaProducto, Producto,
    OrdenTrabajo, OrdenServicio, OrdenProducto,
    Agrandamiento, EtapaAgrandamiento,
    Cotizacion, ItemCotizacion,
    Factura, Pago,
    CategoriaContable, Transaccion,
    Recordatorio, RegistroLlamada,
    Promocion, CampanaMarketing,
)

admin.site.site_header  = '🏎️ ARM Racing Performance'
admin.site.site_title   = 'ARM Racing'
admin.site.index_title  = 'Panel de administración'

# ── Usuarios ──────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'nombre_completo', 'rol', 'telefono', 'activo')
    list_filter   = ('rol', 'activo')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos del taller', {'fields': ('rol', 'telefono', 'foto', 'activo')}),
    )

    def nombre_completo(self, obj):
        return obj.get_full_name()
    nombre_completo.short_description = 'Nombre'

# ── Clientes ──────────────────────────────
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('nombre_completo', 'numero_documento', 'telefono', 'email', 'activo')
    list_filter   = ('activo', 'tipo_documento', 'ciudad')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'telefono', 'email')

# ── Vehículos ─────────────────────────────
@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display  = ('placa', 'tipo', 'marca', 'modelo', 'anio', 'color', 'cliente')
    list_filter   = ('tipo', 'marca')
    search_fields = ('placa', 'marca', 'modelo', 'numero_motor', 'cliente__nombre', 'cliente__apellido')

# ── Servicios ─────────────────────────────
@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'categoria', 'precio_base', 'aplica_moto', 'aplica_carro', 'activo')
    list_filter   = ('categoria', 'aplica_moto', 'aplica_carro', 'activo')
    search_fields = ('nombre',)

# ── Productos ─────────────────────────────
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'referencia', 'categoria', 'precio_venta', 'stock', 'bajo_stock', 'activo')
    list_filter   = ('categoria', 'activo')
    search_fields = ('nombre', 'referencia')

# ── Órdenes de trabajo ────────────────────
class OrdenServicioInline(admin.TabularInline):
    model  = OrdenServicio
    extra  = 1

class OrdenProductoInline(admin.TabularInline):
    model  = OrdenProducto
    extra  = 1

@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'vehiculo', 'estado', 'prioridad', 'tecnico', 'fecha_entrada', 'fecha_prometida')
    list_filter   = ('estado', 'prioridad', 'tecnico')
    search_fields = ('numero', 'vehiculo__placa', 'vehiculo__cliente__nombre')
    inlines       = [OrdenServicioInline, OrdenProductoInline]
    readonly_fields = ('numero', 'fecha_entrada')

# ── Agrandamientos ────────────────────────
class EtapaInline(admin.TabularInline):
    model = EtapaAgrandamiento
    extra = 1

@admin.register(Agrandamiento)
class AgrandamientoAdmin(admin.ModelAdmin):
    list_display  = ('orden', 'tipo', 'porcentaje_avance')
    list_filter   = ('tipo',)
    inlines       = [EtapaInline]

# ── Cotizaciones ──────────────────────────
class ItemCotizacionInline(admin.TabularInline):
    model = ItemCotizacion
    extra = 1

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'cliente', 'estado', 'creado_en')
    list_filter   = ('estado',)
    search_fields = ('numero', 'cliente__nombre', 'cliente__apellido')
    inlines       = [ItemCotizacionInline]
    readonly_fields = ('numero',)

# ── Facturas ──────────────────────────────
class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display  = ('numero', 'cliente', 'estado', 'total', 'total_pagado', 'saldo_pendiente', 'creado_en')
    list_filter   = ('estado', 'metodo_pago')
    search_fields = ('numero', 'cliente__nombre', 'cliente__apellido')
    inlines       = [PagoInline]
    readonly_fields = ('numero',)

# ── Contabilidad ──────────────────────────
@admin.register(CategoriaContable)
class CategoriaContableAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    list_filter  = ('tipo',)

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display  = ('fecha', 'tipo', 'categoria', 'descripcion', 'monto', 'proveedor')
    list_filter   = ('tipo', 'categoria', 'fecha')
    search_fields = ('descripcion', 'proveedor')

# ── Recordatorios ─────────────────────────
@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display  = ('cliente', 'tipo', 'canal', 'estado', 'programado_para')
    list_filter   = ('tipo', 'canal', 'estado')
    search_fields = ('cliente__nombre', 'cliente__apellido')

@admin.register(RegistroLlamada)
class RegistroLlamadaAdmin(admin.ModelAdmin):
    list_display  = ('cliente', 'resultado', 'realizada_por', 'fecha')
    list_filter   = ('resultado',)
    search_fields = ('cliente__nombre', 'cliente__apellido')

# ── Marketing ─────────────────────────────
@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'tipo', 'valor', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter   = ('tipo', 'activa')

@admin.register(CampanaMarketing)
class CampanaMarketingAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'red', 'presupuesto', 'gasto_real', 'impresiones', 'clics', 'activa')
    list_filter   = ('red', 'activa')

    # ── Permisos por rol ──────────────────────────────────
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model

class TallerAdminSite(AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff