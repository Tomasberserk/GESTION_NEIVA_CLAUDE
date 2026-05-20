from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user_admin
from app.schemas.usuario import UsuarioCrear, UsuarioRespuesta
from app.services import auth_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{empresa_id}", response_model=list[UsuarioRespuesta])
def listar_usuarios(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    return db.query(models.Usuario).filter(
        models.Usuario.empresa_id == empresa_id,
        models.Usuario.is_active.is_(True),
    ).all()


@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    data: UsuarioCrear,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    # empresa_id siempre del JWT — previene crear usuarios en otra empresa
    data_con_empresa = data.model_copy(update={"empresa_id": current_user.empresa_id})
    return auth_service.registrar_usuario(data_con_empresa, db)


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def desactivar_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user_admin),
):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id,
        models.Usuario.empresa_id == current_user.empresa_id,
        models.Usuario.is_active.is_(True),
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta",
        )

    usuario.is_active = False
    db.commit()
    return {"mensaje": "Usuario desactivado exitosamente"}
