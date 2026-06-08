#!/usr/bin/env python3
"""
Script para poblar datos de prueba en la BD.
"""

import sys
import os
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Empresa, Usuario

def main():
    db = SessionLocal()
    try:
        # Crear empresa de prueba
        print("1. Creando empresa...")
        empresa = Empresa(
            nombre_comercial="Distribuidora Test",
            nit_o_cedula="900123456-7",
            plan="trial"
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        print(f"   ✅ Empresa ID: {empresa.id}")

        # Crear usuario admin
        print("2. Creando usuario admin...")
        password_hash = bcrypt.hashpw("admin123456".encode(), bcrypt.gensalt()).decode()
        usuario = Usuario(
            empresa_id=empresa.id,
            email="distribuidora@gmail.com",
            hashed_password=password_hash,
            rol="admin",
            is_active=True
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        print(f"   ✅ Usuario: distribuidora@gmail.com")
        print(f"\nCredenciales de login:")
        print(f"  Email: distribuidora@gmail.com")
        print(f"  Contraseña: admin123456")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
