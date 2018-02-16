from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = [
            'nombre',
            'nit',
            'direccion',
            'estado'
        ]

        labels = {
            'nombre': 'Nombre',
            'nit': 'Nit',
            'direccion': 'Direccion',
            'estado': 'Estado'
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
