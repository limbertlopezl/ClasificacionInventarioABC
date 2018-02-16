from django.conf.urls import url, include
from .views import abc, abc_almacen, abc_utilidad, abc_valor_total, abc_demanda

urlpatterns = [
    url(r'^$', abc),
    url(r'^almacen/', abc_almacen),
    url(r'^utilidad/', abc_utilidad),
    url(r'^valor/', abc_valor_total),
    url(r'^demanda/', abc_demanda),
]
