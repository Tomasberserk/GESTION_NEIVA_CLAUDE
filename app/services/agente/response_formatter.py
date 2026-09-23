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
    return f"Venta registrada exitosamente por {total_str}."


def formatear_exito_reabastecer(result: dict[str, Any]) -> str:
    nom = result.get("producto", "Producto")
    nuevo_stock = result.get("stock_nuevo", 0)
    unidad = result.get("unidad", "unidades")
    return f"Stock actualizado. Ahora tienes {nuevo_stock} {unidad} de {nom}."


def formatear_exito_crear_producto(result: dict[str, Any]) -> str:
    nom = result.get("nombre", "Producto")
    precio = fmt_moneda(result.get("precio_venta", 0))
    stock = result.get("stock_inicial", 0)
    return f"Producto {nom} registrado exitosamente con precio de {precio} y {stock} unidades."


def formatear_consulta_ventas(datos: dict[str, Any]) -> str:
    periodo = datos.get("periodo", "hoy")
    total = fmt_moneda(datos.get("total", 0))
    cantidad = datos.get("cantidad_transacciones", 0)

    if cantidad == 0:
        return f"En el periodo de {periodo} no has registrado ninguna venta todavía."

    return f"En {periodo} has vendido {total} en {cantidad} transacciones."


def formatear_consulta_ventas_vendedor(datos: dict[str, Any]) -> str:
    if not datos.get("encontrado"):
        vend = datos.get("vendedor", "el usuario")
        return f"No encontré a ningún cajero registrado como '{vend}' en tu tienda."

    vend = datos.get("vendedor", "Cajero")
    total = fmt_moneda(datos.get("total", 0))
    cant = datos.get("cantidad_transacciones", 0)
    per = datos.get("periodo", "hoy")
    return f"El cajero {vend} ha registrado ventas por {total} en {cant} transacciones en el periodo de {per}."


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


def formatear_conteo_productos(datos: dict[str, Any]) -> str:
    total = datos.get("total_activos", 0)
    return f"Tienes {total} productos activos registrados en el catálogo de tu tienda."


def formatear_consulta_stock(datos: dict[str, Any]) -> str:
    nom = datos.get("nombre", "Producto")
    stock = datos.get("cantidad_actual", 0)
    unidad = datos.get("unidad", "unidades")
    precio = fmt_moneda(datos.get("precio_venta", 0))

    if stock <= 0:
        return f"De {nom} NO tienes existencias actualmente (Stock: 0 {unidad}). Precio: {precio}."
    return f"De {nom} te quedan {stock} {unidad} disponibles a un precio de {precio}."


def formatear_consulta_precio(datos: dict[str, Any]) -> str:
    nom = datos.get("nombre", "Producto")
    precio = fmt_moneda(datos.get("precio_venta", 0))
    stock = datos.get("cantidad_actual", 0)
    unidad = datos.get("unidad", "unidades")
    return f"El precio de venta de {nom} es de {precio}. Te quedan {stock} {unidad} disponibles en inventario."


def formatear_productos_agotados(datos: dict[str, Any]) -> str:
    total = datos.get("total_agotados", 0)
    prods = datos.get("productos", [])

    if total == 0:
        return "No tienes productos agotados en tu tienda actualmente. Todo el catálogo tiene existencias."

    lineas = [f"Tienes {total} producto(s) agotados (existencia en cero):"]
    for p in prods:
        nom = p.get("nombre")
        pr = fmt_moneda(p.get("precio_venta", 0))
        lineas.append(f"• {nom} (Stock: 0, Precio: {pr})")

    lineas.append("Te sugiero reabastecerlos para no perder ventas de mostrador.")
    return "\n".join(lineas)


def formatear_productos_stock_bajo(datos: dict[str, Any]) -> str:
    total = datos.get("total_stock_bajo", 0)
    umbral = datos.get("umbral", 5.0)
    prods = datos.get("productos", [])

    if total == 0:
        return f"Todo tu inventario está en buen nivel. No hay productos con stock bajo (menos de {umbral:.0f} unidades)."

    lineas = [f"Tienes {total} producto(s) con stock bajo (menos de {umbral:.0f} unidades):"]
    for p in prods:
        nom = p.get("nombre")
        cant = p.get("cantidad_actual", 0)
        unid = p.get("unidad", "unidades")
        lineas.append(f"• {nom}: quedan solo {cant} {unid}")

    lineas.append("Te sugiero hacer pedido pronto.")
    return "\n".join(lineas)


def formatear_top_ventas(datos: dict[str, Any]) -> str:
    per = datos.get("periodo", "hoy")
    top = datos.get("top_1")
    prods = datos.get("productos", [])

    if not top:
        return f"En el periodo de {per} no se registran ventas de productos todavía."

    nom = top.get("nombre")
    cant = top.get("unidades_vendidas", 0)
    tot = fmt_moneda(top.get("total_facturado", 0))

    lineas = [f"El producto más vendido en {per} es '{nom}' con {cant:.0f} unidades vendidas ({tot})."]
    if len(prods) > 1:
        lineas.append("Otros productos destacados:")
        for p in prods[1:4]:
            p_nom = p.get("nombre")
            p_cant = p.get("unidades_vendidas", 0)
            lineas.append(f"• {p_nom}: {p_cant:.0f} unidades")

    return "\n".join(lineas)


def formatear_menor_rotacion(datos: dict[str, Any]) -> str:
    return "Los productos con menor salida son aquellos que no han registrado ventas en los últimos días. Te sugiero revisar las promociones en tienda."


