from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, FloatField, Sum
from django.db.models.signals import post_save
from django.db.transaction import commit
from django.dispatch import receiver

from django.utils.translation import pgettext_lazy
from ..inventario.models import Almacen, Proveedor, Producto, Stock
from datetime import datetime
from django.core.exceptions import ValidationError


# Modelo Estados



class Estados(object):
    ACTIVO = 'activo'
    DESACTIVO = 'desactivo'
    PROCESO = 'proceso'
    TERMINADO = 'terminado'
    OTRO = 'otro'

    CHOICES_SIMPLE = [
        (ACTIVO, pgettext_lazy('Estado', 'activo')),
        (DESACTIVO, pgettext_lazy('Estado', 'desactivo'))]

    CHOICES_NORMAL = [
        (PROCESO, pgettext_lazy('Estado', 'proceso')),
        (TERMINADO, pgettext_lazy('Estado', 'terminado')),
        (OTRO, pgettext_lazy('Estado', 'fallo'))]


# Modelo Usuario
class Usuario(models.Model):
    cod = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    tipo = models.IntegerField()
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.nombre


# Modelo Cliente
class Cliente(models.Model):
    cod = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20)
    direccion = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.nombre


# =============================  Modelo Ingreso  ==============================================
class Ingreso(models.Model):
    nro = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cod_proveedor = models.ForeignKey(Proveedor, related_name='ingreso_proveedor', verbose_name='Proveedor')
    cod_almacen = models.ForeignKey(Almacen, verbose_name='Almacen')
    cod_usuario = models.ForeignKey(User, verbose_name='Usuario')
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_NORMAL, default=Estados.PROCESO)

    def __str__(self):
        return str(self.nro)

    def get_total(self):
        total = (self.detalle_ingreso
            .all()
            .aggregate(
            total=Sum(
                F('precio') * F('cantidad'),
                output_field=FloatField()
            )))
        return total['total']

    get_total.short_description = 'Total'


class Detalle_Ingreso(models.Model):
    cod = models.AutoField(primary_key=True)
    cod_producto = models.ForeignKey(Producto, verbose_name='Producto')
    cod_ingreso = models.ForeignKey(Ingreso, null=True, blank=True, related_name='detalle_ingreso')
    cantidad = models.IntegerField()
    precio = models.FloatField()
    total = models.FloatField(default=0)

    def __str__(self):
        return f'{self.cod}{self.cod_ingreso}'

    # Metodo para actualizar el stok del producto cuando se ingresa o Sale.
    def save(self, *args, **kwargs):
        self.total = self.precio * self.cantidad

        # Condicion Para Saber si es un Ingreso o Salida.
        if self.cod_ingreso is not None:

            try:
                almacen = Almacen.objects.get(cod=self.cod_ingreso.cod_almacen.cod)
                producto = Producto.objects.get(cod=self.cod_producto.cod)
                stock = Stock.objects.get(cod_almacen=almacen, cod_producto=producto)
                stock.cantidad += self.cantidad
                stock.save()
            except (Stock.DoesNotExist):
                cat = Stock.objects.create(cod_almacen=self.cod_ingreso.cod_almacen, cod_producto=self.cod_producto)
                cat.save()
                almacen = Almacen.objects.get(cod=self.cod_ingreso.cod_almacen.cod)
                producto = Producto.objects.get(cod=self.cod_producto.cod)
                stock = Stock.objects.get(cod_almacen=almacen, cod_producto=producto)
                stock.cantidad += self.cantidad
                stock.save()
            super(Detalle_Ingreso, self).save(*args, **kwargs)


# ========================   Modelo Salida  =================================
class Salida(models.Model):
    tipos = (('salida', 'Salida'), ('proforma', 'Proforma'))
    nro = models.AutoField(primary_key=True)
    cod_almacen = models.ForeignKey(Almacen, related_name='salida_almacenes', verbose_name='Almacen')
    cod_usuario = models.ForeignKey(User, verbose_name='Usuario')
    cod_cliente = models.ForeignKey(Cliente, related_name='salida_cliente', verbose_name='Cliente')
    fecha = models.DateTimeField(default=datetime.now, blank=True, verbose_name='Fecha')
    fecha_entrega = models.DateTimeField(default=datetime.now, blank=True, verbose_name='Entrega')
    tipo_cambio = models.DecimalField(max_digits=6, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=tipos)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_NORMAL, default=Estados.PROCESO)

    def __str__(self):
        return f'{self.nro}{self.cod_almacen}'

    def get_total(self):
        total = (self.detalle_salida
            .all()
            .aggregate(
            total=Sum(
                F('precio') * F('cantidad'),
                output_field=FloatField()
            )))
        return total['total'] or 0.0

    get_total.short_description = 'Total'


