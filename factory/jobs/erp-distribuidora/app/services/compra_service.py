from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schemas.compra import CompraCrear, CompraRespuesta, DetalleCompraRespuesta
from app.services.proveedor_service import obtener_proveedor_por_id


def obtener_compras(
    empresa_id: UUID,
    db: Session,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    proveedor_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Compra]:
    query = db.query(models.Compra).filter(
        models.Compra.empresa_id == empresa_id,
        models.Compra.is_active.is_(True),
    )
    if desde:
        query = query.filter(models.Compra.fecha_compra >= desde)
    if hasta:
        query = query.filter(models.Compra.fecha_compra <= hasta)
    if proveedor_id:
        query = query.filter(models.Compra.proveedor_id == proveedor_id)
    if estado:
        query = query.filter(models.Compra.estado == estado)

    return (
        query.options(
            joinedload(models.Compra.proveedor),
            joinedload(models.Compra.usuario),
            joinedload(models.Compra.detalles).joinedload(models.DetalleCompra.producto),
        )
        .order_by(models.Compra.fecha_compra.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_compra_por_id(empresa_id: UUID, compra_id: UUID, db: Session) -> models.Compra:
    compra = (
        db.query(models.Compra)
        .filter(
            models.Compra.id == compra_id,
            models.Compra.empresa_id == empresa_id,
            models.Compra.is_active.is_(True),
        )
        .options(
            joinedload(models.Compra.proveedor),
            joinedload(models.Compra.usuario),
            joinedload(models.Compra.detalles).joinedload(models.DetalleCompra.producto),
        )
        .first()
    )
    if not compra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada",
        )
    return compra


def registrar_compra(
    empresa_id: UUID,
    data: CompraCrear,
    current_user: models.Usuario,
    db: Session,
) -> CompraRespuesta:
    # 1. Validar que el proveedor exista y pertenezca a la empresa
    proveedor = obtener_proveedor_por_id(empresa_id, data.proveedor_id, db)

    metodo_pago = data.metodo_pago.upper()
    if metodo_pago == "CREDITO" and not data.fecha_vencimiento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de vencimiento es requerida para compras a crédito",
        )

    # 2. Inicializar la compra
    compra_estado = "PENDIENTE" if metodo_pago == "CREDITO" else "PAGADA"
    nueva_compra = models.Compra(
        empresa_id=empresa_id,
        proveedor_id=proveedor.id,
        usuario_id=current_user.id,
        numero_factura=data.numero_factura,
        metodo_pago=metodo_pago,
        fecha_vencimiento=data.fecha_vencimiento if metodo_pago == "CREDITO" else None,
        estado=compra_estado,
        total=Decimal("0.00"),
    )
    db.add(nueva_compra)
    db.flush()  # Obtener ID de compra

    total_acumulado = Decimal("0.00")
    detalles_resp = []

    try:
        # 3. Procesar productos
        for item in data.items:
            producto = (
                db.query(models.Producto)
                .filter(
                    models.Producto.id == item.producto_id,
                    models.Producto.empresa_id == empresa_id,
                    models.Producto.is_active.is_(True),
                )
                .with_for_update()  # Lock de fila
                .first()
            )
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto '{item.producto_id}' no encontrado o no pertenece a la empresa",
                )

            subtotal_linea = item.cantidad * item.precio_costo
            total_acumulado += subtotal_linea

            # Crear detalle
            nuevo_detalle = models.DetalleCompra(
                compra_id=nueva_compra.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_costo=item.precio_costo,
                subtotal=subtotal_linea,
            )
            db.add(nuevo_detalle)

            # Efectos de inventario: Incrementar stock y actualizar costo más reciente
            producto.cantidad_actual += item.cantidad
            producto.precio_costo = item.precio_costo

            detalles_resp.append(
                DetalleCompraRespuesta(
                    id=uuid_generador_temporal(),  # Temporal hasta flush/commit
                    producto_id=producto.id,
                    nombre=producto.nombre,
                    cantidad=item.cantidad,
                    precio_costo=item.precio_costo,
                    subtotal=subtotal_linea,
                )
            )

        nueva_compra.total = total_acumulado

        # 4. Crear Cuenta por Pagar si es a Crédito
        cuenta_pagar_id = None
        if metodo_pago == "CREDITO":
            nueva_cxp = models.CuentaPorPagar(
                empresa_id=empresa_id,
                compra_id=nueva_compra.id,
                proveedor_id=proveedor.id,
                monto_total=total_acumulado,
                saldo_pendiente=total_acumulado,
                fecha_vencimiento=data.fecha_vencimiento,
                estado="PENDIENTE",
            )
            db.add(nueva_cxp)
            db.flush()
            cuenta_pagar_id = nueva_cxp.id

        db.commit()

        # Actualizar IDs reales en respuesta
        db.refresh(nueva_compra)
        for i, det_db in enumerate(nueva_compra.detalles):
            detalles_resp[i].id = det_db.id

        return CompraRespuesta(
            id=nueva_compra.id,
            numero_factura=nueva_compra.numero_factura,
            fecha_compra=nueva_compra.fecha_compra,
            metodo_pago=nueva_compra.metodo_pago,
            fecha_vencimiento=nueva_compra.fecha_vencimiento,
            estado=nueva_compra.estado,
            total=nueva_compra.total,
            detalles=detalles_resp,
            cuenta_por_pagar_id=cuenta_pagar_id,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al registrar la compra y actualizar inventario",
        ) from exc


def anular_compra(empresa_id: UUID, compra_id: UUID, db: Session) -> bool:
    compra = obtener_compra_por_id(empresa_id, compra_id, db)

    if compra.estado == "ANULADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta compra ya se encuentra anulada",
        )

    try:
        # 1. Reversar stock de productos con lock de base de datos
        for detalle in compra.detalles:
            producto = (
                db.query(models.Producto)
                .filter(
                    models.Producto.id == detalle.producto_id,
                    models.Producto.empresa_id == empresa_id,
                    models.Producto.is_active.is_(True),
                )
                .with_for_update()
                .first()
            )
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto '{detalle.producto_id}' no encontrado al reversar stock",
                )

            # Validar que el stock no quede negativo (mercancía ya vendida)
            if producto.cantidad_actual < detalle.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"No se puede anular la compra. El producto '{producto.nombre}' "
                        f"ya se ha vendido y el stock actual ({producto.cantidad_actual}) "
                        f"es menor que la cantidad comprada ({detalle.cantidad})"
                    ),
                )

            # Restar del stock
            producto.cantidad_actual -= detalle.cantidad
            detalle.is_active = False

        # 2. Anular cuentas por pagar asociadas si las hay
        if compra.cuenta_por_pagar:
            compra.cuenta_por_pagar.is_active = False
            compra.cuenta_por_pagar.estado = "PAGADA"  # Para propósitos de lógica de saldo
            compra.cuenta_por_pagar.saldo_pendiente = Decimal("0.00")
            for abono in compra.cuenta_por_pagar.abonos:
                abono.is_active = False

        # 3. Cambiar estado de la compra a ANULADA
        compra.estado = "ANULADA"
        compra.is_active = False

        db.commit()
        return True

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la anulación de la compra",
        ) from exc


def uuid_generador_temporal() -> UUID:
    import uuid
    return uuid.uuid4()
