# Visión y Roadmap — Fábrica de Agentes IA + Gestión Neiva

**Versión:** 2.0  
**Fecha:** 2026-05-11  
**Estado:** Activo

---

## 1. La visión real: una fábrica de agentes IA

El objetivo de este proyecto no es solo Gestión Neiva. Es construir una **fábrica de agentes IA** capaz de generar sistemas de software de gestión empresarial de forma semi-automática, usando Claude + Gemini como equipo de desarrollo.

**El negocio en una frase:** orquestar IA para construir sistemas completos a ~$0.21 de costo IA y venderlos entre $300 y $15,000 USD según complejidad.

Gestión Neiva es el primer producto de esa fábrica y su implementación de referencia para el tier "basic". Primero hay que facturar con Gestión Neiva — después se construye la fábrica a escala.

```
[1] Cerrar MVP Gestión Neiva  →  [2] Primer cliente paga  →  [3] Construir la fábrica
```

---

## 2. Los tres tiers de producto

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Tier | Sistema | Módulos core | Precio cliente | Costo IA |
|------|---------|-------------|---------------|---------|
| **Basic** | POS simple | Inventario + Ventas + Reportes + Dashboard | $300–800 USD | ~$0.21 |
| **Medium** | ERP ligero | + Proveedores + Contabilidad + Multi-usuario avanzado | $1,500–3,500 USD | ~$0.80 |
| **Professional** | SaaS completo | + Multi-tenant + Pagos + SSO + API pública + nomina y facturación electrónica Colombia | $5,000–15,000 USD | ~$2.50 |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

Ver `factory/pricing/PORTFOLIO.md` para el catálogo completo.

---

## 3. Stack de agentes — fase actual

**Tabla 2**  
*Registro estructurado de especificaciones técnicas ( Sección 2 )*

| Agente | Modelo | Costo | Rol |
|--------|--------|-------|-----|
| Architect | Claude Sonnet/Opus | Pago | Diseño de sistema, schema DB, contratos API |
| Builder | Claude Sonnet | Pago | Generación de código principal |
| Worker | Claude Haiku | Pago | Schemas, tests, migrations, boilerplate |
| Analyst | Gemini CLI | **Gratis** | Análisis de codebase, QA, requirements |
| Hermes-3 | ~~Together AI~~ | **BLOQUEADO** | Se activa con primer ingreso recurrente |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

**Restricción activa:** Hermes-3 y otras APIs pagas adicionales están bloqueadas hasta que Gestión Neiva genere su primera factura real.

---

## 4. Gestión Neiva — Sistema POS SaaS

### Qué es y para quién

Sistema POS SaaS multi-tenant para tiendas de barrio, minimercados y pequeños comercios de Neiva, Colombia. Alternativa accesible a Siigo o World Office — diseñado para tenderos sin capacitación técnica.

### Stack técnico

- **Backend:** FastAPI + SQLAlchemy sync + PostgreSQL 16 + Alembic
- **Frontend:** React 19 JSX + Vite + TailwindCSS v4 + Shadcn/UI
- **Auth:** JWT (python-jose + bcrypt)
- **Infra dev:** Docker Compose (PostgreSQL 16 + Redis 7) + Codespaces

### Arquitectura

```
Empresa (raíz multi-tenant)
  └─ Usuarios (admin, tendero)
  └─ Productos (inventario con soft delete)
  └─ Ventas
       └─ DetalleVenta (snapshot de precio al momento de venta)
```

**Flujo de venta:**
```
ProductoCard → CartContext → CartSidebar → POST /ventas/{empresa_id}
  → SELECT FOR UPDATE (lock) → descuento stock → INSERT ventas + detalles → 201
```

---

## 5. Estado del MVP (Sprint 3)

**Tabla 3**  
*Registro estructurado de especificaciones técnicas ( Sección 3 )*

| Módulo | Estado |
|--------|--------|
| Auth (registro, login, JWT, logout) | ✅ Funcionando |
| Inventario (CRUD + foto + stock) | ✅ Backend listo, frontend integrado |
| Punto de venta (carrito + checkout) | ✅ CartSidebar en layout |
| Historial de ventas | ✅ Backend listo |
| Reportes Excel | ✅ Backend listo |
| Dashboard (métricas reales) | ✅ Endpoint + UI reales |
| Tests automatizados | ⏳ Pendiente |
| Flujo end-to-end probado | ⏳ Pendiente |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

---

## 6. Cómo arrancar el entorno

```bash
docker compose up -d
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload   # terminal 1
cd frontend && npm run dev                  # terminal 2
```

**API docs:** http://localhost:8000/docs  
**Frontend:** http://localhost:5173

---

## 7. Equipo de desarrollo

El proyecto es desarrollado por un equipo IA:

**Tabla 4**  
*Registro estructurado de especificaciones técnicas ( Sección 4 )*

| Agente | Herramienta | Responsabilidad |
|--------|------------|-----------------|
| **Claude** | Claude Code en Codespaces | Implementación, arquitectura, ejecución |
| **Gemini** | Antigravity editor (Google) | Análisis, QA, propuestas de mejora al plan |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

Los planes son **co-autoría de ambos AIs** — Gemini puede proponer cambios al `PLAN_ACTIVO.md`.  
Ver `AGENTS.md` para el protocolo de colaboración.

---

## 8. Roadmap

### Sprint 3 — Cierre MVP Gestión Neiva (activo)
- Probar flujo end-to-end completo
- Correr migración 002 (barcode por empresa)
- Tests básicos de auth y ventas
- Script de arranque del entorno
- **Meta: sistema listo para el primer cliente real**

