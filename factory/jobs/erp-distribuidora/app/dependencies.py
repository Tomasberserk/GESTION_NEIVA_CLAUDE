import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.models import RolUsuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Secret keys para el hash (pueden ser cargados de .env)
SECRET_KEY = "super-secret-key-for-jwt-distribuidora-mayorista-medium"
ALGORITHM = "HS256"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.Usuario:
    _no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise _no_autenticado
        import uuid
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise _no_autenticado

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == user_id,
        models.Usuario.is_active.is_(True),
    ).first()

    if not usuario:
        raise _no_autenticado

    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == usuario.empresa_id,
        models.Empresa.is_active.is_(True),
    ).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empresa inactiva o no encontrada",
        )

    return usuario


def get_current_user_admin(
    current_user: models.Usuario = Depends(get_current_user),
) -> models.Usuario:
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador (Rol Admin)",
        )
    return current_user
