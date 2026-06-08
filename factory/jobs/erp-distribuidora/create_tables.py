#!/usr/bin/env python3
"""
Script para crear todas las tablas de la BD del ERP Distribuidora.
Ejecuta: python create_tables.py
"""

import sys
import os

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def main():
    print("Creando todas las tablas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise

if __name__ == "__main__":
    main()
