from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user_admin
from app.schemas.usuario import (
    EmpleadoCrear,
    EmpleadoEstadoUpdate,
    EmpleadoRespuesta,
)
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Gestión de Empleados / Cajeros"])


@router.get("/empleados", response_model=List[EmpleadoRespuesta])
def listar_empleados(
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    """Lista todos los cajeros/empleados de la empresa del administrador."""
    return usuario_service.listar_cajeros(current_user, db)


@router.post("/empleados", response_model=EmpleadoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    data: EmpleadoCrear,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo cajero. En Plan Básico valida con SELECT FOR UPDATE
    que no se superen los 3 cajeros activos permitidos.
    """
    return usuario_service.crear_cajero(current_user, data, db)


@router.patch("/empleados/{cajero_id}/estado", response_model=EmpleadoRespuesta)
def cambiar_estado_empleado(
    cajero_id: UUID,
    data: EmpleadoEstadoUpdate,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    """
    Activa o desactiva a un cajero. Si es reactivación en Plan Básico,
    valida con SELECT FOR UPDATE que no se exceda el cupo de 3 cajeros activos.
    """
    return usuario_service.cambiar_estado_cajero(
        admin_user=current_user,
        cajero_id=cajero_id,
        nuevo_estado=data.is_active,
        db=db,
    )
