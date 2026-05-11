from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{empresa_id}")
def resumen_dashboard(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Acceso no autorizado")

    hoy_inicio = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)

    ventas_hoy = db.query(func.count(models.Venta.id)).filter(
        models.Venta.empresa_id == empresa_id,
        models.Venta.fecha_venta >= hoy_inicio,
    ).scalar() or 0

    ingresos_hoy = db.query(func.sum(models.Venta.total)).filter(
        models.Venta.empresa_id == empresa_id,
        models.Venta.fecha_venta >= hoy_inicio,
    ).scalar() or 0

    stock_bajo = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
        models.Producto.cantidad_actual <= 5,
    ).all()

    total_productos = db.query(func.count(models.Producto.id)).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    ).scalar() or 0

    return {
        "ventas_hoy": ventas_hoy,
        "ingresos_hoy": float(ingresos_hoy),
        "total_productos": total_productos,
        "stock_bajo": [
            {"id": str(p.id), "nombre": p.nombre, "cantidad": p.cantidad_actual}
            for p in stock_bajo
        ],
    }
