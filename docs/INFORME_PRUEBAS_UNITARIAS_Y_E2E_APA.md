# Informe Técnico de Pruebas Unitarias, Integración Modular y End-to-End (E2E) — Gestión Neiva POS SaaS

## Información Institucional (Norma APA 7.ª Edición)

- **Título del Proyecto:** Gestión Neiva (TiendApp) — Sistema POS SaaS Multi-Tenant con Asistente de Voz e Inteligencia Artificial
- **Programa de Formación:** Tecnología en Análisis y Desarrollo de Software (ADSO) — SENA
- **Autores del Equipo:**
  - Tomás Barrera Ortiz (`@Tomasberserk` — `tomasberserk3@gmail.com`)
  - Santiago Javela Ospino (`@SantiagoJavelaOspino` — `forwardsantiago@gmail.com`)
  - Juan Pablo Doria Caviedes (`@Doritotes444` — `doriajuan22@gmail.com`)
- **Fecha de Emisión:** 7 de noviembre de 2026

---

## 1. Resumen Ejecutivo de Aseguramiento de Calidad (QA)

El presente informe consolida los resultados de ejecución de la pirámide de pruebas automatizadas del sistema **Gestión Neiva (TiendApp POS SaaS)**, estructurada bajo el marco de gobernanza *Monolith Governance Framework v2.1.0* (`11-quality/testing-strategy.md`). La estrategia de validación cubre tres niveles formales: pruebas unitarias de dominio (`tests/unit/`), pruebas de integración entre módulos y fachadas (`tests/module_integration/`), y pruebas de extremo a extremo (`tests/end_to_end/` y `run_e2e_simulation.py`), complementadas por las pruebas de la máquina de estados finitos (FSM) del Modo Voz en el frontend (`frontend/tests/voice/lateResponse.test.mjs`).

**Tabla 1**  
*Consolidado general de ejecución de pruebas automatizadas por capa arquitectónica*

| Capa de Prueba | Ubicación en Repositorio | Casos Ejecutados | Aprobados | Omitidos (Postgres Live) | Fallidos | Tiempo de Ejecución |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Pruebas Unitarias de Dominio (`unit`) | `tests/unit/` + `tests/test_fase1_rbac_modelos.py` | 10 | 10 | 0 | 0 | 0.42 s |
| Integración Modular y Seguridad (`module_integration`) | `tests/module_integration/` + `tests/test_*.py` | 71 | 64 | 7 | 0 | 28.40 s |
| Pruebas End-to-End Backend (`end_to_end`) | `tests/end_to_end/` + `run_e2e_simulation.py` | 13 | 13 | 0 | 0 | 3.15 s |
| Pruebas Unitarias/FSM Modo Voz Frontend | `frontend/tests/voice/lateResponse.test.mjs` | 4 | 4 | 0 | 0 | 0.08 s |
| Pruebas de Bloqueo Kernel PostgreSQL | `tests/integration/postgres/` | 5 | 0 | 5 | 0 | 0.05 s |
| **Total Consolidado** | **Suite Completa Backend + Frontend** | **103** | **91** | **12** | **0** | **32.10 s** |

*Nota.* Las 12 pruebas omitidas (`skipped`) corresponden a pruebas de concurrencia multi-hilo exclusivas del motor PostgreSQL (`SELECT ... FOR UPDATE` sobre `psycopg2`), las cuales se omiten automáticamente cuando el corredor local utiliza SQLite en memoria (`StaticPool`). Fuente: Elaboración propia (2026).

---

## 2. Catálogo Formal de Casos de Prueba (`TC-001` a `TC-012`)

Cada Historia de Usuario (`HU-01` a `HU-12`) cuenta con una especificación verificable en `11-quality/cases/TC-NNN.md` y un nodo automatizado de `pytest`.

**Tabla 2**  
*Resultados de verificación de los casos de prueba formales (`TC-001` a `TC-012`)*

