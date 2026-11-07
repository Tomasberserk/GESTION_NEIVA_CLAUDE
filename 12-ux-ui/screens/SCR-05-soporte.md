# SCR-05 — Mesa de Ayuda y Soporte CRM

## Identification

| Field | Value |
|---|---|
| Screen | Soporte y Tickets (`/soporte`) |
| Serves | `HU-07`, `HU-08` |
| Route | `frontend/src/pages/Soporte.jsx` |

## States

| State | What the user sees |
|---|---|
| Empty Inbox | "No tienes tickets de soporte activos." Button: "+ Crear Ticket" |
| Thread Active | Left sidebar shows ticket list (colored by status); center panel shows message thread history |
| Sending Message | Input disabled with spinner: "Enviando respuesta..." |
| SuperAdmin View | Global view showing tickets from all stores with merchant NIT and name badge |

## Wireframe outline

```
+------------------------------------+-----------------------------+
| BANDEJA DE SOPORTE  [+ Nuevo Ticket]| TICKET: #104 - Duda en caja |
|                                    | De: Don Pedro (Tienda Neiva)|
| • Ticket #104 [Abierto]            | --------------------------- |
|   Duda sobre corte de caja         | [Usuario - 10:15 AM]        |
|   10:15 AM                         | Hola, ¿cómo saco el total?  |
|                                    |                             |
| • Ticket #102 [Respondido]         | [Superadmin - 10:20 AM]     |
|   Solicitud de upgrade Plan Pro    | Puedes ir a Dashboard y...  |
|   Ayer                             | --------------------------- |
|                                    | [ Escribe tu respuesta... ] |
|                                    | [ ENVIAR RESPUESTA ]        |
+------------------------------------+-----------------------------+
```

## Validation rules

| Field | Rule | Message shown |
|---|---|---|
| `asunto` | Required; minimum 5 characters | "Escribe un asunto descriptivo para tu ticket" |
| `mensaje` | Required; cannot be blank | "El mensaje no puede estar vacío" |

---

**Related:** [`../design-system.md`](../design-system.md) · [`../../04-requirements/user-stories.md`](../../04-requirements/user-stories.md)
