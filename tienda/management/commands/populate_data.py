"""python manage.py populate_data — datos Caso 2 (100 productos, 20 usuarios, 50 órdenes, 100 reseñas)."""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tienda.models import Categoria, Producto, Resena, Orden, ItemOrden


class Command(BaseCommand):
    help = "Puebla datos Caso 2."
    def handle(self, *a, **o):
        for M in [ItemOrden, Orden, Resena, Producto]: M.objects.all().delete()
        Categoria.objects.all().delete(); User.objects.filter(is_superuser=False).delete()
        # Reinicia los autoincrement para IDs deterministas en cada ejecucion (SQLite)
        from django.db import connection
        with connection.cursor() as cur:
            for t in ["tienda_itemorden","tienda_orden","tienda_resena","tienda_producto","tienda_categoria"]:
                try: cur.execute("DELETE FROM sqlite_sequence WHERE name=%s", [t])
                except Exception: pass

        cats_d = [("Laptops","LAP"),("Smartphones","CEL"),("Componentes","CMP"),
                  ("Accesorios","ACC"),("Audio","AUD"),("Monitores","MON")]
        cats = [Categoria.objects.create(nombre=n, imagen=i, descripcion=f"Productos de {n}") for n,i in cats_d]
        marcas = ["Dell","HP","Lenovo","Asus","Samsung","Logitech","Sony","Corsair","MSI","Acer"]

        for i in range(100):
            precio = round(random.uniform(50, 4000), 2)
            Producto.objects.create(
                sku=f"SKU-{10000+i}", nombre=f"{random.choice(marcas)} {random.choice(['Pro','Air','Gaming','Ultra','Max','Lite'])} {random.randint(100,999)}",
                marca=random.choice(marcas), categoria=random.choice(cats),
                descripcion="Producto tecnológico de alta calidad.", precio=precio,
                descuento=random.choice([0,0,0,10,15,20,25]), stock=random.randint(0,50),
                especificaciones={"color": random.choice(["Negro","Plata","Azul"]), "garantia": "12 meses"})

        usuarios = []
        for i in range(20):
            u = User.objects.create_user(username=f"cliente{i+1}", password="tecno2026",
                first_name=f"Cliente{i+1}", email=f"cliente{i+1}@mail.com")
            usuarios.append(u)

        productos = list(Producto.objects.all())
        for i in range(50):
            u = random.choice(usuarios)
            orden = Orden.objects.create(usuario=u, direccion_envio=f"Av. Siempre Viva {random.randint(100,999)}, Lima",
                metodo_pago=random.choice(["tarjeta","yape","plin","mercadopago"]),
                estado=random.choice(["pendiente","pagada","enviada","entregada","cancelada"]))
            total = 0
            for _ in range(random.randint(1,3)):
                p = random.choice(productos); cant = random.randint(1,2)
                ItemOrden.objects.create(orden=orden, producto=p, cantidad=cant, precio_compra=p.precio)
                total += float(p.precio)*cant
            orden.total = round(total,2); orden.save()

        for i in range(100):
            Resena.objects.create(producto=random.choice(productos), usuario=random.choice(usuarios),
                calificacion=random.randint(1,5), titulo=random.choice(["Excelente","Bueno","Regular","Recomendado","Me encantó"]),
                comentario="Reseña de prueba del producto.")

        self.stdout.write(self.style.SUCCESS(
            f"OK: {Producto.objects.count()} productos, {len(usuarios)} usuarios, "
            f"{Orden.objects.count()} órdenes, {Resena.objects.count()} reseñas."))
