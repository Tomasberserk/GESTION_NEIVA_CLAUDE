import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

from app.database import SessionLocal
from app import models

EMPRESA_EMAIL = "judini@gmail.com"

PRODUCTOS_DEMO = [
    ("Cuaderno universitario 100 hojas", "7702009001001", 2200,  3500,  45, "unidad", "Utiles escolares", 10),
    ("Cuaderno cosido 50 hojas",         "7702009001002", 1100,  1800,  60, "unidad", "Utiles escolares", 15),
    ("Lapicero Bic azul",                "7702009002001",  300,   500, 120, "unidad", "Utiles escolares", 20),
    ("Lapicero Bic negro",               "7702009002002",  300,   500,  95, "unidad", "Utiles escolares", 20),
    ("Lapicero Bic rojo",                "7702009002003",  300,   500,  80, "unidad", "Utiles escolares", 15),
    ("Borrador grande blanco",           "7702009003001",  200,   400,  70, "unidad", "Utiles escolares", 10),
    ("Corrector liquido Pelikan",        "7702009004001",  900,  1500,  30, "unidad", "Utiles escolares",  5),
    ("Colores x12 Norma",                "7702009005001", 3500,  5500,  25, "unidad", "Utiles escolares",  5),
    ("Colores x6 Pelikan",               "7702009005002", 1800,  2800,  35, "unidad", "Utiles escolares",  8),
    ("Marcador permanente negro",        "7702009006001",  600,  1000,  50, "unidad", "Utiles escolares", 10),
    ("Resma papel carta 500 hojas",      "7702009007001", 9500, 13000,  18, "unidad", "Papel y resmas",    3),
    ("Resma papel oficio 500 hojas",     "7702009007002",10500, 14500,  12, "unidad", "Papel y resmas",    3),
    ("Cartucho tinta negra HP 664",      "7702009008001",18000, 25000,   8, "unidad", "Tecnologia",        2),
    ("Cartucho tinta color HP 664",      "7702009008002",19000, 27000,   6, "unidad", "Tecnologia",        2),
    ("USB 16GB Kingston",                "7702009009001",12000, 18000,  10, "unidad", "Tecnologia",        3),
    ("Tijeras escolar punta roma",       "7702009010001", 1500,  2500,  28, "unidad", "Utiles escolares",  5),
    ("Regla 30cm plastico",              "7702009011001",  400,   700,  55, "unidad", "Utiles escolares", 10),
    ("Sacapuntas metalico doble",        "7702009012001",  500,   900,  65, "unidad", "Utiles escolares", 10),
    ("Fotocopia carta por hoja",         "7702009013001",   50,   100,9999, "unidad", "Servicios",         0),
    ("Impresion a color por hoja",       "7702009014001",  200,   500,9999, "unidad", "Servicios",         0),
]


random.seed(42)


def run():
    db = SessionLocal()
    try:
        usuario = db.query(models.Usuario).filter(
            models.Usuario.email == EMPRESA_EMAIL,
            models.Usuario.is_active.is_(True),
        ).first()

        if not usuario:
            print("[ERROR] Usuario no encontrado:", EMPRESA_EMAIL)
            return

        empresa_id = usuario.empresa_id
        print("[OK] Empresa ID:", empresa_id)
        print("[OK] Usuario:", usuario.email)

        # ---------- 20 productos ----------
        print("\n[*] Insertando productos...")
        productos_insertados = []

        for (nombre, barcode, costo, venta, cantidad, unidad, cat, stock_min) in PRODUCTOS_DEMO:
            existe = db.query(models.Producto).filter(
                models.Producto.empresa_id == empresa_id,
                models.Producto.codigo_barras == barcode,
            ).first()
            if existe:
                print("   [SKIP]", nombre)
                productos_insertados.append(existe)
                continue

            p = models.Producto(
                empresa_id=empresa_id,
                nombre=nombre,
                codigo_barras=barcode,
                precio_costo=Decimal(str(costo)),
                precio_venta=Decimal(str(venta)),
                cantidad_actual=cantidad,
                unidad_medida=unidad,
                categoria=cat,
                stock_minimo=stock_min,
                is_active=True,
            )
            db.add(p)
            db.flush()
            productos_insertados.append(p)
            print(f"   [OK] {nombre} | ${venta:,} | stock={cantidad}")

        db.commit()
        print("[OK] Productos guardados:", len(productos_insertados))

        # ---------- 20 ventas ----------
        print("\n[*] Insertando ventas...")

        fisicos   = [p for p in productos_insertados if p.cantidad_actual < 9000]
        servicios = [p for p in productos_insertados if p.cantidad_actual >= 9000]

        ahora = datetime.now(timezone.utc)
        ventas_ok = 0

        for i in range(20):
            dias   = random.randint(0, 29)
            hora   = random.randint(7, 20)
            minuto = random.randint(0, 59)
            fecha  = (ahora - timedelta(days=dias)).replace(hour=hora, minute=minuto, second=0, microsecond=0)

            venta = models.Venta(
                empresa_id=empresa_id,
                usuario_id=usuario.id,
                fecha_venta=fecha,
                total=Decimal("0.00"),
                is_active=True,
            )
            db.add(venta)
            db.flush()

            total = Decimal("0.00")
            pool  = fisicos.copy()
            if servicios and random.random() < 0.4:
                pool += servicios

            elegidos = random.sample(pool, min(random.randint(1, 3), len(pool)))
            lineas   = []

            for prod in elegidos:
                es_srv = prod.cantidad_actual >= 9000
                cant   = random.randint(1, 10 if es_srv else 5)

                if not es_srv:
                    if prod.cantidad_actual == 0:
                        continue
                    cant = min(cant, prod.cantidad_actual)

                sub = prod.precio_venta * cant
                total += sub

                db.add(models.DetalleVenta(
                    venta_id=venta.id,
                    producto_id=prod.id,
                    cantidad=cant,
                    precio_unitario=prod.precio_venta,
                    subtotal=sub,
                ))
                lineas.append(f"{prod.nombre} x{cant}")
                if not es_srv:
                    prod.cantidad_actual -= cant

            if not lineas:
                db.expunge(venta)
                continue

            venta.total = total
            db.commit()
            ventas_ok += 1
            print(f"   [OK] Venta {ventas_ok:02d} [{fecha.strftime('%d/%m %H:%M')}] ${float(total):,.0f}")

        print("\n[DONE] Seed finalizado.")
        print("       Productos:", len(productos_insertados))
        print("       Ventas:   ", ventas_ok)

    except Exception as exc:
        db.rollback()
        print("[ERROR]", exc)
        import traceback; traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run()
