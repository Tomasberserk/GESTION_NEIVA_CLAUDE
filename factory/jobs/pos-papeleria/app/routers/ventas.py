from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.venta import VentaCrear, VentaRespuesta, VentaResumen
from app.services import venta_service

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.post("/{empresa_id}", response_model=VentaResumen, status_code=status.HTTP_201_CREATED)
def registrar_venta(
    empresa_id: UUID,
    data: VentaCrear,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    return venta_service.registrar_venta(empresa_id, data, current_user, db)


@router.get("/{empresa_id}", response_model=list[VentaRespuesta])
def listar_ventas(
    empresa_id: UUID,
    desde: Optional[datetime] = Query(None, description="ISO datetime — ej: 2026-05-01T00:00:00Z"),
    hasta: Optional[datetime] = Query(None, description="ISO datetime — ej: 2026-05-19T23:59:59Z"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    return venta_service.obtener_ventas_empresa(empresa_id, db, desde, hasta)
