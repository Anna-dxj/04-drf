from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    is_vendor = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
            return self.user.username
        
class Vendor(models.Model):
    profile = models.OneToOneField(Customer, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    customer_service_email = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name

class Shipping(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='shipping')
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state_district = models.CharField(max_length=100)
    post_code = models.CharField(max_length=50)
    country = models.CharField(max_length=100)

    def __str__(self):
        address = f'{self.street_address} {self.city}, {self.state_district}, {self.country}'
        return address