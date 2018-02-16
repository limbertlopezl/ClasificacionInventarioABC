from django.core.management import BaseCommand
from faker import Factory
from faker import Faker
from ....inventario.models import Proveedor, Categoria, Producto
from random import sample

fake = Factory.create('es_MX')


class Command(BaseCommand):
    def proveedor(self):
        for i in range(0, 20):
            nombre = fake.company()
            telefono = f'7{fake.numerify(text="#######")}'
            Descripcion = f'La Empresa {nombre} es una de las mas conocidos en las fabricacion de juguestes'
            Proveedor.objects.create(nombre=nombre,
                                     telefono=telefono,
                                     descripcion=Descripcion)

    def categoria(self):
        lista_categoria = ["Juguetes para Adolescente", "Juguetes para niños y niñas", "Juguetes didácticos",
                           "Juguetes de mesa", "Juguetes para adultos", "Juguetes deportivos", "Juguetes para bebés",
                           "Juguetes para todas las edades", "Juegos de pintar y dibujar", "Juguetes de encajar",
                           "Puzles y rompecabezas", "Juegos de Madera", "Juguetes adaptados"]
        for i in range(0, 13):
            Categoria.objects.create(descripcion=lista_categoria[i])

    def producto(self):

        lista_producto1 = (("Cartas de apuesta", "Mabbel", "40", "60"),
                           ("Tornado Towe ", "Mabbel", "50", "70"),
                           ("Action Figuris", "Maka", "70", "90"),
                           ("Arca de Noe", "Dirner", "90", "110"),
                           ("Cubo de Actividad Mediano", "Rubycub", "30", "50"),
                           ("Cubo de Actividad pequeño", "Rubycub", "30", "40"),
                           ("Cubo de Actividad Grande", "Rubycub", "50", "70"),
                           ("Laberinto ciudad pequeño", "Rasber", "20", "40"),
                           ("Laberinto ciudad Grande", "Rasbel", "30", "50"),
                           ("Tren de madera circula", "Dorbel", "100", "120"),
                           ("Tren de madera pista 8", "Rasbel", "150", "200"),
                           ("Cartas", "KOPO", "70", "90"),
                           ("Reloj Mano", "Relojers", "30", "40"),
                           ("Set de Cubos", "Mabbel", "20", "35"),
                           ("Caja de cocina", "Mabbel", "24", "50"),
                           ("Tren de Madera", "BEFU", "50", "90"),
                           ("Casa de madera", "BEFU", "20", "80"),
                           ("Cartas de apuesta", "Mabbel", "40", "60"),
                           ("Computadores Plastico", "Brevo", "100", "150"),
                           ("Mono Peluche", "Brevo", "25", "60"),
                           ("Oso Panda", "Promel", "25", "50"))

        lista_categ = list(Categoria.objects.all())
        lista_prove = list(Proveedor.objects.all())
        print(lista_producto1.__len__())
        for lista in lista_producto1:
            i = 0
            item_categ = sample(lista_categ, 1)[0]
            item_prove = sample(lista_prove, 1)[0]
            Producto.objects.create(nombre=lista[i], marca=lista[i + 1], cod_proveedor=item_prove, costo=lista[i + 2],
                                    precio=lista[i + 3], cod_categoria=item_categ)

    def handle(self, *args, **options):
        self.proveedor()
        self.categoria()
        self.producto()
