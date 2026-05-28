from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.soporte import TicketCrear, TicketListOut, TicketOut, TicketResponder

router = APIRouter(prefix="/soporte", tags=["Soporte"])


@router.post("/tickets", status_code=status.HTTP_201_CREATED, response_model=TicketOut)
def crear_ticket(
    data: TicketCrear,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Crea un nuevo ticket de soporte con el mensaje inicial del usuario.
    Registra automáticamente el primer mensaje asociado al ticket.
    """
    ticket = models.SoporteTicket(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        asunto=data.asunto,
        is_active=True,
    )
    db.add(ticket)
    db.flush()

    primer_mensaje = models.SoporteMensaje(
        ticket_id=ticket.id,
        remitente_rol=models.RemitenteRol.USUARIO,
        remitente_email=current_user.email,
        mensaje=data.mensaje,
    )
    db.add(primer_mensaje)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[TicketListOut])
def listar_tickets(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Lista todos los tickets de la empresa del usuario actual.
    Ordena por fecha de actualización descendente.
    Solo devuelve tickets activos (soft delete).
    """
    return (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .order_by(models.SoporteTicket.updated_at.desc())
        .all()
    )


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def obtener_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Obtiene un ticket específico con todos sus mensajes.
    El usuario solo puede ver tickets de su propia empresa.
    """
    ticket = (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.id == ticket_id,
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@router.post("/tickets/{ticket_id}/responder")
def responder_ticket(
    ticket_id: UUID,
    data: TicketResponder,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Añade una respuesta del usuario a un ticket de soporte.
    No permite responder tickets cerrados.
    """
    ticket = (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.id == ticket_id,
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.estado == models.EstadoTicket.CERRADO:
        raise HTTPException(status_code=400, detail="El ticket está cerrado")

    mensaje = models.SoporteMensaje(
        ticket_id=ticket_id,
        remitente_rol=models.RemitenteRol.USUARIO,
        remitente_email=current_user.email,
        mensaje=data.mensaje,
    )
    ticket.estado = models.EstadoTicket.ABIERTO
    db.add(mensaje)
    db.commit()
    return {"mensaje": "Respuesta enviada"}
