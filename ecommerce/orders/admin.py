from django.contrib import admin
from .models import Payment, Order, OrderDetail, SpecialShipping
from django.db.models import Sum, F
from django.utils.html import format_html


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'price', 'non_default_shipping_address', 'order_date', 'is_in_cart', 'is_shipped', 'shipped_date')
    list_filter = ('is_in_cart', 'is_shipped')
    search_fields = ('customer__user__first_name', 'customer__user__last_name')
    ordering=('-order_date',)

    def user_name(self, obj):
        return f'{obj.customer.user.first_name} {obj.customer.user.last_name}'
    
    user_name.admin_order_field = 'customer__user__full_name'
    user_name.short_description = 'Name'

    def price(self, obj):
        order = OrderDetail.objects.filter(order=obj).aggregate(
            total_price = Sum(F('quantity') * F('unit_price'))
        )

        return order['total_price']
    
    price.short_description = 'Total Cost'

    def non_default_shipping_address(self, obj):
        shipping = SpecialShipping.objects.filter(order=obj)

        if shipping:
            return format_html('<span style="color: red;">✗</span>')
        else:
            return format_html('<span style="color: green;">✓</span>')
    
    non_default_shipping_address.short_description = 'Default Shipping Address'

class OrderDetailAdmin(admin.ModelAdmin):
    list_display=('user_name', 'product_name', 'quantity', 'unit_price', 'order_date')
    search_fields = ('order__customer__user__first_name', 'order__customer__user__last_name', 'product__name')
    ordering = ('-order__order_date',)

    def user_name(self, obj):
        return f'{obj.order.customer.user.first_name} {obj.order.customer.user.last_name}'
    
    user_name.admin_order_field = 'order__customer__user__full_name'
    user_name.short_description = 'Name'

    def order_date(self, obj):
        return obj.order.order_date
    
    order_date.admin_order_field = 'order__order_date'
    order_date.short_description = 'Order Date' 

    def product_name(self, obj):
        return obj.product.name
    
    product_name.admin_order_field = 'product__name'
    product_name.short_description = 'Product'


class PaymentAdmin(admin.ModelAdmin):
    list_display=('payment_method_display', 'total_payment_methods')
    ordering = ('method',)

    def payment_method_display(self, obj):
        return obj.method
    
    payment_method_display.short_description = 'Method'

    def total_payment_methods (self, obj):
        payment_methods = Order.objects.filter(payment=obj).aggregate(
            total_payments = Sum('payment')
        )
    
        return payment_methods['total_payments'] or 0

    total_payment_methods.short_description = 'Times Used'

class SpecialShippingAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'account_name', 'order_status', 'order_status_date', 'shipping_address')
    list_filter = ('order__is_shipped',)
    search_fields = ('recipient_first_name','recipient_last_name', 'specialshipping__order__customer__user__first_name', 'specialshipping__order__customer__user__last_name')
    ordering = ('recipient_last_name',)
    def account_name(self, obj):
        user = obj.order.customer.user
        return f'{user.first_name} {user.last_name}'
    
    account_name.short_description = 'Ordered By'

    def order_status(self, obj):
        is_shipped = obj.order.is_shipped

        if is_shipped:
            return format_html('<span style="color: green;">✓</span>')
        else:
            return format_html('<span style="color: red;">✗</span>')
    
    order_status.short_description = 'Shipping Status'
    order_status.admin_order_field = 'order__is_shipped'

    def order_status_date(self, obj):
        shipped_date = obj.order.shipped_date

        return shipped_date
    
    order_status_date.short_description = 'Shipping Status Date'

    def recipient_name(self, obj):
        return f'{obj.recipient_first_name} {obj.recipient_last_name}'
    
    recipient_name.short_description = 'ship to'

    def shipping_address(self, obj):
        return f'{obj.street_address} {obj.city}, {obj.state_district} {obj.post_code} {obj.country}'
    
    shipping_address.short_description = 'Shipping Address'

# Register your models here.
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(SpecialShipping, SpecialShippingAdmin)