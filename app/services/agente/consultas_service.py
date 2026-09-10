"""Consultas financieras y de inventario determinísticas para el Agente.

Todas las métricas son calculadas directamente por SQLAlchemy y PostgreSQL,
garantizando exactitud matemática, respeto a las fechas UTC y aislamiento multi-tenant.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models

# Zona horaria oficial de negocio para tiendas en Colombia (UTC-5)
try:
    TZ_COLOMBIA = ZoneInfo("America/Bogota")
except Exception:
    TZ_COLOMBIA = timezone(timedelta(hours=-5))


def _norm_uuid(val: UUID | str) -> UUID:
    if isinstance(val, UUID):
        return val
    return UUID(str(val))


def _obtener_rango_hoy() -> tuple[datetime, datetime]:
    """Calcula inicio y fin del día en hora colombiana (UTC-5) convertidos a UTC."""
    ahora_co = datetime.now(TZ_COLOMBIA)
    inicio_co = ahora_co.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_co = ahora_co.replace(hour=23, minute=59, second=59, microsecond=999999)
    return inicio_co.astimezone(timezone.utc), fin_co.astimezone(timezone.utc)


def consultar_ventas_periodo(
    empresa_id: UUID | str,
    db: Session,
    periodo: str = "hoy",
) -> dict:
    """Calcula ventas totales y cantidad de transacciones para hoy, semana o mes."""
    empresa_id = _norm_uuid(empresa_id)
    ahora_co = datetime.now(TZ_COLOMBIA)

    if periodo == "hoy":
        inicio, fin = _obtener_rango_hoy()
        label_periodo = "hoy"
    elif periodo == "semana":
        inicio_co = (ahora_co - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        inicio = inicio_co.astimezone(timezone.utc)
        fin = ahora_co.astimezone(timezone.utc)
        label_periodo = "los últimos 7 días"
    elif periodo == "mes":
        inicio_co = ahora_co.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio = inicio_co.astimezone(timezone.utc)
        fin = ahora_co.astimezone(timezone.utc)
        label_periodo = "este mes"
    else:
        inicio, fin = _obtener_rango_hoy()
        label_periodo = "hoy"

    resultado = (
        db.query(
            func.coalesce(func.sum(models.Venta.total), Decimal("0.00")),
            func.count(models.Venta.id),
        )
        .filter(
            models.Venta.empresa_id == empresa_id,
            or_(models.Venta.is_active.is_(True), models.Venta.is_active == "true"),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .first()
    )

    total_ventas = float(resultado[0]) if resultado else 0.0
    cantidad_ventas = int(resultado[1]) if resultado else 0

    return {
        "periodo": label_periodo,
        "total": total_ventas,
        "cantidad_transacciones": cantidad_ventas,
    }


def consultar_recaudo_actual(empresa_id: UUID | str, db: Session) -> dict:
    """Calcula el total de dinero recaudado por ventas en el día de hoy."""
    empresa_id = _norm_uuid(empresa_id)
    inicio, fin = _obtener_rango_hoy()

    resultado = (
        db.query(
            func.coalesce(func.sum(models.Venta.total), Decimal("0.00")),
            func.count(models.Venta.id),
        )
        .filter(
            models.Venta.empresa_id == empresa_id,
            or_(models.Venta.is_active.is_(True), models.Venta.is_active == "true"),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .first()
    )

    return {
        "recaudo_hoy": float(resultado[0]) if resultado else 0.0,
        "cantidad_ventas": int(resultado[1]) if resultado else 0,
    }


def consultar_total_inventario(empresa_id: UUID | str, db: Session) -> dict:
    """Calcula cantidad de SKUs y valorización estimada a precio de costo."""
    empresa_id = _norm_uuid(empresa_id)
    resultado = (
        db.query(
            func.count(models.Producto.id),
            func.coalesce(
                func.sum(models.Producto.cantidad_actual * models.Producto.precio_costo),
                Decimal("0.00"),
            ),
        )
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
        )
        .first()
    )

    total_productos = int(resultado[0]) if resultado else 0
    valor_costo = float(resultado[1]) if resultado else 0.0

    return {
        "total_productos": total_productos,
        "valor_total_costo": valor_costo,
    }


def consultar_stock_producto(producto_id: UUID | str, empresa_id: UUID | str, db: Session) -> dict | None:
    """Obtiene stock y precio de un producto específico."""
    empresa_id = _norm_uuid(empresa_id)
    producto_id = _norm_uuid(producto_id)
    prod = (
        db.query(models.Producto)
        .filter(
            models.Producto.id == producto_id,
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
        )
        .first()
    )
    if not prod:
        return None

    unidad = prod.unidad_medida.value if prod.unidad_medida else "unidad"
    return {
        "id": str(prod.id),
        "nombre": prod.nombre,
        "cantidad_actual": float(prod.cantidad_actual),
        "precio_venta": float(prod.precio_venta),
        "unidad": unidad,
    }


def consultar_resumen_actual(empresa_id: UUID | str, db: Session) -> dict:
    """Dashboard rápido: ventas hoy, productos en stock bajo y productos por vencer."""
    empresa_id = _norm_uuid(empresa_id)
    inicio, fin = _obtener_rango_hoy()

    # Ventas hoy
    res_ventas = (
        db.query(
            func.coalesce(func.sum(models.Venta.total), Decimal("0.00")),
            func.count(models.Venta.id),
        )
        .filter(
            models.Venta.empresa_id == empresa_id,
            or_(models.Venta.is_active.is_(True), models.Venta.is_active == "true"),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .first()
    )

    # Stock bajo (<= 5 unidades)
    stock_bajo = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.cantidad_actual <= Decimal("5.00"),
        )
        .scalar()
        or 0
    )

    # Productos por vencer en los próximos 15 días
    hoy_date = datetime.now(timezone.utc).date()
    limite_vencimiento = hoy_date + timedelta(days=15)
    por_vencer = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.fecha_vencimiento.isnot(None),
            models.Producto.fecha_vencimiento <= limite_vencimiento,
        )
        .scalar()
        or 0
    )

    return {
        "ventas_hoy": float(res_ventas[0]) if res_ventas else 0.0,
        "cantidad_ventas_hoy": int(res_ventas[1]) if res_ventas else 0,
        "productos_stock_bajo": stock_bajo,
        "productos_por_vencer": por_vencer,
    }


def consultar_recuperacion_inversion(empresa_id: UUID | str, db: Session) -> dict:
    """Provee datos reales de inventario y ventas; no inventa cifras de ROI si falta capital inicial."""
    empresa_id = _norm_uuid(empresa_id)
    inv = consultar_total_inventario(empresa_id, db)
    ventas = consultar_ventas_periodo(empresa_id, db, periodo="hoy")

    return {
        "inventario_costo": inv["valor_total_costo"],
        "ventas_hoy": ventas["total"],
        "tiene_capital_inicial": False,
    }
