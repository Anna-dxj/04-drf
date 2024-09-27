from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from orders.models import Order, SpecialShipping, OrderDetail, Payment
from products.models import Product, Category
from .permissions import IsVendorOrReadOnly, IsAdminOrReadOnly, IsOwner
from rest_framework import viewsets, status, generics, filters
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .serializers import ProductSerializer, CategorySerializer, VendorSerializer, CustomerSerializer, UserSerializer, ShippingSerializer, OrderSerializer, OrderDetailSerializer, SpecialShippingSerializer, PaymentSerializer
from users.models import Vendor, Customer, Shipping

class PaymentViewSet(viewsets.ModelViewSet):
    """Viewset for payment methods. All users able to read, but only admin able to create, update, delete"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    pagination_class = None
    

class OrderViewSet(viewsets.ModelViewSet):
    """Vieset for shipping objects. admin able to read all order instances as well as update an order's shipping status, but a customer is only able to CRUD the instance associated with their user and do not have any order marked with 'is_in_cart' True."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes=[IsOwner]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)
    
    def perform_create(self, serializer):
        user = self.request.user
        customer = serializer.validated_data.get('customer')

        if customer.user != user: 
            raise ValidationError('You cannot create an order for another customer')
        
        if Order.objects.filter(customer=customer, is_in_cart=True).exists():
            raise ValidationError('Customer already has an order in their cart')
        
        order = serializer.save()

        if not hasattr(order, 'payment') or order.payment is None: 
            order.is_in_cart = True
        else: 
            order.is_in_cart = False
            order.order_date = timezone.now()
        
        if order.is_shipped:
            order.shipped_date = timezone.now()
        
        order.save()
    
    def perform_update(self, serializer):
        order = serializer.save()

        if not hasattr(order, 'payment') or order.payment is None: 
            order.is_in_cart = True
        else: 
            order.is_in_cart = False
            order.order_date = timezone.now()
        
        if order.is_shipped:
            order.shipped_date = timezone.now()
        
        order.save()

        

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes=[IsOwner]
    throttle_classes = [UserRateThrottle]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_staff:
            return  OrderDetail.objects.all()
        customer = Customer.objects.get(user=self.request.user)
        order = Order.objects.filter(customer=customer)
        return super().get_queryset().filter(order__in=order)
    
    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')
        customer = Customer.objects.get(user=self.request.user)

        if order.customer != customer:
            raise PermissionDenied({'detail': 'You do not have permission to assign order details for this order'})
        if not order.is_in_cart:
            raise ValidationError({'detail': f'You cannot assign order details to an order that is not in the cart.'})
        
        product = serializer.validated_data.get('product')
        if product:
            serializer.validated_data['unit_price'] = product.price
        serializer.save()

    def perform_update(self, serializer):
        order = serializer.validated_data.get('order')
        customer = Customer.objects.get(user=self.request.user)

        if order.customer != customer:
            raise PermissionDenied({'detail': 'You do not have permission to assign order details for this order'})
        
        if not order.is_in_cart:
            raise ValidationError({'detail': f'You cannot assign order details to an order that is not in the cart.'})

        product = serializer.validated_data.get('product')
        if product:
            serializer.validated_data['unit_price'] = product.price

        serializer.save()