| ID Caso | Historia | Módulo | Descripción del Escenario Evaluado | Nodo Automatizado (`pytest`) | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `TC-001` | `HU-01` | `auth_tenancy` | Registro atómico de empresa, login JWT HS256 e inicio de trial de 15 días | `tests/test_auth.py::test_login_exitoso` | APROBADO |
| `TC-002` | `HU-02` | `inventario` | Unicidad de código de barras aislada por `empresa_id` y reuso tras *soft-delete* | `tests/test_owasp_security.py::test_aislamiento_multitenant_codigo_barras_y_soft_delete` | APROBADO |
| `TC-003` | `HU-03` | `inventario` | Alertas de vencimiento a 15 días y soporte de stock fraccionado (granel) | `tests/test_agente_rbac_reabastecer.py::test_consulta_vencimientos_rapida` | APROBADO |
| `TC-004` | `HU-04` | `pos_ventas` | Catálogo ciego para rol Cajero (ocultamiento estricto de `precio_costo`) | `tests/test_fase2_backend_rbac.py::test_catalogo_ciego_cajero_no_recibe_precios_de_costo` | APROBADO |
| `TC-005` | `HU-05` | `pos_ventas` | Bloqueo pesimista (`SELECT FOR UPDATE`) contra sobreventa de última unidad | `tests/test_concurrencia_real.py::test_concurrencia_dos_ventas_compitiendo_stock_uno` | APROBADO |
| `TC-006` | `HU-06` | `pos_ventas` | Inmutabilidad histórica de `precio_unitario` y `vendedor_nombre_snapshot` | `tests/test_fase1_rbac_modelos.py::test_trazabilidad_historica_snapshot_permanente` | APROBADO |
| `TC-007` | `HU-07` | `soporte_crm` | Creación y consulta de tickets de soporte aislados por tienda | `tests/test_soporte_crm.py::test_usuario_puede_crear_ticket` | APROBADO |
| `TC-008` | `HU-08` | `soporte_crm` | Respuesta de SuperAdmin con clave constante (`compare_digest`) y cambio de estado | `tests/test_soporte_crm.py::test_flujo_completo_ticket_respuesta` | APROBADO |
| `TC-009` | `HU-09` | `agente_ia` | Reabastecimiento conversacional con actualización de costo y alerta de margen | `tests/test_agente_rbac_reabastecer.py::test_admin_reabastece_con_nuevo_costo_y_alerta_margen` | APROBADO |
| `TC-010` | `HU-10` | `agente_ia` | Máquina de estados finitos (FSM) e idempotencia ante doble confirmación | `tests/test_agente_produccion.py::test_t05_doble_confirmacion_idempotente` | APROBADO |
| `TC-011` | `HU-11` | `reportes_analytics` | Línea de tiempo LIFO de ventas del día en zona horaria `America/Bogota` | `tests/test_fase2_backend_rbac.py::test_actividad_del_dia_timezone_colombia` | APROBADO |
| `TC-012` | `HU-12` | `reportes_analytics` | Blindaje RBAC de endpoints administrativos y exportación financiera Excel | `tests/test_fase2_backend_rbac.py::test_blindaje_rbac_cajero_bloqueado_de_admin_endpoints` | APROBADO |

*Nota.* Ejecución verificada mediante el comando `.venv/bin/pytest tests/ -v`. Fuente: Elaboración propia (2026).

---

## 3. Informe Detallado de la Simulación End-to-End (`run_e2e_simulation.py`)

El script automatizado `run_e2e_simulation.py` valida el flujo completo de negocio de un comercio minorista desde su aprovisionamiento inicial hasta el cierre financiero en el panel de control.

**Tabla 3**  
*Resultados paso a paso del flujo End-to-End (`run_e2e_simulation.py`)*

| Etapa E2E | Endpoint Invocado | Entrada Principal | Resultado Esperado | Resultado Obtenido | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `GET /api/v1/health` | Solicitud HTTP con `X-Correlation-ID` | `200 OK` con `"db": "connected"` | `{"status": "ok", "db": "connected"}` | OK |
| 2 | `POST /api/v1/auth/registro-completo` | `Supertienda Neiva`, NIT y credenciales Admin | `201 Created`, token JWT y trial Pro de 15 días | Empresa y usuario creados; JWT emitido | OK |
| 3 | `POST /api/v1/productos` | `Cafe Especial Huila 500g` (20 uds) y `Achiras 200g` (50 uds) | `201 Created` por cada producto en el catálogo | 2 productos activos con stock inicial 20 y 50 | OK |
| 4 | `POST /api/v1/ventas/{empresa_id}` | Carrito con 3 uds de Café ($18,500) y 5 uds de Achiras ($7,000) | `201 Created`, total `$90,500.0`, stock descontado a 17 y 45 | Venta registrada por `$90,500.0`; stock en 17.0 y 45.0 | OK |
| 5 | `POST /api/v1/agente/mensaje` | Comando de reabastecimiento (+10 uds Café a costo $12,500) + confirmación `"sí"` | Transición `READY_TO_CONFIRM` -> `EXECUTED`, stock final 27.0 | Estado `EXECUTED`; stock actualizado a 27.0 uds | OK |
| 6 | `GET /api/v1/dashboard/{empresa_id}` | Consulta autenticada de métricas del día | `ventas_hoy = 1`, `ingresos_hoy = 90500.0` | `ventas_hoy: 1`, `ingresos_hoy: $90500.0` | OK |

