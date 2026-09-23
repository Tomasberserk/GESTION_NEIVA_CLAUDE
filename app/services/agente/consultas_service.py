"""Consultas financieras y de inventario determinísticas para el Agente.

Todas las métricas son calculadas directamente por SQLAlchemy y PostgreSQL/SQLite,
garantizando exactitud matemática, respeto a las fechas UTC y aislamiento multi-tenant.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any
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
    """Calcula inicio y fin del día actual en hora colombiana (UTC-5) convertidos a UTC."""
    ahora_co = datetime.now(TZ_COLOMBIA)
    inicio_co = ahora_co.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_co = ahora_co.replace(hour=23, minute=59, second=59, microsecond=999999)
    return inicio_co.astimezone(timezone.utc), fin_co.astimezone(timezone.utc)


def _obtener_rango_ayer() -> tuple[datetime, datetime]:
    """Calcula inicio y fin del día de ayer en hora colombiana (UTC-5) convertidos a UTC."""
    ahora_co = datetime.now(TZ_COLOMBIA)
    ayer_co = ahora_co - timedelta(days=1)
    inicio_co = ayer_co.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_co = ayer_co.replace(hour=23, minute=59, second=59, microsecond=999999)
    return inicio_co.astimezone(timezone.utc), fin_co.astimezone(timezone.utc)


def _obtener_rango_semana() -> tuple[datetime, datetime]:
    """Calcula rango de los últimos 7 días en hora colombiana convertidos a UTC."""
    ahora_co = datetime.now(TZ_COLOMBIA)
    inicio_co = (ahora_co - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio_co.astimezone(timezone.utc), ahora_co.astimezone(timezone.utc)


def _obtener_rango_mes() -> tuple[datetime, datetime]:
    """Calcula rango desde el inicio del mes actual en hora colombiana convertidos a UTC."""
    ahora_co = datetime.now(TZ_COLOMBIA)
    inicio_co = ahora_co.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return inicio_co.astimezone(timezone.utc), ahora_co.astimezone(timezone.utc)


def consultar_ventas_periodo(
    empresa_id: UUID | str,
    db: Session,
    periodo: str = "hoy",
    usuario_id: UUID | str | None = None,
) -> dict[str, Any]:
    """Calcula ventas totales y cantidad de transacciones para hoy, ayer, semana o mes."""
    empresa_id = _norm_uuid(empresa_id)

    periodo_norm = (periodo or "hoy").lower().strip()
    if periodo_norm in ["ayer", "dia_anterior"]:
        inicio, fin = _obtener_rango_ayer()
        label_periodo = "ayer"
    elif periodo_norm in ["semana", "ultimos_7_dias", "semanal"]:
        inicio, fin = _obtener_rango_semana()
        label_periodo = "los últimos 7 días"
    elif periodo_norm in ["mes", "mensual"]:
        inicio, fin = _obtener_rango_mes()
        label_periodo = "este mes"
    else:
        inicio, fin = _obtener_rango_hoy()
        label_periodo = "hoy"

    query = (
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
    )

    if usuario_id:
        query = query.filter(models.Venta.usuario_id == _norm_uuid(usuario_id))

    resultado = query.first()

    total_ventas = float(resultado[0]) if resultado else 0.0
    cantidad_ventas = int(resultado[1]) if resultado else 0

    return {
        "periodo": label_periodo,
        "total": total_ventas,
        "cantidad_transacciones": cantidad_ventas,
    }


def consultar_ventas_vendedor(
    empresa_id: UUID | str,
    db: Session,
    vendedor_query: str,
    periodo: str = "hoy",
    current_user_id: UUID | str | None = None,
) -> dict[str, Any]:
    """Calcula ventas de un cajero o vendedor específico por su nombre o 'yo'."""
    empresa_id = _norm_uuid(empresa_id)
    query_clean = vendedor_query.strip().lower()

    target_user = None
    if query_clean in ["yo", "mi", "mis", "mías", "mias"]:
        if current_user_id:
            target_user = db.query(models.Usuario).filter(
                models.Usuario.id == _norm_uuid(current_user_id),
                models.Usuario.empresa_id == empresa_id,
            ).first()
    else:
        # Búsqueda por nombre en los usuarios de la empresa
        usuarios = db.query(models.Usuario).filter(
            models.Usuario.empresa_id == empresa_id,
            models.Usuario.is_active.is_(True),
        ).all()
        for u in usuarios:
            nom = (u.nombre or u.email or "").lower()
            # Si el query está contenido en el nombre o viceversa
            if query_clean in nom or any(token in nom.split() for token in query_clean.split()):
                target_user = u
                break

    if not target_user:
        return {
            "encontrado": False,
            "vendedor": vendedor_query,
            "periodo": periodo,
            "total": 0.0,
            "cantidad_transacciones": 0,
        }

    res = consultar_ventas_periodo(
        empresa_id=empresa_id,
        db=db,
        periodo=periodo,
        usuario_id=target_user.id,
    )
    res["encontrado"] = True
    res["vendedor"] = target_user.nombre or vendedor_query
    res["vendedor_id"] = str(target_user.id)
    return res


def consultar_recaudo_actual(empresa_id: UUID | str, db: Session) -> dict[str, Any]:
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


def consultar_total_inventario(empresa_id: UUID | str, db: Session) -> dict[str, Any]:
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


def consultar_stock_producto(producto_id: UUID | str, empresa_id: UUID | str, db: Session) -> dict[str, Any] | None:
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

    unidad = prod.unidad_medida.value if hasattr(prod.unidad_medida, "value") else str(prod.unidad_medida or "unidad")
    return {
        "id": str(prod.id),
        "nombre": prod.nombre,
        "cantidad_actual": float(prod.cantidad_actual),
        "precio_venta": float(prod.precio_venta),
        "unidad": unidad,
    }


def consultar_productos_agotados(empresa_id: UUID | str, db: Session, limite: int = 10) -> dict[str, Any]:
    """Retorna los productos con stock en cero (agotados)."""
    empresa_id = _norm_uuid(empresa_id)
    prods = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.cantidad_actual <= Decimal("0.00"),
        )
        .order_by(models.Producto.nombre.asc())
        .limit(limite)
        .all()
    )

    total_count = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.cantidad_actual <= Decimal("0.00"),
        )
        .scalar()
        or 0
    )

    items = [
        {
            "id": str(p.id),
            "nombre": p.nombre,
            "cantidad_actual": float(p.cantidad_actual),
            "precio_venta": float(p.precio_venta),
            "unidad": p.unidad_medida.value if hasattr(p.unidad_medida, "value") else str(p.unidad_medida or "unidad"),
        }
        for p in prods
    ]

    return {
        "total_agotados": total_count,
        "productos": items,
    }


def consultar_productos_stock_bajo(
    empresa_id: UUID | str,
    db: Session,
    umbral: float = 5.0,
    limite: int = 10,
) -> dict[str, Any]:
    """Retorna productos con stock positivo pero crítico (menor o igual a umbral)."""
    empresa_id = _norm_uuid(empresa_id)
    umbral_dec = Decimal(str(umbral))

    prods = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.cantidad_actual > Decimal("0.00"),
            models.Producto.cantidad_actual <= umbral_dec,
        )
        .order_by(models.Producto.cantidad_actual.asc())
        .limit(limite)
        .all()
    )

    total_count = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.cantidad_actual > Decimal("0.00"),
            models.Producto.cantidad_actual <= umbral_dec,
        )
        .scalar()
        or 0
    )

    items = [
        {
            "id": str(p.id),
            "nombre": p.nombre,
            "cantidad_actual": float(p.cantidad_actual),
            "precio_venta": float(p.precio_venta),
            "unidad": p.unidad_medida.value if hasattr(p.unidad_medida, "value") else str(p.unidad_medida or "unidad"),
        }
        for p in prods
    ]

    return {
        "total_stock_bajo": total_count,
        "umbral": umbral,
        "productos": items,
    }


def consultar_conteo_productos_activos(empresa_id: UUID | str, db: Session) -> dict[str, Any]:
    """Calcula el total de productos activos en el catálogo de la tienda."""
    empresa_id = _norm_uuid(empresa_id)
    total_prods = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
        )
        .scalar()
        or 0
    )
    return {
        "total_activos": total_prods,
    }


def consultar_productos_mas_vendidos(
    empresa_id: UUID | str,
    db: Session,
    periodo: str = "hoy",
    limite: int = 5,
) -> dict[str, Any]:
    """Calcula los productos con mayor volumen de venta sumando DetalleVenta agrupado."""
    empresa_id = _norm_uuid(empresa_id)
    periodo_norm = (periodo or "hoy").lower().strip()

    if periodo_norm in ["ayer", "dia_anterior"]:
        inicio, fin = _obtener_rango_ayer()
        label_periodo = "ayer"
    elif periodo_norm in ["semana", "ultimos_7_dias", "semanal"]:
        inicio, fin = _obtener_rango_semana()
        label_periodo = "la semana"
    elif periodo_norm in ["mes", "mensual"]:
        inicio, fin = _obtener_rango_mes()
        label_periodo = "este mes"
    else:
        inicio, fin = _obtener_rango_hoy()
        label_periodo = "hoy"

    filas = (
        db.query(
            models.Producto.id,
            models.Producto.nombre,
            func.sum(models.DetalleVenta.cantidad).label("unidades_vendidas"),
            func.sum(models.DetalleVenta.subtotal).label("total_facturado"),
        )
        .join(models.DetalleVenta, models.DetalleVenta.producto_id == models.Producto.id)
        .join(models.Venta, models.Venta.id == models.DetalleVenta.venta_id)
        .filter(
            models.Venta.empresa_id == empresa_id,
            or_(models.Venta.is_active.is_(True), models.Venta.is_active == "true"),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .group_by(models.Producto.id, models.Producto.nombre)
        .order_by(func.sum(models.DetalleVenta.cantidad).desc())
        .limit(limite)
        .all()
    )

    items = [
        {
            "producto_id": str(f[0]),
            "nombre": f[1],
            "unidades_vendidas": float(f[2]) if f[2] else 0.0,
            "total_facturado": float(f[3]) if f[3] else 0.0,
        }
        for f in filas
    ]

    return {
        "periodo": label_periodo,
        "total_items": len(items),
        "productos": items,
        "top_1": items[0] if items else None,
    }


def consultar_comparacion_ventas_periodo(
    empresa_id: UUID | str,
    db: Session,
    periodo_a: str = "hoy",
    periodo_b: str = "ayer",
) -> dict[str, Any]:
    """Compara determinísticamente las ventas entre dos períodos (ej: hoy vs ayer)."""
    empresa_id = _norm_uuid(empresa_id)
    datos_a = consultar_ventas_periodo(empresa_id, db, periodo=periodo_a)
    datos_b = consultar_ventas_periodo(empresa_id, db, periodo=periodo_b)

    total_a = datos_a["total"]
    total_b = datos_b["total"]
    diferencia = total_a - total_b

    porcentaje = 0.0
    if total_b > 0:
        porcentaje = round(((total_a - total_b) / total_b) * 100.0, 1)
    elif total_a > 0:
        porcentaje = 100.0

    return {
        "periodo_a": datos_a["periodo"],
        "total_a": total_a,
        "transacciones_a": datos_a["cantidad_transacciones"],
        "periodo_b": datos_b["periodo"],
        "total_b": total_b,
        "transacciones_b": datos_b["cantidad_transacciones"],
        "diferencia": diferencia,
        "porcentaje_cambio": porcentaje,
        "mayor": "a" if total_a > total_b else ("b" if total_b > total_a else "igual"),
    }


def consultar_comparacion_vendedores(
    empresa_id: UUID | str,
    db: Session,
    periodo: str = "hoy",
) -> dict[str, Any]:
    """Compara las ventas registradas por todos los cajeros en el período."""
    empresa_id = _norm_uuid(empresa_id)
    cajeros = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.empresa_id == empresa_id,
            models.Usuario.is_active.is_(True),
        )
        .all()
    )

    ranking = []
    for c in cajeros:
        res = consultar_ventas_periodo(empresa_id, db, periodo=periodo, usuario_id=c.id)
        ranking.append({
            "usuario_id": str(c.id),
            "nombre": c.nombre or c.email,
            "rol": c.rol,
            "total": res["total"],
            "transacciones": res["cantidad_transacciones"],
        })

    ranking.sort(key=lambda x: x["total"], reverse=True)

    return {
        "periodo": periodo,
        "ranking": ranking,
        "lider": ranking[0] if ranking and ranking[0]["total"] > 0 else None,
    }


def consultar_resumen_actual(empresa_id: UUID | str, db: Session) -> dict[str, Any]:
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


def consultar_recuperacion_inversion(empresa_id: UUID | str, db: Session) -> dict[str, Any]:
    """Provee datos reales de inventario y ventas; no inventa cifras de ROI si falta capital inicial."""
    empresa_id = _norm_uuid(empresa_id)
    inv = consultar_total_inventario(empresa_id, db)
    ventas = consultar_ventas_periodo(empresa_id, db, periodo="hoy")

    return {
        "inventario_costo": inv["valor_total_costo"],
        "ventas_hoy": ventas["total"],
        "tiene_capital_inicial": False,
    }


def consultar_productos_proximos_vencer(
    empresa_id: UUID | str,
    db: Session,
    dias: int = 30,
    limite: int = 10,
) -> dict[str, Any]:
    """Consulta productos con fecha de vencimiento próxima o ya vencidos."""
    empresa_id = _norm_uuid(empresa_id)
    hoy_date = datetime.now(timezone.utc).date()
    limite_fecha = hoy_date + timedelta(days=dias)

    prods = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            or_(models.Producto.is_active.is_(True), models.Producto.is_active == "true"),
            models.Producto.fecha_vencimiento.isnot(None),
            models.Producto.fecha_vencimiento <= limite_fecha,
        )
        .order_by(models.Producto.fecha_vencimiento.asc())
        .limit(limite)
        .all()
    )

    items = []
    for p in prods:
        dias_restantes = (p.fecha_vencimiento - hoy_date).days
        items.append({
            "id": str(p.id),
            "nombre": p.nombre,
            "cantidad_actual": float(p.cantidad_actual),
            "unidad": p.unidad_medida.value if hasattr(p.unidad_medida, "value") else str(p.unidad_medida or "unidad"),
            "fecha_vencimiento": str(p.fecha_vencimiento),
            "dias_restantes": dias_restantes,
            "esta_vencido": dias_restantes < 0,
        })

    return {
        "total_proximos_vencer": len(items),
        "dias_horizonte": dias,
        "productos": items,
    }
