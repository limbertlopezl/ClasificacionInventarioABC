from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.conf import settings
from .models import Almacen, Categoria, Producto, Stock
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from io import BytesIO
from django.core.exceptions import ValidationError


# =========================     VISTA ALMACEN       =========================================

class AlmacenView(LoginRequiredMixin):
    model = Almacen

    def get_queryset(self):
        return Almacen.objects.all()
        # return Proveedor.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class AlmacenList(AlmacenView, ListView):
    paginate_by = 5


class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ('nombre', 'direccion')


class AlmacenCreate(AlmacenView, CreateView):
    form_class = AlmacenForm

    def form_valid(self, form):
        Almacen = form.save(commit=False)
        Almacen.save()
        messages.success(self.request, 'Almacen Creado')
        return redirect('almacen_update', pk=Almacen.cod)


class AlmacenUpdate(AlmacenView, UpdateView):
    form_class = AlmacenForm

    def form_valid(self, form):
        almacen = form.save()
        messages.success(self.request, f'Almacen "{almacen}" Actualizada')
        return redirect('almacen_landing')


class AlmacenDelete(AlmacenView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Almacen eliminado')
        return reverse('almacen_landing')


# =========================     VISTA CATEGORIA   =========================================

class CategoriaView(LoginRequiredMixin):
    model = Categoria

    def get_queryset(self):
        return Categoria.objects.all()
        # return Proveedor.objects.filter(cod_usuario=self.request.user)  # usa la tabla de user de django


class CategoriaList(CategoriaView, ListView):
    paginate_by = 5


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ('descripcion', 'estado')


class CategoriaCreate(CategoriaView, CreateView):
    form_class = CategoriaForm

    def form_valid(self, form):
        Categoria = form.save(commit=False)
        Categoria.save()
        messages.success(self.request, 'Categoria Creado')
        return redirect('categoria_update', pk=Categoria.cod)


class CategoriaUpdate(CategoriaView, UpdateView):
    form_class = CategoriaForm

    def form_valid(self, form):
        categoria = form.save()
        messages.success(self.request, f'Categoria "{categoria}" Actualizada')
        return redirect('categoria_landing')


class CategoriaDelete(CategoriaView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Categoria eliminado')
        return reverse('categoria_landing')


# =========================     VISTA PRODUCTO  =========================================

class ProductoView(LoginRequiredMixin):
    model = Producto

    def get_queryset(self):
        return Producto.objects.all()


class ProductoList(ProductoView, ListView):
    paginate_by = 5


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('nombre', 'foto', 'marca', 'costo', 'precio', 'cod_categoria')


class ProductoCreate(ProductoView, CreateView):
    form_class = ProductoForm

    def form_valid(self, form):
        Producto = form.save(commit=False)
        Producto.save()
        messages.success(self.request, 'Producto Creado')
        return redirect('producto_update', pk=Producto.cod)


class ProductoUpdate(ProductoView, UpdateView):
    form_class = ProductoForm

    def form_valid(self, form):
        producto = form.save()
        messages.success(self.request, f'Producto "{producto}" Actualizada')
        return redirect('producto_landing')


class ProductoDelete(ProductoView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Producto eliminado')
        return reverse('producto_landing')


# =========================     VISTA STOCK  =========================================

class StockView(LoginRequiredMixin):
    model = Stock

    def get_queryset(self):
        return Stock.objects.all()


class StockList(StockView, ListView):
    paginate_by = 7


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('id', 'cod_almacen', 'cod_producto', 'cantidad', 'estado')


class StockCreate(StockView, CreateView):
    form_class = StockForm

    def form_valid(self, form):
        Stock = form.save(commit=False)
        Stock.save()
        messages.success(self.request, 'Stock Creado')
        return redirect('stock_update', pk=Stock.id)


class StockUpdate(StockView, UpdateView):
    form_class = StockForm

    def form_valid(self, form):
        stock = form.save()
        messages.success(self.request, f'Stock "{stock}" Actualizada')
        return redirect('stock_landing')


class StockDelete(StockView, DeleteView):
    def get_success_url(self):
        messages.warning(self.request, 'Stock eliminado')
        return reverse('stock_landing')


# =================================      REPORTES ==============================
def report_almacen(request):
    print("Genero el PDF")
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Almacenes.pdf"  # llamado clientes
    # la linea 26 es por si deseas descargar el pdf a tu computadora
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )

    clientes = []
    styles = getSampleStyleSheet()
    header0 = Paragraph("Lomerco", styles['Heading1'])
    header = Paragraph("Listado de Almacenes", styles['Heading1'])

    clientes.append(header0)
    clientes.append(header)
    headings = ('ID', 'NOMBRE', 'DIRECCION', 'ESTADO')
    allclientes = [(p.cod, p.nombre, p.direccion, p.estado) for p in Almacen.objects.all()]
    print(allclientes)

    t = Table([headings] + allclientes)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.dodgerblue),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))

    clientes.append(t)
    doc.build(clientes)
    response.write(buff.getvalue())
    buff.close()
    return response


def report_stock(request):
    print("Genero el PDF")
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Stock.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )

    clientes = []
    styles = getSampleStyleSheet()
    header0 = Paragraph("Lomerco", styles['Heading1'])
    header = Paragraph("Listado de Stock", styles['Heading1'])

    clientes.append(header0)
    clientes.append(header)
    headings = ('ID', 'ALMACEN', 'PRODUCTO', 'CANTIDAD', 'ESTADO')
    all_stock = [(p.id, p.cod_almacen, p.cod_producto, p.cantidad, p.estado) for p in Stock.objects.all()]
    print(all_stock)

    t = Table([headings] + all_stock)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (4, -1), 1, colors.dodgerblue),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))

    clientes.append(t)
    doc.build(clientes)
    response.write(buff.getvalue())
    buff.close()
    return response


def report_producto(request):
    print("Genero el PDF")
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Producto.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )

    clientes = []
    styles = getSampleStyleSheet()
    header0 = Paragraph("Lomerco", styles['Heading1'])
    header = Paragraph("Listado de Producto", styles['Heading1'])

    clientes.append(header0)
    clientes.append(header)
    headings = ('COD', 'NOMBRE', 'MARCA', 'PROVEEDOR', 'COSTO', 'PRECIO', 'CATEGORIA', 'ESTADO')
    all_producto = [(p.cod, p.nombre, p.marca, p.cod_proveedor, p.costo, p.precio, p.cod_categoria, p.estado) for p in
                    Producto.objects.all()]
    print(all_producto)

    t = Table([headings] + all_producto)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (7, -1), 1, colors.dodgerblue),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))

    clientes.append(t)
    doc.build(clientes)
    response.write(buff.getvalue())
    buff.close()
    return response
