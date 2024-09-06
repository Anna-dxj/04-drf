from .models import Customer, Vendor
from products.models import Category

def customer_processor(request):
    customer=None
    vendor=None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.is_vendor:
                vendor = Vendor.objects.get(profile=customer)
        except Customer.DoesNotExist:
            customer = None
        except Vendor.DoesNotExist:
            vendor=None
    return {'customer': customer, 'current_vendor': vendor}
