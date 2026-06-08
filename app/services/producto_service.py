import os
import uuid as uuid_lib
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.schemas.producto import ProductoActualizar, ProductoCrear

_EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "webp"}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _obtener_producto_activo(
    producto_id: UUID, empresa_id: UUID, db: Session
) -> models.Producto:
    """Busca el producto validando pertenencia a la empresa. Lanza 404 si no existe."""
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
    db: Session,
    excluir_id: UUID | None = None,
) -> None:
    """Lanza 409 si el código de barras ya está en uso por otro producto."""
    query = db.query(models.Producto).filter(
        models.Producto.codigo_barras == codigo_barras
    )
    if excluir_id:
        query = query.filter(models.Producto.id != excluir_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el código '{codigo_barras}'",
        )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def crear_producto(data: ProductoCrear, db: Session) -> models.Producto:
    # pre-check: empresa existe
    if not db.query(models.Empresa).filter(
        models.Empresa.id == data.empresa_id,
        models.Empresa.is_active.is_(True),
    ).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    # pre-check: código de barras único
    _validar_codigo_barras_unico(data.codigo_barras, db)

    producto = models.Producto(
        empresa_id=data.empresa_id,
        nombre=data.nombre,
        codigo_barras=data.codigo_barras,
        precio_costo=data.precio_costo,
        precio_venta=data.precio_venta,
        cantidad_actual=data.cantidad_actual,
        unidad_medida=data.unidad_medida,
        fecha_vencimiento=data.fecha_vencimiento,
        categoria=data.categoria,
        is_active=True,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def obtener_producto_por_id(
    producto_id: UUID, empresa_id: UUID, db: Session
) -> models.Producto:
    """Obtiene un producto específico validando pertenencia a la empresa."""
    return _obtener_producto_activo(producto_id, empresa_id, db)


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

    # pre-check: nuevo código de barras no colisiona con otro producto
    if data.codigo_barras and data.codigo_barras != producto.codigo_barras:
        _validar_codigo_barras_unico(data.codigo_barras, db, excluir_id=producto_id)

    # Solo actualiza los campos que el cliente envió (PATCH semántica)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(producto_id: UUID, empresa_id: UUID, db: Session) -> None:
    """Soft delete: pone is_active=False, no borra el registro físicamente."""
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

    # Validar extensión del archivo
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

    # 1. Leer el contenido y validar el tamaño límite (máx 5 MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo excede el tamaño máximo permitido de 5 MB",
        )

    # 2. Validar firma mágica binaria (Magic Bytes) para asegurar la integridad de la imagen
    es_imagen_valida = False
    if content.startswith(b"\xff\xd8\xff"):  # JPEG
        es_imagen_valida = True
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):  # PNG
        es_imagen_valida = True
    elif content.startswith(b"RIFF") and b"WEBP" in content[8:12]:  # WEBP
        es_imagen_valida = True

    if not es_imagen_valida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no es una imagen válida (debe ser un JPEG, PNG o WEBP real)",
        )

    upload_dir = os.getenv("UPLOAD_DIR", "media")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid_lib.uuid4()}.{extension}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    producto.foto_url = f"/media/{filename}"
    db.commit()
    return producto.foto_url
