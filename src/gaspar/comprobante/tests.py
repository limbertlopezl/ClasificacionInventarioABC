from django.test import TestCase
from .models import Cliente


# Create your tests here.
class ClienteTest(TestCase):
    def test_cliente(self):
        cliente = Cliente.objects.create(nombre='Limbert', nit='83646', direccion='Barrio 12 de abril')
        self.assertEqual(cliente.nombre, "Limbert")


class PaginaAdminTest(TestCase):
    def test_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_login(self):
        respons = self.client.get("/accounts/login/")
        self.assertEqual(respons.status_code, 200)

    def test_registrar(self):
        respons = self.client.get("/accounts/register/")
        self.assertEqual(respons.status_code, 200)

