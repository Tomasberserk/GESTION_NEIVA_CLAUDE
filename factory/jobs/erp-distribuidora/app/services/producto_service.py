from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.producto import ProductoCrear, ProductoActualizar


def obtener_productos(
    empresa_id: UUID,
    db: Session,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Producto]:
    query = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    )
    if q:
        q_clean = f"%{q.strip()}%"
        query = query.filter(
            models.Producto.nombre.ilike(q_clean) |
            models.Producto.codigo_barras.ilike(q_clean) |
            models.Producto.categoria.ilike(q_clean)
        )
    return query.order_by(models.Producto.nombre.asc()).offset(skip).limit(limit).all()


def obtener_producto_por_id(empresa_id: UUID, producto_id: UUID, db: Session) -> models.Producto:
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id,
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    ).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado o no pertenece a tu empresa",
        )
    return producto


def crear_producto(empresa_id: UUID, data: ProductoCrear, db: Session) -> models.Producto:
    # Validar código de barras único por empresa
    existente = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.codigo_barras == data.codigo_barras,
        models.Producto.is_active.is_(True),
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el código de barras '{data.codigo_barras}' en esta empresa",
        )

    nuevo_producto = models.Producto(
        empresa_id=empresa_id,
        nombre=data.nombre,
        codigo_barras=data.codigo_barras,
        precio_costo=data.precio_costo,
        precio_venta=data.precio_venta,
        cantidad_actual=data.cantidad_actual,
        unidad_medida=data.unidad_medida,
        categoria=data.categoria,
    )
    try:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el producto",
        ) from exc


def actualizar_producto(
    empresa_id: UUID,
    producto_id: UUID,
    data: ProductoActualizar,
    db: Session,
) -> models.Producto:
    producto = obtener_producto_por_id(empresa_id, producto_id, db)

    if data.codigo_barras and data.codigo_barras != producto.codigo_barras:
        # Validar nuevo código
        existente = db.query(models.Producto).filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.codigo_barras == data.codigo_barras,
            models.Producto.is_active.is_(True),
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto con el código de barras '{data.codigo_barras}'",
            )

    # Actualizar campos
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)

    try:
        db.commit()
        db.refresh(producto)
        return producto
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar el producto",
        ) from exc


def eliminar_producto(empresa_id: UUID, producto_id: UUID, db: Session) -> bool:
    producto = obtener_producto_por_id(empresa_id, producto_id, db)
    producto.is_active = False
    try:
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al dar de baja el producto",
        ) from exc
