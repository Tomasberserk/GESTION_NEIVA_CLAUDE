import os
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.empresa import EmpresaCrear, EmpresaRespuesta
from app.services import empresa_service

router = APIRouter(prefix="/empresas", tags=["Empresas"])

_SUPERADMIN_KEY = os.getenv("SUPERADMIN_KEY")


def _check_superadmin(x_superadmin_key: str = Header(alias="x-superadmin-key")):
    if not _SUPERADMIN_KEY or x_superadmin_key != _SUPERADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de superadmin inválida",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_check_superadmin)],
)
def crear_empresa(data: EmpresaCrear, db: Session = Depends(get_db)):
    empresa = empresa_service.crear_empresa(data, db)
    return {
        "mensaje": "Empresa creada exitosamente",
        "empresa": EmpresaRespuesta.model_validate(empresa),
    }


@router.get("/{empresa_id}", response_model=EmpresaRespuesta)
def obtener_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    return empresa_service.obtener_empresa(empresa_id, db)
