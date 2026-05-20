import random
import uuid
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Empresa, Producto, Venta, DetalleVenta, Usuario, RolUsuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    
    # 1. Obtener o crear una empresa
    empresa = db.query(Empresa).first()
    if not empresa:
        empresa = Empresa(nombre_comercial="Tienda La Principal", nit_o_cedula="123456789")
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        
        # Crear un usuario administrador si se creó la empresa nueva
        hash_pw = pwd_context.hash("admin123")
        admin = Usuario(email="admin@admin.com", hashed_password=hash_pw, empresa_id=empresa.id, rol=RolUsuario.ADMIN)
        db.add(admin)
        db.commit()

    print(f"Usando empresa: {empresa.nombre_comercial} (ID: {empresa.id})")

    # 2. Productos a insertar (30 productos típicos de tienda de barrio)
    nombres_productos = [
        "Arroz Diana x 500g", "Frijol Bola Roja x 500g", "Aceite Gourmet 1L", "Sal Refisal 1kg", "Azúcar Manuelita 1kg",
        "Leche Alquería 1L", "Pan Bimbo Blanco", "Huevos AAA (Canasta 30)", "Café Águila Roja 250g", "Chocolate Corona",
        "Galletas Saltín Noel", "Gaseosa Coca-Cola 2L", "Jugo Hit Mora 500ml", "Agua Brisa 600ml", "Cerveza Poker Lata",
        "Detergente Ariel 1kg", "Jabón Rey 250g", "Crema Dental Colgate", "Papel Higiénico Familia (4 rollos)", "Shampoo Savital 500ml",
        "Margarina Rama 250g", "Salsa de Tomate Fruco", "Mayonesa Fruco", "Atún Van Camp's en Aceite", "Sardinas en Salsa de Tomate",
        "Pasta Doria (Spaghetti)", "Lentejas x 500g", "Harina Pan Amarilla", "Queso Campesino", "Jamón Zenú x 200g"
    ]

    productos_creados = []
    
    print("Borrando productos y ventas anteriores de la empresa...")
    db.query(Venta).filter(Venta.empresa_id == empresa.id).delete()
    db.query(Producto).filter(Producto.empresa_id == empresa.id).delete()
    db.commit()

    print("Creando 15 productos...")
    for idx, nombre in enumerate(nombres_productos[:15]):
        costo = random.randint(1000, 15000)
        # Margen aleatorio entre 15% y 35%
        venta = int(costo * (1 + random.uniform(0.15, 0.35)))
        stock = random.randint(10, 100)
        
        prod = Producto(
            empresa_id=empresa.id,
            nombre=nombre,
            codigo_barras=f"770{random.randint(1000000000, 9999999999)}",
            precio_costo=costo,
            precio_venta=venta,
            cantidad_actual=stock,
            foto_url=f"https://picsum.photos/seed/{idx+1}/200/200"  # Imagen placeholder
        )
        db.add(prod)
        productos_creados.append(prod)
    
    db.commit()
    for p in productos_creados:
        db.refresh(p)
    print("¡Productos creados exitosamente!")

    # 3. Crear 20 ventas aleatorias
    print("Creando 20 ventas...")
    now = datetime.now()
    
    for i in range(20):
        # Fecha aleatoria en los últimos 7 días
        dias_restar = random.randint(0, 7)
        horas_restar = random.randint(0, 23)
        fecha_venta = now - timedelta(days=dias_restar, hours=horas_restar)
        
        nueva_venta = Venta(
            empresa_id=empresa.id,
            fecha_venta=fecha_venta,
            total=0 # Se actualiza luego de los detalles
        )
        db.add(nueva_venta)
        db.commit()
        db.refresh(nueva_venta)
        
        # Seleccionar entre 1 y 5 productos aleatorios para esta venta
        num_productos_venta = random.randint(1, 5)
        productos_venta = random.sample(productos_creados, num_productos_venta)
        
        total_venta = 0
        for p in productos_venta:
            cantidad_comprada = random.randint(1, 4)
            # Reducir stock
            p.cantidad_actual -= cantidad_comprada
            
            subtotal = p.precio_venta * cantidad_comprada
            total_venta += subtotal
            
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=p.id,
                cantidad=cantidad_comprada,
                precio_unitario=p.precio_venta,
                subtotal=subtotal
            )
            db.add(detalle)
            
        nueva_venta.total = total_venta
        db.commit()
        
    print("¡14 ventas creadas exitosamente!")
    
    db.close()

if __name__ == "__main__":
    seed()
