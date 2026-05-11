# Checklist de Customización — Tier Basic

> Usar este checklist al inicio de cada proyecto tier basic para identificar qué adaptar del template.  
> Cada ítem marcado `[x]` es trabajo de customización que va al presupuesto del cliente.

---

## 1. Identidad del negocio

- [ ] Nombre del sistema (reemplazar "Gestión Neiva" en toda la UI)
- [ ] Logo del cliente en Sidebar
- [ ] Colores primarios (TailwindCSS config: violet → color del cliente)
- [ ] Ciudad/contexto en textos de la app

---

## 2. Entidades de datos

- [ ] ¿El "producto" se llama diferente? (ej: "servicio", "artículo", "plato")
- [ ] ¿Hay categorías de producto? → agregar tabla `categorias`, FK en productos
- [ ] ¿Hay múltiples unidades de medida? → agregar `unidad` (kg, litro, unidad, caja)
- [ ] ¿El stock se maneja en decimales? → cambiar `cantidad_actual` a NUMERIC
- [ ] ¿Hay precio mayorista además de precio minorista?

---

## 3. Usuarios y roles

- [ ] ¿Los roles son admin/tendero o necesita otros? (supervisor, cajero, bodeguero)
- [ ] ¿Hay múltiples sucursales? → agregar tabla `sucursales`, cambiar scope multi-tenant
- [ ] ¿Los usuarios pueden ver reportes sin ser admin?

---

## 4. Ventas

- [ ] ¿Hay descuentos por venta o por ítem?
- [ ] ¿Hay métodos de pago (efectivo, transferencia, fiado)?
- [ ] ¿Se registra el cliente en la venta?
- [ ] ¿Hay devoluciones? → agregar flujo de reversión de venta
- [ ] ¿El precio puede diferir del precio_venta del producto?

---

## 5. Dashboard y reportes

- [ ] ¿Qué KPIs son los más importantes para este negocio?
- [ ] ¿El reporte Excel necesita columnas específicas?
- [ ] ¿Hay reportes adicionales? (por categoría, por cajero, por cliente)
- [ ] ¿Necesita gráficas? → usar Recharts o Chart.js

---

## 6. Integraciones

- [ ] ¿Necesita impresora de tickets? → librería de impresión o API de impresora
- [ ] ¿Necesita lector de código de barras por hardware?
- [ ] ¿Necesita WhatsApp para enviar recibos? (Twilio o Green API)
- [ ] ¿Necesita facturación electrónica DIAN? → fuera del tier basic, cotizar aparte

---

## 7. Infraestructura

- [ ] ¿El cliente tiene servidor propio o necesita hosting?
- [ ] ¿Necesita dominio personalizado?
- [ ] ¿Necesita SSL/HTTPS desde el día 1?
- [ ] ¿Cuántos usuarios concurrentes se esperan? (impacta sizing del servidor)

---

## Estimación de horas por sección

| Sección | Sin cambios | Cambios menores | Cambios mayores |
|---------|-------------|-----------------|-----------------|
| Identidad | 0h | 1h | 2h |
| Entidades | 0h | 2–4h | 8–16h |
| Usuarios/roles | 0h | 2h | 6h |
| Ventas | 0h | 2–4h | 8h |
| Dashboard | 0h | 2h | 4–8h |
| Integraciones | 0h | variable | variable |

---

## Total estimado para el presupuesto

```
Base tier basic (template directo):    $300 USD
+ customización (sumar horas × tarifa): $X
+ hosting primer año:                  $150–300 USD
─────────────────────────────────────────────────
Total proyecto:                        $XXX USD
```
