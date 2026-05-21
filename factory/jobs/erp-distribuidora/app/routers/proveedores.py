from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.proveedor import (
    ProveedorCrear,
    ProveedorActualizar,
    ProveedorRespuesta,
)
from app.services import proveedor_service
from app import models

router = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])


@router.get(
    "",
    summary="Listar y buscar proveedores de forma paginada",
)
def listar_proveedores(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Obtener proveedores filtrados
    proveedores = proveedor_service.obtener_proveedores(
        empresa_id=current_user.empresa_id,
        db=db,
        q=q,
        skip=skip,
        limit=limit,
    )
    
    # Contar total con los mismos filtros
    query = db.query(models.Proveedor).filter(
        models.Proveedor.empresa_id == current_user.empresa_id,
        models.Proveedor.is_active.is_(True),
    )
    if q:
        q_clean = f"%{q.strip()}%"
        query = query.filter(
            models.Proveedor.razon_social.ilike(q_clean) |
            models.Proveedor.nit_o_cedula.ilike(q_clean) |
            models.Proveedor.contacto_nombre.ilike(q_clean)
        )
    total = query.count()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ProveedorRespuesta.model_validate(p) for p in proveedores],
    }


@router.get(
    "/{proveedor_id}",
    response_model=ProveedorRespuesta,
    summary="Obtener detalle de un proveedor por ID",
)
def obtener_proveedor(
    proveedor_id: str,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(proveedor_id)
    proveedor = proveedor_service.obtener_proveedor_por_id(
        empresa_id=current_user.empresa_id,
        proveedor_id=p_id,
        db=db,
    )
    return ProveedorRespuesta.model_validate(proveedor)


@router.post(
    "",
    response_model=ProveedorRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo proveedor",
)
def crear_proveedor(
    data: ProveedorCrear,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proveedor = proveedor_service.crear_proveedor(
        empresa_id=current_user.empresa_id,
        data=data,
        db=db,
    )
    return ProveedorRespuesta.model_validate(proveedor)


@router.put(
    "/{proveedor_id}",
    response_model=ProveedorRespuesta,
    summary="Actualizar un proveedor existente",
)
def actualizar_proveedor(
    proveedor_id: str,
    data: ProveedorActualizar,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(proveedor_id)
    proveedor = proveedor_service.actualizar_proveedor(
        empresa_id=current_user.empresa_id,
        proveedor_id=p_id,
        data=data,
        db=db,
    )
    return ProveedorRespuesta.model_validate(proveedor)


@router.delete(
    "/{proveedor_id}",
    summary="Dar de baja (soft-delete) un proveedor",
)
def eliminar_proveedor(
    proveedor_id: str,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid
    p_id = uuid.UUID(proveedor_id)
    proveedor_service.eliminar_proveedor(
        empresa_id=current_user.empresa_id,
        proveedor_id=p_id,
        db=db,
    )
    return {"ok": True, "message": "Proveedor desactivado correctamente"}
