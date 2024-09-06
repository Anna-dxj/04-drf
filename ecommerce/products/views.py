from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product,Category
from .forms import ProductForm, AddToCartForm
from users.models import Vendor, Customer
from django.db.models import Sum, F, FloatField, ExpressionWrapper


# Create your views here.
# add a product & add product to category (form)
# edit product & category (form)
# view all products
# view products by category (if time)
# view specific product 

class AllProductsView(ListView):
    model = Product
    template_name = 'products/all_products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        return context
    def get_queryset(self):
        return Product.objects.filter(stock__gt=0).order_by('name')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['add_to_cart_form'] = AddToCartForm()
        product = self.get_object()
        context['categories'] = product.category.all()
        context['all_categories'] = Category.objects.all().order_by('name')
        return context 

class ProductByCategory(ListView):
    model = Product
    template_name = 'products/product_by_category.html'
    context_object_name = 'products'
    pk_url_kwarg = 'category_id'
    paginate_by=20

    def get_queryset(self):
        category_id = self.kwargs.get(self.pk_url_kwarg)
        category = get_object_or_404(Category, id=category_id)
        return Product.objects.filter(category=category)
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        category_id = self.kwargs.get(self.pk_url_kwarg)
        category = get_object_or_404(Category, id=category_id)
        context['categories'] = Category.objects.all().order_by('name')
        context['current_category'] = category
        return context 

class ProductByVendorList(ListView):
    model = Product
    template_name = 'products/product_by_vendor.html'
    context_object_name = 'products'
    paginate_by=20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor_id = self.kwargs.get('vendor_id')
        context['vendor'] = get_object_or_404(Vendor, id=vendor_id)
        context['categories'] = Category.objects.all().order_by('name')

        return context
    
    def get_queryset(self):
        vendor_id = self.kwargs.get('vendor_id')
        return Product.objects.filter(vendor_id=vendor_id)

class VendorOwnProductList(ListView):
    model = Product
    template_name = 'products/company_products.html'
    context_object_name = 'products'
    paginate_by=20

    def get_queryset(self):
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        return Product.objects.filter(vendor=vendor)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create_form.html'
    success_url = reverse_lazy('all_products')

    def form_valid(self, form):
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        form.instance.vendor = vendor

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['type'] = 'create product'

        return context 

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price', 'stock', 'description']
    template_name = 'products/product_create_form.html'
    success_url = reverse_lazy('company_products')
    pk_url_kwarg = 'product_id'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        product_id = self.kwargs.get(self.pk_url_kwarg)
        product = get_object_or_404(Product, id=product_id)
        context['type'] = 'update product'
        context['product'] = product

        return context 

class ProductDeleteView(DeleteView):
    model = Product
    template_name='products/product_confirm_delete.html'
    success_url = reverse_lazy('company_products')
    pk_url_kwarg = 'product_id'

class LowStockProductsView(ListView):
    model = Product
    template_name = 'products/company_products.html'
    context_object_name = 'products'
    paginate_by=20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)
        context['vendor'] = vendor
        context['type'] = 'low stock'

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        queryset = Product.objects.filter(
            vendor=vendor,
            stock__lte=50,
            stock__gt=0            
        ).order_by('-stock')

        return queryset

class OutOfStockProductsView(ListView):
    model = Product
    template_name = 'products/company_products.html'
    context_object_name = 'products'
    paginate_by=20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)
        context['vendor'] = vendor
        context['type'] = 'no stock'

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        queryset = Product.objects.filter(
            vendor=vendor,
            stock=0            
        ).order_by('-name')

        return queryset

class BestSeillingByVendorProductsView(ListView):
    model = Product
    template_name = 'products/company_products.html'
    context_object_name = 'products'
    paginate_by=20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)
        context['vendor'] = vendor
        context['type'] = 'best selling'
        total_amount = Product.objects.filter(vendor=vendor).annotate(
            total_amount= ExpressionWrapper(
                F('OrderDetails__quantity') * F('OrderDetails__unit_price'), 
                output_field = FloatField()
            )
        ).aggregate(
            total_sum = Sum('total_amount')
        )

        context['total_revenue'] = total_amount['total_sum'] or 0

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        queryset = Product.objects.filter(vendor=vendor).annotate(
            total_sales=Sum('OrderDetails__quantity')
        ).order_by('-total_sales')

        return queryset