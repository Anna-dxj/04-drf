from django.contrib import admin
from .models import Vendor, Customer, Shipping
from products.models import Product
from orders.models import OrderDetail, Order
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, FloatField


class VendorAdmin(admin.ModelAdmin):
    list_display=('company_name', 'total_products_sold', 'total_product_value', 'total_revenue',)
    list_display_links=('company_name',)
    search_fields = ('company_name', 'description',)
    ordering=('company_name',)
    
    def total_products_sold (self, obj):
        products_sold = OrderDetail.objects.filter(product__vendor=obj).aggregate(
            all_products_sold = Sum('quantity')
        )

        return products_sold['all_products_sold'] or 0
    
    total_products_sold.short_description = 'Total Products Sold'

    def total_product_value (self, obj):
        product_value = Product.objects.filter(vendor=obj).aggregate(
            total_value = Sum(F('price') * F('stock'))
        )

        return product_value['total_value'] or 0.00
    
    total_product_value.short_description = 'Total Product Value (Current)'

    def total_revenue (self, obj):
        revenue = OrderDetail.objects.filter(product__vendor=obj).aggregate(
            total_revenue = Sum(F('unit_price')*F('quantity'))
        )

        return revenue['total_revenue'] or 0.00
    
    total_revenue.short_description = 'Total Revenue'

class CustomerAdmin(admin.ModelAdmin):
    list_display=('user_email', 'user_name', 'total_paid', 'total_orders', 'total_unshipped', 'is_vendor')
    list_filter = ('is_vendor',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__email',)
    

    def user_email(self, obj):
        return obj.user.email
    
    user_email.admin_order_field = 'user__email'
    user_email.short_description = 'Email'
    
    def user_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    
    user_name.admin_order_field = 'user__full_name'
    user_name.short_description = 'Name'

    def total_paid(self, obj):
        payment = Order.objects.filter(customer=obj).aggregate(
            total_amount = Sum(
                ExpressionWrapper(
                    F('order_details__quantity') * F('order_details__unit_price'),
                    output_field=FloatField()
                )
            )
        )

        return payment['total_amount'] or 0
    
    total_paid.short_description = 'Total Paid'

    def total_orders(self, obj):
        orders = Order.objects.filter(customer=obj).count()

        return orders

    total_orders.short_description = 'Total Orders Made'

    def total_unshipped(self, obj):
        unshipped_orders = Order.objects.filter(
            customer=obj,
            is_shipped=False
        ).count()

        return unshipped_orders 
    
    total_unshipped.short_description = 'Unshipped Orders'

class ShippingAdmin(admin.ModelAdmin):
    list_display=('user_name', 'street_address', 'city', 'state_district', 'post_code', 'country')
    list_display_links=('user_name', 'street_address',)
    list_filter = ('city', 'state_district', 'country')
    search_fields = ('customer__user__first_name', 'customer__user__last_name', 'street_address', 'city', 'state_district', 'country')
    ordering = ('customer__user__last_name',)


    def user_name(self, obj):
        return f'{obj.customer.user.first_name} {obj.customer.user.last_name}'
    
    user_name.short_description = 'Name'
    

# Register your models here.
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Shipping, ShippingAdmin)