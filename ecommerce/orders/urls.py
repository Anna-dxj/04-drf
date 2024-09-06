from django.urls import path
from .views import PreviousOrderList, OrderDetails, MakePaymentView, RemoveCartItem, UpdateCartQuantityView, AddToCartView, CurrentOrderDetail, ShippingAddressView, TemporaryShippingView
from users.views import UpdateShippingFromPurchase

urlpatterns = [
    path('previous-orders/', PreviousOrderList.as_view(), name='previous_orders'), 
    path('cart/', CurrentOrderDetail.as_view(), name='cart'),
    path('<int:order_id>/', OrderDetails.as_view(), name='order_detail'), 
    path('checkout/confirm-shipping/<int:order_id>/', ShippingAddressView.as_view(), name='shipping_info_check'),
    path('checkout/shipping-info/<int:order_id>/', TemporaryShippingView.as_view(), name='temporary_shipping_form'),
    path('checkout/update-shipping/<int:order_id>/', UpdateShippingFromPurchase.as_view(), name='update_shipping_from_checkout'),
    path('checkout/payment-info/<int:order_id>/', MakePaymentView.as_view(), name='payment_form'), 
    path('remove-item/<int:order_detail_id>/', RemoveCartItem.as_view(), name='remove_cart_item'), 
    path('update-item/<int:order_detail_id>/', UpdateCartQuantityView.as_view(), name='update_cart_item'), 
    path('add-item/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'), 
]