class SpecialShippingViewSet(viewsets.ModelViewSet):
    queryset = SpecialShipping.objects.all()
    serializer_class = SpecialShippingSerializer
    permission_classes=[IsOwner]
    throttle_classes = [UserRateThrottle]
    pagination_class = None
    

    def get_queryset(self):
        if self.request.user.is_staff: 
            return SpecialShipping.objects.all()
        customer = Customer.objects.get(user=self.request.user)
        order = Order.objects.filter(customer=customer)
        return super().get_queryset().filter(order__in=order)
    
    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')
        customer = Customer.objects.get(user=self.request.user)

        if order.customer != customer:
            raise PermissionDenied({'detail': 'You do not have permission to assign special shipping for this order'})

        if not order.is_in_cart:
            raise ValidationError({'detail': f'You cannot assign special shipping to an order that is not in the cart.'})
        
        if order.is_shipped:
            raise ValidationError({'detail': 'You cannot change the address for this order any more.'})
        
        serializer.save()
    
    def perform_update(self, serializer):
        order = serializer.validated_data.get('order')
        customer = Customer.objects.get(user=self.request.user)

        if order.customer != customer:
            raise PermissionDenied({'detail': 'You do not have permission to assign special shipping for this order'})
        
        if not order.is_in_cart:
            raise ValidationError({'detail': f'You cannot assign special shipping to an order that is not in the cart.'})

        if order.is_shipped:
            raise ValidationError({'detail': 'You cannot change the address for this order any more.'})
        
        serializer.save()


class ShippingViewSet(viewsets.ModelViewSet):
    """Vieset for shipping objects. admin able to read all shipping instances, but a customer is only able to CRUD the instance associated with their user. Customer only able to create an instance if one is not already associated with it"""
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [IsOwner]
    throttle_classes = [UserRateThrottle]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_staff: 
            return User.objects.all()
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)
    
    def perform_create(self, serializer):
        customer = Customer.objects.get(user=self.request.user)
        serializer.save(customer=customer)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'detail': "User already has a default shipping address or cannot affect another user's profile"}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user object. admin able to read all user instances, but a user is only able to CRUD their own instance. user is only able to create an instance if one is not already associated with their user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    throttle_classes = [UserRateThrottle]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return super().get_queryset().filter(id=self.request.user.id)
    
    def perform_create(self, serializer):
            serializer.save(id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'detail': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    

class CustomerViewSet(viewsets.ModelViewSet):
    """Viewset for custmers object. admin able to read all customer instances, but a customer is only able to CRUD their own instance. Customer is only able to create an instance if one is not already associated with their user."""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsOwner]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return super().get_queryset().filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'detail': 'Customer already exists'}, status=status.HTTP_400_BAD_REQUEST)


# api viewset for category for product: 
class ProductViewSet(viewsets.ModelViewSet):
    """Viewset for products object. All read operations can be done by anyone, but a vendor is only able to create, update, delete their own products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle] 
    filter_backends = [
	    DjangoFilterBackend, 
	    filters.SearchFilter, 
	    filters.OrderingFilter
	]
    filterset_fields = ['category', 'vendor']
    search_fields = ['name', 'description']
    ordering_fields = ['price']
    ordering = ['price']

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
    
    def perform_create(self, serializer):
        vendor = Vendor.objects.get(profile__user=self.request.user)
        serializer.save(vendor = vendor)
    
    def perform_update(self, serializer):
        product = self.get_object()
        print('product: ', product)
        if product.vendor.profile.user != self.request.user:
            return PermissionDenied('You do not have permission to update this.')
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.vendor.profile != self.request.user:
            return Response({'detail': 'You do not have permission to delete this product.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

# api viewset for category
class CategoryViewSet(viewsets.ModelViewSet):
    """Viewset for categories object. All read operations can be done by anyone, but create, update, delete operations limited to admin users"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    pagination_class = None
    filter_backends = [
	    filters.SearchFilter, 
	    filters.OrderingFilter
	]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']    

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)

# api viewset for vendors
class VendorViewSet(viewsets.ModelViewSet):
    """Viewset for vendors object. All read operations can be done by anyone, but a vendor is only able to create, update, delete their own information. vendor is only able to create an isntance if one isn't already associated with their user"""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsVendorOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle] 
    filter_backends = [
	    filters.SearchFilter, 
	    filters.OrderingFilter
	]
    search_fields = ['company_name', 'description']
    ordering_fields = ['company_name']
    ordering = ['company_name']
    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
    
    def perform_create(self, serializer):
        user = self.request.user
        customer = Customer.objects.get(user=user)
        serializer.save(profile=customer)