def formatear_comparacion_ventas(datos: dict[str, Any]) -> str:
    per_a = datos.get("periodo_a", "hoy")
    per_b = datos.get("periodo_b", "ayer")
    tot_a = fmt_moneda(datos.get("total_a", 0))
    tot_b = fmt_moneda(datos.get("total_b", 0))
    dif = fmt_moneda(abs(datos.get("diferencia", 0)))
    pct = datos.get("porcentaje_cambio", 0)
    mayor = datos.get("mayor")

    if mayor == "a":
        return f"Comparación de ventas: En {per_a} van {tot_a} frente a {tot_b} de {per_b}. Se vendió más en {per_a} por una diferencia de {dif} (+{pct}%)."
    elif mayor == "b":
        return f"Comparación de ventas: En {per_b} se vendieron {tot_b} frente a {tot_a} de {per_a}. En {per_b} superó a {per_a} por {dif}."
    else:
        return f"Comparación de ventas: Las ventas de {per_a} ({tot_a}) y {per_b} ({tot_b}) son exactamente iguales."


def formatear_comparacion_vendedores(datos: dict[str, Any]) -> str:
    per = datos.get("periodo", "hoy")
    ranking = datos.get("ranking", [])
    lider = datos.get("lider")

    if not ranking:
        return f"No hay cajeros con ventas registradas en {per}."

    lineas = [f"Comparación de ventas entre cajeros ({per}):"]
    for r in ranking:
        nom = r.get("nombre")
        tot = fmt_moneda(r.get("total", 0))
        trx = r.get("transacciones", 0)
        lineas.append(f"• {nom}: {tot} ({trx} ventas)")

    if lider:
        l_nom = lider.get("nombre")
        lineas.append(f"El cajero que más ha vendido es {l_nom}.")

    return "\n".join(lineas)


def formatear_comparacion_productos(prod_a: str, prod_b: str, datos: dict[str, Any]) -> str:
    return f"Comparación entre '{prod_a}' y '{prod_b}': Ambos productos están activos en catálogo. Puedes consultar sus existencias o ventas individuales."


def formatear_aclaracion_ambiguedad(ambiguity_type: str | None = None) -> str:
    t = (ambiguity_type or "").lower()
    if any(k in t for k in ["cuanto tenemos", "cuánto tenemos", "total", "cuanto hay", "cuánto hay"]):
        return "¿Te refieres al total de ventas de hoy o al valor total del inventario en tienda?"
    if any(k in t for k in ["como vamos", "cómo vamos", "como estamos", "cómo estamos"]):
        return "¿Te refieres a las ventas de hoy o al resumen general del día con alertas de stock?"
    if any(k in t for k in ["cuanto salio", "cuánto salió", "cuanto fue", "cuanto dio", "cuanto se hizo", "cuánto se hizo", "cuanto entro"]):
        return "¿Te refieres al total de dinero en ventas de hoy o a la salida de algún producto específico?"
    if any(k in t for k in ["ventas"]):
        return "¿Te refieres a las ventas de hoy, a las ventas de ayer o a las de la semana?"
    if any(k in t for k in ["stock", "cuanto queda", "cuánto queda", "hay o no hay"]):
        return "¿De qué producto específico deseas consultar el stock o la existencia?"
    if any(k in t for k in ["reporte"]):
        return "¿Te refieres a ver el resumen del día, el producto más vendido o los productos agotados?"
    if any(k in t for k in ["inventario", "que falta", "qué falta"]):
        return "¿Te refieres a los productos agotados, a los que tienen stock bajo o al valor total invertido?"
    if any(k in t for k in ["a como", "a cómo"]):
        return "¿De qué producto deseas consultar el precio de venta?"

    return "¿A qué te refieres? Puedes consultar ventas de hoy, stock de un producto o el resumen del día."


def formatear_resumen_actual(datos: dict[str, Any]) -> str:
    ventas_hoy = fmt_moneda(datos.get("ventas_hoy", 0))
    count = datos.get("cantidad_ventas_hoy", 0)
    stock_bajo = datos.get("productos_stock_bajo", 0)
    por_vencer = datos.get("productos_por_vencer", 0)

    lineas = [
        "Resumen del día:",
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
        f"No hay suficiente stock para '{nombre}'. "
        f"Tienes {disponible} disponibles e intentaste vender {solicitado}."
    )


def formatear_precio_cambiado(nombre: str, precio_anterior: float, precio_nuevo: float, total_nuevo: float) -> str:
    p_ant = fmt_moneda(precio_anterior)
    p_nue = fmt_moneda(precio_nuevo)
    tot = fmt_moneda(total_nuevo)
    return (
        f"El precio de '{nombre}' cambió de {p_ant} a {p_nue} mientras confirmabas. "
        f"El nuevo total es {tot}. ¿Deseas confirmar la venta con este nuevo precio?"
    )


def formatear_cancelacion() -> str:
    return "Operación cancelada. No se realizó ningún cambio en el inventario ni en las ventas."


def formatear_fuera_de_alcance() -> str:
    return "Solo puedo ayudarte con la gestión de tu tienda y las operaciones del POS: registrar ventas, stock, precios, inventario y finanzas de tu negocio."


def formatear_operacion_destructiva_bloqueada() -> str:
    return "Por motivos de seguridad, la eliminación de productos está deshabilitada mediante comandos de voz o texto. Puedes hacerlo desde el panel web de Inventario."
