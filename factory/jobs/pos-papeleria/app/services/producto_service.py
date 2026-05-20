import os
import uuid as uuid_lib
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.producto import ProductoActualizar, ProductoCrear

_EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "webp"}


def _obtener_producto_activo(
    producto_id: UUID, empresa_id: UUID, db: Session
) -> models.Producto:
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id,
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    ).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto


def _validar_codigo_barras_unico(
    codigo_barras: str,
    empresa_id: UUID,
    db: Session,
    excluir_id: UUID | None = None,
) -> None:
    # Barcode único por empresa (multi-tenant): dos tiendas pueden tener el mismo código
    query = db.query(models.Producto).filter(
        models.Producto.codigo_barras == codigo_barras,
        models.Producto.empresa_id == empresa_id,
    )
    if excluir_id:
        query = query.filter(models.Producto.id != excluir_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el código '{codigo_barras}' en esta tienda",
        )


def crear_producto(data: ProductoCrear, db: Session) -> models.Producto:
    if not db.query(models.Empresa).filter(
        models.Empresa.id == data.empresa_id,
        models.Empresa.is_active.is_(True),
    ).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    _validar_codigo_barras_unico(data.codigo_barras, data.empresa_id, db)

    producto = models.Producto(
        empresa_id=data.empresa_id,
        nombre=data.nombre,
        codigo_barras=data.codigo_barras,
        precio_costo=data.precio_costo,
        precio_venta=data.precio_venta,
        cantidad_actual=data.cantidad_actual,
        unidad_medida=data.unidad_medida,
        categoria=data.categoria,
        stock_minimo=data.stock_minimo,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def obtener_productos_empresa(empresa_id: UUID, db: Session) -> dict:
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == empresa_id,
        models.Empresa.is_active.is_(True),
    ).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    productos = db.query(models.Producto).filter(
        models.Producto.empresa_id == empresa_id,
        models.Producto.is_active.is_(True),
    ).all()

    return {
        "tienda": empresa.nombre_comercial,
        "total_items": len(productos),
        "inventario": productos,
    }


def actualizar_producto(
    producto_id: UUID,
    empresa_id: UUID,
    data: ProductoActualizar,
    db: Session,
) -> models.Producto:
    producto = _obtener_producto_activo(producto_id, empresa_id, db)

    if data.codigo_barras and data.codigo_barras != producto.codigo_barras:
        _validar_codigo_barras_unico(data.codigo_barras, empresa_id, db, excluir_id=producto_id)

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(producto_id: UUID, empresa_id: UUID, db: Session) -> None:
    producto = _obtener_producto_activo(producto_id, empresa_id, db)
    producto.is_active = False
    db.commit()


async def guardar_imagen_producto(
    producto_id: UUID,
    empresa_id: UUID,
    file: UploadFile,
    db: Session,
) -> str:
    producto = _obtener_producto_activo(producto_id, empresa_id, db)

    extension = (
        file.filename.rsplit(".", 1)[-1].lower()
        if file.filename and "." in file.filename
        else ""
    )
    if extension not in _EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión no permitida. Usa: {', '.join(_EXTENSIONES_PERMITIDAS)}",
        )

    upload_dir = os.getenv("UPLOAD_DIR", "media")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid_lib.uuid4()}.{extension}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    producto.foto_url = f"/media/{filename}"
    db.commit()
    return producto.foto_url
