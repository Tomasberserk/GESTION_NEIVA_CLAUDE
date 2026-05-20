import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.usuario import UsuarioCrear

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en las variables de entorno")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def crear_token_acceso(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def registrar_usuario(data: UsuarioCrear, db: Session) -> models.Usuario:
    if db.query(models.Usuario).filter(
        models.Usuario.email == data.email
    ).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email ya está registrado",
        )

    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == data.empresa_id,
        models.Empresa.is_active.is_(True),
    ).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    usuario = models.Usuario(
        email=data.email,
        hashed_password=hash_password(data.password),
        empresa_id=data.empresa_id,
        rol=data.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def registrar_usuario_con_empresa(
    nombre_comercial: str,
    nit_o_cedula: str,
    email: str,
    password: str,
    rol: models.RolUsuario,
    db: Session,
) -> dict:
    if db.query(models.Usuario).filter(models.Usuario.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email ya está registrado",
        )

    if db.query(models.Empresa).filter(models.Empresa.nit_o_cedula == nit_o_cedula).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una empresa con NIT/Cédula '{nit_o_cedula}'",
        )

    try:
        empresa = models.Empresa(
            nombre_comercial=nombre_comercial.strip(),
            nit_o_cedula=nit_o_cedula.strip(),
        )
        db.add(empresa)
        db.flush()

        usuario = models.Usuario(
            email=email,
            hashed_password=hash_password(password),
            empresa_id=empresa.id,
            rol=rol,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        token = crear_token_acceso({"sub": str(usuario.id)})
        return {"access_token": token, "token_type": "bearer", "usuario": usuario}  # nosec B105

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el registro: {str(exc)}",
        )


def login_usuario(email: str, password: str, db: Session) -> dict:
    _credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email,
        models.Usuario.is_active.is_(True),
    ).first()

    if not usuario or not verificar_password(password, usuario.hashed_password):
        raise _credenciales_invalidas

    token = crear_token_acceso({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}  # nosec B105
