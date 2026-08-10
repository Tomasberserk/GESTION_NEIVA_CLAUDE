from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.dashboard import DashboardRespuesta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{empresa_id}", response_model=DashboardRespuesta)
def resumen_dashboard(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado",
        )

    hoy = date.today()
    hoy_inicio = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=timezone.utc)

    # --- Métricas básicas ---
    ventas_hoy = db.query(func.count(models.Venta.id)).filter(
        models.Venta.empresa_id == empresa_id,
        models.Venta.fecha_venta >= hoy_inicio,
    ).scalar() or 0

    ingresos_hoy = db.query(func.sum(models.Venta.total)).filter(
        models.Venta.empresa_id == empresa_id,
        models.Venta.fecha_venta >= hoy_inicio,
    ).scalar() or 0

    total_productos = db.query(func.count(models.Producto.id)).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    ).scalar() or 0

    stock_bajo = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
        models.Producto.cantidad_actual <= 5,
    ).all()

    # --- Top 5 productos más vendidos ---
    # JOIN Producto → DetalleVenta, filtra por empresa, agrupa y ordena por suma desc
    top_rows = (
        db.query(
            models.Producto.nombre,
            func.sum(models.DetalleVenta.cantidad).label("total_vendido"),
        )
        .join(models.DetalleVenta, models.DetalleVenta.producto_id == models.Producto.id)
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        )
        .group_by(models.Producto.id, models.Producto.nombre)
        .order_by(func.sum(models.DetalleVenta.cantidad).desc())
        .limit(5)
        .all()
    )

    # --- Alertas de vencimiento (próximos 15 días) ---
    limite_vencimiento = hoy + timedelta(days=15)
    proximos_a_vencer = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
            models.Producto.fecha_vencimiento.isnot(None),
            models.Producto.fecha_vencimiento <= limite_vencimiento,
        )
        .order_by(models.Producto.fecha_vencimiento)
        .all()
    )

    # --- Trial info ---
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
    ).first()

    dias_trial_restantes = None
    if empresa and empresa.trial_expires_at:
        trial_dt = empresa.trial_expires_at
        if trial_dt.tzinfo is None:
            trial_dt = trial_dt.replace(tzinfo=timezone.utc)
        delta = trial_dt - datetime.now(timezone.utc)
        dias_trial_restantes = max(0, delta.days)

    return {
        "ventas_hoy": ventas_hoy,
        "ingresos_hoy": float(ingresos_hoy),
        "total_productos": total_productos,
        "stock_bajo": [
            {"id": str(p.id), "nombre": p.nombre, "cantidad": float(p.cantidad_actual)}
            for p in stock_bajo
        ],
        "top_productos": [
            {"nombre": row.nombre, "total_vendido": float(row.total_vendido)}
            for row in top_rows
        ],
        "alertas_vencimiento": [
            {
                "id": str(p.id),
                "nombre": p.nombre,
                "fecha_vencimiento": p.fecha_vencimiento,
                "dias_restantes": (p.fecha_vencimiento - hoy).days,
            }
            for p in proximos_a_vencer
        ],
        "dias_trial_restantes": dias_trial_restantes,
        "plan": empresa.plan.value if empresa else "basic",
    }
