from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.usuario import EmpleadoCrear
from app.services import auth_service

MAX_CAJEROS_BASIC = 3


def listar_cajeros(admin_user: models.Usuario, db: Session) -> List[models.Usuario]:
    """Retorna la lista de cajeros pertenecientes a la empresa del administrador."""
    return (
        db.query(models.Usuario)
        .filter(
            models.Usuario.empresa_id == admin_user.empresa_id,
            models.Usuario.rol == models.RolUsuario.TENDERO,
        )
        .order_by(models.Usuario.created_at.asc())
        .all()
    )


def crear_cajero(
    admin_user: models.Usuario,
    data: EmpleadoCrear,
    db: Session,
) -> models.Usuario:
    """
    Crea un nuevo cajero garantizando atomicidad mediante bloqueo de fila (SELECT FOR UPDATE)
    sobre la empresa, evitando race conditions sobre el límite de 3 cajeros en Plan Básico.
    """
    # 1. Validar unicidad global del email
    if db.query(models.Usuario).filter(models.Usuario.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    # 2. Bloquear la fila de la empresa para serializar verificaciones concurrentes
    empresa = (
        db.query(models.Empresa)
        .filter(models.Empresa.id == admin_user.empresa_id)
        .with_for_update()
        .first()
    )
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    # 3. Validar límite de cajeros activos si el plan es BASIC
    if empresa.plan == models.PlanEmpresa.BASIC:
        cajeros_activos = (
            db.query(models.Usuario)
            .filter(
                models.Usuario.empresa_id == admin_user.empresa_id,
                models.Usuario.rol == models.RolUsuario.TENDERO,
                models.Usuario.is_active.is_(True),
            )
            .count()
        )
        if cajeros_activos >= MAX_CAJEROS_BASIC:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Has alcanzado el límite de 3 cajeros activos en tu Plan Básico. Actualiza al Plan Pro para cajeros ilimitados.",
            )

    # 4. Crear usuario cajero dentro de la misma transacción
    nuevo_cajero = models.Usuario(
        email=data.email,
        nombre=data.nombre,
        hashed_password=auth_service.hash_password(data.password),
        empresa_id=admin_user.empresa_id,
        rol=models.RolUsuario.TENDERO,
        is_active=True,
    )
    db.add(nuevo_cajero)
    db.commit()
    db.refresh(nuevo_cajero)
    return nuevo_cajero


def cambiar_estado_cajero(
    admin_user: models.Usuario,
    cajero_id: UUID,
    nuevo_estado: bool,
    db: Session,
) -> models.Usuario:
    """
    Activa o desactiva a un cajero. Si es reactivación (nuevo_estado=True),
    adquiere lock sobre la empresa y valida que no supere el límite de 3 cajeros activos.
    """
    # 1. Aislamiento multi-tenant estricto: buscar por id, empresa_id y rol
    cajero = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.id == cajero_id,
            models.Usuario.empresa_id == admin_user.empresa_id,
            models.Usuario.rol == models.RolUsuario.TENDERO,
        )
        .first()
    )
    if not cajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cajero no encontrado",
        )

    # No-op si ya tiene el estado deseado
    if cajero.is_active == nuevo_estado:
        return cajero

    # 2. Si se va a reactivar, adquirir lock y verificar cupo en Plan Básico
    if nuevo_estado is True:
        empresa = (
            db.query(models.Empresa)
            .filter(models.Empresa.id == admin_user.empresa_id)
            .with_for_update()
            .first()
        )
        if empresa and empresa.plan == models.PlanEmpresa.BASIC:
            cajeros_activos = (
                db.query(models.Usuario)
                .filter(
                    models.Usuario.empresa_id == admin_user.empresa_id,
                    models.Usuario.rol == models.RolUsuario.TENDERO,
                    models.Usuario.is_active.is_(True),
                )
                .count()
            )
            if cajeros_activos >= MAX_CAJEROS_BASIC:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Has alcanzado el límite de 3 cajeros activos en tu Plan Básico. Actualiza al Plan Pro para cajeros ilimitados.",
                )

    cajero.is_active = nuevo_estado
    db.commit()
    db.refresh(cajero)
    return cajero
