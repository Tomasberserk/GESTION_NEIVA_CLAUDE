from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schemas.venta import VentaCrear, VentaResumen


def registrar_venta(
    empresa_id: UUID,
    data: VentaCrear,
    current_user: models.Usuario,
    db: Session,
) -> VentaResumen:
    """
    Registra una venta completa en una transacción ACID.

    Patrón: flush (obtener id) → por cada item: lock → validar → descontar
            → agregar detalle → commit. Si algo falla: rollback total.
    """
    # 1. Multi-tenant: el usuario solo puede operar en su propia empresa
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para operar en esta empresa",
        )

    # 2. Crear el documento maestro de venta con total provisional = 0
    nueva_venta = models.Venta(empresa_id=empresa_id, total=Decimal("0.00"))
    db.add(nueva_venta)
    # flush: escribe en la transacción activa sin hacer commit,
    # para obtener el UUID asignado por PostgreSQL
    db.flush()

    total_venta = Decimal("0.00")

    try:
        for item in data.detalles:
            # 3a. LOCK de fila: previene race conditions cuando dos ventas
            #     simultáneas intentan usar el mismo producto
            producto = (
                db.query(models.Producto)
                .filter(
                    models.Producto.id == item.producto_id,
                    models.Producto.empresa_id == empresa_id,
                    models.Producto.is_active.is_(True),
                )
                .with_for_update()
                .first()
            )

            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Producto '{item.producto_id}' no encontrado "
                        "o no pertenece a esta empresa"
                    ),
                )

            # 3b. Validar stock DESPUÉS del lock (no antes), para evitar
            #     que otro proceso modifique el stock entre la lectura y
            #     el descuento
            if producto.cantidad_actual < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.cantidad_actual}, "
                        f"Solicitado: {item.cantidad}"
                    ),
                )

            # 3c. Descontar stock
            producto.cantidad_actual -= item.cantidad

            # 3d. Calcular subtotal usando Decimal para evitar errores de
            #     punto flotante en acumulación
            subtotal = producto.precio_venta * item.cantidad
            total_venta += subtotal

            # 3e. Crear línea de detalle con precio_unitario congelado:
            #     si el precio cambia mañana, esta venta conserva el precio
            #     histórico del momento de la transacción
            detalle = models.DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio_venta,
                subtotal=subtotal,
            )
            db.add(detalle)

        # 4. Actualizar el total en el documento maestro
        nueva_venta.total = total_venta

        # 5. COMMIT: persiste todos los cambios (venta + detalles + stocks)
        db.commit()

    except HTTPException:
        # Rollback explícito: deshace el flush y todos los cambios en la sesión
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la venta",
        ) from exc

    return VentaResumen(
        mensaje="Venta registrada exitosamente",
        total=float(total_venta),
        venta_id=nueva_venta.id,
    )


def obtener_ventas_empresa(empresa_id: UUID, db: Session) -> list:
    if not db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.is_active.is_(True),
    ).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    return (
        db.query(models.Venta)
        .filter(
            models.Venta.empresa_id == empresa_id,
            models.Venta.is_active.is_(True),
        )
        # joinedload: carga detalles + productos en una sola query (evita N+1)
        # y asegura que DetalleVentaRespuesta.modelo_validator encuentre
        # detalle.producto cargado
        .options(
            joinedload(models.Venta.detalles).joinedload(models.DetalleVenta.producto)
        )
        .order_by(models.Venta.fecha_venta.desc())
        .all()
    )
