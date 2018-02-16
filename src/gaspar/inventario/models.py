from django.db import models
from django.utils.translation import pgettext_lazy


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


# Modelo Almacen
class Almacen(models.Model):
    cod = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.nombre


# Modelo Categoria
class Categoria(models.Model):
    cod = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.descripcion


        # Modelo Proveedor


class Proveedor(models.Model):
    cod = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.nombre


# Modelo Producto
class Producto(models.Model):
    cod = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    foto = models.ImageField(blank=True)
    marca = models.CharField(max_length=50)
    cod_proveedor = models.ForeignKey(Proveedor, verbose_name='Proveedor')
    costo = models.FloatField()
    precio = models.FloatField()
    cod_categoria = models.ForeignKey(Categoria, verbose_name='Categoria')
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return self.nombre


# Modelo Stock
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    cod_almacen = models.ForeignKey(Almacen, verbose_name='almacen', related_name='almacenes')
    cod_producto = models.ForeignKey(Producto, verbose_name='Producto', related_name='productos')
    cantidad = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=Estados.CHOICES_SIMPLE, default=Estados.ACTIVO)

    def __str__(self):
        return f'{self.id}'
