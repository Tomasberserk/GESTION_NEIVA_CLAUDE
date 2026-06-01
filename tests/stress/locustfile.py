import uuid
import random
from locust import HttpUser, task, between

class UsuarioPOS(HttpUser):
    # Tiempo de espera aleatorio entre peticiones (simula la velocidad de operacion del cajero)
    wait_time = between(1, 3)

    def on_start(self):
        """
        Se ejecuta al iniciar cada usuario virtual.
        Registra una empresa de prueba y crea productos iniciales en su inventario.
        """
        self.productos = []
        self.empresa_id = None
        self.token = None
        
        # Generar identificadores unicos para esta sesion de estres
        unique_id = str(uuid.uuid4())[:8]
        self.email = f"user_{unique_id}@stress-tienda.com"
        self.password = "StressPassword123!"
        self.nombre_comercial = f"Tienda Stress {unique_id}"
        self.nit = f"nit-{unique_id}"

        # 1. Registrar empresa y administrador
        payload_registro = {
            "nombre_comercial": self.nombre_comercial,
            "nit_o_cedula": self.nit,
            "email": self.email,
            "password": self.password,
            "rol": "admin"
        }
        
        with self.client.post("/auth/registro-completo", json=payload_registro, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                self.token = data.get("access_token")
                self.empresa_id = data.get("usuario", {}).get("empresa_id")
                # Actualizar cabecera de autorizacion por defecto para las siguientes peticiones
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                response.success()
            else:
                response.failure(f"Error al registrar: {response.text}")
                return

        # 2. Registrar 3 productos basicos en el inventario para poder hacer ventas despues
        if self.empresa_id:
            for i in range(1, 4):
                payload_producto = {
                    "nombre": f"Producto Stress {i} - {unique_id}",
                    "codigo_barras": f"bar-{i}-{unique_id}",
                    "precio_costo": round(random.uniform(500, 3000), 2),
                    "precio_venta": round(random.uniform(3500, 8000), 2),
                    "cantidad_actual": 100.0,
                    "unidad_medida": "unidad",
                    "empresa_id": self.empresa_id
                }
                with self.client.post("/productos/", json=payload_producto, catch_response=True) as p_res:
                    if p_res.status_code == 201:
                        p_data = p_res.json()
                        self.productos.append(p_data.get("id"))
                        p_res.success()
                    else:
                        p_res.failure(f"Fallo creacion de producto {i}: {p_res.text}")

    @task(3)
    def ver_dashboard(self):
        """Simula al cajero mirando el Dashboard para ver las ventas e ingresos de hoy."""
        if self.empresa_id:
            self.client.get(f"/dashboard/{self.empresa_id}")

    @task(4)
    def ver_inventario(self):
        """Simula al cajero cargando la grilla de productos en el POS."""
        if self.empresa_id:
            self.client.get(f"/productos/{self.empresa_id}")

    @task(2)
    def ver_reportes_financieros(self):
        """Simula al administrador cargando el reporte de ROI y analisis de reinversion."""
        if self.empresa_id:
            self.client.get(f"/reportes/financieros/{self.empresa_id}")

    @task(3)
    def registrar_venta(self):
        """Simula al cajero completando el checkout de un carrito de compras."""
        if self.empresa_id and self.productos:
            # Seleccionar de 1 a 2 productos aleatorios del inventario
            productos_venta = random.sample(self.productos, k=random.randint(1, min(2, len(self.productos))))
            
            detalles = []
            for p_id in productos_venta:
                detalles.append({
                    "producto_id": p_id,
                    "cantidad": float(random.randint(1, 3))
                })
                
            payload_venta = {
                "detalles": detalles
            }
            
            self.client.post(f"/ventas/{self.empresa_id}", json=payload_venta)
