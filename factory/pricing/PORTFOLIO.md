# Portafolio de Productos — Fábrica de Agentes IA

> Catálogo de sistemas disponibles para clientes.  
> Última actualización: 2026-05-11

---

## Propuesta de valor

Construimos sistemas de software de gestión empresarial a una fracción del costo y tiempo del desarrollo tradicional, usando orquestación de IA con Claude + Gemini.

**Tiempo de entrega:**
- Tier basic: 3–5 días hábiles
- Tier medium: 2–3 semanas
- Tier premium: 4–8 semanas

---

## Tier Basic — POS en la nube

**Ideal para:** tiendas de barrio, minimercados, panaderías, ferreterías pequeñas, papelerías con internet estable.

**Infraestructura:** Cloud (Supabase) — requiere conexión a internet.

### Módulos incluidos

| Módulo | Descripción |
|--------|-------------|
| **Control de inventario** | CRUD de productos con foto, código de barras, precio costo/venta, stock |
| **Punto de venta** | Carrito visual, checkout, descuento automático de stock |
| **Historial de ventas** | Lista completa con detalle por producto |
| **Reportes** | Exportar ventas a Excel por rango de fechas |
| **Dashboard** | KPIs del día: ventas, ingresos, productos con stock bajo |
| **Autenticación** | Multi-usuario por tienda: admin + tenderos |
| **Acceso multi-dispositivo** | PC, tablet, celular — cualquier navegador |

### Qué NO incluye

- Múltiples sucursales
- Facturación electrónica DIAN
- Pasarela de pagos
- App móvil nativa
- Proveedores o cuentas por pagar
- Reportes avanzados o gráficas
- Funcionamiento sin internet

### Precios

| Modalidad | Precio |
|-----------|--------|
| Sistema completo (pago único) | $300–500 USD |
| Sistema + personalización visual | $400–600 USD |
| Sistema + hosting primer año | $450–750 USD |
| Mantenimiento mensual (opcional) | $30–60 USD/mes |

---

## Tier Medium — ERP Ligero en la nube

**Ideal para:** distribuidores, restaurantes, tiendas con múltiples cajeros, empresas con manejo de proveedores.

**Infraestructura:** Cloud (Supabase) — requiere conexión a internet.

### Módulos incluidos (todo el Basic +)

| Módulo adicional | Descripción |
|-----------------|-------------|
| **Gestión de proveedores** | Directorio de proveedores, historial de compras |
| **Órdenes de compra** | Crear OC, recibir mercancía, actualizar stock automáticamente |
| **Cuentas por pagar** | Seguimiento de deudas con proveedores |
| **Contabilidad básica** | Balance de ingresos vs egresos por período |
| **Multi-usuario avanzado** | Roles granulares: admin, supervisor, cajero, bodeguero |
| **Reportes avanzados** | Por categoría, por proveedor, por usuario, por turno |
| **Gráficas** | Ventas por período, productos top, rotación de inventario |
| **Multi-sucursal** | Varias sedes, un solo panel de control |

### Precios

| Modalidad | Precio |
|-----------|--------|
| Sistema completo (pago único) | $1,500–2,500 USD |
| Sistema + personalización | $2,000–3,000 USD |
| Sistema + hosting primer año | $2,200–3,500 USD |
| Mantenimiento mensual | $80–150 USD/mes |

---

## Tier Premium — On-Premise / Híbrido

**Ideal para:** negocios en zonas con internet inestable o sin internet, empresas que exigen que su data viva localmente, clientes con alta rotación de ventas que no pueden depender de la nube.

**Infraestructura:** instalación local en el equipo del cliente + sincronización opcional a la nube cuando hay señal.

### Qué lo diferencia

- **Funciona sin internet** — ventas, inventario y reportes operan aunque se caiga la señal
- **Data local** — la base de datos vive en el PC del cliente, no en servidores externos
- **Sincronización automática** — cuando vuelve el internet, sincroniza con la nube sin intervención
- **Backup en la nube** — aunque la data sea local, hay respaldo automático para evitar pérdidas

### Módulos incluidos (todo el Medium +)

| Módulo adicional | Descripción |
|-----------------|-------------|
| **Motor offline** | SQLite local sincronizado con PostgreSQL en la nube |
| **Cola de sincronización** | Las ventas hechas sin internet se envían al reconectar |
| **Dashboard de sync** | El admin ve cuándo fue la última sincronización |
| **Instalador** | Ejecutable para Windows/Mac que levanta el sistema local |
| **Soporte presencial** | Instalación y configuración en sitio incluida |

### Qué NO incluye

- Multi-tenant SaaS
- SSO / login con Google
- API pública
- Webhooks

### Precios

| Modalidad | Precio |
|-----------|--------|
| Sistema completo (pago único) | $2,500–4,000 USD |
| Sistema + personalización | $3,500–5,500 USD |
| Mantenimiento anual (incluye actualizaciones) | $300–600 USD/año |
| Soporte presencial adicional | $50–100 USD/visita |

> **Por qué es más caro:** cada instalación es única, requiere presencia física, las actualizaciones son manuales por cliente, y el soporte es de mayor complejidad.

---

## Servicios adicionales (cualquier tier)

| Servicio | Precio |
|---------|--------|
| Capacitación al equipo del cliente | $100–200 USD |
| Migración de datos desde Excel/sistema anterior | $150–400 USD |
| Integración con facturación electrónica DIAN | $500–1,000 USD |
| Integración con WhatsApp (envío de recibos) | $200–400 USD |
| Integración con impresoras de tickets | $150–300 USD |
| Lector de código de barras por hardware | $100–200 USD |
| App móvil React Native (iOS + Android) | $2,000–5,000 USD |

---

## Comparación rápida

| Característica | Basic | Medium | Premium |
|----------------|-------|--------|---------|
| Inventario y ventas | ✅ | ✅ | ✅ |
| Reportes Excel | ✅ | ✅ | ✅ |
| Dashboard KPIs | ✅ | ✅ | ✅ |
| Acceso multi-dispositivo | ✅ | ✅ | ✅ |
| Proveedores y compras | ❌ | ✅ | ✅ |
| Contabilidad | ❌ | ✅ | ✅ |
| Multi-sucursal | ❌ | ✅ | ✅ |
| Funciona sin internet | ❌ | ❌ | ✅ |
| Data 100% local | ❌ | ❌ | ✅ |
| Instalación presencial | ❌ | ❌ | ✅ |
| Multi-tenant SaaS | ❌ | ❌ | ❌ |
| Tiempo de entrega | 3–5 días | 2–3 semanas | 4–8 semanas |
| Precio desde | $300 USD | $1,500 USD | $2,500 USD |

---

## Cómo cotizar un proyecto

1. Identificar el tier base según los módulos requeridos
2. Completar el `customization-checklist.md` del tier correspondiente
3. Estimar horas de customización (ver checklist → tabla de estimación)
4. Agregar servicios adicionales si aplica
5. Definir modalidad (pago único vs mantenimiento mensual)

**Precio final = precio base tier + (horas customización × tarifa hora) + servicios adicionales**
