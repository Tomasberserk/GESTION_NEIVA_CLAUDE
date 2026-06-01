# Lista de Tareas — Panel de Super Admin y Sistema de Soporte CRM

- [ ] **Estructuración de Base de Datos y Modelos**
  - [ ] Implementar modelos `SoporteTicket` y `SoporteMensaje` en `app/models.py`.
  - [ ] Diseñar y ejecutar la migración de Alembic para crear las nuevas tablas en la base de datos (`alembic revision --autogenerate -m "crear_tablas_soporte"`).
- [ ] **Desarrollo del Backend API**
  - [ ] Crear el archivo de esquemas Pydantic `app/schemas/soporte.py`.
  - [ ] Crear el router `app/routers/superadmin.py` con middleware de validación de cabecera `x-superadmin-key`.
  - [ ] Implementar endpoints del Super Admin para listar empresas, actualizar trial (`trial_expires_at`) e inactivar/activar cuentas.
  - [ ] Crear el router `app/routers/soporte.py` para la gestión de tickets y mensajería bidireccional del lado de la tienda.
  - [ ] Registrar ambos routers en `app/main.py`.
- [ ] **Desarrollo del Frontend UI**
  - [ ] Añadir la opción "Soporte Técnico" en `frontend/src/components/layout/Sidebar.jsx` (debajo de Reportes, usando un icono de mensaje de Lucide).
  - [ ] Configurar las rutas en `frontend/src/App.jsx` para `/soporte` y `/superadmin`.
  - [ ] Diseñar el panel del cliente en `frontend/src/pages/Soporte.jsx` con bandeja estilo Gmail e hilos de chat.
  - [ ] Diseñar la consola de administración en `frontend/src/pages/SuperAdmin.jsx` (acceso con login de clave, control de tiendas e inbox de soporte global).
- [ ] **Validación y QA Final**
  - [ ] Escribir tests de integración para el control de acceso del Super Admin.
  - [ ] Probar el flujo extremo a extremo: Crear ticket como comercio -> Recibir y responder como Super Admin -> Verificar actualización del hilo en el cliente.
