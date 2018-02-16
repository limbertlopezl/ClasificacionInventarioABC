from django.contrib import admin

# Register your models here.
from .models import Usuario, Ingreso, Cliente, Salida, Traspaso, Detalle_Ingreso, Detalle_Salida, Detalle_Traspaso


# Register your models here.e
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    pass


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre', 'nit', 'direccion', 'estado')
    search_fields = ('nombre', 'nit')


class DetalleIngresoInlineAdmin(admin.TabularInline):
    model = Detalle_Ingreso
    extra = 0
    min_num = 1


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    inlines = [DetalleIngresoInlineAdmin]
    list_display = ('nro', 'fecha', 'cod_almacen', 'cod_usuario', 'get_total', 'estado')
    search_fields = ('nro', 'cod_almacen', 'cod_usuario')
    list_filter = ['estado', 'fecha']


class DetalleSalidaInlineAdmin(admin.TabularInline):
    model = Detalle_Salida
    extra = 0
    min_num = 1


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = (
    'nro', 'tipo', 'fecha', 'fecha_entrega', 'cod_almacen', 'cod_usuario', 'cod_cliente', 'get_total', 'estado')
    inlines = [DetalleSalidaInlineAdmin]
    list_filter = ['estado', 'fecha']


class DetalleTraspasoInlineAdmin(admin.TabularInline):
    model = Detalle_Traspaso
    extra = 0
    min_num = 1


@admin.register(Traspaso)
class TraspasoAdmin(admin.ModelAdmin):
    list_display = ('nro', 'fecha', 'cod_almacen_origen', 'cod_almacen_destino', 'cod_usuario', 'get_total', 'estado')
    inlines = [DetalleTraspasoInlineAdmin]
    list_filter = ['estado', 'fecha']
