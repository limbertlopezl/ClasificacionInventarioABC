from rest_framework import routers
from .views import SalidaViewset

router = routers.DefaultRouter()
router.register('salidas', SalidaViewset, base_name='salida')
