from django.conf.urls import url, include
from .views import report_almacen, report_stock, report_producto

urlpatterns = [
    url(r'^reporte/almacen/', report_almacen),
    url(r'^reporte/stock/', report_stock),
    url(r'^reporte/producto/', report_producto),
]
