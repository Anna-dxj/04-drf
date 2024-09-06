from django.urls import path
from .views import AllProductsView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductByVendorList, VendorOwnProductList, ProductByCategory, LowStockProductsView, OutOfStockProductsView, BestSeillingByVendorProductsView

from .decorators import vendor_required

urlpatterns = [
    path('', AllProductsView.as_view(), name='all_products'),
    path('category/<int:category_id>/', ProductByCategory.as_view(), name='product_by_category'),
    path('<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('vendor/all-products/', VendorOwnProductList.as_view(), name='company_products'),
    path('vendor/low-stock-products/', vendor_required(LowStockProductsView.as_view()), name='company_low_stocks'),
    path('vendor/out-of-stock-products/', vendor_required(OutOfStockProductsView.as_view()), name='company_out_of_stock'),
    path('vendor/best-selling-products/', vendor_required(BestSeillingByVendorProductsView.as_view()), name='company_best_selling'),
    path('by-vendor/<int:vendor_id>/', ProductByVendorList.as_view(), name='product_by_vendor'),
    path('create/', vendor_required(ProductCreateView.as_view()), name='product_create'),
    path('<int:product_id>/update/', vendor_required(ProductUpdateView.as_view()), name='product_update'),
    path('<int:product_id>/delete/', vendor_required(ProductDeleteView.as_view()), name='product_delete'),
]