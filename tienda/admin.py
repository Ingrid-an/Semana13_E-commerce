from django.contrib import admin
from .models import Categoria, Producto, Resena, Orden, ItemOrden

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre","marca","categoria","precio","descuento","stock","rating_promedio")
    list_filter = ("categoria","marca"); search_fields = ("nombre","sku","marca")

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("id","usuario","estado","total","fecha_creacion"); list_filter = ("estado",)

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("producto","usuario","calificacion","es_compra_verificada"); list_filter = ("calificacion",)

admin.site.register(Categoria); admin.site.register(ItemOrden)
