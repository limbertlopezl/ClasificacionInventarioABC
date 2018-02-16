from rest_framework import serializers
from rest_framework import viewsets

from ..comprobante.models import Salida, Detalle_Salida
from ..inventario.models import Stock, Almacen


class NotaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Salida
        fields = ('cod', 'cod_producto', 'cod_salida', 'cantidad', 'precio', 'total')


class SalidaSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    nota_detalle_salida = NotaDetalleSerializer(many=True)

    class Meta:
        model = Salida
        fields = (
            'nro', 'cod_almacen', 'cod_usuario', 'fecha', 'tipo_cambio', 'tipo', 'estado', 'total',
            'detalle_salida')

    def get_total(self, obj):
        return obj.get_total()


class SalidaViewset(viewsets.ModelViewSet):
    model = Salida

    serializer_class = SalidaSerializer

    def get_queryset(self):
        return Salida.objects.all()
