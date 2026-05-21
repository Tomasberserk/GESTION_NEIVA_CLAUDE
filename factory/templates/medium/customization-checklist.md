# Checklist de Customización — Tier Medium (ERP Ligero)

> Usar este checklist al inicio de cada proyecto del Tier Medium para estructurar y dimensionar el alcance de las adaptaciones requeridas por el cliente.
> Cada casilla de verificación representa un elemento personalizable que incrementa el valor de la cotización final del proyecto.

---

## 1. Identidad y Módulos Core

- [ ] Reemplazar la marca corporativa por el logotipo y colores institucionales del cliente.
- [ ] Configurar los accesos del `Sidebar` según el alcance contratado.
- [ ] Idioma y configuración regional (moneda, formatos de fecha, huso horario local).

---

## 2. Gestión de Proveedores

- [ ] ¿Cómo se denomina legalmente al proveedor? (ej: "Acreedor", "Distribuidor", "Socio comercial").
- [ ] ¿Requiere clasificación o categorización de proveedores? (ej: insumos, mercancía para reventa, servicios).
- [ ] ¿Se requiere adjuntar archivos digitales al proveedor? (ej: copia del RUT, certificado bancario, contratos en PDF).
- [ ] ¿Maneja retención en la fuente o retenciones de impuestos locales aplicables a proveedores?

---

## 3. Compras y Abastecimiento

- [ ] ¿Las compras requieren flujo de aprobación? (ej: borrador de orden de compra → aprobación por supervisor → registro definitivo).
- [ ] ¿Se manejan múltiples bodegas o ubicaciones de almacenamiento?
- [ ] ¿Se requiere registrar costos adicionales asociados a la compra? (ej: fletes, aranceles, empaque) que deban prorratearse en el `precio_costo` unitario de los productos.
- [ ] ¿Cómo se calcula el costo del inventario?
  - [ ] **Último Costo Pactado** (Predeterminado en template: actualiza el costo al último valor de compra).
  - [ ] **Costo Promedio Ponderado** (Requiere lógica adicional para recalcular `precio_costo` con base al saldo anterior y el nuevo ingreso).
- [ ] ¿Permite devoluciones de compra a proveedores con descuento automático de inventario y reversión de cuentas por pagar?

---

## 4. Cuentas por Pagar (Obligaciones a Crédito)

- [ ] ¿Maneja plazos estandarizados por proveedor? (ej: crédito a 15, 30, 60 días predefinido al elegir el proveedor).
- [ ] ¿Se requiere un sistema de notificaciones automáticas para alertar sobre deudas próximas a vencer?
  - [ ] Alertas por correo electrónico internas a contabilidad.
  - [ ] Envío automatizado de reportes semanales de saldos por pagar.
- [ ] ¿Hay control de intereses por mora o recargos en deudas vencidas?
- [ ] ¿Se requiere conciliación bancaria? (vincular el abono de la cuenta por pagar a un movimiento real de banco o caja general).

---

## 5. Reportes y Dashboards ERP

- [ ] KPI Dashboard específico: ¿El cliente necesita ver márgenes de utilidad bruta calculados a partir de `precio_venta - precio_costo` reales del historial de ventas?
- [ ] ¿El reporte Excel de compras necesita columnas específicas? (ej: desglose de impuestos, usuario que registró, NIT proveedor).
- [ ] Gráficas adicionales de deudas por proveedor y proyección de flujo de caja para pagos programados.

---

## Estimación de Esfuerzo por Módulo ERP

| Módulo Personalizable | Sin Adaptar | Adaptación Menor | Adaptación Compleja |
|-----------------------|-------------|------------------|---------------------|
| **Proveedores** | 0h | 2h (Campos extra) | 8h (Gestión de documentos) |
| **Compras & Stock** | 0h | 4h (Flujo de IVA) | 16–24h (Costo Promedio / Múltiples Bodegas) |
| **Cuentas por Pagar** | 0h | 3h (Plazos automáticos) | 12h (Notificaciones programadas) |
| **Reportes Financieros** | 0h | 4h (Excel detallado) | 10h (Dashboard de utilidades netas) |

---

## Estructura de Precios Tier Medium (SaaS ERP)

```
Base Tier Medium (Despliegue del Template estándar):  $1,500 USD
+ Customizaciones complejas (Horas estimadas × Tarifa): $X USD
+ Soporte técnico y hosting anualizado:               $350–600 USD
───────────────────────────────────────────────────────────────────────
Valor Total Sugerido de Contrato:                       $1,850 - $3,500 USD
```
