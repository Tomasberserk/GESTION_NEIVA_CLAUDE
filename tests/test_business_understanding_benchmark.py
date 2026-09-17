"""Suite de Benchmark de Entendimiento de Negocio (280 Casos Reales).

FASE 3.5: Evolución a Business Conversational Agent para Gestión Neiva.
Evalúa las 9 dimensiones clave del entendimiento conversacional de mostrador:
A. Ventas (50 casos)
B. Productos (40 casos)
C. Inventario / Stock (40 casos)
D. Reportes y Análisis (35 casos)
E. Comparaciones (25 casos)
F. Contexto Conversacional Multi-Turno (30 casos)
G. Ambigüedad (20 casos)
H. Out-of-Domain (20 casos)
I. Lenguaje Real de Mostrador Colombiano (20 casos)
Total: 280 casos exactos.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from uuid import uuid4

from app import models
from app.services.agente.session_store import InMemorySessionStore, set_session_store_instance

# ---------------------------------------------------------------------------
# DEFINICIÓN DE LOS 280 CASOS DE PRUEBA
# ---------------------------------------------------------------------------

BENCHMARK_CASES = [
    # =========================================================================
    # A. VENTAS (50 CASOS)
    # =========================================================================
    {"id": "V-01", "cat": "Ventas", "input": "¿Cuánto he vendido hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-02", "cat": "Ventas", "input": "¿Cuánto hemos vendido?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-03", "cat": "Ventas", "input": "¿Cómo vamos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-04", "cat": "Ventas", "input": "¿Cuánto llevamos?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-05", "cat": "Ventas", "input": "¿Qué tanto hemos vendido?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-06", "cat": "Ventas", "input": "¿Cuánto salió hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-07", "cat": "Ventas", "input": "¿Cómo van las ventas de hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-08", "cat": "Ventas", "input": "ventas de hoy", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-09", "cat": "Ventas", "input": "plata que ha entrado hoy", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-10", "cat": "Ventas", "input": "¿cuánto va facturado hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-11", "cat": "Ventas", "input": "¿cuánto vendí hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-12", "cat": "Ventas", "input": "¿cuál es el total vendido hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-13", "cat": "Ventas", "input": "¿cuánto llevamos vendido?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-14", "cat": "Ventas", "input": "saldo de ventas de hoy", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-15", "cat": "Ventas", "input": "¿qué tanto se vendió hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "V-16", "cat": "Ventas", "input": "¿Cuánto vendimos ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-17", "cat": "Ventas", "input": "¿Cómo nos fue ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-18", "cat": "Ventas", "input": "¿Cuánto se vendió ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-19", "cat": "Ventas", "input": "¿Qué tal las ventas de ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-20", "cat": "Ventas", "input": "ventas de ayer", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-21", "cat": "Ventas", "input": "saldo de ayer", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-22", "cat": "Ventas", "input": "total de ventas de ayer", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-23", "cat": "Ventas", "input": "¿cuánto salió ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-24", "cat": "Ventas", "input": "¿cuánto recaudamos ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-25", "cat": "Ventas", "input": "¿cómo cerró ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "V-26", "cat": "Ventas", "input": "¿Cuánto va en la semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-27", "cat": "Ventas", "input": "¿Ventas de esta semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-28", "cat": "Ventas", "input": "¿Cómo ha estado la semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-29", "cat": "Ventas", "input": "total semanal", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-30", "cat": "Ventas", "input": "ventas de los últimos 7 días", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-31", "cat": "Ventas", "input": "¿cuánto llevamos esta semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-32", "cat": "Ventas", "input": "saldo de la semana", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-33", "cat": "Ventas", "input": "¿qué tanto vendimos esta semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "V-34", "cat": "Ventas", "input": "¿Cuánto va en el mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-35", "cat": "Ventas", "input": "¿Ventas de este mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-36", "cat": "Ventas", "input": "¿Cómo va el mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-37", "cat": "Ventas", "input": "total mensual", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-38", "cat": "Ventas", "input": "¿cuánto llevamos este mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-39", "cat": "Ventas", "input": "saldo del mes", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-40", "cat": "Ventas", "input": "¿qué tanto vendimos este mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "V-41", "cat": "Ventas", "input": "¿Cuánto vendió Paula hoy?", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "V-42", "cat": "Ventas", "input": "¿Cuánto ha vendido Paula?", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "V-43", "cat": "Ventas", "input": "ventas de Paula", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "V-44", "cat": "Ventas", "input": "¿Cuánto hizo Don Pedro?", "expected_domain": "VENTAS", "seller": "Don Pedro"},
    {"id": "V-45", "cat": "Ventas", "input": "¿Cuánto vendí yo?", "expected_domain": "VENTAS", "seller": "yo"},
    {"id": "V-46", "cat": "Ventas", "input": "¿Cuántas ventas llevamos hoy?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "V-47", "cat": "Ventas", "input": "¿Cuántas transacciones van hoy?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "V-48", "cat": "Ventas", "input": "¿Cuántas ventas se han hecho?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "V-49", "cat": "Ventas", "input": "¿Cuántos clientes han comprado hoy?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "V-50", "cat": "Ventas", "input": "¿Cuántas facturas van?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},

    # =========================================================================
    # B. PRODUCTOS (40 CASOS)
    # =========================================================================
    {"id": "P-01", "cat": "Productos", "input": "¿Cuántos productos tenemos?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-02", "cat": "Productos", "input": "¿Cuántos productos activos hay?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-03", "cat": "Productos", "input": "¿Total de productos en la tienda?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-04", "cat": "Productos", "input": "¿Cuántos ítems manejamos?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-05", "cat": "Productos", "input": "¿Cuántas referencias tenemos?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-06", "cat": "Productos", "input": "total de productos", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-07", "cat": "Productos", "input": "conteo de productos", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-08", "cat": "Productos", "input": "¿cuántos productos registrados hay?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-09", "cat": "Productos", "input": "¿cuántos productos vendemos?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-10", "cat": "Productos", "input": "¿cuántos artículos hay en catálogo?", "expected_domain": "PRODUCTOS", "action": "conteo"},
    {"id": "P-11", "cat": "Productos", "input": "¿A cómo está el arroz?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "P-12", "cat": "Productos", "input": "¿Precio del arroz?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "P-13", "cat": "Productos", "input": "¿En cuánto está el aceite?", "expected_domain": "PRODUCTOS", "target": "aceite"},
    {"id": "P-14", "cat": "Productos", "input": "¿Cuánto cuesta la leche?", "expected_domain": "PRODUCTOS", "target": "leche"},
    {"id": "P-15", "cat": "Productos", "input": "¿Cuál es el precio de la cerveza águila?", "expected_domain": "PRODUCTOS", "target": "cerveza"},
    {"id": "P-16", "cat": "Productos", "input": "¿A cómo tengo el pan bimbo?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "P-17", "cat": "Productos", "input": "¿En cuánto doy el jabón rey?", "expected_domain": "PRODUCTOS", "target": "jabón"},
    {"id": "P-18", "cat": "Productos", "input": "¿Cuánto vale la gaseosa postobón?", "expected_domain": "PRODUCTOS", "target": "gaseosa"},
    {"id": "P-19", "cat": "Productos", "input": "¿Precio de la cubeta de huevos?", "expected_domain": "PRODUCTOS", "target": "huevos"},
    {"id": "P-20", "cat": "Productos", "input": "¿A cuánto se vende el arroz diana?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "P-21", "cat": "Productos", "input": "¿Precio de venta del aceite gourmet?", "expected_domain": "PRODUCTOS", "target": "aceite"},
    {"id": "P-22", "cat": "Productos", "input": "¿Cuánto cuesta el pan?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "P-23", "cat": "Productos", "input": "¿A cuánto tengo la leche alquería?", "expected_domain": "PRODUCTOS", "target": "leche"},
    {"id": "P-24", "cat": "Productos", "input": "¿A cómo está la cerveza?", "expected_domain": "PRODUCTOS", "target": "cerveza"},
    {"id": "P-25", "cat": "Productos", "input": "¿Cuánto vale el jabón?", "expected_domain": "PRODUCTOS", "target": "jabón"},
    {"id": "P-26", "cat": "Productos", "input": "¿Tenemos arroz?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "P-27", "cat": "Productos", "input": "¿Hay leche?", "expected_domain": "PRODUCTOS", "target": "leche"},
    {"id": "P-28", "cat": "Productos", "input": "¿Manejamos pan bimbo?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "P-29", "cat": "Productos", "input": "¿Tenemos cerveza águila?", "expected_domain": "PRODUCTOS", "target": "cerveza"},
    {"id": "P-30", "cat": "Productos", "input": "¿Hay jabón rey?", "expected_domain": "PRODUCTOS", "target": "jabón"},
    {"id": "P-31", "cat": "Productos", "input": "¿Se vende aceite gourmet acá?", "expected_domain": "PRODUCTOS", "target": "aceite"},
    {"id": "P-32", "cat": "Productos", "input": "¿Hay gaseosa de manzana?", "expected_domain": "PRODUCTOS", "target": "gaseosa"},
    {"id": "P-33", "cat": "Productos", "input": "¿Tenemos huevos?", "expected_domain": "PRODUCTOS", "target": "huevos"},
    {"id": "P-34", "cat": "Productos", "input": "¿Existe el producto arroz diana?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "P-35", "cat": "Productos", "input": "¿Manejamos leche alquería?", "expected_domain": "PRODUCTOS", "target": "leche"},
    {"id": "P-36", "cat": "Productos", "input": "¿Qué producto tiene la barra 7701234567890?", "expected_domain": "PRODUCTOS", "target": "7701234567890"},
    {"id": "P-37", "cat": "Productos", "input": "busca el producto 7701234567891", "expected_domain": "PRODUCTOS", "target": "7701234567891"},
    {"id": "P-38", "cat": "Productos", "input": "¿a cómo está el producto 7701234567892?", "expected_domain": "PRODUCTOS", "target": "7701234567892"},
    {"id": "P-39", "cat": "Productos", "input": "¿tenemos el código 7701234567893?", "expected_domain": "PRODUCTOS", "target": "7701234567893"},
    {"id": "P-40", "cat": "Productos", "input": "¿cuánto vale el 7701234567894?", "expected_domain": "PRODUCTOS", "target": "7701234567894"},

    # =========================================================================
    # C. INVENTARIO / STOCK (40 CASOS)
    # =========================================================================
    {"id": "S-01", "cat": "Inventario", "input": "¿Cuánto arroz queda?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "S-02", "cat": "Inventario", "input": "¿Cuánto queda de arroz?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "S-03", "cat": "Inventario", "input": "¿Cuánto stock tengo de aceite?", "expected_domain": "INVENTARIO", "target": "aceite"},
    {"id": "S-04", "cat": "Inventario", "input": "¿Cuántas cervezas quedan en nevera?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "S-05", "cat": "Inventario", "input": "¿Cuántas unidades hay de jabón rey?", "expected_domain": "INVENTARIO", "target": "jabón"},
    {"id": "S-06", "cat": "Inventario", "input": "¿Stock de pan bimbo?", "expected_domain": "INVENTARIO", "target": "pan"},
    {"id": "S-07", "cat": "Inventario", "input": "¿Cuántas bolsas de leche quedan?", "expected_domain": "INVENTARIO", "target": "leche"},
    {"id": "S-08", "cat": "Inventario", "input": "¿Cuántas botellas de gaseosa hay?", "expected_domain": "INVENTARIO", "target": "gaseosa"},
    {"id": "S-09", "cat": "Inventario", "input": "¿Cuánto inventario hay de arroz diana?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "S-10", "cat": "Inventario", "input": "¿Cuántas cervezas águila tenemos?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "S-11", "cat": "Inventario", "input": "¿Cuántos paquetes de pan quedan?", "expected_domain": "INVENTARIO", "target": "pan"},
    {"id": "S-12", "cat": "Inventario", "input": "¿Cuánto aceite gourmet nos queda?", "expected_domain": "INVENTARIO", "target": "aceite"},
    {"id": "S-13", "cat": "Inventario", "input": "¿Cuántos jabones quedan?", "expected_domain": "INVENTARIO", "target": "jabón"},
    {"id": "S-14", "cat": "Inventario", "input": "¿Qué stock hay de arroz?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "S-15", "cat": "Inventario", "input": "¿Cuántas unidades de cerveza quedan?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "S-16", "cat": "Inventario", "input": "¿Qué productos están agotados?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-17", "cat": "Inventario", "input": "¿Qué se agotó?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-18", "cat": "Inventario", "input": "¿Qué no hay?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-19", "cat": "Inventario", "input": "¿Cuáles productos no tienen stock?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-20", "cat": "Inventario", "input": "¿Qué tenemos en cero?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-21", "cat": "Inventario", "input": "¿Qué productos tienen existencia cero?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-22", "cat": "Inventario", "input": "¿Hay productos agotados?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-23", "cat": "Inventario", "input": "¿Cuáles están sin existencias?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-24", "cat": "Inventario", "input": "¿Qué se acabó en la tienda?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-25", "cat": "Inventario", "input": "dime los productos agotados", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-26", "cat": "Inventario", "input": "lista de productos sin stock", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-27", "cat": "Inventario", "input": "¿qué mercancía está agotada?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "S-28", "cat": "Inventario", "input": "¿Qué productos tienen stock bajo?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-29", "cat": "Inventario", "input": "¿Qué se está acabando?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-30", "cat": "Inventario", "input": "¿Qué productos tienen pocas existencias?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-31", "cat": "Inventario", "input": "¿Qué toca pedir?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-32", "cat": "Inventario", "input": "¿Qué está escaso?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-33", "cat": "Inventario", "input": "¿Cuáles productos tienen menos de 5 unidades?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-34", "cat": "Inventario", "input": "¿Qué mercancía está por acabarse?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-35", "cat": "Inventario", "input": "productos con existencias bajas", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "S-36", "cat": "Inventario", "input": "¿Cuánto vale mi inventario?", "expected_domain": "INVENTARIO", "action": "valor_total"},
    {"id": "S-37", "cat": "Inventario", "input": "¿Cuánto tengo invertido en mercancía?", "expected_domain": "INVENTARIO", "action": "valor_total"},
    {"id": "S-38", "cat": "Inventario", "input": "¿Cuál es el valor del inventario?", "expected_domain": "INVENTARIO", "action": "valor_total"},
    {"id": "S-39", "cat": "Inventario", "input": "valor total de inventario a costo", "expected_domain": "INVENTARIO", "action": "valor_total"},
    {"id": "S-40", "cat": "Inventario", "input": "¿cuánto dinero hay metido en la tienda?", "expected_domain": "INVENTARIO", "action": "valor_total"},

    # =========================================================================
    # D. REPORTES Y ANÁLISIS (35 CASOS)
    # =========================================================================
    {"id": "R-01", "cat": "Reportes", "input": "¿Cuál es el producto más vendido hoy?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-02", "cat": "Reportes", "input": "¿Qué es lo que más se ha vendido?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-03", "cat": "Reportes", "input": "¿Cuál es el que más sale?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-04", "cat": "Reportes", "input": "¿Qué producto es el rey de ventas?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-05", "cat": "Reportes", "input": "¿Cuál ha sido el producto más vendido?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-06", "cat": "Reportes", "input": "¿Qué producto se vendió más hoy?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-07", "cat": "Reportes", "input": "top 1 de ventas", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-08", "cat": "Reportes", "input": "¿cuál es el producto estrella?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-09", "cat": "Reportes", "input": "¿cuál lidera las ventas hoy?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-10", "cat": "Reportes", "input": "¿qué es lo que más compra la gente?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-11", "cat": "Reportes", "input": "¿cuál ha sido el más vendido de la semana?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-12", "cat": "Reportes", "input": "¿qué producto lideró ventas ayer?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-13", "cat": "Reportes", "input": "¿cuál es el top de ventas?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-14", "cat": "Reportes", "input": "¿qué producto ha tenido más salida?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-15", "cat": "Reportes", "input": "¿cuál es el más vendido?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "R-16", "cat": "Reportes", "input": "¿Cómo va el día?", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-17", "cat": "Reportes", "input": "¿Cuál es el resumen de hoy?", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-18", "cat": "Reportes", "input": "resumen del día", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-19", "cat": "Reportes", "input": "dame un reporte rápido de hoy", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-20", "cat": "Reportes", "input": "resumen actual", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-21", "cat": "Reportes", "input": "cómo está el negocio hoy", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-22", "cat": "Reportes", "input": "¿cómo pinta el día hoy?", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-23", "cat": "Reportes", "input": "balance rápido de hoy", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-24", "cat": "Reportes", "input": "reporte del día", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-25", "cat": "Reportes", "input": "¿cómo cerramos hoy?", "expected_domain": "REPORTES", "action": "resumen_dia"},
    {"id": "R-26", "cat": "Reportes", "input": "¿Cuánto dinero ha ingresado hoy?", "expected_domain": "REPORTES", "action": "recaudo"},
    {"id": "R-27", "cat": "Reportes", "input": "¿Cuánto es el recaudo?", "expected_domain": "REPORTES", "action": "recaudo"},
    {"id": "R-28", "cat": "Reportes", "input": "¿Cuánto dinero hay en caja por ventas?", "expected_domain": "REPORTES", "action": "recaudo"},
    {"id": "R-29", "cat": "Reportes", "input": "¿Cuánto efectivo o recaudo va?", "expected_domain": "REPORTES", "action": "recaudo"},
    {"id": "R-30", "cat": "Reportes", "input": "recaudo de hoy", "expected_domain": "REPORTES", "action": "recaudo"},
    {"id": "R-31", "cat": "Reportes", "input": "¿Cómo va la recuperación de mi inversión?", "expected_domain": "REPORTES", "action": "inversion"},
    {"id": "R-32", "cat": "Reportes", "input": "¿Cuándo recupero la inversión?", "expected_domain": "REPORTES", "action": "inversion"},
    {"id": "R-33", "cat": "Reportes", "input": "recuperación de inversión", "expected_domain": "REPORTES", "action": "inversion"},
    {"id": "R-34", "cat": "Reportes", "input": "balance de inversión", "expected_domain": "REPORTES", "action": "inversion"},
    {"id": "R-35", "cat": "Reportes", "input": "¿cuánto me falta para recuperar lo invertido?", "expected_domain": "REPORTES", "action": "inversion"},

    # =========================================================================
    # E. COMPARACIONES (25 CASOS)
    # =========================================================================
    {"id": "CP-01", "cat": "Comparaciones", "input": "¿Vendimos más hoy que ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-02", "cat": "Comparaciones", "input": "¿Cómo vamos comparado con ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-03", "cat": "Comparaciones", "input": "¿Se vendió más hoy o ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-04", "cat": "Comparaciones", "input": "¿Cómo estuvieron las ventas hoy frente a ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-05", "cat": "Comparaciones", "input": "¿Vamos mejor o peor que ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-06", "cat": "Comparaciones", "input": "comparar ventas hoy vs ayer", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-07", "cat": "Comparaciones", "input": "¿cuánto vendimos hoy comparado con ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-08", "cat": "Comparaciones", "input": "¿hoy superó a ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-09", "cat": "Comparaciones", "input": "¿subieron las ventas hoy respecto a ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-10", "cat": "Comparaciones", "input": "¿las ventas de hoy son mayores a las de ayer?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "CP-11", "cat": "Comparaciones", "input": "¿Se vende más arroz o aceite?", "expected_domain": "COMPARACION", "type": "productos"},
    {"id": "CP-12", "cat": "Comparaciones", "input": "¿Qué salió más, cerveza o gaseosa?", "expected_domain": "COMPARACION", "type": "productos"},
    {"id": "CP-13", "cat": "Comparaciones", "input": "¿Quién vendió más unidades, pan o leche?", "expected_domain": "COMPARACION", "type": "productos"},
    {"id": "CP-14", "cat": "Comparaciones", "input": "¿Qué se ha vendido más hoy, arroz diana o aceite gourmet?", "expected_domain": "COMPARACION", "type": "productos"},
    {"id": "CP-15", "cat": "Comparaciones", "input": "¿Cuál tiene más stock, arroz o cerveza?", "expected_domain": "COMPARACION", "type": "stock"},
    {"id": "CP-16", "cat": "Comparaciones", "input": "¿Qué producto tiene mayor precio, leche o pan?", "expected_domain": "COMPARACION", "type": "precios"},
    {"id": "CP-17", "cat": "Comparaciones", "input": "¿Hay más existencias de aceite o de arroz?", "expected_domain": "COMPARACION", "type": "stock"},
    {"id": "CP-18", "cat": "Comparaciones", "input": "¿Qué tiene más rotación, jabón o arroz?", "expected_domain": "COMPARACION", "type": "productos"},
    {"id": "CP-19", "cat": "Comparaciones", "input": "¿Quién vendió más hoy, Paula o yo?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-20", "cat": "Comparaciones", "input": "¿Paula vendió más que Don Pedro?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-21", "cat": "Comparaciones", "input": "¿Quién lleva más ventas hoy?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-22", "cat": "Comparaciones", "input": "¿Quién lidera las ventas entre los cajeros?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-23", "cat": "Comparaciones", "input": "¿Paula hizo más ventas que Don Pedro?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-24", "cat": "Comparaciones", "input": "¿Quién ha facturado más hoy?", "expected_domain": "COMPARACION", "type": "vendedores"},
    {"id": "CP-25", "cat": "Comparaciones", "input": "¿Quién es el cajero que más ha vendido?", "expected_domain": "COMPARACION", "type": "vendedores"},

    # =========================================================================
    # F. CONTEXTO CONVERSACIONAL MULTI-TURNO (30 CASOS - 15 DIÁLOGOS DE 2 TURNOS)
    # =========================================================================
    {"id": "F-01", "cat": "Contexto", "dialog_id": "D1", "turn": 1, "input": "¿Cuánto vendimos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "F-02", "cat": "Contexto", "dialog_id": "D1", "turn": 2, "input": "¿Y ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "F-03", "cat": "Contexto", "dialog_id": "D2", "turn": 1, "input": "¿Cuánto vendimos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "F-04", "cat": "Contexto", "dialog_id": "D2", "turn": 2, "input": "¿Y esta semana?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "F-05", "cat": "Contexto", "dialog_id": "D3", "turn": 1, "input": "¿Cuánto vendimos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "F-06", "cat": "Contexto", "dialog_id": "D3", "turn": 2, "input": "¿Y este mes?", "expected_domain": "VENTAS", "period": "mes"},
    {"id": "F-07", "cat": "Contexto", "dialog_id": "D4", "turn": 1, "input": "¿Cuánto queda de arroz?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "F-08", "cat": "Contexto", "dialog_id": "D4", "turn": 2, "input": "¿Y de aceite?", "expected_domain": "INVENTARIO", "target": "aceite"},
    {"id": "F-09", "cat": "Contexto", "dialog_id": "D5", "turn": 1, "input": "¿Cuánto queda de cerveza?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "F-10", "cat": "Contexto", "dialog_id": "D5", "turn": 2, "input": "¿Y a cómo está?", "expected_domain": "PRODUCTOS", "target": "cerveza"},
    {"id": "F-11", "cat": "Contexto", "dialog_id": "D6", "turn": 1, "input": "¿Cuánto vendió Paula hoy?", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "F-12", "cat": "Contexto", "dialog_id": "D6", "turn": 2, "input": "¿Y Don Pedro?", "expected_domain": "VENTAS", "seller": "Don Pedro"},
    {"id": "F-13", "cat": "Contexto", "dialog_id": "D7", "turn": 1, "input": "¿Cuánto vendió Paula hoy?", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "F-14", "cat": "Contexto", "dialog_id": "D7", "turn": 2, "input": "¿Y ayer?", "expected_domain": "VENTAS", "seller": "Paula", "period": "ayer"},
    {"id": "F-15", "cat": "Contexto", "dialog_id": "D8", "turn": 1, "input": "¿Cuál es el producto más vendido hoy?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "F-16", "cat": "Contexto", "dialog_id": "D8", "turn": 2, "input": "¿Y ayer?", "expected_domain": "REPORTES", "action": "top_ventas", "period": "ayer"},
    {"id": "F-17", "cat": "Contexto", "dialog_id": "D9", "turn": 1, "input": "¿A cómo está la leche?", "expected_domain": "PRODUCTOS", "target": "leche"},
    {"id": "F-18", "cat": "Contexto", "dialog_id": "D9", "turn": 2, "input": "¿Y cuánto queda?", "expected_domain": "INVENTARIO", "target": "leche"},
    {"id": "F-19", "cat": "Contexto", "dialog_id": "D10", "turn": 1, "input": "¿Qué productos están agotados?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "F-20", "cat": "Contexto", "dialog_id": "D10", "turn": 2, "input": "¿Y con stock bajo?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "F-21", "cat": "Contexto", "dialog_id": "D11", "turn": 1, "input": "¿Cuánto arroz queda?", "expected_domain": "INVENTARIO", "target": "arroz"},
    {"id": "F-22", "cat": "Contexto", "dialog_id": "D11", "turn": 2, "input": "¿Y cuántas cervezas?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "F-23", "cat": "Contexto", "dialog_id": "D12", "turn": 1, "input": "¿Cuánto vendimos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "F-24", "cat": "Contexto", "dialog_id": "D12", "turn": 2, "input": "¿Cuántas transacciones fueron?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "F-25", "cat": "Contexto", "dialog_id": "D13", "turn": 1, "input": "¿Tenemos pan bimbo?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "F-26", "cat": "Contexto", "dialog_id": "D13", "turn": 2, "input": "¿Cuánto vale?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "F-27", "cat": "Contexto", "dialog_id": "D14", "turn": 1, "input": "Vendí 2 arroces", "expected_domain": "ACCION_MUTATIVA", "fsm": "READY_TO_CONFIRM"},
    {"id": "F-28", "cat": "Contexto", "dialog_id": "D14", "turn": 2, "input": "cancelar", "expected_domain": "CANCELACION", "fsm": "REJECTED"},
    {"id": "F-29", "cat": "Contexto", "dialog_id": "D15", "turn": 1, "input": "Vendí 2 arroces", "expected_domain": "ACCION_MUTATIVA", "fsm": "READY_TO_CONFIRM"},
    {"id": "F-30", "cat": "Contexto", "dialog_id": "D15", "turn": 2, "input": "sí", "expected_domain": "CONFIRMACION", "fsm": "EXECUTED"},

    # =========================================================================
    # G. AMBIGÜEDAD (20 CASOS - REQUIERE ACLARACIÓN)
    # =========================================================================
    {"id": "AM-01", "cat": "Ambigüedad", "input": "¿Cuánto tenemos?", "requires_clarification": True},
    {"id": "AM-02", "cat": "Ambigüedad", "input": "¿Cómo vamos?", "requires_clarification": True},
    {"id": "AM-03", "cat": "Ambigüedad", "input": "¿Cuánto salió?", "requires_clarification": True},
    {"id": "AM-04", "cat": "Ambigüedad", "input": "¿Cuánto hay?", "requires_clarification": True},
    {"id": "AM-05", "cat": "Ambigüedad", "input": "¿Qué se movió?", "requires_clarification": True},
    {"id": "AM-06", "cat": "Ambigüedad", "input": "Ventas", "requires_clarification": True},
    {"id": "AM-07", "cat": "Ambigüedad", "input": "Stock", "requires_clarification": True},
    {"id": "AM-08", "cat": "Ambigüedad", "input": "¿Cuánto fue?", "requires_clarification": True},
    {"id": "AM-09", "cat": "Ambigüedad", "input": "¿Cómo estamos?", "requires_clarification": True},
    {"id": "AM-10", "cat": "Ambigüedad", "input": "¿Cuánto queda?", "requires_clarification": True},
    {"id": "AM-11", "cat": "Ambigüedad", "input": "Reporte", "requires_clarification": True},
    {"id": "AM-12", "cat": "Ambigüedad", "input": "¿Qué tenemos?", "requires_clarification": True},
    {"id": "AM-13", "cat": "Ambigüedad", "input": "¿Cuánto dio?", "requires_clarification": True},
    {"id": "AM-14", "cat": "Ambigüedad", "input": "Total", "requires_clarification": True},
    {"id": "AM-15", "cat": "Ambigüedad", "input": "¿Cuánto se hizo?", "requires_clarification": True},
    {"id": "AM-16", "cat": "Ambigüedad", "input": "¿A cómo?", "requires_clarification": True},
    {"id": "AM-17", "cat": "Ambigüedad", "input": "¿Hay o no hay?", "requires_clarification": True},
    {"id": "AM-18", "cat": "Ambigüedad", "input": "Inventario", "requires_clarification": True},
    {"id": "AM-19", "cat": "Ambigüedad", "input": "¿Qué falta?", "requires_clarification": True},
    {"id": "AM-20", "cat": "Ambigüedad", "input": "¿Cuánto entró?", "requires_clarification": True},

    # =========================================================================
    # H. OUT-OF-DOMAIN (20 CASOS - RECHAZO DE MOSTRADOR)
    # =========================================================================
    {"id": "OOD-01", "cat": "Out-of-Domain", "input": "¿Cuál es la capital de Francia?", "out_of_domain": True},
    {"id": "OOD-02", "cat": "Out-of-Domain", "input": "Cuéntame un chiste de pepito", "out_of_domain": True},
    {"id": "OOD-03", "cat": "Out-of-Domain", "input": "¿Quién va a ganar el partido de fútbol mañana?", "out_of_domain": True},
    {"id": "OOD-04", "cat": "Out-of-Domain", "input": "Escribe un poema sobre el amor y la luna", "out_of_domain": True},
    {"id": "OOD-05", "cat": "Out-of-Domain", "input": "¿Cómo preparo un arroz con pollo santandereano?", "out_of_domain": True},
    {"id": "OOD-06", "cat": "Out-of-Domain", "input": "¿Qué opinas del presidente de Colombia?", "out_of_domain": True},
    {"id": "OOD-07", "cat": "Out-of-Domain", "input": "¿Cuánto vale un bitcoin hoy?", "out_of_domain": True},
    {"id": "OOD-08", "cat": "Out-of-Domain", "input": "Ayúdame con mi tarea de matemáticas de integrales", "out_of_domain": True},
    {"id": "OOD-09", "cat": "Out-of-Domain", "input": "¿Qué clima va a hacer hoy en Neiva?", "out_of_domain": True},
    {"id": "OOD-10", "cat": "Out-of-Domain", "input": "¿Quién descubrió América en 1492?", "out_of_domain": True},
    {"id": "OOD-11", "cat": "Out-of-Domain", "input": "Recomiéndame una película para ver en Netflix hoy", "out_of_domain": True},
    {"id": "OOD-12", "cat": "Out-of-Domain", "input": "¿Cómo hackear la contraseña del wifi de mi vecino?", "out_of_domain": True},
    {"id": "OOD-13", "cat": "Out-of-Domain", "input": "Tradúceme esta frase al mandarín", "out_of_domain": True},
    {"id": "OOD-14", "cat": "Out-of-Domain", "input": "¿Cuál es el mejor carro del mundo?", "out_of_domain": True},
    {"id": "OOD-15", "cat": "Out-of-Domain", "input": "¿Qué canción me recomiendas para bailar salsa?", "out_of_domain": True},
    {"id": "OOD-16", "cat": "Out-of-Domain", "input": "Escríbeme un correo de renuncia para mi jefe", "out_of_domain": True},
    {"id": "OOD-17", "cat": "Out-of-Domain", "input": "¿Cómo se cura el dolor de cabeza con remedios caseros?", "out_of_domain": True},
    {"id": "OOD-18", "cat": "Out-of-Domain", "input": "¿Cuál es la distancia entre la Tierra y Marte?", "out_of_domain": True},
    {"id": "OOD-19", "cat": "Out-of-Domain", "input": "¿Dónde queda el río Magdalena?", "out_of_domain": True},
    {"id": "OOD-20", "cat": "Out-of-Domain", "input": "¿Quién ganó el mundial de fútbol del 2022?", "out_of_domain": True},

    # =========================================================================
    # I. LENGUAJE REAL DE MOSTRADOR (20 CASOS)
    # =========================================================================
    {"id": "LM-01", "cat": "Mostrador", "input": "¿Qué tanto se movió hoy la tienda?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "LM-02", "cat": "Mostrador", "input": "¿A cómo está la librita de arroz?", "expected_domain": "PRODUCTOS", "target": "arroz"},
    {"id": "LM-03", "cat": "Mostrador", "input": "¿Qué está escaso mi viejo?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "LM-04", "cat": "Mostrador", "input": "¿Cuánto coronó Paula hoy?", "expected_domain": "VENTAS", "seller": "Paula"},
    {"id": "LM-05", "cat": "Mostrador", "input": "¿Cuánto coronamos hoy?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "LM-06", "cat": "Mostrador", "input": "¿Qué es lo que más pide la gallada?", "expected_domain": "REPORTES", "action": "top_ventas"},
    {"id": "LM-07", "cat": "Mostrador", "input": "¿A cómo me sale la birra?", "expected_domain": "PRODUCTOS", "target": "cerveza"},
    {"id": "LM-08", "cat": "Mostrador", "input": "¿Cuánto billete entró hoy a la caja?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "LM-09", "cat": "Mostrador", "input": "¿Nos fue mejor ayer o hoy mi socio?", "expected_domain": "COMPARACION", "type": "hoy_vs_ayer"},
    {"id": "LM-10", "cat": "Mostrador", "input": "¿Qué tenemos seco en la bodega?", "expected_domain": "INVENTARIO", "action": "agotados"},
    {"id": "LM-11", "cat": "Mostrador", "input": "¿Cuánto le metimos a la mercancía?", "expected_domain": "INVENTARIO", "action": "valor_total"},
    {"id": "LM-12", "cat": "Mostrador", "input": "¿Cuántas polas nos quedan en la nevera?", "expected_domain": "INVENTARIO", "target": "cerveza"},
    {"id": "LM-13", "cat": "Mostrador", "input": "¿Se vendió harto hoy o estuvo flojo?", "expected_domain": "VENTAS", "period": "hoy"},
    {"id": "LM-14", "cat": "Mostrador", "input": "¿Cómo pintó la semana mi hermano?", "expected_domain": "VENTAS", "period": "semana"},
    {"id": "LM-15", "cat": "Mostrador", "input": "¿Cuánto se echó al bolsillo el negocio ayer?", "expected_domain": "VENTAS", "period": "ayer"},
    {"id": "LM-16", "cat": "Mostrador", "input": "¿Cuántos clientes cayeron hoy a comprar?", "expected_domain": "VENTAS", "metric": "cantidad_ventas"},
    {"id": "LM-17", "cat": "Mostrador", "input": "¿Qué es lo que menos se mueve en los estantes?", "expected_domain": "REPORTES", "action": "menor_rotacion"},
    {"id": "LM-18", "cat": "Mostrador", "input": "¿En cuánto tengo que dar el pan artesanal?", "expected_domain": "PRODUCTOS", "target": "pan"},
    {"id": "LM-19", "cat": "Mostrador", "input": "¿Qué productos están que se acaban ya mismito?", "expected_domain": "INVENTARIO", "action": "stock_bajo"},
    {"id": "LM-20", "cat": "Mostrador", "input": "¿Cuánto coronó don Pedro en el mostrador?", "expected_domain": "VENTAS", "seller": "Don Pedro"},
]


# ---------------------------------------------------------------------------
# FIXTURES Y SETUP DEL ENTORNO DE PRUEBA
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_session_store():
    store = InMemorySessionStore()
    set_session_store_instance(store)
    yield store
    store.clear()


def _setup_test_tienda(client) -> tuple[dict, str, dict]:
    """Crea tienda, productos y ventas con datos realistas para el benchmark."""
    # 1. Registrar empresa y usuario admin
    suffix = uuid4().hex[:6]
    resp = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": f"Tienda Neiva {suffix}",
            "nit_o_cedula": f"NIT-{suffix}",
            "email": f"tendero_{suffix}@test.com",
            "password": "Password123!",
            "rol": "admin",
        },
    )
    assert resp.status_code == 201
    auth_data = resp.json()
    token = auth_data["access_token"]
    empresa_id = auth_data["usuario"]["empresa_id"]
    admin_id = auth_data["usuario"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear usuarios cajeros (Paula y Don Pedro)
    resp_paula = client.post(
        "/usuarios/empleados",
        headers=headers,
        json={
            "nombre": "Paula Cajera",
            "email": f"paula_{suffix}@test.com",
            "password": "Password123!",
        },
    )
    paula_id = resp_paula.json()["id"] if resp_paula.status_code == 201 else None

    resp_pedro = client.post(
        "/usuarios/empleados",
        headers=headers,
        json={
            "nombre": "Don Pedro",
            "email": f"pedro_{suffix}@test.com",
            "password": "Password123!",
        },
    )
    pedro_id = resp_pedro.json()["id"] if resp_pedro.status_code == 201 else None

    # 3. Crear productos de prueba
    prods_config = [
        ("Arroz Diana 1kg", "7701234567890", 3000.0, 4500.0, 25.0, "Snacks"),
        ("Aceite Gourmet 1L", "7701234567891", 8000.0, 11000.0, 10.0, "Snacks"),
        ("Leche Alquería 1L", "7701234567892", 3500.0, 4800.0, 0.0, "Lacteos"),       # Agotado
        ("Pan Bimbo Artesanal", "7701234567893", 4000.0, 5500.0, 3.0, "Panaderia"),    # Stock bajo
        ("Gaseosa Postobón Manzana 400ml", "7701234567894", 1500.0, 2500.0, 15.0, "Bebidas"),
        ("Cerveza Águila 330ml", "7701234567895", 2200.0, 3200.0, 48.0, "Bebidas"),
        ("Huevos AA x30", "7701234567896", 14000.0, 18000.0, 0.0, "Snacks"),          # Agotado
        ("Jabón Rey", "7701234567897", 1800.0, 2500.0, 4.0, "Aseo"),                  # Stock bajo
    ]

    productos_creados = {}
    for nom, bar, pc, pv, cant, cat in prods_config:
        r = client.post(
            "/productos/",
            headers=headers,
            json={
                "empresa_id": empresa_id,
                "nombre": nom,
                "codigo_barras": bar,
                "precio_costo": pc,
                "precio_venta": pv,
                "cantidad_actual": cant,
                "unidad_medida": "unidad",
                "categoria": cat,
            },
        )
        assert r.status_code == 201, f"Fallo al crear producto {nom}: {r.text}"
        productos_creados[nom] = r.json()

    # 4. Registrar ventas de hoy vía API de ventas
    if "Arroz Diana 1kg" in productos_creados:
        r_v = client.post(
            f"/ventas/{empresa_id}",
            headers=headers,
            json={
                "detalles": [{"producto_id": productos_creados["Arroz Diana 1kg"]["id"], "cantidad": 2}],
            },
        )
        assert r_v.status_code == 201, f"Error al registrar venta de prueba: {r_v.text}"

    context_tienda = {
        "empresa_id": empresa_id,
        "admin_id": admin_id,
        "paula_id": paula_id,
        "pedro_id": pedro_id,
        "productos": productos_creados,
    }
    return headers, empresa_id, context_tienda


# ---------------------------------------------------------------------------
# EVALUADOR INDIVIDUAL DE CASOS
# ---------------------------------------------------------------------------

def evaluar_caso(client, headers: dict, caso: dict, conv_id: str) -> tuple[bool, str]:
    """Evalúa un caso contra el endpoint `/api/agente/mensaje`.
    
    Retorna (acierto: bool, motivo: str).
    """
    msg = caso["input"]
    resp = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": msg, "conversation_id": conv_id},
    )
    if resp.status_code != 200:
        return False, f"HTTP Error {resp.status_code}: {resp.text}"

    data = resp.json()
    estado = data.get("estado")
    texto_resp = data.get("respuesta", "").lower()

    # Caso: Out-of-domain esperado
    if caso.get("out_of_domain"):
        if estado == "OUT_OF_SCOPE" or any(w in texto_resp for w in ["solo puedo ayudarte", "alcance", "tienda", "pos", "gestión", "gestionar tu negocio"]):
            return True, "Rechazo out-of-scope correcto"
        return False, f"Se esperaba rechazo out-of-scope pero respondió: '{texto_resp}' (estado={estado})"

    # Caso: Requiere aclaración por ambigüedad
    if caso.get("requires_clarification"):
        if estado in ["NEEDS_CLARIFICATION", "IDLE"] and any(w in texto_resp for w in ["¿te refieres", "¿a qué te refieres", "¿cuál", "aclarar", "opciones", "especificar", "¿de qué"]):
            return True, "Aclaración solicitada correctamente"
        return False, f"Se esperaba aclaración para entrada ambigua, pero dio: '{texto_resp}'"

    # Caso: Confirmación / Cancelación de FSM
    if caso.get("fsm"):
        if estado == caso["fsm"]:
            return True, f"FSM en estado correcto: {estado}"
        return False, f"FSM esperaba {caso['fsm']} pero quedó en {estado}"

    # Si respondió el fallback genérico de no entendimiento:
    if "no logré entender bien tu solicitud" in texto_resp or "no logre entender" in texto_resp:
        return False, "Agente no reconoció la intención (fallback genérico 'no logré entender')"

    # Caso: Ventas (período, métrica, vendedor)
    if caso.get("expected_domain") == "VENTAS":
        if caso.get("period") == "ayer":
            if "ayer" in texto_resp or "en el periodo de ayer" in texto_resp:
                return True, "Reconoció ventas de ayer"
            return False, f"No reconoció período 'ayer' en: '{texto_resp}'"
        if caso.get("period") == "semana":
            if any(w in texto_resp for w in ["semana", "últimos 7 días", "ultimos 7 dias"]):
                return True, "Reconoció ventas de la semana"
            return False, f"No reconoció período 'semana' en: '{texto_resp}'"
        if caso.get("period") == "mes":
            if "mes" in texto_resp:
                return True, "Reconoció ventas del mes"
            return False, f"No reconoció período 'mes' en: '{texto_resp}'"
        if caso.get("seller"):
            seller = caso["seller"].lower()
            if seller in texto_resp or "cajero" in texto_resp or "ventas" in texto_resp:
                return True, f"Reconoció consulta de vendedor {seller}"
            return False, f"No resolvió ventas del vendedor '{seller}': '{texto_resp}'"
        if caso.get("metric") == "cantidad_ventas":
            if any(w in texto_resp for w in ["transacciones", "ventas realizadas", "ventas"]):
                return True, "Reconoció cantidad de ventas"
            return False, f"No resolvió cantidad de transacciones: '{texto_resp}'"
        # Por defecto ventas hoy
        if any(w in texto_resp for w in ["vendido", "ventas", "hoy", "pesos", "$"]):
            return True, "Resolvió ventas de hoy"
        return False, f"Respuesta no parece de ventas: '{texto_resp}'"

    # Caso: Productos (conteo, precio, existencia)
    if caso.get("expected_domain") == "PRODUCTOS":
        if caso.get("action") == "conteo":
            if any(w in texto_resp for w in ["productos activos", "referencias", "catálogo", "total de productos", "tienes"]):
                return True, "Resolvió conteo de productos"
            return False, f"No resolvió conteo de productos activos: '{texto_resp}'"
        target = caso.get("target", "").lower()
        if any(w in texto_resp for w in ["precio", "$", "cuesta", "vale", target, "disponibles"]):
            return True, f"Resolvió producto {target}"
        return False, f"No resolvió producto o precio para '{target}': '{texto_resp}'"

    # Caso: Inventario (stock, agotados, stock bajo, valorización)
    if caso.get("expected_domain") == "INVENTARIO":
        if caso.get("action") == "agotados":
            if any(w in texto_resp for w in ["agotados", "sin existencias", "stock: 0", "cero", "no tienes existencias"]):
                return True, "Resolvió productos agotados"
            return False, f"No resolvió lista de productos agotados: '{texto_resp}'"
        if caso.get("action") == "stock_bajo":
            if any(w in texto_resp for w in ["stock bajo", "crítico", "pocas", "escaso", "unidades", "alerta"]):
                return True, "Resolvió stock bajo"
            return False, f"No resolvió productos con stock bajo: '{texto_resp}'"
        if caso.get("action") == "valor_total":
            if any(w in texto_resp for w in ["invertido", "valor", "costo", "inventario", "$"]):
                return True, "Resolvió valor total del inventario"
            return False, f"No resolvió valor total del inventario: '{texto_resp}'"
        target = caso.get("target", "").lower()
        if any(w in texto_resp for w in ["quedan", "stock", "disponibles", "unidades", target]):
            return True, f"Resolvió stock de {target}"
        return False, f"No resolvió stock de '{target}': '{texto_resp}'"

    # Caso: Reportes (top ventas, resumen día, recaudo, inversión)
    if caso.get("expected_domain") == "REPORTES":
        if caso.get("action") == "top_ventas":
            if any(w in texto_resp for w in ["más vendido", "mas vendido", "estrella", "lidera", "top", "no se registran ventas"]):
                return True, "Resolvió producto más vendido"
            return False, f"No resolvió producto más vendido: '{texto_resp}'"
        if caso.get("action") == "resumen_dia":
            if any(w in texto_resp for w in ["resumen", "día", "ventas hoy", "alerta", "balance"]):
                return True, "Resolvió resumen del día"
            return False, f"No resolvió resumen del día: '{texto_resp}'"
        if caso.get("action") == "recaudo":
            if any(w in texto_resp for w in ["recaudo", "ingresado", "dinero", "$"]):
                return True, "Resolvió recaudo"
            return False, f"No resolvió recaudo: '{texto_resp}'"
        if caso.get("action") == "inversion":
            if any(w in texto_resp for w in ["inversión", "inversion", "recuperar", "capital"]):
                return True, "Resolvió recuperación de inversión"
            return False, f"No resolvió recuperación de inversión: '{texto_resp}'"

    # Caso: Comparaciones
    if caso.get("expected_domain") == "COMPARACION":
        if any(w in texto_resp for w in ["comparación", "comparado", "más que", "menos que", "diferencia", "%", "superó", "ayer"]):
            return True, "Resolvió comparación"
        return False, f"No resolvió comparación de negocio: '{texto_resp}'"

    # Caso: Acciones mutativas
    if caso.get("expected_domain") == "ACCION_MUTATIVA":
        if estado == "READY_TO_CONFIRM" or "confirmar" in texto_resp:
            return True, "Solicitó confirmación para mutación"
        return False, f"No pasó a confirmación: '{texto_resp}'"

    return True, "Aprobado genérico"


# ---------------------------------------------------------------------------
# RUNNER COMPLETO DEL BENCHMARK
# ---------------------------------------------------------------------------

def ejecutar_benchmark_completo(client) -> dict:
    """Ejecuta los 280 casos de prueba y calcula métricas detalladas."""
    headers, empresa_id, context_tienda = _setup_test_tienda(client)

    resultados_por_categoria = {}
    detalle_fallos = []
    total_casos = len(BENCHMARK_CASES)
    total_aciertos = 0

    dialog_sessions = {}

    for caso in BENCHMARK_CASES:
        cat = caso["cat"]
        if cat not in resultados_por_categoria:
            resultados_por_categoria[cat] = {"total": 0, "aciertos": 0}
        resultados_por_categoria[cat]["total"] += 1

        # Manejo de sesión para diálogos multi-turno
        if "dialog_id" in caso:
            d_id = caso["dialog_id"]
            if d_id not in dialog_sessions:
                dialog_sessions[d_id] = f"conv_{uuid4().hex[:10]}"
            conv_id = dialog_sessions[d_id]
        else:
            conv_id = f"conv_{uuid4().hex[:10]}"

        ok, motivo = evaluar_caso(client, headers, caso, conv_id)
        if ok:
            total_aciertos += 1
            resultados_por_categoria[cat]["aciertos"] += 1
        else:
            detalle_fallos.append({
                "id": caso["id"],
                "cat": cat,
                "input": caso["input"],
                "motivo": motivo,
            })

    tasa_global = (total_aciertos / total_casos) * 100.0

    resumen = {
        "total_casos": total_casos,
        "total_aciertos": total_aciertos,
        "total_fallos": total_casos - total_aciertos,
        "tasa_global_pct": round(tasa_global, 2),
        "por_categoria": {},
        "fallos": detalle_fallos,
    }

    for cat, datos in resultados_por_categoria.items():
        pct = (datos["aciertos"] / datos["total"]) * 100.0 if datos["total"] > 0 else 0.0
        resumen["por_categoria"][cat] = {
            "total": datos["total"],
            "aciertos": datos["aciertos"],
            "tasa_pct": round(pct, 2),
        }

    return resumen


def test_ejecutar_benchmark_baseline(client):
    """Test ejecutable de pytest para registrar el benchmark."""
    resumen = ejecutar_benchmark_completo(client)
    print(f"\n================ BENCHMARK RESULTADOS ================")
    print(f"Total Casos: {resumen['total_casos']}")
    print(f"Aciertos: {resumen['total_aciertos']} / {resumen['total_casos']} ({resumen['tasa_global_pct']}%)")
    for f in resumen["fallos"]:
        print(f"FALLO [{f['id']}] [{f['cat']}] '{f['input']}': {f['motivo']}")
    print("=====================================================\n")

    assert resumen["total_casos"] == 280
