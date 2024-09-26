from django.urls import path, include 
from .views import ProductViewSet, CategoryViewSet, VendorViewSet, CustomerViewSet, UserViewSet, ShippingViewSet, SpecialShippingViewSet, OrderDetailViewSet, OrderViewSet, PaymentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'vendors', VendorViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'users', UserViewSet)
router.register(r'shipping', ShippingViewSet)
router.register(r'special-shipping', SpecialShippingViewSet)
router.register(r'order-detail', OrderDetailViewSet)
router.register(r'order', OrderViewSet)
router.register(r'payment', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls))
]
