# Fábrica de Agentes IA — Cómo funciona

> La fábrica usa Claude + Gemini para construir sistemas de software de negocio de forma semi-automática.  
> Gestión Neiva es el primer producto y la implementación de referencia del tier basic.

---

## Los tres tiers

| Tier | Qué incluye | Para quién | Precio cliente | Costo IA |
|------|------------|-----------|---------------|---------|
| **Basic** | Inventario + Ventas + Reportes básicos | Tiendas, pequeños comercios | $300–800 USD | ~$0.21 |
| **Medium** | + Proveedores + Compras + Contabilidad simple + Multi-usuario | Medianas empresas | $1,500–3,500 USD | ~$0.80 |
| **Professional** | + Multi-tenant real + Pasarela de pagos + SSO + API pública | Startups / SaaS | $5,000–15,000 USD | ~$2.50 |

---

## Cómo construir un sistema nuevo

### Paso 0: Recolectar requirements del cliente

El cliente describe su negocio en lenguaje natural. Se captura en:
```
factory/jobs/{nombre-sistema}/requirements-raw.txt
```

### Paso 1: Gemini analiza los requirements (gratis)

```bash
gemini analyze factory/jobs/{sistema}/requirements-raw.txt \
  --output factory/jobs/{sistema}/requirements.json \
  --prompt "Extrae entidades, relaciones, flujos de negocio y reglas especiales"
```

Output: `requirements.json` estructurado con entidades, módulos, reglas de negocio.

### Paso 2: Architect diseña el sistema (~$0.05)

```
Spawns: architect agent
Input:  factory/jobs/{sistema}/requirements.json
        factory/templates/{tier}/schema.md (referencia)
Output: factory/jobs/{sistema}/schema.md
        factory/jobs/{sistema}/api-contracts.md
```

### Paso 3-4: Haiku construye el backend (~$0.05)

```
Spawns: haiku-worker × 3 (paralelo)
Input:  schema.md + api-contracts.md
Output: app/models.py, app/schemas/, alembic/versions/
        app/routers/, app/services/
```

### Paso 5: Sonnet construye el frontend (~$0.08)

```
Spawns: Claude Sonnet
Input:  api-contracts.md + factory/templates/{tier}/components-list.md
Output: frontend/src/pages/, frontend/src/components/, frontend/src/hooks/
```

### Paso 6: Haiku escribe tests (~$0.02)

```
Spawns: haiku-worker
Input:  routers/ + services/
Output: tests/
```

### Paso 7: Gemini hace QA (gratis)

```bash
gemini review factory/jobs/{sistema}/ \
  --output factory/jobs/{sistema}/qa-report.md
```

Output: lista de bugs, inconsistencias, mejoras sugeridas.

### Paso 8: Haiku genera DevOps (~$0.01)

```
Spawns: haiku-worker
Input:  stack definido
Output: docker-compose.yml, README.md, .env.example, Makefile
```

---

## Estructura de un job

```
factory/jobs/{nombre-sistema}/
├── requirements-raw.txt      # Input del cliente
├── requirements.json         # Gemini estructurado
├── schema.md                 # Architect: modelo de datos
├── api-contracts.md          # Architect: contratos de API
├── qa-report.md              # Gemini: reporte de calidad
└── ESTADO.md                 # Estado del job (en progreso, entregado, etc.)
```

---

## Templates disponibles

```
factory/templates/
├── basic/                    # Patrón Gestión Neiva
│   ├── schema.md             # Modelo de datos base
│   ├── api-contracts.md      # Endpoints estándar
│   ├── components-list.md    # Componentes React del tier
│   └── customization-checklist.md
├── medium/                   # (próximo sprint)
└── professional/             # (sprint 7)
```

---

## Costo estimado por sistema

### Tier basic (~$0.21 total)

| Paso | Agente | Costo |
|------|--------|-------|
| Requirements análisis | Gemini | $0.00 |
| Schema + contratos | Sonnet | ~$0.05 |
| Backend boilerplate ×3 | Haiku | ~$0.02 |
| Backend routers ×3 | Haiku | ~$0.03 |
| Frontend | Sonnet | ~$0.08 |
| Tests | Haiku | ~$0.02 |
| QA review | Gemini | $0.00 |
| DevOps | Haiku | ~$0.01 |
| **Total** | | **~$0.21** |

Con precio de venta de $500 USD promedio = **margen de ~2380x sobre costo IA**.

---

## Reglas de la fábrica

1. Siempre empezar con el template del tier correspondiente
2. El Architect revisa los requirements antes de generar código
3. Gemini hace QA antes de entregar al cliente
4. Todo código generado va en `factory/jobs/{sistema}/` hasta ser validado
5. El cliente NO ve el costo IA — ve el producto terminado
