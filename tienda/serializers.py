"""Serialización avanzada - Caso 2 E-commerce."""
from rest_framework import serializers
from .models import Categoria, Producto, Resena, Orden, ItemOrden


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "imagen"]


class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    """RF1 - Producto con nested categoría, 3 campos calculados y HATEOAS."""
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source="categoria", write_only=True)
    precio_con_descuento = serializers.ReadOnlyField()
    rating_promedio = serializers.ReadOnlyField()
    disponible = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ["url", "id", "sku", "nombre", "descripcion", "marca", "categoria",
                  "categoria_id", "precio", "descuento", "precio_con_descuento",
                  "rating_promedio", "stock", "disponible", "especificaciones"]
        extra_kwargs = {"url": {"view_name": "producto-detail"}}

    def get_disponible(self, obj): return obj.stock > 0

    def validate_precio(self, v):
        if v < 0: raise serializers.ValidationError("El precio no puede ser negativo.")
        return v


class ResenaSerializer(serializers.HyperlinkedModelSerializer):
    """RF4 - Reseña con validaciones y campo calculado."""
    es_compra_verificada = serializers.ReadOnlyField()
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    usuario_nombre = serializers.ReadOnlyField(source="usuario.username")
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = Resena
        fields = ["url", "id", "producto", "usuario", "usuario_nombre", "calificacion",
                  "titulo", "comentario", "es_compra_verificada", "creado"]
        read_only_fields = ["creado", "usuario"]
        extra_kwargs = {"url": {"view_name": "resena-detail"}}

    def validate_calificacion(self, v):
        """RF4 - Validación: calificación entre 1 y 5."""
        if v < 1 or v > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5.")
        return v


class ItemOrdenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source="producto.nombre")
    class Meta:
        model = ItemOrden
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_compra"]


class OrdenSerializer(serializers.HyperlinkedModelSerializer):
    """RF3 - Orden con items anidados (snapshot) y campos calculados."""
    items = ItemOrdenSerializer(many=True, read_only=True)
    tiempo_estimado_entrega = serializers.ReadOnlyField()
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    usuario_nombre = serializers.ReadOnlyField(source="usuario.username")

    class Meta:
        model = Orden
        fields = ["url", "id", "usuario", "usuario_nombre", "direccion_envio",
                  "metodo_pago", "estado", "total", "numero_seguimiento",
                  "tiempo_estimado_entrega", "items", "fecha_creacion"]
        read_only_fields = ["numero_seguimiento", "total", "usuario"]
        extra_kwargs = {"url": {"view_name": "orden-detail"}}
