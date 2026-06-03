import os
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas.soporte import (
    ActualizarEstado,
    ActualizarPlan,
    ActualizarTrial,
    EmpresaAdminOut,
    TicketListOut,
    TicketResponder,
)

router = APIRouter(prefix="/superadmin", tags=["SuperAdmin"])


def _check_superadmin(x_superadmin_key: str = Header(default=None, alias="x-superadmin-key")):
    """
    Verifica la clave de superadmin en cada request.
    Se ejecuta en cada llamada para que monkeypatch.setenv funcione en tests.
    """
    key = os.getenv("SUPERADMIN_KEY")
    if not key or x_superadmin_key != key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de superadmin inválida",
        )


@router.get("/empresas", response_model=list[EmpresaAdminOut])
def listar_empresas(
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Lista todas las empresas con estadísticas básicas.
    Requiere header x-superadmin-key.
    Optimizado: usa GROUP BY en vez de N+1 queries.
    """
    from sqlalchemy import func

    # Single aggregated query for user counts per empresa
    counts = dict(
        db.query(models.Usuario.empresa_id, func.count(models.Usuario.id))
        .group_by(models.Usuario.empresa_id)
        .all()
    )

    # Single query for all empresas
    empresas = db.query(models.Empresa).order_by(models.Empresa.created_at.desc()).all()

    return [
        EmpresaAdminOut(
            id=e.id,
            nombre_comercial=e.nombre_comercial,
            nit_o_cedula=e.nit_o_cedula,
            plan=e.plan.value if e.plan else "basic",
            is_active=e.is_active,
            trial_expires_at=e.trial_expires_at,
            total_usuarios=counts.get(e.id, 0),
        )
        for e in empresas
    ]


@router.put("/empresas/{empresa_id}/trial")
def actualizar_trial(
    empresa_id: UUID,
    data: ActualizarTrial,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Actualiza la fecha de expiración del trial de una empresa.
    """
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.trial_expires_at = data.trial_expires_at
    db.commit()
    return {"mensaje": "Trial actualizado", "trial_expires_at": empresa.trial_expires_at}


@router.put("/empresas/{empresa_id}/status")
def actualizar_estado(
    empresa_id: UUID,
    data: ActualizarEstado,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Actualiza el estado is_active de una empresa.
    """
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.is_active = data.is_active
    db.commit()
    return {"mensaje": "Estado actualizado", "is_active": empresa.is_active}


@router.put("/empresas/{empresa_id}/plan")
def actualizar_plan(
    empresa_id: UUID,
    data: ActualizarPlan,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Cambia el plan de una empresa (basic / medium / premium).
    Activa/desactiva los módulos ERP en el frontend automáticamente.
    """
    from app.models import PlanEmpresa
    try:
        nuevo_plan = PlanEmpresa(data.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan inválido. Valores permitidos: {[p.value for p in PlanEmpresa]}",
        )
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.plan = nuevo_plan
    db.commit()
    return {"mensaje": "Plan actualizado", "plan": empresa.plan.value}


@router.get("/tickets", response_model=list[TicketListOut])
def listar_todos_tickets(
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Lista todos los tickets de soporte activos (soft delete).
    """
    return (
        db.query(models.SoporteTicket)
        .filter(models.SoporteTicket.is_active.is_(True))
        .order_by(models.SoporteTicket.updated_at.desc())
        .all()
    )


@router.delete("/empresas/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empresa(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    db.delete(empresa)
    db.commit()


@router.post("/tickets/{ticket_id}/responder")
def responder_ticket(
    ticket_id: UUID,
    data: TicketResponder,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Responde un ticket de soporte desde el superadmin.
    Registra el mensaje como SUPERADMIN y marca el ticket como RESPONDIDO.
    """
    ticket = db.query(models.SoporteTicket).filter(
        models.SoporteTicket.id == ticket_id,
        models.SoporteTicket.is_active.is_(True),
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    mensaje = models.SoporteMensaje(
        ticket_id=ticket_id,
        remitente_rol=models.RemitenteRol.SUPERADMIN,
        remitente_email="soporte@gestionneiva.com",
        mensaje=data.mensaje,
    )
    ticket.estado = models.EstadoTicket.RESPONDIDO
    db.add(mensaje)
    db.commit()
    return {"mensaje": "Respuesta enviada"}
