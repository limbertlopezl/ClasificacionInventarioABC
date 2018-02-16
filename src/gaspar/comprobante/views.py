from django.contrib.auth import get_user_model
from django.db.models import F, Count, FloatField, DateField, IntegerField
from django.db.models import Sum, Max, Avg
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.views.generic import View
from django import forms
from django.forms import widgets
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import CreateView, ListView, UpdateView

from ..inventario.models import Producto, Stock, Almacen
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Ingreso, Usuario, Proveedor, Cliente, Salida, Traspaso, Detalle_Salida, Detalle_Ingreso

from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
import datetime
from django.core.exceptions import ValidationError


# Create your views here.


def index(request):
    return HttpResponse("Index")


def cliente_insertar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('index')
    else:
        form = ClienteForm()

    return render(request, 'comprobante/cliente_form.html', {'form': form})


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


# LoginRequiredMixin-> Obliga a logearse al usuario que quiera entrar.
class UserSettings(LoginRequiredMixin, FormView):
    template_name = 'users/settings.html'
    form_class = UserForm

    # se ejecuta cuando el formulario se carga por primera vez.
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    # se ejecutara cuando el formulario sea valido.
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Sus datos fueron actualizados')
        return redirect('/accounts/')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", max_length=100, help_text="Ambas contraseñas deben ser iguales.",
                               widget=widgets.PasswordInput)
    password2 = forms.CharField(label="Repetir Contraseña", max_length=100, widget=widgets.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        value = self.cleaned_data['email']

        if User.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese email')

        return value

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError('Ambas contraseñas no coinciden')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user


class RegistrationView(FormView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm
    success_url = '/accounts/login/'

    if __name__ == '__main__':
        def form_valid(self, form):
            form.save()
            return super().form_valid(form)


# =========================== Vistas Para el Proveedor ===================================================

class ProveedorView(LoginRequiredMixin):
    model = Proveedor

    def get_queryset(self):
        return Proveedor.objects.all()
        # return Proveedor.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class ProveedorList(ProveedorView, ListView):
    pass


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ('nombre', 'telefono', 'descripcion')


class ProveedorCreate(ProveedorView, CreateView):
    form_class = ProveedorForm

    def form_valid(self, form):
        Proveedor = form.save(commit=False)
        Proveedor.save()
        messages.success(self.request, 'Proveedor Creado')
        return redirect('proveedor_update', pk=Proveedor.cod)


class ProveedorUpdate(ProveedorView, UpdateView):
    form_class = ProveedorForm

    def form_valid(self, form):
        proveedor = form.save()
        messages.success(self.request, f'Proveedor "{proveedor}" Actualizada')
        return redirect('proveedor_landing')


class ProveedorDelete(ProveedorView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Proveedor eliminado')
        return reverse('proveedor_landing')


# ===========================   Vistas Para el CLIENTE  =============================================

class ClienteView(LoginRequiredMixin):
    model = Cliente

    def get_queryset(self):
        return Cliente.objects.all()
        # return Proveedor.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class ClienteList(ClienteView, ListView):
    pass


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nombre', 'nit', 'direccion')


class ClienteCreate(ClienteView, CreateView):
    form_class = ClienteForm

    def form_valid(self, form):
        Cliente = form.save(commit=False)
        Cliente.save()
        messages.success(self.request, 'Cliente Creado')
        return redirect('cliente_update', pk=Cliente.cod)


class ClienteUpdate(ClienteView, UpdateView):
    form_class = ClienteForm

    def form_valid(self, form):
        cliente = form.save()
        messages.success(self.request, f'Cliente "{cliente}" Actualizada')
        return redirect('cliente_landing')


class ClienteDelete(ClienteView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Cliente eliminado')
        return reverse('cliente_landing')


# ==========================       COMPROBANTE DE INGRESOS     ==========================

class IngresoView(LoginRequiredMixin):
    model = Ingreso

    def get_queryset(self):
        # return Ingreso.objects.all()  // cuando use mi propia tabla user
        return Ingreso.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class IngresoList(IngresoView, ListView):
    paginate_by = 5


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ('cod_proveedor', 'cod_almacen', 'cod_usuario')


class IngresoCreate(IngresoView, CreateView):
    form_class = IngresoForm

    def form_valid(self, form):
        Ingreso = form.save(commit=False)
        Ingreso.cod_usuario = self.request.user
        Ingreso.save()
        messages.success(self.request, 'Ingreso Creada')
        return redirect('ingreso_update', pk=Ingreso.nro)


class IngresoUpdate(IngresoView, UpdateView):
    form_class = IngresoForm

    def form_valid(self, form):
        ingreso = form.save()
        messages.success(self.request, f'Ingreso "{ingreso}" Actualizada')
        return redirect('ingreso_landing')


class IngresoDelete(IngresoView, DeleteView):
    def get_sucess_url(self):
        return reverse('ingreso_landing')


class IngresoDelete(IngresoView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Ingreso eliminada')
        return reverse('ingreso_landing')


# ============================       COMPROBANTE DE SALIDAS     ==========================

class SalidaView(LoginRequiredMixin):
    model = Salida

    def get_queryset(self):
        # return Salida.objects.all()  // cuando use mi propia tabla user
        return Salida.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class SalidaList(SalidaView, ListView):
    paginate_by = 5


class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ('cod_almacen', 'cod_usuario', 'cod_cliente', 'fecha_entrega', 'tipo', 'tipo_cambio',)


class SalidaCreate(SalidaView, CreateView):
    form_class = SalidaForm

    def form_valid(self, form):
        Salida = form.save(commit=False)
        Salida.cod_usuario = self.request.user

        Salida.save()
        messages.success(self.request, 'Salida Creada')
        return redirect('salida_update', pk=Salida.nro)


class SalidaUpdate(SalidaView, UpdateView):
    form_class = SalidaForm

    def form_valid(self, form):
        salida = form.save()
        messages.success(self.request, f'Salida "{salida}" Actualizada')
        return redirect('salida_landing')


class SalidaDelete(SalidaView, DeleteView):
    def get_sucess_url(self):
        return reverse('salida_landing')


class SalidaDelete(SalidaView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Salida eliminada')
        return reverse('salida_landing')


# ============================       COMPROBANTE DE TRASPASO     ==========================

class TraspasoView(LoginRequiredMixin):
    model = Traspaso

    def get_queryset(self):
        # return Traspaso.objects.all()  // cuando use mi propia tabla user
        return Traspaso.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class TraspasoList(TraspasoView, ListView):
    paginate_by = 5


class TraspasoForm(forms.ModelForm):
    class Meta:
        model = Traspaso
        fields = ('cod_almacen_origen', 'cod_almacen_destino')


''''
    def clean_cod_almacen_origen(self):
        value1 = self.cleaned_data['cod_almacen_origen']
        value2 = self.cleaned_data['cod_almacen_destino']
        if value1 == value2:
            raise ValidationError("El Traspaso no puede realizarse entre el mismo almacen")
        return value1

'''


class TraspasoCreate(TraspasoView, CreateView):
    form_class = TraspasoForm

    def form_valid(self, form):
        Traspaso = form.save(commit=False)
        Traspaso.cod_usuario = self.request.user
        Traspaso.save()
        messages.success(self.request, 'Traspaso Creada')
        return redirect('traspaso_update', pk=Traspaso.nro)


class TraspasoUpdate(TraspasoView, UpdateView):
    form_class = TraspasoForm

    def form_valid(self, form):
        traspaso = form.save()
        messages.success(self.request, f'Traspaso "{traspaso}" Actualizada')
        return redirect('traspaso_landing')


class TraspasoDelete(TraspasoView, DeleteView):
    def get_sucess_url(self):
        return reverse('traspaso_landing')


class TraspasoDelete(TraspasoView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Traspaso eliminada')
        return reverse('traspaso_landing')


# ============================     METODOLOGIA ABC     ==========================


def abc(request):
    id_almacen = 1
    if request.method == 'POST':
        id_almacen = request.POST['cod_almacen']
    lista_almacen = Almacen.objects.all().order_by('cod')

    if id_almacen != 'todos':
        lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by(
            "cod_producto__costo").reverse().annotate(
            Costo_Unitario=F("cod_producto__costo"), Producto_Nombre=F("cod_producto__nombre"),
            Almacen_Nombre=F("cod_almacen__nombre"), total=Sum(
                F('cod_producto__costo') * F('cantidad'), output_field=FloatField()))

        Total_Inversion = lista_ordenado.all().aggregate(
            total_inversion=Sum(F('cantidad') * F('Costo_Unitario'), output_field=FloatField()))
        Nombre_Almacen = lista_ordenado[0].Almacen_Nombre
        # raise Exception(lista_ordenado.values())

        Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

        tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
        tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
        tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
        ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
        ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
        ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

        Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        # res_lista_total_b = [] //Opcion de cesar para facilitar? ¿Analizarlo....

        Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        context = {'objecto_lista': lista_ordenado.values(), 'listaA': ListaTipoA.values(),
                   'listaB': ListaTipoB.values(),
                   'listaC': ListaTipoC.values(), 'listaTotalA': Lista_Total_A, 'listaTotalB': Lista_Total_B,
                   'listaTotalC': Lista_Total_C, 'totalProductos': Cantidad_Productos,
                   'totalInversion': Total_Inversion,
                   'Nombre_Almacen': Nombre_Almacen, 'lista_almacen': lista_almacen}

        return render(request, 'abc/abc.html', context)
    else:
        article_group = []
        # ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate()
        ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate(total=Count('cod_producto_id'))
        for almacen in ListaAlmacenes:
            id_almacen = almacen['cod_almacen_id']

            lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by(
                "cod_producto__costo").reverse().annotate(
                Costo_Unitario=F("cod_producto__costo"), Producto_Nombre=F("cod_producto__nombre"),
                Almacen_Nombre=F("cod_almacen__nombre"), total=Sum(
                    F('cod_producto__costo') * F('cantidad'), output_field=FloatField()))

            Total_Inversion = lista_ordenado.all().aggregate(
                total_inversion=Sum(F('cantidad') * F('Costo_Unitario'), output_field=FloatField()))
            Nombre_Almacen = lista_ordenado[0].Almacen_Nombre
            Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

            tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
            tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
            tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
            ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
            ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
            ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

            Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            article_group.append(
                {'Almacen': Nombre_Almacen, 'listaA': Lista_Total_A, 'listaB': Lista_Total_B, 'listaC': Lista_Total_C,
                 'Total_Inversion': Total_Inversion, 'Cantidad_Productos': Cantidad_Productos})

        contexto = {'article_group': article_group, 'lista_almacen': lista_almacen}
        return render(request, 'abc/almacenes.html', contexto)


def abc_valor_total(request):
    id_almacen = 1
    if request.method == 'POST':
        id_almacen = request.POST['cod_almacen']
    lista_almacen = Almacen.objects.all().order_by('cod')

    if id_almacen != 'todos':
        lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by("total").reverse().annotate(
            Costo_Unitario=F("cod_producto__costo"), Producto_Nombre=F("cod_producto__nombre"),
            Almacen_Nombre=F("cod_almacen__nombre"), total=Sum(
                F('cod_producto__costo') * F('cantidad'), output_field=FloatField()))

        Total_Inversion = lista_ordenado.all().aggregate(
            total_inversion=Sum(F('cantidad') * F('Costo_Unitario'), output_field=FloatField()))
        Nombre_Almacen = lista_ordenado[0].Almacen_Nombre
        Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

        tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
        tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
        tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
        ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
        ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
        ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

        Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        # res_lista_total_b = [] //Opcion de cesar para facilitar? ¿Analizarlo....

        Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        context = {'objecto_lista': lista_ordenado.values(), 'listaA': ListaTipoA.values(),
                   'listaB': ListaTipoB.values(),
                   'listaC': ListaTipoC.values(), 'listaTotalA': Lista_Total_A, 'listaTotalB': Lista_Total_B,
                   'listaTotalC': Lista_Total_C, 'totalProductos': Cantidad_Productos,
                   'totalInversion': Total_Inversion,
                   'Nombre_Almacen': Nombre_Almacen, 'lista_almacen': lista_almacen}

        return render(request, 'abc/valor.html', context)
    else:
        article_group = []
        ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate(total=Count('cod_producto_id'))
        for almacen in ListaAlmacenes:
            id_almacen = almacen['cod_almacen_id']

            lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by("total").reverse().annotate(
                Costo_Unitario=F("cod_producto__costo"), Producto_Nombre=F("cod_producto__nombre"),
                Almacen_Nombre=F("cod_almacen__nombre"), total=Sum(
                    F('cod_producto__costo') * F('cantidad'), output_field=FloatField()))

            Total_Inversion = lista_ordenado.all().aggregate(
                total_inversion=Sum(F('cantidad') * F('Costo_Unitario'), output_field=FloatField()))
            Nombre_Almacen = lista_ordenado[0].Almacen_Nombre
            Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

            tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
            tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
            tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
            ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
            ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
            ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

            Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       PorcentajeInversion=Sum('total') / Total_Inversion[
                                                           'total_inversion'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            article_group.append(
                {'Almacen': Nombre_Almacen, 'listaA': Lista_Total_A, 'listaB': Lista_Total_B, 'listaC': Lista_Total_C,
                 'Total_Inversion': Total_Inversion, 'Cantidad_Productos': Cantidad_Productos})

        contexto = {'article_group': article_group, 'lista_almacen': lista_almacen}
        return render(request, 'abc/valor_almacenes.html', contexto)


def abc_almacen(request):
    article_group = []
    # ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate()
    ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate(total=Count('cod_producto_id'))
    for almacen in ListaAlmacenes:
        id_almacen = almacen['cod_almacen_id']

        lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by(
            "cod_producto__costo").reverse().annotate(
            Costo_Unitario=F("cod_producto__costo"), Producto_Nombre=F("cod_producto__nombre"),
            Almacen_Nombre=F("cod_almacen__nombre"), total=Sum(
                F('cod_producto__costo') * F('cantidad'), output_field=FloatField()))

        Total_Inversion = lista_ordenado.all().aggregate(
            total_inversion=Sum(F('cantidad') * F('Costo_Unitario'), output_field=FloatField()))
        Nombre_Almacen = lista_ordenado[0].Almacen_Nombre
        Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

        tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
        tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
        tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
        ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
        ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
        ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

        Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   PorcentajeInversion=Sum('total') / Total_Inversion[
                                                       'total_inversion'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        article_group.append(
            {'Almacen': Nombre_Almacen, 'listaA': Lista_Total_A, 'listaB': Lista_Total_B, 'listaC': Lista_Total_C,
             'Total_Inversion': Total_Inversion, 'Cantidad_Productos': Cantidad_Productos})

    contexto = {'article_group': article_group}
    return render(request, 'abc/almacenes.html', contexto)


def abc_utilidad(request):
    id_almacen = 1
    if request.method == 'POST':
        id_almacen = request.POST['cod_almacen']
    lista_almacen = Almacen.objects.all().order_by('cod')

    if id_almacen != 'todos':
        lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by("Utilidad").reverse().annotate(
            Costo_Unitario=F("cod_producto__costo"),
            Precio_Unitario=F("cod_producto__precio"),
            Producto_Nombre=F("cod_producto__nombre"),
            Almacen_Nombre=F("cod_almacen__nombre"),
            Utilidad=F('cod_producto__precio') - F('cod_producto__costo'),
            total=Cast(F('cod_producto__precio') - F('cod_producto__costo'), FloatField()) * Cast(F('cantidad'),
                                                                                                  FloatField()))

        Total_Utilidad = lista_ordenado.all().aggregate(Total_Utilidad_=Sum(F('Utilidad')))
        Nombre_Almacen = lista_ordenado[0].Almacen_Nombre

        Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

        tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
        tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
        tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
        ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
        ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
        ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

        Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'),
                                                   Utilidades=Sum('Utilidad'),
                                                   PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                       'Total_Utilidad_'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   Utilidades=Sum('Utilidad'),
                                                   PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                       'Total_Utilidad_'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                   Utilidades=Sum('Utilidad'),
                                                   PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                       'Total_Utilidad_'] * 100,
                                                   PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                           FloatField()) / Cast(
                                                       Cantidad_Productos['Cantidad'], FloatField()) * 100)

        context = {'objecto_lista': lista_ordenado.values(), 'listaA': ListaTipoA.values(),
                   'listaB': ListaTipoB.values(),
                   'listaC': ListaTipoC.values(), 'listaTotalA': Lista_Total_A, 'listaTotalB': Lista_Total_B,
                   'listaTotalC': Lista_Total_C, 'totalProductos': Cantidad_Productos, 'totalUtilidad': Total_Utilidad,
                   'Nombre_Almacen': Nombre_Almacen, 'lista_almacen': lista_almacen}

        return render(request, 'abc/utilidad.html', context)

    else:
        article_group = []
        ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate(total=Count('cod_producto_id'))
        for almacen in ListaAlmacenes:
            id_almacen = almacen['cod_almacen_id']

            lista_ordenado = Stock.objects.filter(cod_almacen=id_almacen).order_by("Utilidad").reverse().annotate(
                Costo_Unitario=F("cod_producto__costo"),
                Precio_Unitario=F("cod_producto__precio"),
                Producto_Nombre=F("cod_producto__nombre"),
                Almacen_Nombre=F("cod_almacen__nombre"),
                Utilidad=F('cod_producto__precio') - F('cod_producto__costo'),
                total=Cast(F('cod_producto__precio') - F('cod_producto__costo'), FloatField()) * Cast(F('cantidad'),
                                                                                                      FloatField()))

            Total_Utilidad = lista_ordenado.all().aggregate(Total_Utilidad_=Sum(F('Utilidad')))
            Nombre_Almacen = lista_ordenado[0].Almacen_Nombre

            Cantidad_Productos = lista_ordenado.aggregate(Cantidad=Count('*'))

            tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
            tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
            tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)
            ListaTipoA = lista_ordenado.annotate(Cantidad=Count('*'))[:tipoa]
            ListaTipoB = lista_ordenado[tipoa:tipoa + tipob]
            ListaTipoC = lista_ordenado[tipoa + tipob:tipoa + tipob + tipoc]

            Lista_Total_A = ListaTipoA.all().aggregate(Productos=Count('cod_producto_id'),
                                                       Utilidades=Sum('Utilidad'),
                                                       PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                           'Total_Utilidad_'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_B = ListaTipoB.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       Utilidades=Sum('Utilidad'),
                                                       PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                           'Total_Utilidad_'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)

            Lista_Total_C = ListaTipoC.all().aggregate(Productos=Count('cod_producto_id'), Inversion=Sum('total'),
                                                       Utilidades=Sum('Utilidad'),
                                                       PorcentajeUtilidad=Sum('Utilidad') / Total_Utilidad[
                                                           'Total_Utilidad_'] * 100,
                                                       PorcentajeProducto=Cast(Count('cod_producto_id'),
                                                                               FloatField()) / Cast(
                                                           Cantidad_Productos['Cantidad'], FloatField()) * 100)
            article_group.append(
                {'Almacen': Nombre_Almacen, 'listaA': Lista_Total_A, 'listaB': Lista_Total_B, 'listaC': Lista_Total_C,
                 'Total_Inversion': Total_Utilidad, 'Cantidad_Productos': Cantidad_Productos})

        contexto = {'article_group': article_group, 'lista_almacen': lista_almacen}

        return render(request, 'abc/utilidad_almacenes.html', contexto)


def abc_demanda(request):
    id_almacen = 1
    if request.method == 'POST':
        id_almacen = request.POST['cod_almacen']
    lista_almacen = Almacen.objects.all().order_by('cod')
    if id_almacen != 'todos':
        today = datetime.date.today()
        lista_ordenado = Detalle_Salida.objects.filter(cod_salida__cod_almacen=id_almacen).filter(
            cod_salida__fecha__year=today.year).order_by(
            "cod_producto_id").reverse().annotate(
            almacen=F("cod_salida__cod_almacen__nombre"), producto=F("cod_producto__nombre"),
            fecha=F("cod_salida__fecha"))

        nombre_almacen = lista_ordenado[0].almacen

        lista_demanda = lista_ordenado.all().values('cod_producto').annotate(
            nombre_almacen=F('cod_salida__cod_almacen__nombre'),
            nombre_producto=F('cod_producto__nombre'), costo_producto=F('cod_producto__costo'),
            precio_producto=Avg('precio'), cantidad_producto_vendida=Sum('cantidad'), monto_total_vendida=Sum('total')
        ).order_by('cantidad_producto_vendida')

        Cantidad_Productos = lista_demanda.aggregate(Cantidad=Count('*'))

        total_cantidad_producto_vendidos = lista_demanda.all().aggregate(
            cant_producto=Sum(F('cantidad_producto_vendida')))
        total_monto_producto_vendidos = lista_demanda.all().aggregate(monto_producto=Sum(F('monto_total_vendida')))

        tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
        tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
        tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)

        ListaTipoA = lista_demanda.annotate(Cantidad=Count('*'))[:tipoa]
        ListaTipoB = lista_demanda[tipoa:tipoa + tipob]
        ListaTipoC = lista_demanda[tipoa + tipob:tipoa + tipob + tipoc]

        Lista_Total_A = ListaTipoA.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                   cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                   porcentaje_cantidad_vendida=Cast(Sum('cantidad_producto_vendida'),
                                                                                    FloatField()) /
                                                                               Cast(total_cantidad_producto_vendidos[
                                                                                        'cant_producto'],
                                                                                    FloatField()) * 100,
                                                   monto_total=Sum('monto_total_vendida'),
                                                   porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                               FloatField()) / Cast(
                                                       total_monto_producto_vendidos['monto_producto'],
                                                       FloatField()) * 100)

        Lista_Total_B = ListaTipoB.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                   cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                   porcentaje_cantidad_vendida=Cast(Sum('cantidad_producto_vendida'),
                                                                                    FloatField()) /
                                                                               Cast(total_cantidad_producto_vendidos[
                                                                                        'cant_producto'],
                                                                                    FloatField()) * 100,
                                                   monto_total=Sum('monto_total_vendida'),
                                                   porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                               FloatField()) / Cast(
                                                       total_monto_producto_vendidos['monto_producto'],
                                                       FloatField()) * 100)

        Lista_Total_C = ListaTipoC.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                   cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                   porcentaje_cantidad_vendida=Cast(Sum('cantidad_producto_vendida'),
                                                                                    FloatField()) /
                                                                               Cast(total_cantidad_producto_vendidos[
                                                                                        'cant_producto'],
                                                                                    FloatField()) * 100,
                                                   monto_total=Sum('monto_total_vendida'),
                                                   porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                               FloatField()) / Cast(
                                                       total_monto_producto_vendidos['monto_producto'],
                                                       FloatField()) * 100)

        context = {'objecto_lista': lista_ordenado.values(), 'lista_demanda': lista_demanda, 'listaA': ListaTipoA,
                   'listaB': ListaTipoB, 'listaC': ListaTipoC, 'listaTotalA': Lista_Total_A,
                   'listaTotalB': Lista_Total_B,
                   'listaTotalC': Lista_Total_C,
                   'totalProductos': Cantidad_Productos,
                   'total_cantidad_productos_vendido': total_cantidad_producto_vendidos,
                   'total_monto_producto_vendidos': total_monto_producto_vendidos, 'nombre_almacen': nombre_almacen,
                   'lista_almacen': lista_almacen}

        return render(request, 'abc/demanda.html', context)

    else:
        article_group = []
        ListaAlmacenes = Stock.objects.values('cod_almacen_id').annotate(total=Count('cod_producto_id'))
        for almacen in ListaAlmacenes:
            id_almacen = almacen['cod_almacen_id']

            today = datetime.date.today()
            lista_ordenado = Detalle_Salida.objects.filter(cod_salida__cod_almacen=id_almacen).filter(
                cod_salida__fecha__year=today.year).order_by(
                "cod_producto_id").reverse().annotate(
                almacen=F("cod_salida__cod_almacen__nombre"), producto=F("cod_producto__nombre"),
                fecha=F("cod_salida__fecha"))

            nombre_almacen = lista_ordenado[0].almacen

            lista_demanda = lista_ordenado.all().values('cod_producto').annotate(
                nombre_almacen=F('cod_salida__cod_almacen__nombre'),
                nombre_producto=F('cod_producto__nombre'), costo_producto=F('cod_producto__costo'),
                precio_producto=Avg('precio'), cantidad_producto_vendida=Sum('cantidad'),
                monto_total_vendida=Sum('total')
            ).order_by('cantidad_producto_vendida')

            Cantidad_Productos = lista_demanda.aggregate(Cantidad=Count('*'))

            total_cantidad_producto_vendidos = lista_demanda.all().aggregate(
                cant_producto=Sum(F('cantidad_producto_vendida')))
            total_monto_producto_vendidos = lista_demanda.all().aggregate(monto_producto=Sum(F('monto_total_vendida')))

            tipoa = int(Cantidad_Productos['Cantidad'] * 0.15)
            tipob = int(Cantidad_Productos['Cantidad'] * 0.20)
            tipoc = Cantidad_Productos['Cantidad'] - (tipoa + tipob)

            ListaTipoA = lista_demanda.annotate(Cantidad=Count('*'))[:tipoa]
            ListaTipoB = lista_demanda[tipoa:tipoa + tipob]
            ListaTipoC = lista_demanda[tipoa + tipob:tipoa + tipob + tipoc]

            Lista_Total_A = ListaTipoA.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                       cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                       porcentaje_cantidad_vendida=Cast(
                                                           Sum('cantidad_producto_vendida'),
                                                           FloatField()) /
                                                                                   Cast(
                                                                                       total_cantidad_producto_vendidos[
                                                                                           'cant_producto'],
                                                                                       FloatField()) * 100,
                                                       monto_total=Sum('monto_total_vendida'),
                                                       porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                                   FloatField()) / Cast(
                                                           total_monto_producto_vendidos['monto_producto'],
                                                           FloatField()) * 100)

            Lista_Total_B = ListaTipoB.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                       cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                       porcentaje_cantidad_vendida=Cast(
                                                           Sum('cantidad_producto_vendida'),
                                                           FloatField()) /
                                                                                   Cast(
                                                                                       total_cantidad_producto_vendidos[
                                                                                           'cant_producto'],
                                                                                       FloatField()) * 100,
                                                       monto_total=Sum('monto_total_vendida'),
                                                       porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                                   FloatField()) / Cast(
                                                           total_monto_producto_vendidos['monto_producto'],
                                                           FloatField()) * 100)

            Lista_Total_C = ListaTipoC.all().aggregate(cantidad_productos=Count('cod_producto'),
                                                       cantidad_total_vendida=Sum('cantidad_producto_vendida'),
                                                       porcentaje_cantidad_vendida=Cast(
                                                           Sum('cantidad_producto_vendida'),
                                                           FloatField()) /
                                                                                   Cast(
                                                                                       total_cantidad_producto_vendidos[
                                                                                           'cant_producto'],
                                                                                       FloatField()) * 100,
                                                       monto_total=Sum('monto_total_vendida'),
                                                       porcentaje_monto_total=Cast(Sum('monto_total_vendida'),
                                                                                   FloatField()) / Cast(
                                                           total_monto_producto_vendidos['monto_producto'],
                                                           FloatField()) * 100)

            article_group.append(
                {'Almacen': nombre_almacen, 'listaA': Lista_Total_A, 'listaB': Lista_Total_B, 'listaC': Lista_Total_C,
                 'total_cantidad_productos_vendido': total_cantidad_producto_vendidos,
                 'total_monto_producto_vendidos': total_monto_producto_vendidos, 'nombre_almacen': nombre_almacen,
                 'Cantidad_Productos': Cantidad_Productos})

        contexto = {'article_group': article_group, 'lista_almacen': lista_almacen}

        return render(request, 'abc/demanda_almacenes.html', contexto)


def landing_view(request):
    proveedores = Proveedor.objects.all().count()
    clientes = Cliente.objects.all().count()
    productos = Producto.objects.all().count()
    today = datetime.date.today()
    ventas = Detalle_Salida.objects.filter(cod_salida__fecha__year=today.year).aggregate(
        ventas_anual=Cast(Sum('total'), IntegerField()))
    compras = Detalle_Ingreso.objects.filter(cod_ingreso__fecha__year=today.year).aggregate(
        compra_anual=Cast(Sum('total'), IntegerField()))

    contexto = {'proveedores': proveedores, 'clientes': clientes, 'productos': productos, 'ventas': ventas,
                'compras': compras}
    return render(request, 'landing.html', contexto)
