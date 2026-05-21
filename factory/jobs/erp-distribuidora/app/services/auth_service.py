import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from app import models
from app.schemas.usuario import UsuarioCrearConEmpresa, LoginForm
from app.dependencies import SECRET_KEY, ALGORITHM


def obtener_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def crear_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=180)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def registrar_empresa_y_admin(data: UsuarioCrearConEmpresa, db: Session) -> models.Usuario:
    # 1. Validar que la empresa no exista
    existente_nit = db.query(models.Empresa).filter(
        models.Empresa.nit_o_cedula == data.nit_o_cedula,
        models.Empresa.is_active.is_(True),
    ).first()
    if existente_nit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una empresa con este NIT o cédula ya está registrada",
        )

    # 2. Validar que el email no esté ocupado
    existente_email = db.query(models.Usuario).filter(
        models.Usuario.email == data.email,
        models.Usuario.is_active.is_(True),
    ).first()
    if existente_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este correo electrónico ya está registrado",
        )

    try:
        # 3. Crear empresa
        nueva_empresa = models.Empresa(
            nombre_comercial=data.nombre_comercial,
            nit_o_cedula=data.nit_o_cedula,
            plan="medium",
        )
        db.add(nueva_empresa)
        db.flush()  # Obtener ID de la empresa

        # 4. Crear administrador
        nuevo_usuario = models.Usuario(
            email=data.email,
            hashed_password=obtener_password_hash(data.password),
            empresa_id=nueva_empresa.id,
            rol="admin",
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al registrar la empresa y administrador",
        ) from exc


def autenticar_usuario(data: LoginForm, db: Session) -> models.Usuario:
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == data.email,
        models.Usuario.is_active.is_(True),
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    if not verificar_password(data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    return usuario
