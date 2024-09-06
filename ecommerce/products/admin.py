from django.contrib import admin
from .models import Category, Product
from orders.models import OrderDetail
from django.db.models import Sum, F


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_num')
    list_display_links = ('name',)
    search_fields = ('name',)

    def product_num(self, obj):
        products = Product.objects.filter(category=obj).count()

        return products or 0
    
    product_num.short_description = 'Num of Products'

class ProductCategory(admin.ModelAdmin):
    list_display=('name', 'price', 'stock', 'products_sold', 'total_revenue_made', 'current_value', 'vendor_name', 'category_name',)
    list_filter = ('vendor__company_name', 'category__name')
    search_fields = ('name', 'description')
    ordering = ('name',)

    def vendor_name(self, obj):
        return obj.vendor.company_name
    
    vendor_name.short_description = 'Vendor'
    vendor_name.admin_order_field = 'vendor__company_name'

    def category_name(self, obj):
        categories = obj.category.all()

        if len(categories) > 1:
            return ', '.join(category.name for category in categories)
        else:
            return ''.join(category.name for category in categories)
    
    category_name.short_description = 'Categories'
    category_name.admin_order_field = 'category__name'

    def products_sold(self, obj):
        products = OrderDetail.objects.filter(product=obj).aggregate(
            total_sold = Sum('quantity')
        )

        return products['total_sold'] or 0
    
    products_sold.short_description = 'Units Sold'

    def total_revenue_made(self, obj):
        revenue = OrderDetail.objects.filter(product=obj).aggregate(
            total_revenue = Sum(F('quantity') * F('unit_price'))
        )

        return revenue['total_revenue'] or 0
    
    total_revenue_made.short_description = 'Total Revenue'

    def current_value(self, obj):
        value = obj.stock * obj.price

        return value or 0
    
    current_value.short_description = 'Total Current Value'

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductCategory)
