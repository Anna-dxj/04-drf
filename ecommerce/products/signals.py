from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Product
from orders.models import Order, OrderDetail
from django.db import transaction

# @receiver(post_save, sender=OrderDetail)
@receiver(pre_save, sender=OrderDetail)
def update_product_stock(sender, instance, **kwargs):

    product = instance.product
    new_quantity = instance.quantity

    print(f'stock old: {product.stock}')
    # if instance.pk, updates stock based off existing cart item
    if instance.pk:
        old_quantity=sender.objects.get(pk=instance.pk).quantity

        delta_quantity = new_quantity - old_quantity

        # checks if ultimately adding/removing stock
        if delta_quantity > 0:
            product.stock -= delta_quantity
        else:
            product.stock -= abs(delta_quantity)
    # otherwise simple stock decrement
    else:
        product.stock -= new_quantity
    
    product.save()
    print('new stock: ', product.stock)

@receiver(post_delete, sender=OrderDetail)
def restore_product_stock(sender, instance, **kwargs):
    product = instance.product
    print('before: ', product.stock)
    product.stock += instance.quantity 
    product.save()
    print('restore product to: ', product.stock)