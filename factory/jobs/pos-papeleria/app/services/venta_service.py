from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schemas.venta import VentaCrear, VentaResumen


def registrar_venta(
    empresa_id: UUID,
    data: VentaCrear,
    current_user: models.Usuario,
    db: Session,
) -> VentaResumen:
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para operar en esta empresa",
        )

    # usuario_id es obligatorio en Venta — registra el cajero que procesó la venta
    nueva_venta = models.Venta(
        empresa_id=empresa_id,
        usuario_id=current_user.id,
        total=Decimal("0.00"),
    )
    db.add(nueva_venta)
    db.flush()

    total_venta = Decimal("0.00")

    try:
        for item in data.items:
            producto = (
                db.query(models.Producto)
                .filter(
                    models.Producto.id == item.producto_id,
                    models.Producto.empresa_id == empresa_id,
                    models.Producto.is_active.is_(True),
                )
                .with_for_update()
                .first()
            )

            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Producto '{item.producto_id}' no encontrado "
                        "o no pertenece a esta empresa"
                    ),
                )

            if producto.cantidad_actual < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.cantidad_actual}, "
                        f"Solicitado: {item.cantidad}"
                    ),
                )

            producto.cantidad_actual -= item.cantidad

            subtotal = producto.precio_venta * item.cantidad
            total_venta += subtotal

            detalle = models.DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio_venta,
                subtotal=subtotal,
            )
            db.add(detalle)

        nueva_venta.total = total_venta
        db.commit()

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
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
) -> list:
    if not db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.is_active.is_(True),
    ).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    ahora = datetime.now(timezone.utc)
    inicio = desde or (ahora - timedelta(days=30))
    fin    = hasta or ahora

    return (
        db.query(models.Venta)
        .filter(
            models.Venta.empresa_id == empresa_id,
            models.Venta.is_active.is_(True),
            models.Venta.fecha_venta >= inicio,
            models.Venta.fecha_venta <= fin,
        )
        .options(
            joinedload(models.Venta.usuario),
            joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto),
        )
        .order_by(models.Venta.fecha_venta.desc())
        .all()
    )
