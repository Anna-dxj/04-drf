from django.db import models
from django.utils import timezone
from products.models import Product
from users.models import Customer


class Payment(models.Model):
    method = models.CharField(max_length=100)

    def __str__(self):
        return self.method


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(blank=True, null=True)
    is_in_cart = models.BooleanField(default=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    is_shipped = models.BooleanField(default=False)
    payment = models.ManyToManyField(Payment, related_name='orders', blank=True)

    def __str__(self):
        return f'{self.customer} - {self.order_date}'

    def make_order(self, payment=None):
        self.order_date = timezone.now()
        self.is_in_cart = False
        self.save()
        if payment: 
            self.payment.add(payment)

    def ship(self):
        self.shipped_date = timezone.now()
        self.is_shipped = True
        self.save()

class SpecialShipping(models.Model):
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, related_name='specialshipping', null=True)
    recipient_first_name = models.CharField(max_length=50)
    recipient_last_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state_district = models.CharField(max_length=100)
    post_code = models.CharField(max_length=50)
    country = models.CharField(max_length=100)

class OrderDetail(models.Model):
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_details')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')

    def __str__(self):
        return f'{self.product}({self.order}) x{self.quantity}'