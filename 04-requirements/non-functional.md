# 04 — Non-Functional Requirements

## What makes a requirement here valid

| Not this | This |
|---|---|
| The system must be fast | POS checkout p95 under 300 ms at 50 concurrent transactions |
| The system must be secure | Zero cross-tenant data leakage across all read/write endpoints |

## Requirements

| NFR-NN | Category | Threshold | How it is measured |
|---|---|---|---|
| NFR-01 | Performance | p95 response time under 300 ms at 50 concurrent transactions on POS checkout | Locust load test (`tests/stress/locustfile.py`) |
| NFR-02 | Security | Zero cross-tenant data leakage across all read/write endpoints | Automated test asserting 404/403 on mismatched `empresa_id` (`test_owasp_security.py`) |
| NFR-03 | Concurrency | Zero overselling or negative stock under race conditions on the last available item | Threaded concurrency test with 10 simultaneous buyers (`test_concurrencia_real.py`) |
| NFR-04 | Availability | 99.5% uptime per month during commercial retail hours (6:00 AM – 10:00 PM COT) | Cloud uptime monitor polling `GET /health` every 5 minutes |
| NFR-05 | Security | 100% of write endpoints reject unauthenticated or expired JWT requests | Automated authentication suite (`tests/test_auth.py`) |
| NFR-06 | Performance | Voice audio transcription and FSM intent turn completes in under 3.0s | Timed roundtrip benchmark (`tests/test_agente_produccion.py`) |
| NFR-07 | Maintainability | Unit test coverage >= 80% on changed files, >= 90% on `pos_ventas` | `pytest --cov=app --cov-fail-under=80` run in CI |
| NFR-08 | Maintainability | A new developer boots the system locally in under 1 hour from scratch | Timed verification using `Makefile` (`make dev`) or `dev.ps1` |
| NFR-09 | Observability | 100% of unhandled errors logged in structured JSON with `correlationId` | Automated exception handler test checking JSON log format |
| NFR-10 | Usabilidad | UI usable on mobile screens >= 360px without horizontal scroll; touch targets >= 48x48dp | Lighthouse accessibility audit scoring >= 90 and viewport check |

## Identifier format

`NFR-NN` — sequential, two digits, starting at `01`. Never reused.

---

**Related:** [`./user-stories.md`](./user-stories.md) · [`./traceability-matrix.md`](./traceability-matrix.md)
