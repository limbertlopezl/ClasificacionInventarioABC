from django.core.management import BaseCommand
from faker import Factory
from faker import Faker
from ....comprobante.models import Cliente, Ingreso, Detalle_Ingreso, Salida, Detalle_Salida
from ....inventario.models import Proveedor, Almacen, Producto
from random import sample
import random
from django.contrib.auth.models import User
from django.utils.timezone import get_default_timezone
from datetime import datetime

fake = Factory.create('es_MX')


class Command(BaseCommand):
    def cliente(self):
        for i in range(0, 20):
            nombre = f'{fake.first_name()}, {fake.last_name()}'
            nit = fake.numerify(text="##########")
            direccion = fake.address()
            Cliente.objects.create(nombre=nombre, nit=nit, direccion=direccion)

    def ingreso(self):

        lista_almacen = list(Almacen.objects.all())
        for almacen in lista_almacen:

            lista_proveed = list(Proveedor.objects.all())
            item_proveed = sample(lista_proveed, 1)[0]

            lista_user = list(User.objects.all())
            item_user = sample(lista_user, 1)[0]

            ingreso = Ingreso.objects.create(cod_proveedor=item_proveed, cod_almacen=almacen,
                                             cod_usuario=item_user)

            lista_producto = list(Producto.objects.all())
            for producto in lista_producto:
                numero = random.randint(20, 100)
                Detalle_Ingreso.objects.create(cod_producto=producto, cod_ingreso=ingreso, cantidad=numero,
                                               precio=producto.precio, total=producto.precio * numero)

    def salida(self):

        lista_almacen = list(Almacen.objects.all())

        for almacen in lista_almacen:
            lista_user = list(User.objects.all())
            item_user = sample(lista_user, 1)[0]

            lista_cliente = list(Cliente.objects.all())
            item_cliente = sample(lista_cliente, 1)[0]
            salida = Salida.objects.create(cod_almacen=almacen, cod_usuario=item_user, cod_cliente=item_cliente,
                                           tipo_cambio=7, tipo="salida")
            lista_producto = list(Producto.objects.all())
            for producto in lista_producto:
                numero = random.randint(5, 40)
                Detalle_Salida.objects.create(cod_producto=producto, cod_salida=salida, cantidad=numero,
                                              precio=producto.precio, total=numero * producto.precio)

    def handle(self, *args, **options):
        self.cliente()
        self.ingreso()
        self.salida()
