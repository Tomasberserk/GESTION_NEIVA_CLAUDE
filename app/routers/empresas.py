from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.empresa import EmpresaCrear, EmpresaRespuesta
from app.services import empresa_service

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_empresa(data: EmpresaCrear, db: Session = Depends(get_db)):
    empresa = empresa_service.crear_empresa(data, db)
    return {
        "mensaje": "Empresa creada exitosamente",
        "empresa": EmpresaRespuesta.model_validate(empresa),
    }


@router.get("/{empresa_id}", response_model=EmpresaRespuesta)
def obtener_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    return empresa_service.obtener_empresa(empresa_id, db)
