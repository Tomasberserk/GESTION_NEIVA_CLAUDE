"""Database seed script for local development and evaluation environments."""
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.database import SessionLocal
from app.models import DetalleVenta, Empresa, Producto, RolUsuario, Usuario, Venta
from app.services import auth_service, entitlement_service


def seed() -> None:
    """Populate initial demo store, admin user, catalog products, and sample sales."""
    db = SessionLocal()
    try:
        company = db.query(Empresa).first()
        if not company:
            company = Empresa(
                nombre_comercial="Tienda La Principal",
                nit_o_cedula="900123456-7",
                is_active=True,
            )
            entitlement_service.inicializar_trial(company)
            db.add(company)
            db.commit()
            db.refresh(company)

            hashed_pw = auth_service.hash_password("Admin123!")
            admin = Usuario(
                nombre="Administrador Demo",
                email="admin@demo.com",
                hashed_password=hashed_pw,
                empresa_id=company.id,
                rol=RolUsuario.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()

        print(f"Using company: {company.nombre_comercial} (ID: {company.id})")

        product_names = [
            "Arroz Diana x 500g", "Frijol Bola Roja x 500g", "Aceite Gourmet 1L",
            "Sal Refisal 1kg", "Azúcar Manuelita 1kg", "Leche Alquería 1L",
            "Pan Bimbo Blanco", "Huevos AAA (Canasta 30)", "Café Águila Roja 250g",
            "Chocolate Corona", "Galletas Saltín Noel", "Gaseosa Coca-Cola 2L",
            "Jugo Hit Mora 500ml", "Agua Brisa 600ml", "Cerveza Poker Lata",
        ]

        print("Clearing previous sample sales and products for company...")
        db.query(Venta).filter(Venta.empresa_id == company.id).delete()
        db.query(Producto).filter(Producto.empresa_id == company.id).delete()
        db.commit()

        created_products: list[Producto] = []
        print("Creating 15 sample products...")
        for idx, name in enumerate(product_names):
            cost = Decimal(str(random.randint(1000, 15000)))
            price = Decimal(str(int(float(cost) * (1 + random.uniform(0.15, 0.35)))))
            stock = Decimal(str(random.randint(25, 100)))

            prod = Producto(
                empresa_id=company.id,
                nombre=name,
                codigo_barras=f"770{random.randint(1000000000, 9999999999)}",
                precio_costo=cost,
                precio_venta=price,
                cantidad_actual=stock,
                unidad_medida="unidad",
                foto_url=f"https://picsum.photos/seed/{idx + 1}/200/200",
                is_active=True,
            )
            db.add(prod)
            created_products.append(prod)

        db.commit()
        for prod in created_products:
            db.refresh(prod)

        print("Creating 20 sample sales...")
        now = datetime.now(timezone.utc)
        for _ in range(20):
            sale_date = now - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
            )
            sale = Venta(
                empresa_id=company.id,
                fecha_venta=sale_date,
                total=Decimal("0.00"),
                vendedor_nombre_snapshot="Administrador Demo",
                is_active=True,
            )
            db.add(sale)
            db.flush()

            selected_products = random.sample(created_products, random.randint(1, 5))
            sale_total = Decimal("0.00")
            for prod in selected_products:
                qty = Decimal(str(random.randint(1, 3)))
                prod.cantidad_actual -= qty
                subtotal = prod.precio_venta * qty
                sale_total += subtotal
                detail = DetalleVenta(
                    venta_id=sale.id,
                    producto_id=prod.id,
                    cantidad=qty,
                    precio_unitario=prod.precio_venta,
                    subtotal=subtotal,
                    is_active=True,
                )
                db.add(detail)

            sale.total = sale_total
            db.commit()

        print("Seed completed successfully: 15 products and 20 sales created.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
