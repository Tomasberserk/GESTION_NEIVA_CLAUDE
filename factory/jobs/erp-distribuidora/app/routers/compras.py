from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.compra import (
    CompraCrear,
    CompraRespuesta,
    DetalleCompraRespuesta,
)
from app.services import compra_service
from app import models

router = APIRouter(prefix="/api/compras", tags=["Compras"])


# Schemas auxiliares para cumplir con el contrato de la API
class ProveedorMinimo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    razon_social: str


class UsuarioMinimo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str


class CompraListaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    numero_factura: Optional[str] = None
    fecha_compra: datetime
    metodo_pago: str
    fecha_vencimiento: Optional[datetime] = None
    estado: str
    total: Decimal
    proveedor: ProveedorMinimo
    usuario: Optional[UsuarioMinimo] = None


class CompraDetalladaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    numero_factura: Optional[str] = None
    fecha_compra: datetime
    metodo_pago: str
    fecha_vencimiento: Optional[datetime] = None
    estado: str
    total: Decimal
    detalles: List[DetalleCompraRespuesta]
    proveedor: ProveedorMinimo
    usuario: Optional[UsuarioMinimo] = None
    cuenta_por_pagar_id: Optional[UUID] = None


@router.get(
    "",
    summary="Listar compras filtradas de forma paginada",
)
def listar_compras(
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    proveedor_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    compras = compra_service.obtener_compras(
        empresa_id=current_user.empresa_id,
        db=db,
        desde=desde,
        hasta=hasta,
        proveedor_id=proveedor_id,
        estado=estado,
        skip=skip,
        limit=limit,
    )

    # Contar total con mismos filtros
    query = db.query(models.Compra).filter(
        models.Compra.empresa_id == current_user.empresa_id,
        models.Compra.is_active.is_(True),
    )
    if desde:
        query = query.filter(models.Compra.fecha_compra >= desde)
    if hasta:
        query = query.filter(models.Compra.fecha_compra <= hasta)
    if proveedor_id:
        query = query.filter(models.Compra.proveedor_id == proveedor_id)
    if estado:
        query = query.filter(models.Compra.estado == estado.upper())
    
    total = query.count()

    items_res = []
    for c in compras:
        # Llenar nombres en detalles
        for det in c.detalles:
            if det.producto:
                det.nombre = det.producto.nombre
        
        items_res.append(CompraListaRespuesta.model_validate(c))

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items_res,
    }


@router.get(
    "/{compra_id}",
    response_model=CompraDetalladaRespuesta,
    summary="Obtener detalle completo de una compra por ID",
)
def obtener_compra(
    compra_id: UUID,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    compra = compra_service.obtener_compra_por_id(
        empresa_id=current_user.empresa_id,
        compra_id=compra_id,
        db=db,
    )
    
    # Llenar nombres de productos en los detalles
    for det in compra.detalles:
        if det.producto:
            det.nombre = det.producto.nombre

    # Buscar si tiene cxp asociada
    cxp_id = compra.cuenta_por_pagar.id if compra.cuenta_por_pagar else None

    # Mapear a respuesta detallada
    res = CompraDetalladaRespuesta.model_validate(compra)
    res.cuenta_por_pagar_id = cxp_id
    return res


@router.post(
    "",
    response_model=CompraRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva compra",
)
def registrar_compra(
    data: CompraCrear,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return compra_service.registrar_compra(
        empresa_id=current_user.empresa_id,
        data=data,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{compra_id}",
    summary="Anular una compra y reversar stock de inventario",
)
def anular_compra(
    compra_id: UUID,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Obtener detalles antes de anular para saber qué stock se reversa
    compra = compra_service.obtener_compra_por_id(
        empresa_id=current_user.empresa_id,
        compra_id=compra_id,
        db=db,
    )
    
    stock_reversado = {str(d.producto_id): -float(d.cantidad) for d in compra.detalles if d.is_active}

    compra_service.anular_compra(
        empresa_id=current_user.empresa_id,
        compra_id=compra_id,
        db=db,
    )

    return {
        "ok": True,
        "message": "Compra anulada e inventario reversado correctamente",
        "stock_reversado": stock_reversado,
    }
