from rest_framework import permissions
from products.models import Product
from users.models import Vendor

# allow vendors to create, update, delete their own information. everyoen else is read only 

class IsVendorOrReadOnly(permissions.BasePermission):
    """Allows vendors to perform crud operations on their own information and products, but only grants read access to non-vendors."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and hasattr(request.user, 'customer') and request.user.customer.is_vendor
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if isinstance(obj, Product):
           return obj.vendor.profile.user == request.user
        elif isinstance(obj, Vendor):
            return obj.profile.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows admin users to perform crud operations, but only grants read access to non-admin users."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: 
            return True
        
        return request.user.is_staff and request.user.is_authenticated

class IsOwner(permissions.BasePermission):
    """Only allows an owner to perform crud operations pertaining their own customer information, default shipping address, and orders."""
    def has_object_permissions(self, request, view, obj):
        return obj.user == request.user
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
        