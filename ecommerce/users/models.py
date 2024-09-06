from django.db import models
from django.contrib.auth.models import User

# Default abstract user: 
# username, first_name, last_name, email, password, is_active, is_staf, is_superuser, etc. 

# NEED TO MIGRATE

# without defining groups & user_permissions -> clash issues with User
# 
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

# CREATE TABLE shippings(
#     id SERIAL PRIMARY KEY,
#     customer_id INT UNIQUE, 
#     street_address VARCHAR(100),
#     city VARCHAR(50),
#     state_district VARCHAR(100),
#     post_code VARCHAR(50),
#     country CHAR(100),
#     FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
# );
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