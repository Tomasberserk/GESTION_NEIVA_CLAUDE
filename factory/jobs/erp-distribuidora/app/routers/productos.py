from typing import Optional, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.producto import (
    ProductoCrear,
    ProductoActualizar,
    ProductoRespuesta,
)
from app.services import producto_service
from app import models

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.get(
    "",
    response_model=List[ProductoRespuesta],
    summary="Listar todos los productos de la empresa",
)
def listar_productos(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    productos = producto_service.obtener_productos(
        empresa_id=current_user.empresa_id,
        db=db,
        q=q,
        skip=skip,
        limit=limit,
    )
    return [ProductoRespuesta.model_validate(p) for p in productos]


@router.get(
    "/{producto_id}",
    response_model=ProductoRespuesta,
    summary="Obtener detalle de un producto por ID",
)
def obtener_producto(
    producto_id: str,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(producto_id)
    producto = producto_service.obtener_producto_por_id(
        empresa_id=current_user.empresa_id,
        producto_id=p_id,
        db=db,
    )
    return ProductoRespuesta.model_validate(producto)


@router.post(
    "",
    response_model=ProductoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
)
def crear_producto(
    data: ProductoCrear,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    producto = producto_service.crear_producto(
        empresa_id=current_user.empresa_id,
        data=data,
        db=db,
    )
    return ProductoRespuesta.model_validate(producto)


@router.put(
    "/{producto_id}",
    response_model=ProductoRespuesta,
    summary="Actualizar un producto existente",
)
def actualizar_producto(
    producto_id: str,
    data: ProductoActualizar,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(producto_id)
    producto = producto_service.actualizar_producto(
        empresa_id=current_user.empresa_id,
        producto_id=p_id,
        data=data,
        db=db,
    )
    return ProductoRespuesta.model_validate(producto)


@router.delete(
    "/{producto_id}",
    summary="Dar de baja (soft-delete) un producto",
)
def eliminar_producto(
    producto_id: str,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(producto_id)
    producto_service.eliminar_producto(
        empresa_id=current_user.empresa_id,
        producto_id=p_id,
        db=db,
    )
    return {"ok": True, "message": "Producto desactivado correctamente"}