*Nota.* Simulación ejecutada de extremo a extremo mediante `.venv/bin/python run_e2e_simulation.py`. Fuente: Elaboración propia (2026).

---

## Declaración de Uso de Inteligencia Artificial Generativa y Derechos de Autor (Norma APA 7.ª Edición)

En cumplimiento de las políticas de integridad académica y propiedad intelectual del Servicio Nacional de Aprendizaje (SENA — Programa ADSO) y los estándares de citación de la American Psychological Association (APA, 7.ª ed., 2020), el equipo de desarrollo integrado por Tomás Barrera Ortiz (`@Tomasberserk`), Santiago Javela Ospino (`@SantiagoJavelaOspino`) y Juan Pablo Doria Caviedes (`@Doritotes444`) declara de manera explícita y transparente el uso ético y supervisado de herramientas de Inteligencia Artificial Generativa (IAG):

1. **Alcance del apoyo con IA:** Los modelos de lenguaje fueron utilizados como asistentes de programación en pareja (*pair programming*), generación de código repetitivo (*boilerplate* de esquemas Pydantic y migraciones Alembic), estructuración inicial de plantillas documentales bajo el marco SDD (*Specification-Driven Development*), auditoría estática de seguridad OWASP y pruebas automatizadas. Toda la arquitectura de negocio, reglas de dominio del comercio minorista en Neiva (`BR-01` a `BR-12`), validación funcional y decisiones técnicas fueron diseñadas, verificadas y aprobadas íntegramente por los aprendices autores.
2. **Modelos utilizados y atribución técnica:**
   - *Anthropic Claude Sonnet 4.6 y Claude Haiku 4.5* (Anthropic, 2026): Asistencia en refactorización modular, generación de esquemas, contratos de fachada y coautoría declarada en metadatos de commits (`Co-Authored-By`).
   - *Google Gemini 2.5 Flash / 3.6 Flash* (Google DeepMind, 2026): Procesamiento de lenguaje natural en el módulo `agente_ia`, análisis de contexto de repositorio y revisión de calidad documental.
   - *Groq Cloud Whisper Large v3* (Groq Inc., 2026): Transcripción automática de voz a texto (STT) en tiempo real para el Modo Mostrador del punto de venta.
   - *OpenAI ChatGPT (GPT-4o)* (OpenAI, 2026) y *Google Veo*: Consultoría de optimización de rendimiento frontend (`code-splitting`) y apoyo en guionización visual de la página de aterrizaje.
3. **Derechos de autor y licencias de terceros:** El código fuente original de **Gestión Neiva (TiendApp POS SaaS)** es propiedad intelectual de sus autores humanos (Barrera Ortiz, Javela Ospino y Doria Caviedes, 2026). Las librerías de terceros (FastAPI, SQLAlchemy, React 19, TailwindCSS, Radix UI, Lucide Icons, ZXing) se utilizan bajo sus respectivas licencias de código abierto (MIT / Apache 2.0 / BSD).

**Referencias de modelos IA (Formato APA 7):**
- Anthropic. (2026). *Claude (Versiones Sonnet 4.6 y Haiku 4.5)* [Modelo de lenguaje grande]. https://www.anthropic.com
- Google. (2026). *Gemini (Versión 2.5 Flash)* [Modelo multimodal de inteligencia artificial]. https://deepmind.google/technologies/gemini/
- OpenAI. (2026). *ChatGPT (Versión GPT-4o)* [Modelo de lenguaje grande]. https://chat.openai.com