### Sprint 4 — Fundamentos de la fábrica (activo en paralelo)
- CLAUDE.md, GEMINI.md, AGENTS.md, PLAN_ACTIVO.md ✅
- `.claude/settings.json` MCP servers ✅
- Agentes `.claude/agents/` ✅
- `factory/templates/basic/` (4 documentos) ✅
- `factory/workflows/build-basic.md` ✅
- `factory/pricing/PORTFOLIO.md` ✅

### Sprint 5 — Pipeline funcional tier basic
- `build-basic.md` como workflow ejecutable real
- Generar un segundo sistema usando el pipeline (demo para clientes)
- Medir costo real en tokens por sistema
- **Primer cliente Gestión Neiva pagando → desbloquea Hermes-3**

### Sprint 6 — Template medium
- Definir y construir template medium (ERP ligero)
- Módulos: proveedores, compras, contabilidad
- Probar construcción con la fábrica

### Sprint 7 — Template professional + Hermes activado
- Template professional: multi-tenant real, pagos, SSO, API pública
- **Activar Hermes-3 vía Together AI** (primer ingreso recurrente confirmado)
- Landing page pública del portafolio
- Primer cliente tier medium o professional

---

## 9. Convenciones del proyecto

- **Sin TypeScript** en el frontend — JSX puro mientras sea MVP
- **No mover archivos sin preguntar** — el namespace `app/models.py` ya causó problemas
- **Venv siempre** — `.venv/bin/python`, `.venv/bin/uvicorn`, `.venv/bin/alembic`
- **El `.env` nunca va a git** — credenciales solo en Codespaces secrets
- **Multi-tenant siempre** — todas las queries filtran por `empresa_id`
- **Soft delete** — `is_active = False`, nunca DELETE físico
- **Gemini lee, Claude actúa** — Gemini para análisis grandes, Claude para implementar

---

*Documento mantenido por Claude + Gemini. Actualizar al final de cada sprint.*

---

## Declaración de Uso de Inteligencia Artificial Generativa y Derechos de Autor (Norma APA 7.ª Edición)

En cumplimiento de las políticas de integridad académica y propiedad intelectual del Servicio Nacional de Aprendizaje (SENA — Programa ADSO) y los estándares de citación de la American Psychological Association (APA, 7.ª ed., 2020), el equipo de desarrollo integrado por Tomás Barrera Ortiz (`@Tomasberserk`), Santiago Javela Ospino (`@SantiagoJavelaOspino`) y Juan Pablo Doria Caviedes (`@Doritotes444`) declara de manera explícita y transparente el uso ético y supervisado de herramientas de Inteligencia Artificial Generativa (IAG):

1. **Alcance del apoyo con IA:** Los modelos de lenguaje fueron utilizados como asistentes de programación en pareja (*pair programming*), generación de código repetitivo (*boilerplate* de esquemas Pydantic y migraciones Alembic), estructuración inicial de plantillas documentales bajo el marco SDD (*Specification-Driven Development*), auditoría estática de seguridad OWASP y pruebas automatizadas. Toda la arquitectura de negocio, reglas de dominio del comercio minorista en Neiva (`BR-01` a `BR-12`), validación funcional y decisiones técnicas fueron diseñadas, verificadas y aprobadas íntegramente por los aprendices autores.
2. **Modelos utilizados y atribución técnica:**
   - *Anthropic Claude Sonnet 4.6 y Claude Haiku 4.5* (Anthropic, 2026): Asistencia en refactorización modular, generación de esquemas, contratos de fachada y coautoría declarada en metadatos de commits (`Co-Authored-By`).
   - *Google Gemini 2.5 Flash / 3.6 Flash* (Google DeepMind, 2026): Procesamiento de lenguaje natural en el módulo `agente_ia`, análisis de contexto de repositorio y revisión de calidad documental.
   - *Groq Cloud Whisper Large v3* (Groq Inc., 2026): Transcripción automática de voz a texto (STT) en tiempo real para el Modo Mostrador del punto de venta.
   - *OpenAI ChatGPT (GPT-4o)* (OpenAI, 2026) y *Google Veo*: Consultoría de optimización de rendimiento frontend (`code-splitting`) y apoyo en guionización visual de la página de aterrizaje.
3. **Derechos de autor y licencias de terceros:** El código fuente original de **Gestión Neiva (TiendApp POS SaaS)** es propiedad intelectual de sus autores humanos (Barrera Ortiz, Javela Ospino y Doria Caviedes, 2026). Las librerías de terceros (FastAPI, SQLAlchemy, React 19, TailwindCSS, Radix UI, Lucide Icons, ZXing) se utilizan bajo sus respectivas licencias de código abierto (MIT / Apache 2.0 / BSD), y los recursos fotográficos de demostración provienen de bancos libres de regalías (Pexels / Picsum Photos) conforme a sus términos de atribución.

**Referencias de modelos IA (Formato APA 7):**
- Anthropic. (2026). *Claude (Versiones Sonnet 4.6 y Haiku 4.5)* [Modelo de lenguaje grande]. https://www.anthropic.com
- Google. (2026). *Gemini (Versión 2.5 Flash)* [Modelo multimodal de inteligencia artificial]. https://deepmind.google/technologies/gemini/
- OpenAI. (2026). *ChatGPT (Versión GPT-4o)* [Modelo de lenguaje grande]. https://chat.openai.com
