from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_admin
from app.schemas.producto import (
    InventarioRespuesta,
    ProductoActualizar,
    ProductoCrear,
    ProductoRespuesta,
)
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=ProductoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCrear,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    # empresa_id siempre del JWT — previene spoofing multi-tenant
    return producto_service.crear_producto(
        data.model_copy(update={"empresa_id": current_user.empresa_id}), db
    )


@router.get("/{empresa_id}", response_model=InventarioRespuesta)
def listar_productos(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    return producto_service.obtener_productos_empresa(empresa_id, db)


@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(
    producto_id: UUID,
    data: ProductoActualizar,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    return producto_service.actualizar_producto(
        producto_id, current_user.empresa_id, data, db
    )


@router.delete("/{producto_id}", status_code=status.HTTP_200_OK)
def eliminar_producto(
    producto_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    producto_service.eliminar_producto(producto_id, current_user.empresa_id, db)
    return {"mensaje": "Producto eliminado exitosamente"}


@router.post("/{producto_id}/imagen")
async def subir_imagen(
    producto_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    url = await producto_service.guardar_imagen_producto(
        producto_id, current_user.empresa_id, file, db
    )
    return {"mensaje": "Imagen subida exitosamente", "url_acceso": url}
