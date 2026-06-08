#!/usr/bin/env python3
"""
Script para debuggear la creación de productos.
"""

import sys
import os
import uuid
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Empresa, Usuario, Producto
import bcrypt

def main():
    db = SessionLocal()
    try:
        # Crear empresa de prueba
        print("1. Creando empresa...")
        empresa = Empresa(
            nombre_comercial="Distribuidora Test",
            nit_o_cedula="123456789-0",
            plan="trial"
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        print(f"   ✅ Empresa creada: {empresa.id}")

        # Crear usuario admin
        print("2. Creando usuario admin...")
        password_hash = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
        usuario = Usuario(
            empresa_id=empresa.id,
            email="test@distri.com",
            hashed_password=password_hash,
            rol="admin",
            is_active=True
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        print(f"   ✅ Usuario creado: {usuario.id}")

        # Crear producto de prueba
        print("3. Creando producto...")
        producto = Producto(
            empresa_id=empresa.id,
            nombre="Leche Entera 1L",
            codigo_barras="7700123456789",
            precio_costo=Decimal("3500.00"),
            precio_venta=Decimal("5500.00"),
            cantidad_actual=Decimal("50.000"),
            unidad_medida="LITRO",
            categoria="Lácteos"
        )
        db.add(producto)
        db.commit()
        db.refresh(producto)
        print(f"   ✅ Producto creado: {producto.id}")
        print(f"      Nombre: {producto.nombre}")
        print(f"      Stock: {producto.cantidad_actual}")
        
        # Verificar que se creó
        print("4. Consultando producto...")
        p = db.query(Producto).filter(Producto.id == producto.id).first()
        if p:
            print(f"   ✅ Producto encontrado en BD: {p.nombre}")
        else:
            print(f"   ❌ Producto NO encontrado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
