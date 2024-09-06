from django.urls import path
from .views import VendorDetailView, CustomerDetails, UpdateShippingView, CreateUser, CreateCustomer, CreateVendor, CustomLoginView, CompanyProfile, UpdateVendorProfile, UpdateUserView, UpdatePasswordView, UpdateVendorUserView
from django.contrib.auth import views

urlpatterns = [
   path('vendor/<int:vendor_id>/', VendorDetailView.as_view(), name='vendor_details'),
   path('customer/', CustomerDetails.as_view(), name='customer_details'),
   path('update/shipping/<int:shipping_id>/', UpdateShippingView.as_view(), name='update_shipping'),
   path('update/user-details/', UpdateUserView.as_view(), name='update_user_details'),
   path('update/vendor-details/', UpdateVendorUserView.as_view(), name='update_vendor_user'),
   path('update/vendor-profile/', UpdateVendorProfile.as_view(), name='update_vendor_profile'),
   path('update/user-credentials/', UpdatePasswordView.as_view(), name='update_password'),
   path('vendor/', CompanyProfile.as_view(), name='company_info'),
   path('register/', CreateUser.as_view(), name='register'),
   path('customer-profile/create/', CreateCustomer.as_view(), name='create_customer'),
   path('vendor-profile/create/', CreateVendor.as_view(), name='create_vendor'),
   path('login/', CustomLoginView.as_view(), name='login'),
   path('logout/', views.LogoutView.as_view(next_page='/products/'), name='logout'),
]