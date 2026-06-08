from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.erp import ProveedorCrear, ProveedorActualizar


def obtener_proveedores(
    empresa_id: UUID,
    db: Session,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Proveedor]:
    query = db.query(models.Proveedor).filter(
        models.Proveedor.empresa_id == empresa_id,
        models.Proveedor.is_active.is_(True),
    )
    if q:
        q_clean = f"%{q.strip()}%"
        query = query.filter(
            models.Proveedor.razon_social.ilike(q_clean) |
            models.Proveedor.nit_o_cedula.ilike(q_clean) |
            models.Proveedor.contacto_nombre.ilike(q_clean)
        )
    return query.order_by(models.Proveedor.razon_social.asc()).offset(skip).limit(limit).all()


def obtener_proveedor_por_id(empresa_id: UUID, proveedor_id: UUID, db: Session) -> models.Proveedor:
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id == proveedor_id,
        models.Proveedor.empresa_id == empresa_id,
        models.Proveedor.is_active.is_(True),
    ).first()
    if not proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado o no pertenece a tu empresa",
        )
    return proveedor


def crear_proveedor(empresa_id: UUID, data: ProveedorCrear, db: Session) -> models.Proveedor:
    # Validar NIT único por empresa
    existente = db.query(models.Proveedor).filter(
        models.Proveedor.empresa_id == empresa_id,
        models.Proveedor.nit_o_cedula == data.nit_o_cedula,
        models.Proveedor.is_active.is_(True),
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el NIT o Cédula '{data.nit_o_cedula}' en esta empresa",
        )

    nuevo_proveedor = models.Proveedor(
        empresa_id=empresa_id,
        nit_o_cedula=data.nit_o_cedula,
        razon_social=data.razon_social,
        contacto_nombre=data.contacto_nombre,
        telefono=data.telefono,
        email=data.email,
        direccion=data.direccion,
        is_active=True,
    )
    try:
        db.add(nuevo_proveedor)
        db.commit()
        db.refresh(nuevo_proveedor)
        return nuevo_proveedor
    except Exception as exc:
        db.rollback()
        # Detectar si es un error de restricción única
        error_str = str(exc).lower()
        if "unique" in error_str or "constraint" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un proveedor con el NIT o Cédula '{data.nit_o_cedula}' en esta empresa",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al registrar el proveedor",
        ) from exc


def actualizar_proveedor(
    empresa_id: UUID,
    proveedor_id: UUID,
    data: ProveedorActualizar,
    db: Session,
) -> models.Proveedor:
    proveedor = obtener_proveedor_por_id(empresa_id, proveedor_id, db)

    if data.nit_o_cedula and data.nit_o_cedula != proveedor.nit_o_cedula:
        # Validar nuevo NIT
        existente = db.query(models.Proveedor).filter(
            models.Proveedor.empresa_id == empresa_id,
            models.Proveedor.nit_o_cedula == data.nit_o_cedula,
            models.Proveedor.is_active.is_(True),
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un proveedor con el NIT o Cédula '{data.nit_o_cedula}'",
            )

    # Actualizar campos
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(proveedor, campo, valor)

    try:
        db.commit()
        db.refresh(proveedor)
        return proveedor
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar el proveedor",
        ) from exc


def eliminar_proveedor(empresa_id: UUID, proveedor_id: UUID, db: Session) -> bool:
    proveedor = obtener_proveedor_por_id(empresa_id, proveedor_id, db)

    # Validar si tiene compras activas
    compras_activas = db.query(models.Compra).filter(
        models.Compra.proveedor_id == proveedor_id,
        models.Compra.is_active.is_(True),
    ).first()
    if compras_activas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el proveedor porque tiene facturas de compra registradas",
        )

    proveedor.is_active = False
    try:
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al dar de baja el proveedor",
        ) from exc
