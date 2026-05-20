from typing import List
from pydantic import BaseModel


class StockBajoItem(BaseModel):
    id: str
    nombre: str
    categoria: str
    cantidad_actual: int
    stock_minimo: int


class DashboardRespuesta(BaseModel):
    ventas_hoy: int
    ingresos_hoy: float
    total_productos_activos: int
    stock_bajo: List[StockBajoItem]
