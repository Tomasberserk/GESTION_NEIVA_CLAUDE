# Plan de Implementación — Panel de Super Admin y Sistema de Soporte CRM (Inbox)

Este plan define el diseño técnico, de base de datos y la interfaz de usuario para implementar el **Panel de Super Admin** y el **Sistema Integrado de Soporte al Cliente (Inbox estilo Gmail)**. Este módulo permitirá al dueño de la plataforma controlar el estado de las suscripciones, activar/inactivar comercios y chatear directamente con los tenderos en una bandeja de entrada unificada.

---

## 🏛️ 1. Diseño de Base de Datos (Nuevos Modelos)

Añadiremos dos nuevas tablas en el esquema de base de datos relacional para gestionar la mensajería de soporte.

```
                    Empresa / Usuario (Comercio)
                              │
                              ▼
                     SoporteTicket (Hilo de Conversación)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            SoporteMensaje      SoporteMensaje
            (Remitente: User)   (Remitente: Superadmin)
```

### A. Modelo `SoporteTicket` (Mesa de ayuda)
* **Tabla:** `soporte_tickets`
* **Campos:**
  * `id`: UUID (Primary Key, default uuid.uuid4)
  * `empresa_id`: UUID (Foreign Key a `empresas.id`, ondelete="CASCADE", nullable=False)
  * `usuario_id`: UUID (Foreign Key a `usuarios.id`, ondelete="RESTRICT", nullable=False) -- Quién abrió el ticket
  * `asunto`: String(150), nullable=False
  * `estado`: Enum o String (valores: 'abierto', 'respondido', 'cerrado'), default 'abierto', nullable=False
  * `created_at`: DateTime (Audit)
  * `updated_at`: DateTime (Audit)
  * `is_active`: Boolean, default True

### B. Modelo `SoporteMensaje` (Conversación interna)
* **Tabla:** `soporte_mensajes`
* **Campos:**
  * `id`: UUID (Primary Key, default uuid.uuid4)
  * `ticket_id`: UUID (Foreign Key a `soporte_tickets.id`, ondelete="CASCADE", nullable=False)
  * `remitente_rol`: String(30) -- 'superadmin' o 'usuario' (para identificar quién escribe)
  * `remitente_email`: String(255) -- Correo de quien escribe para mostrar en la interfaz
  * `mensaje`: Text, nullable=False
  * `created_at`: DateTime (Audit)

---

## 🔒 2. Seguridad y Autenticación del Super Admin

El acceso al Panel de Super Admin estará protegido en dos niveles:
1. **En Backend:** Todos los endpoints bajo el prefijo `/superadmin/*` validarán la cabecera HTTP `x-superadmin-key` comparándola directamente con la variable de entorno `SUPERADMIN_KEY` (definida en el servidor/.env).
2. **En Frontend:** Crearemos una ruta especial `/superadmin`. La primera vez que se intente ingresar, mostrará una pantalla de login que solicitará la **Llave del Sistema (Superadmin Key)**. Esta clave se guardará localmente en el navegador (`localStorage.setItem('x-superadmin-key', key)`) y se enviará en las cabeceras de cada consulta.

---

## 🔌 3. Contratos de API REST

### A. Rutas de Control de Tiendas (Super Admin)
* `GET /superadmin/empresas` -> Retorna listado de todas las empresas con: NIT, Nombre Comercial, Estado (`is_active`), Fecha de Vencimiento de Trial, y conteo de usuarios.
* `PUT /superadmin/empresas/{empresa_id}/trial` -> Extiende o recorta la fecha de vencimiento (`trial_expires_at`).
  * *Payload:* `{"trial_expires_at": "2026-06-30"}`
* `PUT /superadmin/empresas/{empresa_id}/status` -> Activa (`is_active = true`) o suspende (`is_active = false`) a la empresa del sistema.
  * *Payload:* `{"is_active": false}`

### B. Rutas de Soporte CRM (Super Admin)
* `GET /superadmin/tickets` -> Lista todos los tickets de soporte de todos los tenants de la base de datos (ordenados por fecha de actualización).
* `POST /superadmin/tickets/{ticket_id}/responder` -> Envía una respuesta al comercio.
  * *Payload:* `{"mensaje": "Hola Carlos, ya hemos solucionado tu consulta..."}`

### C. Rutas de Soporte para Usuarios (Tiers Basic, Medium, Professional)
* `POST /soporte/tickets` -> Abre un ticket de soporte.
  * *Payload:* `{"asunto": "Error en inventario", "mensaje": "Hola, al subir fotos..."}`
* `GET /soporte/tickets` -> Obtiene el inbox del usuario (lista de tickets propios).
* `GET /soporte/tickets/{ticket_id}` -> Carga la conversación de un ticket.
* `POST /soporte/tickets/{ticket_id}/responder` -> Responde dentro de un hilo abierto.

---

## 🎨 4. Diseño de la Interfaz (Frontend UI)

### A. Vista del Cliente: Panel de Soporte (`/soporte`)
* Un **Inbox estilo Gmail o Helpdesk** limpio e intuitivo en el sidebar:
  * **Barra lateral izquierda:** Lista de conversaciones con colores según el estado (Verde: Respondido por ti, Naranja: Pendiente por responder por Superadmin, Gris: Cerrado).
  * **Ventana de Chat/Email central:** Muestra el hilo de mensajes ordenado cronológicamente.
  * **Caja de Texto inferior:** Permite escribir y presionar "Enviar Mensaje".
  * **Botón "Nuevo Ticket":** Abre un modal para crear una conversación.

### B. Vista del Super Admin: Consola del Sistema (`/superadmin`)
* **Dashboard global con 2 pestañas:**
  * **Pestaña 1: Control de Comercios:**
    * Grilla con barras de búsqueda y filtros.
    * Indicadores de estado de tiendas.
    * Inputs tipo selector de fecha interactiva para ampliar el Trial al instante.
    * Botón de bloqueo/suspensión en rojo.
  * **Pestaña 2: Bandeja de Soporte Global (Buzón CRM):**
    * Lista de todos los tickets abiertos por todas las tiendas.
    * Permite chatear en tiempo real con cualquier tendero para responder sus dudas técnicas.

---

## 📂 Propuesta de Cambios por Archivos

### Backend
1. **app/models.py:** Crear los modelos SQLAlchemy `SoporteTicket` y `SoporteMensaje`.
2. **migrations:** Generar la migración de Alembic para crear las dos nuevas tablas (`alembic revision --autogenerate -m "crear_tablas_soporte"`).
3. **schemas:** Crear esquemas de validación Pydantic en un nuevo archivo `app/schemas/soporte.py`.
4. **app/routers/superadmin.py [NEW]:** Crear rutas del panel de control de empresas y mensajería global.
5. **app/routers/soporte.py [NEW]:** Crear rutas del lado del usuario de la tienda.
6. **app/main.py:** Registrar los nuevos routers.

### Frontend
1. **frontend/src/components/layout/Sidebar.jsx:** Añadir opción "Soporte Técnico" en la navegación del menú.
2. **frontend/src/App.jsx:** Configurar las rutas `/soporte` y `/superadmin`.
3. **frontend/src/pages/Soporte.jsx [NEW]:** UI de mensajería estilo inbox del cliente.
4. **frontend/src/pages/SuperAdmin.jsx [NEW]:** Panel de control e inbox global del Super Administrador.
