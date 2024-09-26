from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product,Category
from .forms import ProductForm, AddToCartForm
from users.models import Vendor, Customer
from django.db.models import Sum, F, FloatField, ExpressionWrapper
# from rest_framework import viewsets, status
# from .serializers import ProductSerializer, CategorySerializer
# from users.permissions import IsVendorOrReadOnly, IsAdminOrReadOnly
# from rest_framework.permissions import IsAdminUser, AllowAny
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.response import Response
# import logging 

# logger = logging.getLogger(__name__)

# # api viewset for category for product: 
# class ProductViewSet(viewsets.ModelViewSet):
#     """Viewset for products object. All read operations can be done by anyone, but a vendor is only able to create, update, delete their own products"""
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = [IsVendorOrReadOnly]

#     def handle_exception(self, exc):
#         if isinstance(exc, PermissionDenied):
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
#         return super().handle_exception(exc)
    
#     def perform_create(self, serializer):
#         vendor = Vendor.objects.get(profile__user=self.request.user)
#         serializer.save(vendor = vendor)
    
#     def perform_update(self, serializer):
#         product = self.get_object()
#         print('product: ', product)
#         if product.vendor.profile.user != self.request.user:
#             return PermissionDenied('You do not have permission to update this.')
#         serializer.save()
    
#     def perform_destroy(self, instance):
#         if instance.vendor.profile != self.request.user:
#             return Response({'detail': 'You do not have permission to delete this product.'}, status=status.HTTP_403_FORBIDDEN)
#         instance.delete()

# # api viewset for category
# class CategoryViewSet(viewsets.ModelViewSet):
#     """Viewset for categories object. All read operations can be done by anyone, but create, update, delete operations limited to admin users"""
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminOrReadOnly]

#     def handle_exception(self, exc):
#         if isinstance(exc, PermissionDenied):
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
#         return super().handle_exception(exc)


# view all products
class AllProductsView(ListView):
    """List all in-stock products and all categories. Public view. If a user is logged in, also lists top five most viewed products from current session, as well as suggested products based on categories they frequent"""
    model = Product
    template_name = 'products/all_products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')

        viewed_products = self.request.session.get('viewed_products', {})

        # sorts by values descending
        top_viewed = sorted(viewed_products.items(), key=lambda item: item[1], reverse=True)[:5]
        product_ids = [int(pid) for pid, count in top_viewed]
        print(top_viewed)

        if top_viewed: 
            top_products = Product.objects.filter(id__in=product_ids)
            top_products = sorted(top_products, key=lambda product: product_ids.index(product.id))
            print(top_products)
            context['top_viewed_products'] = top_products
        
        recently_viewed_id = self.request.session.get('recently_viewed_id', [])
        recently_viewed_products = Product.objects.filter(id__in=recently_viewed_id)

        categories = set()

        for product in recently_viewed_products:
            categories.update(product.category.values_list('id', flat=True))
        
        list(categories)[:3]
        
        # suggested_by_category = Products.objects.filter(category__in=categories).

        suggested_products = Product.objects.filter(
            category__in=categories
        ).annotate(
            total_units_sold=Sum('order_details__quantity')
        ).order_by('-total_units_sold')[:10]
        print(suggested_products)

        context['suggested_products'] = suggested_products
        return context
    def get_queryset(self):
        return Product.objects.filter(stock__gt=0).order_by('name')

# product detail
class ProductDetailView(DetailView):
    """Lists details of product, the form to add to cart, and product category. Public view"""
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
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        product = self.get_object()
        product_id = str(product.id)

        if 'viewed_products' not in request.session: 
            request.session['viewed_products'] = {}

        viewed_products = request.session['viewed_products']

        if product_id in viewed_products:
            viewed_products[product_id] += 1
        else:
            viewed_products[product_id] = 1

        if 'recently_viewed_id' not in request.session:
            # create queue 
            request.session['recently_viewed_id'] = []
        
        recently_viewed_id = request.session['recently_viewed_id']

        if product_id not in recently_viewed_id:
            recently_viewed_id.append(product_id)
            if len(recently_viewed_id) > 10:
                recently_viewed_id.pop(0)
            
            request.session['recently_viewed_id'] = recently_viewed_id
            
        
        request.session.modified = True

        return response

# product by category
class ProductByCategory(ListView):
    """List all products by category name, public view"""
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

# product by vendor 
class ProductByVendorList(ListView):
    """Lists all products by vendor, public view"""
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

# vendor can see their own products
class VendorOwnProductList(ListView):
    """Lists products by vendor. Vendor view"""
    model = Product
    template_name = 'products/company_products.html'
    context_object_name = 'products'
    paginate_by=20

    def get_queryset(self):
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        vendor = get_object_or_404(Vendor, profile=customer)

        return Product.objects.filter(vendor=vendor)

# create product view
class ProductCreateView(CreateView):
    """Creates products. Vendor view."""
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

# update product info 
class ProductUpdateView(UpdateView):
    """Update product info. Vendor view."""
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

# delete a product
class ProductDeleteView(DeleteView):
    """Deletes a product. Vendor view."""
    model = Product
    template_name='products/product_confirm_delete.html'
    success_url = reverse_lazy('company_products')
    pk_url_kwarg = 'product_id'

# all products with low stock for vendor
class LowStockProductsView(ListView):
    """Lists all low stock products. Vendor view."""
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

# all products with low stock for vendor 
class OutOfStockProductsView(ListView):
    """Lists all out of stock products. Vendor View."""
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

# all products by best selling for vendor 
class BestSeillingByVendorProductsView(ListView):
    """List all best-selling products. Vendor View."""
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
                F('order_details__quantity') * F('order_details__unit_price'), 
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
            total_sales=Sum('order_details__quantity')
        ).order_by('-total_sales')

        return queryset