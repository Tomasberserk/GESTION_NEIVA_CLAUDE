# Template Professional — Listado de Componentes de Interfaz de Usuario (UI)

Este documento define la estructura de componentes React 19 (JSX) y las páginas exclusivas del **Tier Professional** para los sistemas construidos por la fábrica. En este tier, el frontend requiere estar tipado de manera rigurosa utilizando **TypeScript (TSX)** para garantizar la estabilidad y escalabilidad en despliegues corporativos.

---

## 🧭 1. Nuevas Páginas y Portales del Módulo Corporativo

### A. Portal de Facturación y Suscripciones (`BillingPortal.tsx`)
Página de administración donde el comercio gestiona su relación de pagos con el SaaS.
* **Componentes Hijos:**
  * `<PlanSelectorCard />`: Muestra las opciones de planes (Basic, Medium, Professional) con su precio, límites y el plan activo resaltado.
  * `<PaymentMethodCard />`: Permite al usuario ver su tarjeta de crédito activa (enmascarada) e iniciar el flujo de actualización segura mediante Stripe Elements / iframe de Wompi.
  * `<InvoiceHistoryTable />`: Tabla interactiva para descargar los recibos de cobro de sus mensualidades generados por la plataforma.
* **Estados Clave:** `planActivo`, `cargandoCheckout`, `facturasCobro`.

### B. Portal de Desarrollador (`DeveloperPortal.tsx`)
Panel dedicado a administradores para configurar integraciones y sincronizar con tiendas virtuales de terceros.
* **Componentes Hijos:**
  * `<ApiKeyGenerator />`: Formulario para registrar una nueva llave de API (`client_name`). Al crearse, muestra la clave en texto plano dentro de un modal destacado con opción de copiado rápido al portapapeles.
  * `<ActiveApiKeysTable />`: Listado de llaves activas, mostrando fecha de creación, nombre del cliente, y un botón con confirmación modal para revocar de forma inmediata (`DELETE /developer/keys/{id}`).
  * `<ApiUsageChart />`: Gráfico de líneas (usando Recharts) para monitorizar el volumen de peticiones por minuto (Rate Limits) consumido por sus integraciones.
* **Estados Clave:** `apiKeysList`, `newKeyGenerated`, `consumoMinuto`.

### C. Módulo de Facturación Electrónica DIAN (`DianBillingPanel.tsx`)
Panel centralizado de administración tributaria para configurar resoluciones y supervisar los comprobantes oficiales.
* **Componentes Hijos:**
  * `<DianResolutionSetup />`: Formulario para ingresar resoluciones oficiales (número, prefijo, fecha, vigencia, rangos numéricos).
  * `<ElectronicInvoiceList />`: Listado avanzado de comprobantes electrónicos con estado ante la DIAN ('Aprobado', 'Rechazado', 'Procesando').
  * `<CUFESnapshotModal />`: Modal para inspeccionar detalles del envío fiscal (código CUFE, respuesta cruda del servidor de la DIAN, fecha de firma).
* **Estados Clave:** `resolucionActiva`, `listadoFacturas`, `facturaSeleccionada`.

---

## 🧩 2. Componentes Reutilizables de Autenticación y POS

### A. Botón de Single Sign-On (`SSOGoogleButton.tsx`)
Componente interactivo tipo botón para integrar en las páginas de Login y Registro de la plataforma.
* **Características visuales:** Icono oficial SVG de Google alineado, bordes redondeados, micro-animación en hover y feedback de carga.
* **Comportamiento:** Solicita la URL de redirección al backend, inicia el flujo de consentimiento OAuth2 de Google en una ventana emergente segura, y gestiona la captura del token JWT final en el frontend.

### B. Indicador de Estatus Fiscal en POS (`POSFiscalIndicator.tsx`)
Visualizador integrado en la barra de herramientas de la pantalla de ventas (POS) para indicar al cajero si la facturación electrónica está activa y si hay contingencias técnicas.
* **Estados Visuales:**
  * 🟢 **Activo:** Conexión estable. Las ventas se emitirán y validarán al instante ante la DIAN.
  * 🟡 **Contingencia/Sin Resolución:** Alerta que avisa que la numeración está cerca del límite o que no hay resolución activa registrada.
  * 🔴 **Error Técnico:** Fallo de comunicación. Las facturas se guardarán localmente para emisión en lote posterior (modo offline).

---

## 🎨 3. Estilo Visual y UX Recomendada

* **Gradientes Premium en Plan:** Utilizar gradientes HSL (Violeta a Índigo) en los paneles de facturación para destacar el nivel "Professional" del servicio.
* **Modales de Advertencia Críticos:** Al revocar llaves de API o registrar resoluciones fiscales, el sistema debe exigir confirmación de seguridad para evitar interrupciones de servicios externos o facturas rechazadas.
