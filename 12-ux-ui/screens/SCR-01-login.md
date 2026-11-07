# SCR-01 — Inicio de Sesión y Selección de Tenant

## Identification

| Field | Value |
|---|---|
| Screen | Inicio de Sesión (`/login`) |
| Serves | `HU-01` (Autenticación JWT y selección de Tenant) |
| Route | `frontend/src/pages/Login.jsx` |

## States

| State | What the user sees |
|---|---|
| Empty | Centered card with email and password inputs, submit button, and link to register |
| Loading | Disabled button with animated spinner: "Ingresando a tu tienda..." |
| Error | Red alert banner: "Correo o contraseña incorrectos. Verifica tus credenciales." |
| Populated | Inputs filled; button enabled with emerald highlight |

## Wireframe outline

```
+---------------------------------------------+
|              TIENDAPP NEIVA                 |
|   +-------------------------------------+   |
|   | Correo electrónico                  |   |
|   | [ tendero@mitienda.com            ] |   |
|   |                                     |   |
|   | Contraseña                          |   |
|   | [ ****************                ] |   |
|   |                                     |   |
|   | [       INICIAR SESIÓN (48px)     ] |   |
|   |                                     |   |
|   | ¿No tienes cuenta? Regístrate aquí  |   |
|   +-------------------------------------+   |
+---------------------------------------------+
```

## Validation rules

| Field | Rule | Message shown |
|---|---|---|
| `email` | Must be a valid email format | "Ingresa un correo electrónico válido" |
| `password` | Minimum 6 characters | "La contraseña debe tener al menos 6 caracteres" |

---

**Related:** [`../design-system.md`](../design-system.md) · [`../../04-requirements/user-stories.md`](../../04-requirements/user-stories.md)
