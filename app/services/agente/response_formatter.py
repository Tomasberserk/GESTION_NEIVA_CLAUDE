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
    stock_actual = preview.get("stock_actual", 0)
    nuevo_stock = preview.get("stock_nuevo", stock_actual + cant)
    nuevo_costo = preview.get("nuevo_precio_costo")
    costo_anterior = preview.get("precio_costo_anterior")
    nuevo_venta = preview.get("nuevo_precio_venta")
    venta_actual = preview.get("precio_venta_actual")

    lineas = [
        f"Voy a registrar el siguiente reabastecimiento:",
        f"• Producto: {nom}",
        f"• Entrada: +{cant} {unidad} (Stock pasará de {stock_actual} a {nuevo_stock} {unidad})",
    ]

    if nuevo_costo is not None:
        costo_str = fmt_moneda(nuevo_costo)
        if costo_anterior is not None:
            lineas.append(f"• Nuevo costo: {costo_str} (antes {fmt_moneda(costo_anterior)})")
        else:
            lineas.append(f"• Nuevo costo: {costo_str}")

        ref_venta = nuevo_venta if nuevo_venta is not None else venta_actual
        if ref_venta and ref_venta > 0:
            margen = round(((float(ref_venta) - float(nuevo_costo)) / float(ref_venta)) * 100, 1)
            lineas.append(f"• Precio de venta: {fmt_moneda(ref_venta)} (Margen: {margen}%)")
            if margen < 15:
                lineas.append(f"⚠️ Alerta: El margen con este nuevo costo es bajo ({margen}%).")

    if nuevo_venta is not None:
        lineas.append(f"• Nuevo precio de venta al público: {fmt_moneda(nuevo_venta)}")

    lineas.append("\n¿Deseas confirmar la operación?")
    return "\n".join(lineas)


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
    detalles = [f"Stock actualizado. Ahora tienes {nuevo_stock} {unidad} de {nom}."]
    if result.get("nuevo_precio_costo"):
        detalles.append(f"Nuevo precio de costo fijado en {fmt_moneda(result['nuevo_precio_costo'])}.")
    if result.get("nuevo_precio_venta"):
        detalles.append(f"Nuevo precio de venta fijado en {fmt_moneda(result['nuevo_precio_venta'])}.")
    return " ".join(detalles)


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


def formatear_menu_capacidades(usuario: Any = None) -> str:
    """Devuelve el menú de capacidades y comandos de voz diferenciado por rol."""
    nombre = getattr(usuario, "nombre", None) or "Usuario"
    rol = getattr(usuario, "rol", "tendero")
    if hasattr(rol, "value"):
        rol = rol.value
    rol_str = str(rol).lower()

    if rol_str == "admin":
        return (
            f"👑 Asistente POS — Modo Administrador (Control Total)\n\n"
            f"Hola {nombre}, tienes acceso a todas las funciones operativas, de inventario y financieras del negocio:\n\n"
            f"1. 📦 Reabastecimiento y Precios:\n"
            f"• Entrada con nuevo costo: 'Hoy me reabastecí de 10 aceites a 11.000 precio costo'\n"
            f"• Entrada y cambio de venta: 'Llegaron 20 leches a 3.200 costo y venta a 4.000'\n"
            f"• Modificar precios: 'Cambiar precio de venta de Coca-Cola a 5.000'\n\n"
            f"2. 📊 Finanzas y Caja:\n"
            f"• Resumen del día: '¿Cuánto hemos vendido hoy?' o '¿Cuál es el recaudo de hoy?'\n"
            f"• Comparativas: 'Comparar ventas de hoy vs ayer'\n"
            f"• Rendimiento por vendedor: '¿Cuánto ha vendido Pedro hoy?'\n"
            f"• Arqueo y balance: 'Ventas de la semana' o 'Recuperación de inversión'\n\n"
            f"3. 🔍 Inventario y Rotación:\n"
            f"• Alertas críticas: '¿Qué productos están agotados o por acabarse?'\n"
            f"• Vencimientos: '¿Qué está próximo a vencer este mes?'\n"
            f"• Rotación: '¿Cuál es el producto más vendido de la semana?'\n\n"
            f"4. 🛒 Operación de Mostrador:\n"
            f"• Registrar ventas directamente: 'Vendí 2 arroces y 1 aceite'.\n\n"
            f"¿Qué gestión deseas realizar ahora?"
        )
    else:
        return (
            f"👋 Asistente POS — Modo Mostrador (Atención al Cliente)\n\n"
            f"Hola {nombre}, estas son tus herramientas disponibles para la atención rápida en caja:\n\n"
            f"1. 🛒 Registrar Ventas Rápidas:\n"
            f"• Por unidades: 'Vendí 2 Coca-Colas y un paquete de papas'\n"
            f"• Por peso o granel: 'Libra y media de frijol y kilo de arroz'\n"
            f"• Dictado continuo de tickets de clientes.\n\n"
            f"2. 💲 Consulta de Precios al Público:\n"
            f"• '¿Cuánto vale el Aceite Gourmet?'\n"
            f"• '¿A cómo está la cubeta de huevos?'\n\n"
            f"3. 📦 Consulta de Existencias (Stock):\n"
            f"• '¿Cuánto Arroz Diana queda en bodega?'\n"
            f"• '¿Hay existencias de leche entera?'\n\n"
            f"4. ⏰ Vencimientos en Mostrador:\n"
            f"• '¿Qué productos están próximos a vencer?' (para rotar primero en estante)\n\n"
            f"5. 🧾 Tus Ventas del Turno:\n"
            f"• '¿Cuántas ventas llevo registradas hoy?'\n"
            f"• '¿Cuál fue mi última venta?'\n\n"
            f"ℹ️ Nota: Para ingresar compras a proveedores, cambiar precios o consultar reportes financieros de la tienda, solicita apoyo a tu administrador.\n\n"
            f"¿Qué producto deseas consultar o vender?"
        )


