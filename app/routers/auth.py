from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.usuario import (
    LoginForm,
    TokenRespuesta,
    UsuarioCrear,
    UsuarioCrearConEmpresa,
    UsuarioRespuesta,
)
from app.services import auth_service

router = APIRouter(tags=["Autenticación"])


@router.post("/registro", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registro(data: UsuarioCrear, db: Session = Depends(get_db)):
    usuario = auth_service.registrar_usuario(data, db)
    token = auth_service.crear_token_acceso({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}


@router.post("/auth/registro-completo", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registro_completo(data: UsuarioCrearConEmpresa, db: Session = Depends(get_db)):
    return auth_service.registrar_usuario_con_empresa(
        nombre_comercial=data.nombre_comercial,
        nit_o_cedula=data.nit_o_cedula,
        email=data.email,
        password=data.password,
        rol=data.rol,
        db=db,
    )


@router.post("/token", response_model=TokenRespuesta)
def login(data: LoginForm, db: Session = Depends(get_db)):
    # Acepta JSON (no form-data) para compatibilidad con el frontend React
    return auth_service.login_usuario(data.email, data.password, db)


@router.get("/me", response_model=UsuarioRespuesta)
def me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user
