from django.test import TestCase
from .models import Categoria


class CategoriaTestCase(TestCase):
    def setUp(self):
        Categoria.objects.create(descripcion="jovenes")

    def test_categorias_descripcion(self):
        categoria = Categoria.objects.get(descripcion="jovenes")
        self.assertEqual(categoria.descripcion, "jovenes")
