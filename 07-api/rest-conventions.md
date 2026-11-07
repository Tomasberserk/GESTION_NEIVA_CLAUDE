# 07 — REST Conventions

## One unified API

The application exposes one HTTP API under the `/api/v1` prefix. In-process facades
(`api/facade.py`) are strictly internal and never exposed over HTTP.

| Element | Convention | Example |
|---|---|---|
| Base path | `/api/v1` | `/api/v1/productos` |
| Authentication | Bearer token in header | `Authorization: Bearer <jwt>` |
| SuperAdmin auth | Custom secret header | `x-superadmin-key: <key>` |
| Multi-tenancy | Extracted from verified JWT | Injected as dependency, never passed in query |

## Resource naming

- **Plural nouns:** `/api/v1/productos`, `/api/v1/ventas`
- **Nesting shows hierarchy:** `/api/v1/soporte/tickets/{id}/responder`
- **Kebab-case in paths:** `/api/v1/auth/registro-completo`

## Status codes

| Code | When used |
|---|---|
| `200 OK` / `201 Created` | Successful GET/PUT/PATCH or entity creation |
| `204 No Content` | Successful deletion or state change with no response body |
| `400 Bad Request` | Malformed JSON payload or invalid query parameters |
| `401 Unauthorized` | Missing, malformed, or expired JWT token |
| `403 Forbidden` | Valid token lacking permissions, or expired subscription trial per **BR-08** |
| `404 Not Found` | Resource does not exist or belongs to another tenant per **BR-03** |
| `422 Unprocessable` | Well-formed request failing business rules (e.g. insufficient stock per **BR-01**) |
| `500 Server Error` | Unhandled internal exception; logged with `correlationId` per **NFR-09** |

## Standard error format

```json
{
  "error": "INSUFFICIENT_STOCK",
  "message": "El stock disponible no cubre la cantidad solicitada",
  "details": [{ "field": "cantidad", "message": "Solicitado: 5.0, Disponible: 2.0" }]
}
```

## Pagination

List endpoints paginate using `?page=1&limit=20` (maximum `limit=100`).

---

**Related:** [`./README.md`](./README.md) · [`./contracts/openapi/openapi-spec.yaml`](./contracts/openapi/openapi-spec.yaml)
