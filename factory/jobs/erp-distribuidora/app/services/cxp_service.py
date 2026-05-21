from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app import models
from app.schemas.abono import AbonoCrear


def obtener_cuentas_por_pagar(
    empresa_id: UUID,
    db: Session,
    estado: Optional[str] = None,
    proveedor_id: Optional[UUID] = None,
    vence_antes: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.CuentaPorPagar]:
    query = db.query(models.CuentaPorPagar).filter(
        models.CuentaPorPagar.empresa_id == empresa_id,
        models.CuentaPorPagar.is_active.is_(True),
    )
    if estado:
        query = query.filter(models.CuentaPorPagar.estado == estado.upper())
    if proveedor_id:
        query = query.filter(models.CuentaPorPagar.proveedor_id == proveedor_id)
    if vence_antes:
        query = query.filter(models.CuentaPorPagar.fecha_vencimiento <= vence_antes)

    items = (
        query.options(
            joinedload(models.CuentaPorPagar.proveedor),
            joinedload(models.CuentaPorPagar.compra),
        )
        .order_by(models.CuentaPorPagar.fecha_vencimiento.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Computar días para vencimiento dinámicamente
    ahora = datetime.now(timezone.utc)
    for item in items:
        # Asegurar que ambos son timezone aware para restar
        f_venc = item.fecha_vencimiento
        if f_venc.tzinfo is None:
            f_venc = f_venc.replace(tzinfo=timezone.utc)
        diff = f_venc - ahora
        item.dias_para_vencimiento = diff.days

        # Opcional: Auto-degradar estado a VENCIDA si ya pasó la fecha y sigue PENDIENTE
        if item.saldo_pendiente > 0 and item.estado == "PENDIENTE" and diff.days < 0:
            item.estado = "VENCIDA"
            db.add(item)
    
    if db.dirty:
        try:
            db.commit()
        except Exception:
            db.rollback()

    return items


def obtener_cuenta_por_pagar_por_id(
    empresa_id: UUID, cxp_id: UUID, db: Session
) -> models.CuentaPorPagar:
    cxp = (
        db.query(models.CuentaPorPagar)
        .filter(
            models.CuentaPorPagar.id == cxp_id,
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
        )
        .options(
            joinedload(models.CuentaPorPagar.proveedor),
            joinedload(models.CuentaPorPagar.compra),
            joinedload(models.CuentaPorPagar.abonos),
        )
        .first()
    )
    if not cxp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta por pagar no encontrada o no pertenece a la empresa",
        )
    
    # Calcular dias para vencimiento
    ahora = datetime.now(timezone.utc)
    f_venc = cxp.fecha_vencimiento
    if f_venc.tzinfo is None:
        f_venc = f_venc.replace(tzinfo=timezone.utc)
    cxp.dias_para_vencimiento = (f_venc - ahora).days

    return cxp


def registrar_abono(
    empresa_id: UUID,
    cxp_id: UUID,
    data: AbonoCrear,
    db: Session,
) -> models.AbonoCuentaPorPagar:
    # 1. Lock y validación de la cuenta por pagar
    cxp = (
        db.query(models.CuentaPorPagar)
        .filter(
            models.CuentaPorPagar.id == cxp_id,
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
        )
        .with_for_update()
        .first()
    )
    if not cxp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta por pagar no encontrada",
        )

    if cxp.saldo_pendiente == Decimal("0.00") or cxp.estado == "PAGADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta por pagar ya se encuentra completamente pagada",
        )

    if data.monto > cxp.saldo_pendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El monto del abono ({data.monto}) no puede ser mayor que el saldo pendiente ({cxp.saldo_pendiente})",
        )

    try:
        # 2. Registrar el abono
        nuevo_abono = models.AbonoCuentaPorPagar(
            cuenta_por_pagar_id=cxp.id,
            monto=data.monto,
            metodo_pago=data.metodo_pago.upper(),
            nota=data.nota,
        )
        db.add(nuevo_abono)

        # 3. Amortizar saldo
        cxp.saldo_pendiente -= data.monto

        # 4. Actualizar estados si se saldó la deuda
        if cxp.saldo_pendiente == Decimal("0.00"):
            cxp.estado = "PAGADA"
            
            # También actualizar estado de la compra asociada
            compra = (
                db.query(models.Compra)
                .filter(models.Compra.id == cxp.compra_id)
                .with_for_update()
                .first()
            )
            if compra:
                compra.estado = "PAGADA"

        db.commit()
        db.refresh(nuevo_abono)
        return nuevo_abono

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al registrar el abono",
        ) from exc


def obtener_abonos(
    empresa_id: UUID,
    cxp_id: UUID,
    db: Session,
) -> List[models.AbonoCuentaPorPagar]:
    cxp = obtener_cuenta_por_pagar_por_id(empresa_id, cxp_id, db)
    return [a for a in cxp.abonos if a.is_active]