def formatear_bloqueo_rbac(accion: str, usuario: Any = None) -> str:
    """Mensaje amigable y pedagógico cuando un empleado intenta una acción administrativa."""
    nombre = getattr(usuario, "nombre", None) or "compañero"

    if accion in ["reabastecer", "compras"]:
        return (
            f"🔒 {nombre}, como tendero tienes acceso al mostrador para ventas y consulta de existencias. "
            f"El reabastecimiento de mercancía y actualización de costos de compra están reservados para el administrador."
        )
    elif accion in ["modificar_precio", "cambiar_precio"]:
        return (
            f"🔒 {nombre}, no tienes permisos para modificar precios. "
            f"Los precios de costo y de venta al público solo pueden ser modificados por el administrador de la tienda."
        )
    elif accion in ["crear_producto"]:
        return (
            f"🔒 {nombre}, el alta de nuevos productos en el catálogo debe realizarse por el administrador de la tienda."
        )
    elif accion in ["consulta_financiera_global", "comparacion"]:
        return (
            f"🔒 {nombre}, las métricas financieras globales de la tienda y comparativas son confidenciales del administrador. "
            f"Puedes consultarme cuántas ventas has registrado tú en tu turno diciendo: '¿Cuántas ventas llevo hoy?'."
        )
    elif accion in ["ventas_otro_vendedor"]:
        return (
            f"🔒 {nombre}, solo tienes acceso para consultar tus propias ventas registradas en el turno."
        )

    return f"🔒 {nombre}, esta acción requiere permisos de administrador."


def formatear_productos_proximos_vencer(datos: dict[str, Any]) -> str:
    """Formatea la lista de productos próximos a vencer o vencidos."""
    prods = datos.get("productos", [])
    if not prods:
        dias = datos.get("dias_horizonte", 30)
        return f"No tienes productos registrados próximos a vencer en los próximos {dias} días."

    lineas = [f"Tienes {len(prods)} producto(s) en alerta de vencimiento:"]
    for p in prods:
        dias = p["dias_restantes"]
        if dias < 0:
            alerta = f"⚠️ VENCIDO (hace {abs(dias)} días - {p['fecha_vencimiento']})"
        elif dias == 0:
            alerta = f"🚨 VENCE HOY ({p['fecha_vencimiento']})"
        elif dias == 1:
            alerta = f"⚠️ Vence mañana ({p['fecha_vencimiento']})"
        else:
            alerta = f"vence en {dias} días ({p['fecha_vencimiento']})"
        lineas.append(f"• {p['nombre']}: {alerta}, stock disponible: {p['cantidad_actual']} {p['unidad']}.")

    return "\n".join(lineas)

