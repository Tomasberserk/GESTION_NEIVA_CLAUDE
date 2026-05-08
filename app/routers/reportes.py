import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.services.venta_service import obtener_ventas_empresa

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_HEADER_FILL = PatternFill("solid", fgColor="A78BFA")   # neiva-purple
_HEADER_FONT = Font(bold=True, color="FFFFFF")


@router.get("/ventas/excel/{empresa_id}")
def exportar_ventas_excel(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado",
        )

    ventas = obtener_ventas_empresa(empresa_id, db)

    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"

    # Cabeceras
    columnas = [
        "ID Venta", "Fecha", "Producto",
        "Cantidad", "Precio Unitario", "Subtotal", "Total Venta",
    ]
    ws.append(columnas)

    for celda in ws[1]:
        celda.font = _HEADER_FONT
        celda.fill = _HEADER_FILL
        celda.alignment = Alignment(horizontal="center")

    # Filas de datos
    for venta in ventas:
        for detalle in venta.detalles:
            ws.append([
                str(venta.id),
                venta.fecha_venta.strftime("%Y-%m-%d %H:%M"),
                detalle.producto.nombre if detalle.producto else "",
                detalle.cantidad,
                float(detalle.precio_unitario),
                float(detalle.subtotal),
                float(venta.total),
            ])

    # Ajustar ancho de columnas automáticamente
    for col in ws.columns:
        max_len = max((len(str(c.value)) for c in col if c.value), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": f"attachment; filename=ventas_{empresa_id}.xlsx"
        },
    )
