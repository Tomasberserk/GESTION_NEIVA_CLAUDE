from datetime import timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.usuario import (
    UsuarioCrearConEmpresa,
    LoginForm,
    TokenRespuesta,
    UsuarioRespuesta,
)
from app.services import auth_service
from app import models

router = APIRouter(tags=["Autenticación"])


@router.post(
    "/auth/registro-completo",
    response_model=TokenRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva distribuidora y su administrador",
)
def registro_completo(
    data: UsuarioCrearConEmpresa,
    db: Session = Depends(get_db),
):
    nuevo_usuario = auth_service.registrar_empresa_y_admin(data, db)
    access_token = auth_service.crear_access_token(
        data={"sub": str(nuevo_usuario.id)}
    )
    return TokenRespuesta(
        access_token=access_token,
        usuario=UsuarioRespuesta.model_validate(nuevo_usuario),
    )


@router.post(
    "/token",
    response_model=TokenRespuesta,
    summary="Login de usuario y obtención de token de acceso",
)
def login(
    data: LoginForm,
    db: Session = Depends(get_db),
):
    usuario = auth_service.autenticar_usuario(data, db)
    access_token = auth_service.crear_access_token(
        data={"sub": str(usuario.id)}
    )
    return TokenRespuesta(
        access_token=access_token,
        usuario=UsuarioRespuesta.model_validate(usuario),
    )


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Obtener perfil del usuario autenticado",
)
def me(
    current_user: models.Usuario = Depends(get_current_user),
):
    return UsuarioRespuesta.model_validate(current_user)