class Detalle_Salida(models.Model):
    cod = models.AutoField(primary_key=True)
    cod_producto = models.ForeignKey(Producto, verbose_name='Producto')
    cod_salida = models.ForeignKey(Salida, null=True, blank=True, related_name='detalle_salida')
    cantidad = models.IntegerField()
    precio = models.FloatField()
    total = models.FloatField(default=0)

    def __str__(self):
        return f'{self.cod}{self.cod_salida}'

    def clean(self):
        almacen = Almacen.objects.get(cod=self.cod_salida.cod_almacen.cod)
        producto = Producto.objects.get(cod=self.cod_producto.cod)
        stock = Stock.objects.get(cod_almacen=almacen, cod_producto=producto)
        if stock.cantidad < self.cantidad:
            raise ValidationError("No existe esa Cantidad de Stock")

    def save(self, *args, **kwargs):
        self.total = self.precio * self.cantidad

        almacen = Almacen.objects.get(cod=self.cod_salida.cod_almacen.cod)
        producto = Producto.objects.get(cod=self.cod_producto.cod)
        stock = Stock.objects.get(cod_almacen=almacen, cod_producto=producto)
        self.clean()
        if stock.cantidad >= self.cantidad:
            stock.cantidad -= self.cantidad
            stock.save()
            super(Detalle_Salida, self).save(*args, **kwargs)


            # ========================  Modelo Traspaso  =======================================


class Traspaso(models.Model):
    nro = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cod_almacen_origen = models.ForeignKey(Almacen, related_name='almacen_origen', verbose_name='Almacen Origen')
    cod_almacen_destino = models.ForeignKey(Almacen, related_name='almacen_destino', verbose_name='Almacen Destino')
    cod_usuario = models.ForeignKey(User, verbose_name='Usuario')
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_NORMAL, default=Estados.PROCESO)

    def __str__(self):
        return str(self.nro)

    def clean(self):
        if self.cod_almacen_destino == self.cod_almacen_origen:
            raise ValidationError("Almacen Origen y Destino no pueden ser el mismo")

    def get_total(self):
        total = (self.detalle_traspaso
            .all()
            .aggregate(
            total=Sum(
                F('precio') * F('cantidad'),
                output_field=FloatField()
            )))
        return total['total']

    get_total.short_description = 'Total'


# Modelo Nota_Detalle
class Detalle_Traspaso(models.Model):
    cod = models.AutoField(primary_key=True)
    cod_producto = models.ForeignKey(Producto, verbose_name='Producto')
    cod_traspaso = models.ForeignKey(Traspaso, null=True, blank=True, related_name='detalle_traspaso')
    cantidad = models.IntegerField()
    precio = models.FloatField()
    total = models.FloatField(default=0)

    def __str__(self):
        return f'{self.cod}{self.cod_traspaso}'

    def clean(self):
        almacen = Almacen.objects.get(cod=self.cod_traspaso.cod_almacen_origen_id)
        producto = Producto.objects.get(cod=self.cod_producto.cod)
        stock = Stock.objects.get(cod_almacen=almacen, cod_producto=producto)

        if stock.cantidad == 0:
            raise ValidationError("No existe Stock en Almacen Origen")

        if stock.cantidad < self.cantidad:
            raise ValidationError("No existe esa Cantidad de Stock en Almacen Origen")

    def save(self, *args, **kwargs):
        self.total = self.precio * self.cantidad

        almacen_origen = Almacen.objects.get(cod=self.cod_traspaso.cod_almacen_origen_id)
        almacen_destino = Almacen.objects.get(cod=self.cod_traspaso.cod_almacen_destino_id)
        producto = Producto.objects.get(cod=self.cod_producto.cod)
        stock_origen = Stock.objects.get(cod_almacen=almacen_origen, cod_producto=producto)
        stock_destino = Stock.objects.get(cod_almacen=almacen_destino, cod_producto=producto)

        if stock_origen.cantidad >= self.cantidad:
            stock_origen.cantidad -= self.cantidad
            stock_destino.cantidad += self.cantidad
            stock_origen.save()
            stock_destino.save()
            super(Detalle_Traspaso, self).save(*args, **kwargs)
