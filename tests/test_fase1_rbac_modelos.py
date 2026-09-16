import uuid
from datetime import datetime, timezone
from decimal import Decimal
import pytest

from app import models
from app.schemas.producto import ProductoAdminOut, ProductoCajeroOut, ProductoRespuesta
from app.schemas.usuario import UsuarioCrear, UsuarioRespuesta
from app.schemas.venta import VentaRespuesta


def test_modelos_columnas_y_atributos():
    """Verifica que los modelos SQLAlchemy tengan las nuevas columnas y relaciones."""
    usuario_cols = {c.name for c in models.Usuario.__table__.columns}
    assert "nombre" in usuario_cols, "La columna 'nombre' debe existir en la tabla usuarios"

    venta_cols = {c.name for c in models.Venta.__table__.columns}
    assert "usuario_id" in venta_cols, "La columna 'usuario_id' debe existir en la tabla ventas"
    assert "vendedor_nombre_snapshot" in venta_cols, "La columna 'vendedor_nombre_snapshot' debe existir en la tabla ventas"

    # Verificar relaciones bidireccionales
    assert hasattr(models.Usuario, "ventas"), "Usuario debe tener la relacion 'ventas'"
    assert hasattr(models.Venta, "usuario"), "Venta debe tener la relacion 'usuario'"


def test_trazabilidad_historica_snapshot_permanente():
    """
    Verifica que el snapshot del vendedor permanezca intacto
    incluso si el usuario es desligado (usuario_id = NULL).
    """
    empresa_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    venta_id = uuid.uuid4()

    # Venta creada con snapshot
    venta = models.Venta(
        id=venta_id,
        empresa_id=empresa_id,
        total=Decimal("12400.00"),
        usuario_id=usuario_id,
        vendedor_nombre_snapshot="Paula Cajera",
    )

    assert venta.usuario_id == usuario_id
    assert venta.vendedor_nombre_snapshot == "Paula Cajera"

    # Simular desligamiento o eliminacion del usuario (ON DELETE SET NULL)
    venta.usuario_id = None

    # La evidencia historica no se pierde
    assert venta.usuario_id is None
    assert venta.vendedor_nombre_snapshot == "Paula Cajera"


def test_schemas_producto_admin_incluye_costo():
    """ProductoAdminOut debe incluir precio_costo y margen."""
    producto_data = {
        "id": uuid.uuid4(),
        "empresa_id": uuid.uuid4(),
        "nombre": "Papas Fritas 100g",
        "codigo_barras": "770123456789",
        "precio_costo": 1500.0,
        "precio_venta": 2500.0,
        "cantidad_actual": 20.0,
        "unidad_medida": "unidad",
        "fecha_vencimiento": None,
        "categoria": "Snacks",
        "foto_url": None,
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    out_admin = ProductoAdminOut.model_validate(producto_data)
    dump_admin = out_admin.model_dump()

    assert "precio_costo" in dump_admin
    assert dump_admin["precio_costo"] == 1500.0
    assert dump_admin["precio_venta"] == 2500.0


def test_schemas_producto_cajero_no_expone_costo():
    """
    ProductoCajeroOut NUNCA debe contener la clave precio_costo
    bajo ninguna circunstancia (evitando fuga accidental a DevTools o red).
    """
    producto_data = {
        "id": uuid.uuid4(),
        "empresa_id": uuid.uuid4(),
        "nombre": "Papas Fritas 100g",
        "codigo_barras": "770123456789",
        "precio_costo": 1500.0,  # El diccionario interno contiene el costo
        "precio_venta": 2500.0,
        "cantidad_actual": 20.0,
        "unidad_medida": "unidad",
        "fecha_vencimiento": None,
        "categoria": "Snacks",
        "foto_url": None,
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    out_cajero = ProductoCajeroOut.model_validate(producto_data)
    dump_cajero = out_cajero.model_dump()

    # REGLA SAGRADA: Cero presencia de precio_costo
    assert "precio_costo" not in dump_cajero, "ProductoCajeroOut NUNCA debe exponer precio_costo"
    assert dump_cajero["precio_venta"] == 2500.0
    assert dump_cajero["nombre"] == "Papas Fritas 100g"


def test_retrocompatibilidad_ventas_historicas_nulas():
    """
    Ventas historicas existentes con usuario_id y snapshot nulos
    deben serializar limpiamente sin lanzar ValidationError.
    """
    venta_historica = {
        "id": uuid.uuid4(),
        "empresa_id": uuid.uuid4(),
        "fecha_venta": datetime.now(timezone.utc),
        "total": 50000.0,
        "usuario_id": None,
        "vendedor_nombre_snapshot": None,
        "detalles": [],
    }

    resp = VentaRespuesta.model_validate(venta_historica)
    dump = resp.model_dump()

    assert dump["usuario_id"] is None
    assert dump["vendedor_nombre_snapshot"] is None
    assert dump["total"] == 50000.0


def test_schemas_usuario_soporta_nombre_opcional():
    """UsuarioCrear y UsuarioRespuesta soportan el campo nombre."""
    empresa_id = uuid.uuid4()
    user_in = UsuarioCrear(
        nombre="Paula Andrea",
        email="paula@tienda.com",
        password="Password123!",
        empresa_id=empresa_id,
    )
    assert user_in.nombre == "Paula Andrea"

    user_out = UsuarioRespuesta(
        id=uuid.uuid4(),
        nombre="Paula Andrea",
        email="paula@tienda.com",
        empresa_id=empresa_id,
        rol=models.RolUsuario.TENDERO,
        created_at=datetime.now(timezone.utc),
        is_active=True,
    )
    assert user_out.nombre == "Paula Andrea"