def reversar_abono(
    empresa_id: UUID,
    abono_id: UUID,
    db: Session,
) -> models.CuentaPorPagar:
    # 1. Obtener y validar el abono
    abono = (
        db.query(models.AbonoCuentaPorPagar)
        .join(models.CuentaPorPagar)
        .filter(
            models.AbonoCuentaPorPagar.id == abono_id,
            models.AbonoCuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.empresa_id == empresa_id,
        )
        .options(joinedload(models.AbonoCuentaPorPagar.cuenta_por_pagar))
        .with_for_update()
        .first()
    )
    if not abono:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Abono no encontrado",
        )

    cxp = abono.cuenta_por_pagar

    try:
        # 2. Soft delete del abono
        abono.is_active = False

        # 3. Reversar saldo
        cxp.saldo_pendiente += abono.monto

        # 4. Degradación de estados
        ahora = datetime.now(timezone.utc)
        f_venc = cxp.fecha_vencimiento
        if f_venc.tzinfo is None:
            f_venc = f_venc.replace(tzinfo=timezone.utc)

        # Si el saldo pendiente es mayor a 0, ya no está PAGADA
        if cxp.saldo_pendiente > 0:
            if f_venc < ahora:
                cxp.estado = "VENCIDA"
            else:
                cxp.estado = "PENDIENTE"

            # Reversar estado de la compra asociada
            compra = (
                db.query(models.Compra)
                .filter(models.Compra.id == cxp.compra_id)
                .with_for_update()
                .first()
            )
            if compra and compra.estado == "PAGADA":
                compra.estado = "PENDIENTE"

        db.commit()
        db.refresh(cxp)
        return cxp

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al reversar el abono",
        ) from exc


def obtener_dashboard_kpis(
    empresa_id: UUID,
    db: Session,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
) -> dict:
    # 1. Compras totales en periodo
    compra_query = db.query(func.sum(models.Compra.total)).filter(
        models.Compra.empresa_id == empresa_id,
        models.Compra.is_active.is_(True),
    )
    if desde:
        compra_query = compra_query.filter(models.Compra.fecha_compra >= desde)
    if hasta:
        compra_query = compra_query.filter(models.Compra.fecha_compra <= hasta)
    
    compras_totales = compra_query.scalar() or Decimal("0.00")

    # 2. Deudas activas (todas las CxP activas con saldo > 0)
    deudas_activas = (
        db.query(func.sum(models.CuentaPorPagar.saldo_pendiente))
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.estado != "PAGADA",
        )
        .scalar()
        or Decimal("0.00")
    )

    # 3. Deudas vencidas (CxP activas vencidas o con saldo > 0 e hito de fecha superado)
    ahora = datetime.now(timezone.utc)
    deudas_vencidas = (
        db.query(func.sum(models.CuentaPorPagar.saldo_pendiente))
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.estado == "VENCIDA",
        )
        .scalar()
        or Decimal("0.00")
    )

    # Si hay cuentas PENDIENTES que ya vencieron pero no han actualizado su estado
    deudas_vencidas_no_actualizadas = (
        db.query(func.sum(models.CuentaPorPagar.saldo_pendiente))
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.estado == "PENDIENTE",
            models.CuentaPorPagar.fecha_vencimiento < ahora,
        )
        .scalar()
        or Decimal("0.00")
    )
    deudas_vencidas += deudas_vencidas_no_actualizadas

    # 4. Pagos realizados (abonos activos en el periodo)
    abonos_query = (
        db.query(func.sum(models.AbonoCuentaPorPagar.monto))
        .join(models.CuentaPorPagar)
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.AbonoCuentaPorPagar.is_active.is_(True),
        )
    )
    if desde:
        abonos_query = abonos_query.filter(models.AbonoCuentaPorPagar.fecha_abono >= desde)
    if hasta:
        abonos_query = abonos_query.filter(models.AbonoCuentaPorPagar.fecha_abono <= hasta)
    
    pagos_realizados = abonos_query.scalar() or Decimal("0.00")

    # 5. Inventario KPIs
    total_items = (
        db.query(func.count(models.Producto.id))
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    valor_total_stock = (
        db.query(func.sum(models.Producto.cantidad_actual * models.Producto.precio_costo))
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        )
        .scalar()
        or Decimal("0.00")
    )

    # 6. Proveedores KPIs
    total_activos = (
        db.query(func.count(models.Proveedor.id))
        .filter(
            models.Proveedor.empresa_id == empresa_id,
            models.Proveedor.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    con_deuda_activa = (
        db.query(func.count(func.distinct(models.CuentaPorPagar.proveedor_id)))
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.saldo_pendiente > 0,
        )
        .scalar()
        or 0
    )

    con_deuda_vencida = (
        db.query(func.count(func.distinct(models.CuentaPorPagar.proveedor_id)))
        .filter(
            models.CuentaPorPagar.empresa_id == empresa_id,
            models.CuentaPorPagar.is_active.is_(True),
            models.CuentaPorPagar.saldo_pendiente > 0,
            (models.CuentaPorPagar.estado == "VENCIDA") | (models.CuentaPorPagar.fecha_vencimiento < ahora),
        )
        .scalar()
        or 0
    )

    return {
        "periodo": {
            "desde": desde.isoformat() if desde else None,
            "hasta": hasta.isoformat() if hasta else None,
        },
        "resumen_financiero": {
            "compras_totales": float(compras_totales),
            "deudas_activas": float(deudas_activas),
            "deudas_vencidas": float(deudas_vencidas),
            "pagos_realizados": float(pagos_realizados),
            "efectivo_entrada": 0.00,  # En compras/abonos no hay entrada de efectivo directo del POS
            "promedio_dias_pago": 30,  # Valor de referencia
        },
        "inventario": {
            "total_items": total_items,
            "valor_total_stock": float(valor_total_stock),
            "rotacion_promedio_dias": 15,
        },
        "proveedores": {
            "total_activos": total_activos,
            "con_deuda_activa": con_deuda_activa,
            "con_deuda_vencida": con_deuda_vencida,
        }
    }
