from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_admin
from app.services import cxp_service
from app import models

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/kpis",
    summary="Obtener KPIs financieros del dashboard (solo admin)",
)
def obtener_kpis(
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    return cxp_service.obtener_dashboard_kpis(
        empresa_id=current_user.empresa_id,
        db=db,
        desde=desde,
        hasta=hasta,
    )
