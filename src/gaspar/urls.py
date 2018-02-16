from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.conf import settings
from .comprobante.views import UserSettings, RegistrationView, IngresoList, IngresoCreate, IngresoUpdate, IngresoDelete, \
    ProveedorList, ProveedorDelete, ProveedorUpdate, ProveedorCreate, ClienteCreate, ClienteDelete, ClienteUpdate, \
    ClienteList, SalidaCreate, SalidaDelete, SalidaUpdate, SalidaList, TraspasoCreate, TraspasoDelete, \
    TraspasoUpdate, TraspasoList, landing_view

from .inventario.views import AlmacenList, AlmacenCreate, AlmacenUpdate, AlmacenDelete, CategoriaCreate, \
    CategoriaDelete, CategoriaUpdate, CategoriaList, ProductoCreate, ProductoDelete, ProductoList, ProductoUpdate, \
    StockCreate, StockDelete, StockList, StockUpdate, messages
from .api.router import router

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^admin/docs/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/$', UserSettings.as_view(), name='user_settings'),
    url(r'^accounts/register/$', RegistrationView.as_view(), name='user_registration'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', landing_view),

    url(r'^ingreso/$', IngresoList.as_view(), name='ingreso_landing'),
    url(r'^ingreso/create/$', IngresoCreate.as_view(), name='ingreso_create'),
    url(r'^ingreso/(?P<pk>\d+)/$', IngresoUpdate.as_view(), name='ingreso_update'),
    url(r'^ingreso/(?P<pk>\d+)/delete/$', IngresoDelete.as_view(), name='ingreso_delete'),

    url(r'^salida/$', SalidaList.as_view(), name='salida_landing'),
    url(r'^salida/create/$', SalidaCreate.as_view(), name='salida_create'),
    url(r'^salida/(?P<pk>\d+)/$', SalidaUpdate.as_view(), name='salida_update'),
    url(r'^salida/(?P<pk>\d+)/delete/$', SalidaDelete.as_view(), name='salida_delete'),

    url(r'^traspaso/$', TraspasoList.as_view(), name='traspaso_landing'),
    url(r'^traspaso/create/$', TraspasoCreate.as_view(), name='traspaso_create'),
    url(r'^traspaso/(?P<pk>\d+)/$', TraspasoUpdate.as_view(), name='traspaso_update'),
    url(r'^traspaso/(?P<pk>\d+)/delete/$', TraspasoDelete.as_view(), name='traspaso_delete'),

    url(r'^proveedor/$', ProveedorList.as_view(), name='proveedor_landing'),
    url(r'^proveedor/create/$', ProveedorCreate.as_view(), name='proveedor_create'),
    url(r'^proveedor/(?P<pk>\d+)/$', ProveedorUpdate.as_view(), name='proveedor_update'),
    url(r'^proveedor/(?P<pk>\d+)/delete/$', ProveedorDelete.as_view(), name='proveedor_delete'),

    url(r'^cliente/$', ClienteList.as_view(), name='cliente_landing'),
    url(r'^cliente/create/$', ClienteCreate.as_view(), name='cliente_create'),
    url(r'^cliente/(?P<pk>\d+)/$', ClienteUpdate.as_view(), name='cliente_update'),
    url(r'^cliente/(?P<pk>\d+)/delete/$', ClienteDelete.as_view(), name='cliente_delete'),

    # =========================      MODULO DE INVENTARIO        =====================================

    url(r'^almacen/$', AlmacenList.as_view(), name='almacen_landing'),
    url(r'^almacen/create/$', AlmacenCreate.as_view(), name='almacen_create'),
    url(r'^almacen/(?P<pk>\d+)/$', AlmacenUpdate.as_view(), name='almacen_update'),
    url(r'^almacen/(?P<pk>\d+)/delete/$', AlmacenDelete.as_view(), name='almacen_delete'),

    url(r'^categoria/$', CategoriaList.as_view(), name='categoria_landing'),
    url(r'^categoria/create/$', CategoriaCreate.as_view(), name='categoria_create'),
    url(r'^categoria/(?P<pk>\d+)/$', CategoriaUpdate.as_view(), name='categoria_update'),
    url(r'^categoria/(?P<pk>\d+)/delete/$', CategoriaDelete.as_view(), name='categoria_delete'),

    url(r'^producto/$', ProductoList.as_view(), name='producto_landing'),
    url(r'^producto/create/$', ProductoCreate.as_view(), name='producto_create'),
    url(r'^producto/(?P<pk>\d+)/$', ProductoUpdate.as_view(), name='producto_update'),
    url(r'^producto/(?P<pk>\d+)/delete/$', ProductoDelete.as_view(), name='producto_delete'),

    url(r'^stock/$', StockList.as_view(), name='stock_landing'),
    url(r'^stock/create/$', StockCreate.as_view(), name='stock_create'),
    url(r'^stock/(?P<pk>\d+)/$', StockUpdate.as_view(), name='stock_update'),
    url(r'^stock/(?P<pk>\d+)/delete/$', StockDelete.as_view(), name='stock_delete'),

    url(r'^abc/', include('gaspar.comprobante.urls')),
    url(r'^inventario/', include('gaspar.inventario.urls')),
    url(r'^api/', include(router.urls, namespace='api')),

]
# Añadir
admin.site.site_header = 'LOMERCO'
admin.site.index_title = 'LOMERCO'
admin.site.site_title = 'ADMINISTRACION'

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.views import serve as static_serve

    staticpatterns = static(settings.STATIC_URL, view=static_serve)
    mediapatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = staticpatterns + mediapatterns + urlpatterns
