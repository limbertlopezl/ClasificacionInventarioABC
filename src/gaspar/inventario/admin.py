from django.contrib import admin

# Register your models here.
from .models import Almacen, Stock, Producto, Categoria, Proveedor


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre', 'direccion', 'estado')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'cod_almacen', 'cod_producto', 'cantidad', 'estado')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    pass


@admin.register(Proveedor)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre', 'telefono', 'descripcion', 'estado')
    search_fields = ('nombre', 'cod')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre', 'marca', 'costo', 'precio', 'cod_categoria', 'estado')
    search_fields = ('nombre', 'marca')
