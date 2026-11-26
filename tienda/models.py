"""Modelos de la API E-commerce TecnoMarket Perú."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Categoria(models.Model):
    nombre = models.CharField("Nombre", max_length=60, unique=True)
    descripcion = models.TextField("Descripción", blank=True)
    imagen = models.CharField("Imagen (emoji)", max_length=8, default="📦")

    class Meta:
        verbose_name_plural = "Categorías"; ordering = ["nombre"]
    def __str__(self): return self.nombre


class Producto(models.Model):
    """RF1 - Producto del catálogo."""
    sku = models.CharField("SKU", max_length=30, unique=True)
    nombre = models.CharField("Nombre", max_length=150)
    descripcion = models.TextField("Descripción", blank=True)
    marca = models.CharField("Marca", max_length=60)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    descuento = models.PositiveIntegerField("Descuento %", default=0)
    stock = models.PositiveIntegerField("Stock", default=0)
    especificaciones = models.JSONField("Especificaciones", default=dict, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        indexes = [models.Index(fields=["marca"]), models.Index(fields=["categoria"])]
    def __str__(self): return self.nombre

    @property
    def precio_con_descuento(self):
        return round(float(self.precio) * (1 - self.descuento/100), 2)
    @property
    def disponible(self): return self.stock > 0
    @property
    def rating_promedio(self):
        rs = self.resenas.all()
        return round(sum(r.calificacion for r in rs)/rs.count(), 1) if rs.exists() else 0.0


class Resena(models.Model):
    """RF4 - Reseña de un producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="resenas")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resenas")
    calificacion = models.PositiveSmallIntegerField("Calificación")
    titulo = models.CharField("Título", max_length=120)
    comentario = models.TextField("Comentario", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
    def __str__(self): return f"{self.producto.nombre} - {self.calificacion}★"

    @property
    def es_compra_verificada(self):
        return Orden.objects.filter(usuario=self.usuario,
            items__producto=self.producto).exists()


class Orden(models.Model):
    """RF3 - Orden de compra."""
    ESTADOS = [("pendiente","Pendiente"),("pagada","Pagada"),("enviada","Enviada"),
               ("entregada","Entregada"),("cancelada","Cancelada")]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ordenes")
    direccion_envio = models.CharField("Dirección de envío", max_length=200)
    metodo_pago = models.CharField("Método de pago", max_length=40, default="tarjeta")
    estado = models.CharField("Estado", max_length=12, choices=ESTADOS, default="pendiente")
    total = models.DecimalField("Total", max_digits=10, decimal_places=2, default=0)
    numero_seguimiento = models.CharField("N° seguimiento", max_length=20, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
    def __str__(self): return f"Orden #{self.id} - {self.usuario.username}"

    @property
    def tiempo_estimado_entrega(self):
        return (self.fecha_creacion + timedelta(days=4)).date() if self.fecha_creacion else None


class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    def __str__(self): return f"{self.cantidad}x {self.producto.nombre}"
