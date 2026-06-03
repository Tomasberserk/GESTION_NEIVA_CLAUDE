import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.sso import SSOLoginOut, SSOTokenOut
from app.services.auth_service import crear_token_acceso

router = APIRouter(prefix="/sso", tags=["SSO"])

# El token SSO vive 5 minutos — suficiente para abrir pestaña nueva
_SSO_TOKEN_TTL_MINUTES = 5


@router.post("/token", response_model=SSOTokenOut)
def generar_sso_token(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Genera un token SSO de un solo uso para el usuario autenticado.
    Válido 5 minutos. El frontend lo usa para abrir el ERP en nueva pestaña.

    Requisitos:
    - La empresa debe tener factory_url configurada.
    - El trial no debe estar vencido.
    """
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == current_user.empresa_id
    ).first()

    if not empresa or not empresa.factory_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El Plan Medium no está activado para esta empresa.",
        )

    now = datetime.now(timezone.utc)

    trial_exp = empresa.factory_trial_expires_at
    if trial_exp:
        if trial_exp.tzinfo is None:
            trial_exp = trial_exp.replace(tzinfo=timezone.utc)
    if trial_exp and trial_exp < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El trial del Plan Medium ha vencido.",
        )

    # Invalida tokens anteriores del mismo usuario para limpiar la tabla
    db.query(models.SSOToken).filter(
        models.SSOToken.usuario_id == current_user.id,
        models.SSOToken.usado.is_(False),
    ).update({"usado": True}, synchronize_session=False)

    token_value = uuid.uuid4().hex  # 32 chars hex, opaco
    expires_at = now + timedelta(minutes=_SSO_TOKEN_TTL_MINUTES)

    sso_token = models.SSOToken(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        token=token_value,
        expires_at=expires_at,
        usado=False,
    )
    db.add(sso_token)
    db.commit()

    return SSOTokenOut(token=token_value, expires_at=expires_at)


@router.get("/login", response_model=SSOLoginOut)
def login_con_sso_token(
    token: str = Query(..., description="Token SSO de un solo uso"),
    db: Session = Depends(get_db),
):
    """
    Endpoint público. Valida el token SSO y devuelve un JWT real + URL de redirect.
    El frontend redirige a factory_url con el JWT para completar el login automático.

    Seguridad:
    - Token de un solo uso (se marca como usado tras el primer canje).
    - Expira a los 5 minutos de generado.
    - Responde siempre con el mismo mensaje genérico si el token es inválido.
    """
    _token_invalido = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token SSO inválido o expirado",
    )

    sso_token = db.query(models.SSOToken).filter(
        models.SSOToken.token == token,
    ).first()

    now = datetime.now(timezone.utc)

    token_exp = sso_token.expires_at if sso_token else None
    if token_exp and token_exp.tzinfo is None:
        token_exp = token_exp.replace(tzinfo=timezone.utc)

    if not sso_token or sso_token.usado or (token_exp and token_exp < now):
        raise _token_invalido

    # Marcar como usado antes de emitir el JWT — previene doble canje
    sso_token.usado = True
    db.flush()

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == sso_token.usuario_id,
        models.Usuario.is_active.is_(True),
    ).first()

    if not usuario:
        db.rollback()
        raise _token_invalido

    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == sso_token.empresa_id,
    ).first()

    jwt_token = crear_token_acceso({"sub": str(usuario.id)})
    db.commit()

    return SSOLoginOut(
        access_token=jwt_token,
        token_type="bearer",
        empresa_id=sso_token.empresa_id,
        redirect_url=empresa.factory_url or "",
    )
