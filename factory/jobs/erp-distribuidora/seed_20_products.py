#!/usr/bin/env python3
"""
Script para poblar 20 productos realistas en el inventario del ERP Distribuidora.
"""

import sys
import os
from decimal import Decimal

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Empresa, Usuario, Producto

PRODUCTOS_SEEDS = [
    # Categoria: BEBIDAS (Gaseosas, Aguas, Cervezas por cajas)
    {
        "nombre": "Caja Cerveza Águila Light Botella x24",
        "codigo_barras": "7702004001234",
        "categoria": "Bebidas",
        "precio_costo": Decimal("48000.00"),
        "precio_venta": Decimal("60000.00"),
        "cantidad_actual": Decimal("35.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Cerveza Club Colombia Dorada x24",
        "codigo_barras": "7702004005678",
        "categoria": "Bebidas",
        "precio_costo": Decimal("54000.00"),
        "precio_venta": Decimal("68000.00"),
        "cantidad_actual": Decimal("20.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Paca Coca-Cola Original 1.5L x6 Botellas",
        "codigo_barras": "7702001041112",
        "categoria": "Bebidas",
        "precio_costo": Decimal("18500.00"),
        "precio_venta": Decimal("24000.00"),
        "cantidad_actual": Decimal("50.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Paca Coca-Cola Original 2.5L x6 Botellas",
        "codigo_barras": "7702001042225",
        "categoria": "Bebidas",
        "precio_costo": Decimal("27000.00"),
        "precio_venta": Decimal("35000.00"),
        "cantidad_actual": Decimal("40.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Paca Gaseosa Postobón Manzana 1.5L x6",
        "codigo_barras": "7702005012221",
        "categoria": "Bebidas",
        "precio_costo": Decimal("15000.00"),
        "precio_venta": Decimal("20000.00"),
        "cantidad_actual": Decimal("45.000"),
        "unidad_medida": "CAJA"
    },
    
    # Categoria: SNACKS (Papas, Galletas por cajas/display)
    {
        "nombre": "Display Papas Margarita Pollo x12",
        "codigo_barras": "7702006123456",
        "categoria": "Snacks",
        "precio_costo": Decimal("19200.00"),
        "precio_venta": Decimal("26400.00"),
        "cantidad_actual": Decimal("30.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Display Papas Margarita Limón x12",
        "codigo_barras": "7702006123487",
        "categoria": "Snacks",
        "precio_costo": Decimal("19200.00"),
        "precio_venta": Decimal("26400.00"),
        "cantidad_actual": Decimal("25.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Galletas Festival Chocolate x36 paquetes",
        "codigo_barras": "7702007204455",
        "categoria": "Snacks",
        "precio_costo": Decimal("21600.00"),
        "precio_venta": Decimal("30000.00"),
        "cantidad_actual": Decimal("15.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Galletas Oreo Original x36 paquetes",
        "codigo_barras": "7622210123456",
        "categoria": "Snacks",
        "precio_costo": Decimal("28800.00"),
        "precio_venta": Decimal("39600.00"),
        "cantidad_actual": Decimal("12.000"),
        "unidad_medida": "CAJA"
    },

    # Categoria: GRANEL/ABARROTES (Sacos de arroz, azúcar, harina)
    {
        "nombre": "Bulto de Arroz Diana Premium x50kg",
        "codigo_barras": "7703001001111",
        "categoria": "Granel",
        "precio_costo": Decimal("145000.00"),
        "precio_venta": Decimal("175000.00"),
        "cantidad_actual": Decimal("10.000"),
        "unidad_medida": "BULTO"
    },
    {
        "nombre": "Bulto de Azúcar Manuelita x50kg",
        "codigo_barras": "7703002002222",
        "categoria": "Granel",
        "precio_costo": Decimal("165000.00"),
        "precio_venta": Decimal("198000.00"),
        "cantidad_actual": Decimal("8.000"),
        "unidad_medida": "BULTO"
    },
    {
        "nombre": "Saco de Harina de Trigo Haz de Oros x25kg",
        "codigo_barras": "7703003003333",
        "categoria": "Granel",
        "precio_costo": Decimal("82000.00"),
        "precio_venta": Decimal("99000.00"),
        "cantidad_actual": Decimal("12.000"),
        "unidad_medida": "BULTO"
    },
    {
        "nombre": "Fardo de Aceite Premier 1000ml x12 Botellas",
        "codigo_barras": "7703004004444",
        "categoria": "Abarrotes",
        "precio_costo": Decimal("72000.00"),
        "precio_venta": Decimal("90000.00"),
        "cantidad_actual": Decimal("18.000"),
        "unidad_medida": "CAJA"
    },

    # Categoria: LACTEOS (Cajas de leche, quesos en bloque)
    {
        "nombre": "Caja Leche Entera Alquería 1L x12 Bolsas",
        "codigo_barras": "7702012001122",
        "categoria": "Lacteos",
        "precio_costo": Decimal("38400.00"),
        "precio_venta": Decimal("48000.00"),
        "cantidad_actual": Decimal("25.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Leche Deslactosada Alquería 1L x12 Bolsas",
        "codigo_barras": "7702012003344",
        "categoria": "Lacteos",
        "precio_costo": Decimal("41000.00"),
        "precio_venta": Decimal("52000.00"),
        "cantidad_actual": Decimal("20.000"),
        "unidad_medida": "CAJA"
    },

    # Categoria: LIMPIEZA / ASEO (Detergentes en caja, jabones)
    {
        "nombre": "Caja Detergente Fab Floral 2kg x8 bolsas",
        "codigo_barras": "7702015009988",
        "categoria": "Limpieza",
        "precio_costo": Decimal("76000.00"),
        "precio_venta": Decimal("96000.00"),
        "cantidad_actual": Decimal("15.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Suavizante Downy Concentrado 1.4L x6",
        "codigo_barras": "7501006720412",
        "categoria": "Limpieza",
        "precio_costo": Decimal("78000.00"),
        "precio_venta": Decimal("99000.00"),
        "cantidad_actual": Decimal("10.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Jabón Rey x40 unidades (Tradicional)",
        "codigo_barras": "7702015001111",
        "categoria": "Aseo",
        "precio_costo": Decimal("68000.00"),
        "precio_venta": Decimal("88000.00"),
        "cantidad_actual": Decimal("14.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Paca Papel Higiénico Familia Acolchado x12 rollos x4 paq",
        "codigo_barras": "7702026112233",
        "categoria": "Aseo",
        "precio_costo": Decimal("38000.00"),
        "precio_venta": Decimal("48000.00"),
        "cantidad_actual": Decimal("22.000"),
        "unidad_medida": "CAJA"
    },
    {
        "nombre": "Caja Lavaloza Axion Limón 400g x12 unidades",
        "codigo_barras": "7702015004455",
        "categoria": "Limpieza",
        "precio_costo": Decimal("44000.00"),
        "precio_venta": Decimal("57600.00"),
        "cantidad_actual": Decimal("15.000"),
        "unidad_medida": "CAJA"
    }
]

def main():
    db = SessionLocal()
    try:
        # 1. Obtener la última empresa registrada
        empresa = db.query(Empresa).order_by(Empresa.created_at.desc()).first()
        if not empresa:
            print("[ERROR] No se encontro ninguna empresa en la base de datos.")
            print("Por favor, registrate primero desde el frontend.")
            return

        print(f"[INFO] Empresa seleccionada: '{empresa.nombre_comercial}' (ID: {empresa.id})")

        # 2. Mostrar usuarios de la empresa
        usuarios = db.query(Usuario).filter(Usuario.empresa_id == empresa.id).all()
        print(f"[INFO] Usuarios registrados en esta empresa:")
        for u in usuarios:
            print(f"  - {u.email} | Rol: {u.rol} | Activo: {u.is_active}")

        # 3. Poblar productos
        print("\n[INFO] Sembrando 20 productos realistas...")
        agregados = 0
        actualizados = 0
        
        for item in PRODUCTOS_SEEDS:
            # Buscar si el código de barras ya existe en esta empresa
            prod_existente = db.query(Producto).filter(
                Producto.empresa_id == empresa.id,
                Producto.codigo_barras == item["codigo_barras"]
            ).first()

            if prod_existente:
                # Actualizar información
                prod_existente.nombre = item["nombre"]
                prod_existente.categoria = item["categoria"]
                prod_existente.precio_costo = item["precio_costo"]
                prod_existente.precio_venta = item["precio_venta"]
                prod_existente.unidad_medida = item["unidad_medida"]
                prod_existente.is_active = True
                actualizados += 1
            else:
                # Crear nuevo producto
                nuevo_prod = Producto(
                    empresa_id=empresa.id,
                    nombre=item["nombre"],
                    codigo_barras=item["codigo_barras"],
                    categoria=item["categoria"],
                    precio_costo=item["precio_costo"],
                    precio_venta=item["precio_venta"],
                    cantidad_actual=item["cantidad_actual"],
                    unidad_medida=item["unidad_medida"],
                    is_active=True
                )
                db.add(nuevo_prod)
                agregados += 1

        db.commit()
        print(f"[OK] Proceso completado exitosamente.")
        print(f"   [INFO] Productos creados: {agregados}")
        print(f"   [INFO] Productos actualizados: {actualizados}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante la siembra de datos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
