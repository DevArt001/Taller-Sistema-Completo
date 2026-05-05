# taller/fixtures_iniciales.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from taller.models import CategoriaServicio, Servicio, CategoriaProducto

# ── Categorías de servicio ─────────────────────────────
categorias = [
    'Mantenimiento',
    'Mecánica General',
    'Electricidad y Diagnóstico',
    'Latonería y Pintura',
]

for nombre in categorias:
    cat, creado = CategoriaServicio.objects.get_or_create(nombre=nombre)
    print(f"{'✅ Creada' if creado else '⚠️  Ya existe'}: {nombre}")

# ── Servicios ──────────────────────────────────────────
servicios = [
    # (nombre, categoría, aplica_moto, aplica_carro)
    ('Cambio de Aceite',                  'Mantenimiento',              True,  True),
    ('Sincronización',                    'Mantenimiento',              True,  True),
    ('Mantenimiento Preventivo',          'Mantenimiento',              True,  True),
    ('Mantenimiento General',             'Mantenimiento',              True,  True),
    ('Mantenimiento de Freno Delantero',  'Mantenimiento',              True,  True),
    ('Mantenimiento de Freno Trasero',    'Mantenimiento',              True,  True),
    ('Mantenimiento de Cunas',            'Mecánica General',           True,  False),
    ('Mantenimiento de Tren Delantero',   'Mecánica General',           True,  True),
    ('Mantenimiento de Suspensión',       'Mecánica General',           True,  True),
    ('Cambio de Guaya de Clutch',         'Mecánica General',           True,  False),
    ('Cambio de Guaya de Acelerador',     'Mecánica General',           True,  True),
    ('Cambio de Rodamientos Ruedas',      'Mecánica General',           True,  True),
    ('Reparación Motor Completo',         'Mecánica General',           True,  True),
    ('Servicio de Escaner',               'Electricidad y Diagnóstico', True,  True),
    ('Servicio de Diagnóstico Eléctrico', 'Electricidad y Diagnóstico', True,  True),
    ('Reparación Eléctrica',              'Electricidad y Diagnóstico', True,  True),
]

for nombre, cat_nombre, moto, carro in servicios:
    cat = CategoriaServicio.objects.get(nombre=cat_nombre)
    srv, creado = Servicio.objects.get_or_create(
        nombre=nombre,
        defaults={
            'categoria':     cat,
            'precio_base':   0,
            'aplica_moto':   moto,
            'aplica_carro':  carro,
            'activo':        True,
        }
    )
    print(f"{'✅ Creado' if creado else '⚠️  Ya existe'}: {nombre}")

print("\n🏁 Datos cargados correctamente.")