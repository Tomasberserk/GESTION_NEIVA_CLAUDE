from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import (
    auth,
    productos,
    proveedores,
    compras,
    cuentas_por_pagar,
    dashboard,
)

# 1. Crear las tablas de la base de datos de manera automática en inicio (desarrollo/test)
Base.metadata.create_all(bind=engine)

# 2. Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de ERP Distribuidora (Tier Medium)",
    description=(
        "Especificación de endpoints REST de Gestión Comercial, Inventario, "
        "Proveedores, Abastecimiento y Cuentas por Pagar para Distribuidora Mayorista."
    ),
    version="1.0.0",
)

# 3. Configuración de CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Registrar routers de API
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(proveedores.router)
app.include_router(compras.router)
app.include_router(cuentas_por_pagar.router)
app.include_router(dashboard.router)


@app.get("/", tags=["General"])
def read_root():
    return {
        "status": "online",
        "service": "ERP Distribuidora",
        "tier": "Medium",
        "docs_url": "/docs",
    }
