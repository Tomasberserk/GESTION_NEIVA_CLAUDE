from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

from app.database import get_db
from app.dependencies import get_current_user_admin
from app.schemas.cuenta_por_pagar import CuentaPorPagarRespuesta
from app.schemas.abono import AbonoCrear, AbonoRespuesta
from app.services import cxp_service
from app import models

router = APIRouter(prefix="/api/cuentas-por-pagar", tags=["Cuentas por Pagar"])


# Schemas auxiliares de respuesta de abonos para el contrato de la API
class AbonoConSaldoRespuesta(BaseModel):
    id: UUID
    cuenta_por_pagar_id: UUID
    monto: Decimal
    fecha_abono: datetime
    metodo_pago: str
    nota: Optional[str] = None
    nuevo_saldo_pendiente: Decimal
    estado_obligacion: str


class HistorialAbonosRespuesta(BaseModel):
    cuenta_por_pagar_id: UUID
    abonos: List[AbonoRespuesta]


@router.get(
    "",
    summary="Listar cuentas por pagar (solo admin)",
)
def listar_cuentas_por_pagar(
    estado: Optional[str] = None,
    proveedor_id: Optional[UUID] = None,
    vence_antes: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    cxps = cxp_service.obtener_cuentas_por_pagar(
        empresa_id=current_user.empresa_id,
        db=db,
        estado=estado,
        proveedor_id=proveedor_id,
        vence_antes=vence_antes,
        skip=skip,
        limit=limit,
    )

    # Contar total con mismos filtros
    query = db.query(models.CuentaPorPagar).filter(
        models.CuentaPorPagar.empresa_id == current_user.empresa_id,
        models.CuentaPorPagar.is_active.is_(True),
    )
    if estado:
        query = query.filter(models.CuentaPorPagar.estado == estado.upper())
    if proveedor_id:
        query = query.filter(models.CuentaPorPagar.proveedor_id == proveedor_id)
    if vence_antes:
        query = query.filter(models.CuentaPorPagar.fecha_vencimiento <= vence_antes)
    
    total = query.count()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [CuentaPorPagarRespuesta.model_validate(c) for c in cxps],
    }


@router.get(
    "/{cxp_id}",
    response_model=CuentaPorPagarRespuesta,
    summary="Obtener detalle de una cuenta por pagar específica por ID",
)
def obtener_cuenta_por_pagar(
    cxp_id: UUID,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    cxp = cxp_service.obtener_cuenta_por_pagar_por_id(
        empresa_id=current_user.empresa_id,
        cxp_id=cxp_id,
        db=db,
    )
    return CuentaPorPagarRespuesta.model_validate(cxp)


@router.post(
    "/{cxp_id}/abonos",
    response_model=AbonoConSaldoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un abono o pago a una cuenta por pagar",
)
def registrar_abono(
    cxp_id: UUID,
    data: AbonoCrear,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    abono = cxp_service.registrar_abono(
        empresa_id=current_user.empresa_id,
        cxp_id=cxp_id,
        data=data,
        db=db,
    )
    cxp = abono.cuenta_por_pagar
    return AbonoConSaldoRespuesta(
        id=abono.id,
        cuenta_por_pagar_id=abono.cuenta_por_pagar_id,
        monto=abono.monto,
        fecha_abono=abono.fecha_abono,
        metodo_pago=abono.metodo_pago,
        nota=abono.nota,
        nuevo_saldo_pendiente=cxp.saldo_pendiente,
        estado_obligacion=cxp.estado,
    )


@router.get(
    "/{cxp_id}/abonos",
    response_model=HistorialAbonosRespuesta,
    summary="Obtener el historial de abonos de una cuenta por pagar",
)
def listar_abonos(
    cxp_id: UUID,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    abonos = cxp_service.obtener_abonos(
        empresa_id=current_user.empresa_id,
        cxp_id=cxp_id,
        db=db,
    )
    return HistorialAbonosRespuesta(
        cuenta_por_pagar_id=cxp_id,
        abonos=[AbonoRespuesta.model_validate(a) for a in abonos],
    )


@router.delete(
    "/abonos/{abono_id}",
    summary="Reversar un abono registrado",
)
def reversar_abono(
    abono_id: UUID,
    current_user: models.Usuario = Depends(get_current_user_admin),
    db: Session = Depends(get_db),
):
    cxp = cxp_service.reversar_abono(
        empresa_id=current_user.empresa_id,
        abono_id=abono_id,
        db=db,
    )
    return {
        "ok": True,
        "message": "Abono reversado correctamente, saldo pendiente restaurado",
        "nuevo_saldo_pendiente": float(cxp.saldo_pendiente),
        "estado_obligacion": cxp.estado,
    }
