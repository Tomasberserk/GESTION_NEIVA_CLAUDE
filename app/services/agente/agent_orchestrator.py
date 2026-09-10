"""Orquestador Central del Agente de IA para Gestión Neiva.

Aplica las 5 leyes fundamentales:
1. LLM no ejecuta.
2. LLM no calcula.
3. LLM no decide tenant.
4. No duplica lógica de negocio (reutiliza venta_service y producto_service).
5. Transacción atómica compartida para idempotencia con agent_commands en PostgreSQL.
"""

import json
import logging
import math
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.schemas.producto import ProductoCrear
from app.schemas.venta import DetalleVentaCrear, VentaCrear
from app.services import producto_service, venta_service
from app.services.agente import consultas_service, response_formatter
from app.services.agente.catalog_matcher import (
    MATCH_AUTO_RESOLVED,
    MATCH_NEEDS_CLARIFICATION,
    MATCH_NOT_FOUND,
    match_producto,
)
from app.services.agente.fsm import AgentState, validate_transition
from app.services.agente.intent_provider import AgentInterpretation, get_intent_provider
from app.services.agente.session_store import SessionStore, get_session_store

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(
        self,
        session_store: SessionStore | None = None,
        intent_provider: Any = None,
    ):
        self._session_store = session_store
        self._intent_provider = intent_provider

    @property
    def session_store(self) -> SessionStore:
        return self._session_store or get_session_store()

    @property
    def intent_provider(self) -> Any:
        return self._intent_provider or get_intent_provider()

    async def procesar_mensaje(
        self,
        mensaje: str,
        current_user: models.Usuario,
        db: Session,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Punto de entrada principal para procesar mensajes del usuario."""
        empresa_id = current_user.empresa_id
        conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

        # 1. Recuperar contexto de sesión previa
        session = await self.session_store.get(conv_id)
        if session:
            # Regla de seguridad P0.3: empresa_id y usuario_id deben coincidir con el JWT
            if session.get("empresa_id") != str(empresa_id) or (
                session.get("usuario_id") and session.get("usuario_id") != str(current_user.id)
            ):
                logger.warning(
                    "Violación de aislamiento multi-tenant/usuario en sesión %s por usuario %s",
                    conv_id,
                    current_user.id,
                )
                await self.session_store.delete(conv_id)
                session = None

        estado_actual = session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value

        # P0.1: Si estamos en READY_TO_CONFIRM, la decisión es 100% DETERMINÍSTICA.
        # El LLM NO tiene autoridad para autorizar o rechazar una mutación financiera.
        # La confirmación exige expresiones completas e inequívocas (no simple presencia de palabra).
        if estado_actual == AgentState.READY_TO_CONFIRM.value and session and "pending_command" in session:
            msg_norm = " ".join(re.sub(r"[^\w\s]", " ", mensaje.lower()).split())

            # 1. Cancelación determinística (prioridad de seguridad)
            CANCELACIONES_INEQUIVOCAS = {
                "no", "cancelar", "cancela", "cancelado", "abortar", "aborta",
                "olvidalo", "olvídalo", "ya no", "no gracias", "detener", "para",
                "descartar", "descartalo", "descártalo", "rechazar", "rechazo",
            }
            if msg_norm in CANCELACIONES_INEQUIVOCAS or re.match(r"^(no|cancelar|cancela|abortar|aborta|ya no)\b", msg_norm):
                validate_transition(estado_actual, AgentState.REJECTED)
                await self.session_store.delete(conv_id)
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.REJECTED.value,
                    "respuesta": response_formatter.formatear_cancelacion(),
                }

            # 2. Confirmación determinística inequívoca completa
            # Si el usuario añade condiciones (ej: "sí, pero quiero cambiar la cantidad"), NO se ejecuta.
            CONFIRMACIONES_INEQUIVOCAS = {
                "si", "sí", "confirmar", "confirmo", "dale", "de una", "ok", "listo",
                "correcto", "exacto", "hagale", "hágale", "proceder", "adelante",
                "si dale", "sí dale", "dale confirmar", "si confirmar", "sí confirmar",
                "ok confirmar", "confirmar venta", "confirmar orden", "confirmado",
            }
            if msg_norm in CONFIRMACIONES_INEQUIVOCAS:
                return await self._ejecutar_pending_command(session, conv_id, current_user, db)

            # 3. Cualquier otra cosa: NO llamar al LLM ni ejecutar. Exigir decisión binaria clara.
            pending = session["pending_command"]
            action = pending.get("action", "la operación")
            return {
                "conversation_id": conv_id,
                "estado": AgentState.READY_TO_CONFIRM.value,
                "respuesta": f"Tienes pendiente confirmar {action}. Por favor responde únicamente 'sí' para confirmar o 'cancelar' para descartarla.",
                "preview": pending.get("preview"),
                "command_id": pending.get("command_id"),
            }

        # 2. Interpretar mensaje del usuario (solo si no estamos en READY_TO_CONFIRM)
        interp = self.intent_provider.parse(mensaje, context=session)

        # 3. Flujo según la intención detectada
        # 3.1. Cancelación explícita
        if interp.intent == "cancelar":
            if session:
                validate_transition(estado_actual, AgentState.REJECTED)
                await self.session_store.delete(conv_id)
            return {
                "conversation_id": conv_id,
                "estado": AgentState.REJECTED.value,
                "respuesta": response_formatter.formatear_cancelacion(),
            }

        # 3.2. Operación destructiva bloqueada
        if interp.intent == "operacion_destructiva":
            return {
                "conversation_id": conv_id,
                "estado": AgentState.OUT_OF_SCOPE.value,
                "respuesta": response_formatter.formatear_operacion_destructiva_bloqueada(),
            }

        # 3.3. Fuera de alcance
        if interp.intent == "fuera_de_alcance":
            return {
                "conversation_id": conv_id,
                "estado": AgentState.OUT_OF_SCOPE.value,
                "respuesta": response_formatter.formatear_fuera_de_alcance(),
            }

        # 3.4. Confirmación cuando no hay sesión activa (Idempotencia persistente P0)
        if interp.intent == "confirmar":
            cmd_previo = (
                db.query(models.AgentCommand)
                .filter(
                    models.AgentCommand.empresa_id == empresa_id,
                    models.AgentCommand.conversation_id == conv_id,
                    models.AgentCommand.status == "EJECUTADO",
                )
                .order_by(models.AgentCommand.executed_at.desc())
                .first()
            )
            if cmd_previo and cmd_previo.result:
                res_cached = json.loads(cmd_previo.result)
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.EXECUTED.value,
                    "respuesta": res_cached.get("respuesta", "Operación ya procesada exitosamente."),
                    "idempotente": True,
                }

            return {
                "conversation_id": conv_id,
                "estado": AgentState.IDLE.value,
                "respuesta": "No tienes ninguna operación pendiente por confirmar. ¿En qué te puedo ayudar?",
            }

        # 3.5. Consultas financieras directas
        if interp.intent == "consulta_financiera":
            return self._procesar_consulta_financiera(interp, conv_id, empresa_id, db)

        # 3.6. Consultar stock
        if interp.intent == "consultar_stock":
            return self._procesar_consultar_stock(interp, conv_id, empresa_id, db)

        # 3.7. Operaciones de escritura (registrar_venta, reabastecer, crear_producto)
        if interp.intent in ["registrar_venta", "reabastecer", "crear_producto"] or estado_actual == AgentState.NEEDS_CLARIFICATION.value:
            return await self._procesar_escritura(interp, session, conv_id, current_user, db)

        # 3.8. Desconocido / No entendido
        return {
            "conversation_id": conv_id,
            "estado": AgentState.IDLE.value,
            "respuesta": "No logré entender bien tu solicitud. Puedes decirme, por ejemplo: 'Vendí 2 gaseosas', 'Reabastecer arroz' o '¿Cuánto he vendido hoy?'.",
        }

    # -----------------------------------------------------------------------
    # Manejadores Internos
    # -----------------------------------------------------------------------

    def _procesar_consulta_financiera(
        self, interp: AgentInterpretation, conv_id: str, empresa_id: UUID, db: Session
    ) -> dict[str, Any]:
        metric = interp.slots.get("metric", "ventas_hoy")

        if metric == "ventas_hoy":
            datos = consultas_service.consultar_ventas_periodo(empresa_id, db, "hoy")
            resp = response_formatter.formatear_consulta_ventas(datos)
        elif metric == "ventas_semana":
            datos = consultas_service.consultar_ventas_periodo(empresa_id, db, "semana")
            resp = response_formatter.formatear_consulta_ventas(datos)
        elif metric == "ventas_mes":
            datos = consultas_service.consultar_ventas_periodo(empresa_id, db, "mes")
            resp = response_formatter.formatear_consulta_ventas(datos)
        elif metric == "recaudo_actual":
            datos = consultas_service.consultar_recaudo_actual(empresa_id, db)
            resp = response_formatter.formatear_consulta_recaudo(datos)
        elif metric == "cantidad_ventas":
            datos = consultas_service.consultar_ventas_periodo(empresa_id, db, "hoy")
            resp = response_formatter.formatear_consulta_ventas(datos)
        elif metric == "total_inventario":
            datos = consultas_service.consultar_total_inventario(empresa_id, db)
            resp = response_formatter.formatear_consulta_inventario(datos)
        elif metric == "resumen_actual":
            datos = consultas_service.consultar_resumen_actual(empresa_id, db)
            resp = response_formatter.formatear_resumen_actual(datos)
        elif metric == "recuperacion_inversion":
            datos = consultas_service.consultar_recuperacion_inversion(empresa_id, db)
            resp = response_formatter.formatear_recuperacion_inversion(datos)
        else:
            datos = consultas_service.consultar_ventas_periodo(empresa_id, db, "hoy")
            resp = response_formatter.formatear_consulta_ventas(datos)

        return {
            "conversation_id": conv_id,
            "estado": AgentState.IDLE.value,
            "respuesta": resp,
            "datos": datos,
        }

    def _procesar_consultar_stock(
        self, interp: AgentInterpretation, conv_id: str, empresa_id: UUID, db: Session
    ) -> dict[str, Any]:
        query = interp.slots.get("product_query")
        if not query:
            return {
                "conversation_id": conv_id,
                "estado": AgentState.IDLE.value,
                "respuesta": "¿De qué producto deseas consultar el stock?",
            }

        productos = db.query(models.Producto).filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        ).all()

        match_status, match_data = match_producto(query, productos)

        if match_status == MATCH_AUTO_RESOLVED:
            prod = match_data
            datos = consultas_service.consultar_stock_producto(prod.id, empresa_id, db)
            return {
                "conversation_id": conv_id,
                "estado": AgentState.IDLE.value,
                "respuesta": response_formatter.formatear_consulta_stock(datos),
            }
        elif match_status == MATCH_NEEDS_CLARIFICATION:
            clar_id = f"clar_{uuid.uuid4().hex[:6]}"
            options = [
                {"id": str(p.id), "label": f"{p.nombre} ({response_formatter.fmt_moneda(p.precio_venta)})"}
                for p in match_data
            ]
            labels = ", ".join([f"'{p.nombre}'" for p in match_data])
            return {
                "conversation_id": conv_id,
                "estado": AgentState.NEEDS_CLARIFICATION.value,
                "respuesta": f"Encontré varias opciones: {labels}. ¿A cuál te refieres?",
                "clarification": {"clarification_id": clar_id, "options": options},
            }
        else:
            return {
                "conversation_id": conv_id,
                "estado": AgentState.IDLE.value,
                "respuesta": f"No encontré el producto '{query}' en el inventario de tu tienda.",
            }

    async def _procesar_escritura(
        self,
        interp: AgentInterpretation,
        session: dict[str, Any] | None,
        conv_id: str,
        current_user: models.Usuario,
        db: Session,
    ) -> dict[str, Any]:
        empresa_id = current_user.empresa_id
        action = interp.intent if interp.intent in ["registrar_venta", "reabastecer", "crear_producto"] else (session.get("action") if session else "registrar_venta")

        slots = session.get("slots", {}) if session else {}
        # Actualizar slots con lo nuevo
        for k, v in interp.slots.items():
            if v is not None:
                slots[k] = v

        # 1. Caso: Crear Producto
        if action == "crear_producto":
            nombre = slots.get("product_query") or slots.get("nombre")
            precio_v = slots.get("precio_venta")
            if not nombre:
                validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.NEEDS_CLARIFICATION)
                await self.session_store.save(conv_id, {
                    "conversation_id": conv_id,
                    "empresa_id": str(empresa_id),
                    "usuario_id": str(current_user.id),
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "action": "crear_producto",
                    "slots": slots,
                    "missing_slots": ["nombre"],
                })
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "respuesta": "¿Cómo se llama el nuevo producto que deseas registrar?",
                }
            if not precio_v:
                validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.NEEDS_CLARIFICATION)
                await self.session_store.save(conv_id, {
                    "conversation_id": conv_id,
                    "empresa_id": str(empresa_id),
                    "usuario_id": str(current_user.id),
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "action": "crear_producto",
                    "slots": slots,
                    "missing_slots": ["precio_venta"],
                })
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "respuesta": f"¿Cuál será el precio de venta de {nombre}?",
                }

            # P1.3: No inventar precio_costo con márgenes ficticios del 70%
            precio_costo = slots.get("precio_costo")
            if precio_costo is None:
                precio_costo = 0.0

            qty = slots.get("quantity", 0)
            command_id = f"cmd_{uuid.uuid4().hex}"

            preview = {
                "nombre": nombre,
                "precio_venta": float(precio_v),
                "precio_costo": float(precio_costo),
                "cantidad_actual": float(qty),
                "unidad_medida": slots.get("unit", "unidad"),
            }
            pending_command = {
                "command_id": command_id,
                "action": "crear_producto",
                "payload": preview,
                "preview": preview,
            }

            validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.READY_TO_CONFIRM)
            await self.session_store.save(conv_id, {
                "conversation_id": conv_id,
                "empresa_id": str(empresa_id),
                "usuario_id": str(current_user.id),
                "estado": AgentState.READY_TO_CONFIRM.value,
                "action": "crear_producto",
                "pending_command": pending_command,
            })
            return {
                "conversation_id": conv_id,
                "estado": AgentState.READY_TO_CONFIRM.value,
                "respuesta": response_formatter.formatear_confirmacion_crear_producto(preview),
                "command_id": command_id,
            }

        # 2. Caso: Registrar Venta o Reabastecer
        query = slots.get("product_query")
        producto_id = slots.get("producto_id")

        # Resolver producto si no está resuelto
        producto_seleccionado = None
        if producto_id:
            producto_seleccionado = db.query(models.Producto).filter(
                models.Producto.id == UUID(producto_id),
                models.Producto.empresa_id == empresa_id,
                models.Producto.is_active.is_(True),
            ).first()

        if not producto_seleccionado:
            if not query:
                validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.NEEDS_CLARIFICATION)
                await self.session_store.save(conv_id, {
                    "conversation_id": conv_id,
                    "empresa_id": str(empresa_id),
                    "usuario_id": str(current_user.id),
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "action": action,
                    "slots": slots,
                    "missing_slots": ["product_query"],
                })
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "respuesta": "¿Qué producto deseas registrar?",
                }

            productos = db.query(models.Producto).filter(
                models.Producto.empresa_id == empresa_id,
                models.Producto.is_active.is_(True),
            ).all()

            match_status, match_data = match_producto(query, productos)

            if match_status == MATCH_NOT_FOUND:
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.IDLE.value,
                    "respuesta": f"No encontré el producto '{query}' en tu catálogo.",
                }
            elif match_status == MATCH_NEEDS_CLARIFICATION:
                clar_id = f"clar_{uuid.uuid4().hex[:6]}"
                options = [
                    {"id": str(p.id), "label": f"{p.nombre} ({response_formatter.fmt_moneda(p.precio_venta)})"}
                    for p in match_data
                ]
                # Guardar sesión esperando aclaración
                validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.NEEDS_CLARIFICATION)
                await self.session_store.save(conv_id, {
                    "conversation_id": conv_id,
                    "empresa_id": str(empresa_id),
                    "usuario_id": str(current_user.id),
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "action": action,
                    "slots": slots,
                    "missing_slots": ["clarification"],
                    "clarification_options": {opt["id"]: opt["label"] for opt in options},
                })
                labels = ", ".join([f"'{p.nombre}'" for p in match_data])
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.NEEDS_CLARIFICATION.value,
                    "respuesta": f"Encontré varias opciones para '{query}': {labels}. ¿Cuál deseas?",
                    "clarification": {"clarification_id": clar_id, "options": options},
                }
            else:
                producto_seleccionado = match_data
                slots["producto_id"] = str(producto_seleccionado.id)

        # Validar cantidad con límites de producción (0.001 <= cantidad <= 10000.0)
        cantidad_valida = False
        cantidad = 0.0
        try:
            val_raw = slots.get("quantity")
            if val_raw is not None:
                val = float(val_raw)
                if not (math.isnan(val) or math.isinf(val)) and 0.001 <= val <= 10000.0:
                    cantidad = val
                    cantidad_valida = True
        except (ValueError, TypeError):
            cantidad_valida = False

        if not cantidad_valida:
            validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.NEEDS_CLARIFICATION)
            await self.session_store.save(conv_id, {
                "conversation_id": conv_id,
                "empresa_id": str(empresa_id),
                "usuario_id": str(current_user.id),
                "estado": AgentState.NEEDS_CLARIFICATION.value,
                "action": action,
                "slots": slots,
                "missing_slots": ["quantity"],
            })
            return {
                "conversation_id": conv_id,
                "estado": AgentState.NEEDS_CLARIFICATION.value,
                "respuesta": f"Por favor indica una cantidad válida (mayor a 0 y hasta 10,000 unidades) para {producto_seleccionado.nombre}.",
            }

        # Pre-validación de stock para venta (informativa)
        if action == "registrar_venta":
            if producto_seleccionado.cantidad_actual < Decimal(str(cantidad)):
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.IDLE.value,
                    "respuesta": response_formatter.formatear_stock_insuficiente(
                        producto_seleccionado.nombre,
                        float(producto_seleccionado.cantidad_actual),
                        float(cantidad),
                    ),
                }

        # Construir snapshot para READY_TO_CONFIRM
        command_id = f"cmd_{uuid.uuid4().hex}"

        if action == "registrar_venta":
            precio_unitario = float(producto_seleccionado.precio_venta)
            subtotal = precio_unitario * float(cantidad)
            preview = {
                "items": [
                    {
                        "producto_id": str(producto_seleccionado.id),
                        "nombre": producto_seleccionado.nombre,
                        "cantidad": float(cantidad),
                        "precio_unitario": precio_unitario,
                        "subtotal": subtotal,
                    }
                ],
                "total": subtotal,
            }
            payload = {
                "items": [
                    {
                        "producto_id": str(producto_seleccionado.id),
                        "cantidad": float(cantidad),
                        "precio_unitario_esperado": precio_unitario,
                    }
                ]
            }
            resp_texto = response_formatter.formatear_confirmacion_venta(preview)
        else:  # reabastecer
            preview = {
                "producto_id": str(producto_seleccionado.id),
                "producto": producto_seleccionado.nombre,
                "cantidad": float(cantidad),
                "unidad": producto_seleccionado.unidad_medida.value if producto_seleccionado.unidad_medida else "unidad",
            }
            payload = {
                "producto_id": str(producto_seleccionado.id),
                "cantidad": float(cantidad),
            }
            resp_texto = response_formatter.formatear_confirmacion_reabastecer(preview)

        pending_command = {
            "command_id": command_id,
            "action": action,
            "payload": payload,
            "preview": preview,
        }

        validate_transition(session.get("estado", AgentState.IDLE.value) if session else AgentState.IDLE.value, AgentState.READY_TO_CONFIRM)
        await self.session_store.save(conv_id, {
            "conversation_id": conv_id,
            "empresa_id": str(empresa_id),
            "usuario_id": str(current_user.id),
            "estado": AgentState.READY_TO_CONFIRM.value,
            "action": action,
            "pending_command": pending_command,
        })

        return {
            "conversation_id": conv_id,
            "estado": AgentState.READY_TO_CONFIRM.value,
            "respuesta": resp_texto,
            "command_id": command_id,
            "preview": preview,
        }

    # -----------------------------------------------------------------------
    # Ejecución Atómica e Idempotente con agent_commands en PostgreSQL
    # -----------------------------------------------------------------------

    async def _ejecutar_pending_command(
        self,
        session: dict[str, Any],
        conv_id: str,
        current_user: models.Usuario,
        db: Session,
    ) -> dict[str, Any]:
        empresa_id = current_user.empresa_id
        pending = session["pending_command"]
        command_id = pending["command_id"]
        action = pending["action"]
        payload = pending["payload"]
        preview = pending.get("preview", {})

        # 1. Comprobar si el command_id ya existe (Idempotencia en PostgreSQL)
        cmd_existente = (
            db.query(models.AgentCommand)
            .filter(
                models.AgentCommand.empresa_id == empresa_id,
                models.AgentCommand.command_id == command_id,
            )
            .first()
        )

        if cmd_existente and cmd_existente.status == "EJECUTADO":
            logger.info("Comando %s ya ejecutado previamente. Devolviendo resultado en caché.", command_id)
            res_cached = json.loads(cmd_existente.result) if cmd_existente.result else {}
            await self.session_store.delete(conv_id)
            return {
                "conversation_id": conv_id,
                "estado": AgentState.EXECUTED.value,
                "respuesta": res_cached.get("respuesta", "Operación completada."),
                "idempotente": True,
            }

        # 2. Transacción de negocio compartida (Una sola sesión DB atómica)
        try:
            # Crear o actualizar registro de comando en estado PENDIENTE
            if not cmd_existente:
                cmd_record = models.AgentCommand(
                    empresa_id=empresa_id,
                    conversation_id=conv_id,
                    command_id=command_id,
                    action=action,
                    payload=json.dumps(payload),
                    status="PENDIENTE",
                )
                db.add(cmd_record)
                db.flush()
            else:
                cmd_record = cmd_existente

            # Ejecutar según la acción
            if action == "registrar_venta":
                items = payload.get("items", [])
                detalles_schema = []

                for it in items:
                    p_id = UUID(it["producto_id"])
                    cant = Decimal(str(it["cantidad"]))
                    precio_esperado = Decimal(str(it["precio_unitario_esperado"]))

                    # Lock pesimista del producto para revalidar precio y stock
                    prod_locked = (
                        db.query(models.Producto)
                        .filter(
                            models.Producto.id == p_id,
                            models.Producto.empresa_id == empresa_id,
                            models.Producto.is_active.is_(True),
                        )
                        .with_for_update()
                        .first()
                    )

                    if not prod_locked:
                        db.rollback()
                        return {
                            "conversation_id": conv_id,
                            "estado": AgentState.INVALIDATED.value,
                            "respuesta": "El producto ya no está disponible en la tienda.",
                        }

                    # Revalidar precio esperado (Regla de oro: snapshot invariante)
                    if prod_locked.precio_venta != precio_esperado:
                        cmd_record.status = "INVALIDADO"
                        db.commit()
                        await self.session_store.delete(conv_id)
                        nuevo_tot = float(prod_locked.precio_venta) * float(cant)
                        return {
                            "conversation_id": conv_id,
                            "estado": AgentState.INVALIDATED.value,
                            "respuesta": response_formatter.formatear_precio_cambiado(
                                prod_locked.nombre,
                                float(precio_esperado),
                                float(prod_locked.precio_venta),
                                nuevo_tot,
                            ),
                        }

                    # Revalidar stock real bajo lock
                    if prod_locked.cantidad_actual < cant:
                        cmd_record.status = "INVALIDADO"
                        db.commit()
                        await self.session_store.delete(conv_id)
                        return {
                            "conversation_id": conv_id,
                            "estado": AgentState.INVALIDATED.value,
                            "respuesta": response_formatter.formatear_stock_insuficiente(
                                prod_locked.nombre,
                                float(prod_locked.cantidad_actual),
                                float(cant),
                            ),
                        }

                    detalles_schema.append(DetalleVentaCrear(producto_id=p_id, cantidad=cant))

                # Invocar venta_service existente pasando commit=False
                venta_data = VentaCrear(detalles=detalles_schema)
                resumen_venta = venta_service.registrar_venta(
                    empresa_id=empresa_id,
                    data=venta_data,
                    current_user=current_user,
                    db=db,
                    commit=False,
                )

                resp_texto = response_formatter.formatear_exito_venta({"total": resumen_venta.total})
                resultado_final = {
                    "total": resumen_venta.total,
                    "venta_id": str(resumen_venta.venta_id),
                    "respuesta": resp_texto,
                }

            elif action == "reabastecer":
                p_id = UUID(payload["producto_id"])
                cant = Decimal(str(payload["cantidad"]))
                prod_actualizado = producto_service.reabastecer_producto(
                    producto_id=p_id,
                    empresa_id=empresa_id,
                    cantidad=cant,
                    db=db,
                    commit=False,
                )
                resp_texto = response_formatter.formatear_exito_reabastecer({
                    "producto": prod_actualizado.nombre,
                    "stock_nuevo": float(prod_actualizado.cantidad_actual),
                    "unidad": prod_actualizado.unidad_medida.value if prod_actualizado.unidad_medida else "unidad",
                })
                resultado_final = {
                    "producto_id": str(p_id),
                    "stock_nuevo": float(prod_actualizado.cantidad_actual),
                    "respuesta": resp_texto,
                }

            elif action == "crear_producto":
                prod_data = ProductoCrear(
                    empresa_id=empresa_id,
                    nombre=payload["nombre"],
                    codigo_barras=f"IA-{uuid.uuid4().hex[:8].upper()}",
                    precio_costo=Decimal(str(payload["precio_costo"])),
                    precio_venta=Decimal(str(payload["precio_venta"])),
                    cantidad_actual=Decimal(str(payload["cantidad_actual"])),
                    unidad_medida=payload.get("unidad_medida", "unidad"),
                )
                nuevo_p = producto_service.crear_producto(prod_data, db=db, commit=False)
                resp_texto = response_formatter.formatear_exito_crear_producto({
                    "nombre": nuevo_p.nombre,
                    "precio_venta": float(nuevo_p.precio_venta),
                    "stock_inicial": float(nuevo_p.cantidad_actual),
                })
                resultado_final = {
                    "producto_id": str(nuevo_p.id),
                    "respuesta": resp_texto,
                }

            else:
                db.rollback()
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.FAILED.value,
                    "respuesta": f"Acción '{action}' no reconocida para ejecución.",
                }

            # Marcar el comando como EJECUTADO en la misma transacción
            cmd_record.status = "EJECUTADO"
            cmd_record.result = json.dumps(resultado_final)
            cmd_record.executed_at = datetime.now(timezone.utc)

            # COMMIT ATÓMICO ÚNICO
            db.commit()

            # Limpiar sesión efímera
            await self.session_store.delete(conv_id)

            return {
                "conversation_id": conv_id,
                "estado": AgentState.EXECUTED.value,
                "respuesta": resp_texto,
                "resultado": resultado_final,
            }

        except HTTPException as he:
            db.rollback()
            logger.error("HTTPException al ejecutar comando %s: %s", command_id, he.detail)
            return {
                "conversation_id": conv_id,
                "estado": AgentState.FAILED.value,
                "respuesta": f"Error al procesar: {he.detail}",
            }
        except IntegrityError:
            db.rollback()
            logger.warning("Carrera concurrente detectada en comando %s. Recuperando resultado.", command_id)
            cmd_ganador = (
                db.query(models.AgentCommand)
                .filter(
                    models.AgentCommand.empresa_id == empresa_id,
                    models.AgentCommand.command_id == command_id,
                )
                .first()
            )
            if cmd_ganador and cmd_ganador.status == "EJECUTADO":
                res_cached = json.loads(cmd_ganador.result) if cmd_ganador.result else {}
                await self.session_store.delete(conv_id)
                return {
                    "conversation_id": conv_id,
                    "estado": AgentState.EXECUTED.value,
                    "respuesta": res_cached.get("respuesta", "Operación ya procesada exitosamente."),
                    "idempotente": True,
                }
            return {
                "conversation_id": conv_id,
                "estado": AgentState.FAILED.value,
                "respuesta": "La operación ya está siendo procesada concurrentemente por otra solicitud.",
            }
        except Exception as exc:
            db.rollback()
            logger.error("Error crítico inesperado al ejecutar comando %s: %s", command_id, exc, exc_info=True)
            return {
                "conversation_id": conv_id,
                "estado": AgentState.FAILED.value,
                "respuesta": "Ocurrió un error inesperado al procesar la operación en la base de datos.",
            }
