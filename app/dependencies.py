from datetime import datetime, timezone
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.models import RolUsuario
from app.services.auth_service import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


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
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise _no_autenticado
        # Convertir string UUID a UUID object para comparación correcta
        try:
            user_id_uuid = uuid.UUID(user_id)
        except (ValueError, TypeError):
            raise _no_autenticado
    except jwt.InvalidTokenError:
        raise _no_autenticado

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == user_id_uuid,
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

    trial_ts = empresa.trial_expires_at
    if trial_ts is not None and trial_ts.tzinfo is None:
        trial_ts = trial_ts.replace(tzinfo=timezone.utc)
    if trial_ts and trial_ts < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu período de prueba ha vencido. Contacta al administrador para activar tu plan.",
        )

    return usuario


def get_current_user_admin(
    current_user: models.Usuario = Depends(get_current_user),
) -> models.Usuario:
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return current_user
