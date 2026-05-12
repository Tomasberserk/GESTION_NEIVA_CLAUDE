from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class StockBajoItem(BaseModel):
    id: str
    nombre: str
    cantidad: float


class TopProductoItem(BaseModel):
    nombre: str
    total_vendido: float


class AlertaVencimientoItem(BaseModel):
    id: str
    nombre: str
    fecha_vencimiento: date
    dias_restantes: int


class DashboardRespuesta(BaseModel):
    ventas_hoy: int
    ingresos_hoy: float
    total_productos: int
    stock_bajo: List[StockBajoItem]
    top_productos: List[TopProductoItem]
    alertas_vencimiento: List[AlertaVencimientoItem]
    dias_trial_restantes: Optional[int]
    plan: str
