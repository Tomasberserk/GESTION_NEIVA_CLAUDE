# 04 — Traceability Matrix

## Stories

| HU-NN | Module | Design document | Test case |
|---|---|---|---|
| HU-01 | `auth_tenancy` | [`models.md`](../06-data/models.md) | `tests/test_auth.py::test_login_exitoso` |
| HU-02 | `inventario` | [`models.md`](../06-data/models.md) | `tests/test_concurrencia_real.py::test_producto_barcode` |
| HU-03 | `inventario` | [`entities-and-rules.md`](../02-domain/entities-and-rules.md) | `tests/test_business_understanding_benchmark.py` |
| HU-04 | `pos_ventas` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | `tests/test_fase2_backend_rbac.py::test_calculo_subtotal` |
| HU-05 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | `tests/test_concurrencia_real.py::test_carrera_ultima_unidad` |
| HU-06 | `pos_ventas` | [`entities-and-rules.md`](../02-domain/entities-and-rules.md) | `tests/test_fase1_rbac_modelos.py::test_snapshot_inmutable` |
| HU-07 | `soporte_crm` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | `tests/test_soporte_crm.py::test_crear_ticket_soporte` |
| HU-08 | `soporte_crm` | [`rest-conventions.md`](../07-api/rest-conventions.md) | `tests/test_soporte_crm.py::test_superadmin_responder` |
| HU-09 | `agente_ia` | [`module-boundaries.md`](../02-domain/module-boundaries.md) | `tests/test_agente_rbac_reabastecer.py::test_reabastecer` |
| HU-10 | `agente_ia` | [`overview.md`](../01-context/overview.md) | `tests/test_agente_produccion.py::test_consulta_fsm` |
| HU-11 | `reportes_analytics`| [`overview.md`](../01-context/overview.md) | `tests/test_fase2_backend_rbac.py::test_resumen_caja` |
| HU-12 | `reportes_analytics`| [`scope.md`](../01-context/scope.md) | `tests/test_fase2_backend_rbac.py::test_export_excel` |

## Non-functional requirements

| NFR-NN | Module | Design document | Verification gate |
|---|---|---|---|
| NFR-01 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | `tests/stress/locustfile.py` load run |
| NFR-02 | `auth_tenancy` | [`ADR-002`](../05-architecture/decisions/records/ADR-002-aislamiento-multitenant.md) | `tests/test_owasp_security.py` isolation test |
| NFR-03 | `pos_ventas` | [`ADR-003`](../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md) | `tests/test_concurrencia_real.py` multithread check |
| NFR-04 | whole artifact | [`rest-conventions.md`](../07-api/rest-conventions.md) | Uptime health check monitor polling `/health` |
| NFR-05 | `auth_tenancy` | [`rest-conventions.md`](../07-api/rest-conventions.md) | `tests/test_auth.py` unauthenticated rejection suite |
| NFR-06 | `agente_ia` | [`overview.md`](../01-context/overview.md) | `tests/test_llm_provider_smoke.py` latency timer |
| NFR-07 | whole artifact | [`modular-monolith.md`](../05-architecture/modular-monolith.md) | CI coverage gate (`diff-cover` / `pytest-cov`) |
| NFR-08 | whole artifact | [`overview.md`](../01-context/overview.md) | Onboarding test using `Makefile` / `dev.ps1` |
| NFR-09 | whole artifact | [`rest-conventions.md`](../07-api/rest-conventions.md) | Log inspection asserting JSON format and correlationId |
| NFR-10 | whole artifact | [`scope.md`](../01-context/scope.md) | Mobile responsiveness and touch target inspection |

---

**Related:** [`./user-stories.md`](./user-stories.md) · [`./non-functional.md`](./non-functional.md)
