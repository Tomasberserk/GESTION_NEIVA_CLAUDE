"""POS sales service orchestrating atomic checkout through module facades."""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.auth_tenancy.api.facade import AuthTenancyFacade
from app.inventario.api.facade import InventarioFacade
from app.schemas.venta import VentaCrear, VentaResumen

try:
    COLOMBIA_TZ = ZoneInfo("America/Bogota")
except Exception:
    COLOMBIA_TZ = timezone(timedelta(hours=-5))


def registrar_venta(
    empresa_id: UUID,
    data: VentaCrear,
    current_user: models.Usuario,
    db: Session,
    commit: bool = True,
) -> VentaResumen:
    """
    Register a complete POS sale within a single ACID transaction.

    Delegates row locking and stock deduction to InventarioFacade to enforce
    strict module boundary isolation (ADR-001, ADR-003, ARC-04).
    """
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para operar en esta empresa",
        )

    nueva_venta = models.Venta(
        empresa_id=empresa_id,
        total=Decimal("0.00"),
        fecha_venta=datetime.now(COLOMBIA_TZ),
        is_active=True,
        usuario_id=current_user.id,
        vendedor_nombre_snapshot=current_user.nombre or current_user.email,
    )
    db.add(nueva_venta)
    db.flush()

    total_venta = Decimal("0.00")

    try:
        for item in data.detalles:
            stock_dto = InventarioFacade.validar_y_descontar_stock_atomic(
                empresa_id=empresa_id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                db=db,
            )
            total_venta += stock_dto.subtotal

            detalle = models.DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=stock_dto.precio_unitario,
                subtotal=stock_dto.subtotal,
            )
            db.add(detalle)

        nueva_venta.total = total_venta

        if commit:
            db.commit()
        else:
            db.flush()

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la venta",
        ) from exc

    return VentaResumen(
        mensaje="Venta registrada exitosamente",
        total=float(total_venta),
        venta_id=nueva_venta.id,
    )


def obtener_ventas_empresa(
    empresa_id: UUID,
    db: Session,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
) -> list:
    """Return sales history for an active company within the requested date range."""
    AuthTenancyFacade.ensure_active_company(empresa_id=empresa_id, db=db)

    ahora = datetime.now(timezone.utc)
    inicio = fecha_inicio or (ahora - timedelta(days=30))
    fin = fecha_fin or ahora

    return (
        db.query(models.Venta)
        .filter(
            models.Venta.empresa_id == empresa_id,
            models.Venta.is_active.is_(True),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .options(
            joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto)
        )
        .order_by(models.Venta.fecha_venta.desc())
        .all()
    )


def obtener_actividad_ventas(
    admin_user: models.Usuario,
    db: Session,
    fecha: Optional[str] = None,
    usuario_id: Optional[UUID] = None,
) -> list[models.Venta]:
    """
    Return chronological LIFO sales activity for a commercial day in Colombia (America/Bogota).
    """
    if not fecha:
        fecha_dt = datetime.now(COLOMBIA_TZ).date()
    else:
        try:
            fecha_dt = date.fromisoformat(fecha)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use YYYY-MM-DD",
            ) from exc

    inicio = datetime.combine(fecha_dt, time.min, tzinfo=COLOMBIA_TZ)
    fin = inicio + timedelta(days=1)

    if usuario_id:
        AuthTenancyFacade.ensure_company_seller(
            usuario_id=usuario_id,
            empresa_id=admin_user.empresa_id,
            db=db,
        )

    query = (
        db.query(models.Venta)
        .options(
            joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto)
        )
        .filter(
            models.Venta.empresa_id == admin_user.empresa_id,
            models.Venta.is_active.is_(True),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta < fin,
        )
    )

    if usuario_id:
        query = query.filter(models.Venta.usuario_id == usuario_id)

    return query.order_by(models.Venta.fecha_venta.desc(), models.Venta.id.desc()).all()
