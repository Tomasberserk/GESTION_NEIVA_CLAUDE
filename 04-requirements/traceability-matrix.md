# 04 — Traceability Matrix

## User stories (`HU-01` .. `HU-12`)

**Tabla 1**  
*Matriz de trazabilidad bidireccional entre Historias de Usuario, Módulos, Casos de Prueba (`TC-NNN`) y Nodos Automatizados de Pytest*

| HU-NN | Module | Design document | Formal Test Case | Automated Pytest Node |
|---|---|---|---|---|
| HU-01 | `auth_tenancy` | [`models.md`](../06-data/models.md) | [`TC-001`](../11-quality/cases/TC-001.md) | `tests/test_auth.py::test_login_exitoso` |
| HU-02 | `inventario` | [`models.md`](../06-data/models.md) | [`TC-002`](../11-quality/cases/TC-002.md) | `tests/test_owasp_security.py::test_aislamiento_multitenant_codigo_barras_y_soft_delete` |
| HU-03 | `inventario` | [`entities-and-rules.md`](../02-domain/entities-and-rules.md) | [`TC-003`](../11-quality/cases/TC-003.md) | `tests/test_agente_rbac_reabastecer.py::test_consulta_vencimientos_rapida` |
| HU-04 | `pos_ventas` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | [`TC-004`](../11-quality/cases/TC-004.md) | `tests/test_fase2_backend_rbac.py::test_catalogo_ciego_cajero_no_recibe_precios_de_costo` |
| HU-05 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | [`TC-005`](../11-quality/cases/TC-005.md) | `tests/test_concurrencia_real.py::test_concurrencia_dos_ventas_compitiendo_stock_uno` |
| HU-06 | `pos_ventas` | [`entities-and-rules.md`](../02-domain/entities-and-rules.md) | [`TC-006`](../11-quality/cases/TC-006.md) | `tests/test_fase1_rbac_modelos.py::test_trazabilidad_historica_snapshot_permanente` |
| HU-07 | `soporte_crm` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | [`TC-007`](../11-quality/cases/TC-007.md) | `tests/test_soporte_crm.py::test_usuario_puede_crear_ticket` |
| HU-08 | `soporte_crm` | [`rest-conventions.md`](../07-api/rest-conventions.md) | [`TC-008`](../11-quality/cases/TC-008.md) | `tests/test_soporte_crm.py::test_flujo_completo_ticket_respuesta` |
| HU-09 | `agente_ia` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | [`TC-009`](../11-quality/cases/TC-009.md) | `tests/test_agente_rbac_reabastecer.py::test_admin_reabastece_con_nuevo_costo_y_alerta_margen` |
| HU-10 | `agente_ia` | [`overview.md`](../01-context/overview.md) | [`TC-010`](../11-quality/cases/TC-010.md) | `tests/test_agente_produccion.py::test_t05_doble_confirmacion_idempotente` |
| HU-11 | `reportes_analytics`| [`overview.md`](../01-context/overview.md) | [`TC-011`](../11-quality/cases/TC-011.md) | `tests/test_fase2_backend_rbac.py::test_actividad_del_dia_timezone_colombia` |
| HU-12 | `reportes_analytics`| [`scope.md`](../01-context/scope.md) | [`TC-012`](../11-quality/cases/TC-012.md) | `tests/test_fase2_backend_rbac.py::test_blindaje_rbac_cajero_bloqueado_de_admin_endpoints` |

*Nota.* Todos los nodos de prueba fueron verificados mediante `pytest --collect-only`. Fuente: Elaboración propia (2026).

## Non-functional requirements (`NFR-01` .. `NFR-10`)

**Tabla 2**  
*Trazabilidad de Requerimientos No Funcionales y Compuertas de Verificación*

| NFR-NN | Module | Design document | Verification gate |
|---|---|---|---|
| NFR-01 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | `tests/stress/locustfile.py` load run |
| NFR-02 | `auth_tenancy` | [`ADR-002`](../05-architecture/decisions/records/ADR-002-aislamiento-multitenant.md) | `tests/test_fase2_backend_rbac.py::test_aislamiento_multi_tenant_anti_idor` |
| NFR-03 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | `tests/test_concurrencia_real.py::test_concurrencia_dos_ventas_compitiendo_stock_uno` |
| NFR-04 | whole artifact | [`rest-conventions.md`](../07-api/rest-conventions.md) | `tests/test_owasp_security.py::test_deep_health_check_and_correlation_id` |
| NFR-05 | `auth_tenancy` | [`rest-conventions.md`](../07-api/rest-conventions.md) | `tests/test_auth.py::test_me_sin_token` |
| NFR-06 | `agente_ia` | [`overview.md`](../01-context/overview.md) | `tests/test_llm_provider_smoke.py::test_telemetry_exact_semantics` |
| NFR-07 | whole artifact | [`modular-monolith.md`](../05-architecture/modular-monolith.md) | `.github/workflows/ci.yml` automated test gate |
| NFR-08 | whole artifact | [`overview.md`](../01-context/overview.md) | `run_e2e_simulation.py` and `.env.example` local setup |
| NFR-09 | whole artifact | [`rest-conventions.md`](../07-api/rest-conventions.md) | `tests/test_owasp_security.py::test_auditoria_de_seguridad_logging` |
| NFR-10 | whole artifact | [`scope.md`](../01-context/scope.md) | `frontend/tests/voice/lateResponse.test.mjs` & mobile viewport audit |

*Nota.* Compuertas de calidad ejecutadas en el pipeline de integración continua. Fuente: Elaboración propia (2026).

## Gaps

- **GAP-01 (Closed):** All 12 user stories (`HU-01..HU-12`) and 10 non-functional requirements (`NFR-01..NFR-10`) are now mapped to formal `TC-001..TC-012` specifications and verified `pytest` nodes (`0` orphan requirements).
- **GAP-02 (Monitored):** PostgreSQL kernel-level lock tests (`tests/integration/postgres/test_concurrencia_postgres.py`) require a live PostgreSQL instance (`TEST_POSTGRES_URL`) and are skipped when running against in-memory SQLite.

---

**Related:** [`./user-stories.md`](./user-stories.md) · [`./non-functional.md`](./non-functional.md)
