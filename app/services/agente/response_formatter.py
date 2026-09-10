"""Formateador determinístico de respuestas en español natural para el Agente.

Cero llamadas a LLM para redacción: garantiza respuestas rápidas, predecibles,
amables y con cifras exactas sin costo de inferencia ni riesgo de alucinación.
"""

from typing import Any


def fmt_moneda(valor: float | int) -> str:
    """Formatea un valor numérico como moneda colombiana: $15.000"""
    try:
        val_float = float(valor)
        return f"${val_float:,.0f}".replace(",", ".")
    except Exception:
        return f"${valor}"


def formatear_confirmacion_venta(preview: dict[str, Any]) -> str:
    items = preview.get("items", [])
    total_str = fmt_moneda(preview.get("total", 0))

    lineas = []
    for item in items:
        nom = item.get("nombre", "Producto")
        cant = item.get("cantidad", 1)
        sub = fmt_moneda(item.get("subtotal", 0))
        lineas.append(f"• {cant} × {nom} ({sub})")

    detalle = "\n".join(lineas)
    return (
        f"Voy a registrar la siguiente venta:\n{detalle}\n"
        f"Total: {total_str}\n\n¿Confirmar?"
    )


def formatear_confirmacion_reabastecer(preview: dict[str, Any]) -> str:
    nom = preview.get("producto", "Producto")
    cant = preview.get("cantidad", 0)
    unidad = preview.get("unidad", "unidades")
    return f"Voy a agregar {cant} {unidad} a {nom}.\n\n¿Confirmar?"


def formatear_confirmacion_crear_producto(preview: dict[str, Any]) -> str:
    nom = preview.get("nombre", "Nuevo Producto")
    precio_venta = fmt_moneda(preview.get("precio_venta", 0))
    precio_costo = fmt_moneda(preview.get("precio_costo", 0))
    cant = preview.get("cantidad_actual", 0)
    unidad = preview.get("unidad_medida", "unidad")

    return (
        f"Voy a registrar el nuevo producto:\n"
        f"• {nom}\n"
        f"• Precio de venta: {precio_venta}\n"
        f"• Precio de costo: {precio_costo}\n"
        f"• Stock inicial: {cant} {unidad}\n\n"
        f"¿Confirmar?"
    )


def formatear_exito_venta(result: dict[str, Any]) -> str:
    total_str = fmt_moneda(result.get("total", 0))
    return f"✅ Venta registrada exitosamente por {total_str}."


def formatear_exito_reabastecer(result: dict[str, Any]) -> str:
    nom = result.get("producto", "Producto")
    nuevo_stock = result.get("stock_nuevo", 0)
    unidad = result.get("unidad", "unidades")
    return f"✅ Stock actualizado. Ahora tienes {nuevo_stock} {unidad} de {nom}."


def formatear_exito_crear_producto(result: dict[str, Any]) -> str:
    nom = result.get("nombre", "Producto")
    precio = fmt_moneda(result.get("precio_venta", 0))
    stock = result.get("stock_inicial", 0)
    return f"✅ Producto {nom} registrado exitosamente con precio de {precio} y {stock} unidades."


def formatear_consulta_ventas(datos: dict[str, Any]) -> str:
    periodo = datos.get("periodo", "hoy")
    total = fmt_moneda(datos.get("total", 0))
    cantidad = datos.get("cantidad_transacciones", 0)

    if cantidad == 0:
        return f"En el periodo de {periodo} no has registrado ninguna venta todavía."

    return f"En {periodo} has vendido {total} en {cantidad} transacciones."


def formatear_consulta_recaudo(datos: dict[str, Any]) -> str:
    recaudo = fmt_moneda(datos.get("recaudo_hoy", 0))
    ventas_count = datos.get("cantidad_ventas", 0)
    return (
        f"El dinero total ingresado por ventas hoy es de {recaudo} ({ventas_count} ventas realizadas). "
        "Recuerda que esto corresponde al recaudo bruto, no a tu ganancia neta."
    )


def formatear_consulta_inventario(datos: dict[str, Any]) -> str:
    skus = datos.get("total_productos", 0)
    valor = fmt_moneda(datos.get("valor_total_costo", 0))
    return f"Tienes {skus} productos activos en tu tienda, con una inversión estimada en mercancía de {valor} (a precio de costo)."


def formatear_consulta_stock(datos: dict[str, Any]) -> str:
    nom = datos.get("nombre", "Producto")
    stock = datos.get("cantidad_actual", 0)
    unidad = datos.get("unidad", "unidades")
    precio = fmt_moneda(datos.get("precio_venta", 0))

    if stock <= 0:
        return f"De {nom} NO tienes existencias actualmente (Stock: 0 {unidad}). Precio: {precio}."
    return f"De {nom} te quedan {stock} {unidad} disponibles a un precio de {precio}."


def formatear_resumen_actual(datos: dict[str, Any]) -> str:
    ventas_hoy = fmt_moneda(datos.get("ventas_hoy", 0))
    count = datos.get("cantidad_ventas_hoy", 0)
    stock_bajo = datos.get("productos_stock_bajo", 0)
    por_vencer = datos.get("productos_por_vencer", 0)

    lineas = [
        f"📊 Resumen del día:",
        f"• Ventas hoy: {ventas_hoy} ({count} transacciones)",
    ]
    if stock_bajo > 0:
        lineas.append(f"• Alerta: {stock_bajo} producto(s) con stock crítico.")
    if por_vencer > 0:
        lineas.append(f"• Alerta: {por_vencer} producto(s) próximos a vencer en 15 días.")

    return "\n".join(lineas)


def formatear_recuperacion_inversion(datos: dict[str, Any]) -> str:
    inventario_val = fmt_moneda(datos.get("inventario_costo", 0))
    ventas_hoy = fmt_moneda(datos.get("ventas_hoy", 0))

    return (
        f"Actualmente tienes {inventario_val} invertidos en inventario en estantería "
        f"y has generado {ventas_hoy} en ventas hoy. "
        "Para calcular exactamente cuánto te falta para recuperar tu inversión se requiere "
        "registrar tu capital inicial en la configuración del negocio."
    )


def formatear_stock_insuficiente(nombre: str, disponible: float, solicitado: float) -> str:
    return (
        f"❌ No hay suficiente stock para '{nombre}'. "
        f"Tienes {disponible} disponibles e intentaste vender {solicitado}."
    )


def formatear_precio_cambiado(nombre: str, precio_anterior: float, precio_nuevo: float, total_nuevo: float) -> str:
    p_ant = fmt_moneda(precio_anterior)
    p_nue = fmt_moneda(precio_nuevo)
    tot = fmt_moneda(total_nuevo)
    return (
        f"⚠️ El precio de '{nombre}' cambió de {p_ant} a {p_nue} mientras confirmabas. "
        f"El nuevo total es {tot}. ¿Deseas confirmar la venta con este nuevo precio?"
    )


def formatear_cancelacion() -> str:
    return "Operación cancelada. No se realizó ningún cambio en el inventario ni en las ventas."


def formatear_fuera_de_alcance() -> str:
    return "Solo puedo ayudarte con las operaciones de tu tienda: registrar ventas, reabastecer stock, consultar precios e inventario."


def formatear_operacion_destructiva_bloqueada() -> str:
    return "Por motivos de seguridad, la eliminación de productos está deshabilitada mediante comandos de voz o texto. Puedes hacerlo desde el panel web de Inventario."
