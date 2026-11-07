"""Internal domain operations for product locking and stock management."""
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.inventario.api.contracts import StockDeductionResultDTO


def lock_and_deduct_stock(
    empresa_id: UUID,
    producto_id: UUID,
    cantidad: Decimal,
    db: Session,
) -> StockDeductionResultDTO:
    """Acquire row lock on product, verify available stock, and deduct quantity atomically."""
    producto = (
        db.query(models.Producto)
        .filter(
            models.Producto.id == producto_id,
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
                f"Producto '{producto_id}' no encontrado "
                "o no pertenece a esta empresa"
            ),
        )

    if producto.cantidad_actual < cantidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {producto.cantidad_actual}, "
                f"Solicitado: {cantidad}"
            ),
        )

    producto.cantidad_actual -= cantidad
    subtotal = producto.precio_venta * cantidad

    return StockDeductionResultDTO(
        producto_id=producto.id,
        nombre=producto.nombre,
        precio_unitario=producto.precio_venta,
        cantidad_descontada=cantidad,
        subtotal=subtotal,
        stock_restante=producto.cantidad_actual,
    )
