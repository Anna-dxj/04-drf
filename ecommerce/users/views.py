from django.db.models import Sum
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from .models import Vendor, Shipping, Customer
from .forms import CreateCustomerForm, ShippingForm, UserForm, VendorForm, CustomLoginForm, UpdateUserForm, UpdatePasswordForm, UpdateVendorForm
from products.models import Product
from django.contrib.auth.models import User

# vendor detail view to see other vendors
class VendorDetailView(DetailView):
    """Vendor details, including their top five products. Publici view."""
    model = Vendor
    template_name='users/vendor_detail.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.object
        
        top_products = Product.objects.filter(vendor=vendor).annotate(
            total_sales=Sum('order_details__quantity')
        ).order_by('-total_sales')[:5]
        context['top_products'] = top_products

        return context 

    def get_object(self):
        vendor_id = self.kwargs.get('vendor_id')
        return get_object_or_404(Vendor, id=vendor_id)

# own customer detail info 
class CustomerDetails(LoginRequiredMixin, DetailView):
    """Displays customer information. Customer but non-vendor view"""
    model = Shipping
    template_name='users/customer_detail.html'
    context_object_name = 'shipping'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipping = self.get_object()
        context['customer'] = shipping.customer
        context['user'] = shipping.customer.user
        context['type'] = 'customer profile'
        return context 
    
    def get_object(self, queryset=None):
        customer = get_object_or_404(Customer, user=self.request.user)
        try: 
            shipping = Shipping.objects.get(customer=customer)
        except Shipping.DoesNotExist:
            shipping = Shipping.objects.create(customer=customer)
    
        return shipping

# for updating default shipping
class UpdateShippingView(LoginRequiredMixin, UpdateView):
    """Update default shipping information from profile settings. Customer but non-vendor view."""
    model = Shipping
    form_class = ShippingForm
    template_name='users/customer_update_form.html'
    success_url = reverse_lazy('customer_details')

    def get_object(self):
        shipping_id = self.kwargs.get('shipping_id')
        return get_object_or_404(Shipping, id=shipping_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'update shipping'
        return context 

# for updating customer information 
class UpdateUserView(LoginRequiredMixin, UpdateView):
    """Update user information. Customer view."""
    model: User
    form_class = UpdateUserForm
    template_name='users/customer_update_form.html'
    success_url = reverse_lazy('customer_details')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'update user'
        return context

# Update Vendor information 
class UpdateVendorUserView(LoginRequiredMixin, UpdateView):
    """Update vendor information. Vendor View."""
    model = User
    form_class = UpdateVendorForm
    template_name = 'users/customer_update_form.html'
    success_url = reverse_lazy('company_info')

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'update vendor'
        return context

# new password
class UpdatePasswordView(LoginRequiredMixin, View):
    """Associates a customer with a new password. Customer view."""
    template_name='users/customer_update_form.html'

    def get(self, request, *args, **kwargs):
        form = UpdatePasswordForm(user=request.user)

        context = {
            'form': form,
            'type': 'update password'
        }

        return render(request, self.template_name, context)
    def post(self, request, *args, **kwargs):
        form = UpdatePasswordForm(request.POST, user=request.user)

        if form.is_valid():
            user = self.request.user
            new_password = form.cleaned_data.get('password_confirm')
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return redirect('customer_details')

        context = {
            'form': form, 
            'type': 'update password'
        }

        return render(request, self.template_name, context)



# update default address from shipping menus 
class UpdateShippingFromPurchase(LoginRequiredMixin, View):
    """Update default shipping information, but from the payment templates. Customer non vendor veiw."""
    template_name='orders/temporary_shipping.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        customer = get_object_or_404(Customer, user=user)
        shipping = get_object_or_404(Shipping, customer=customer)

        form = ShippingForm(instance=shipping)

        context = {
            'form': form, 
            'order_id': self.kwargs.get('order_id'),
            'type': 'update default address',
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        customer = get_object_or_404(Customer, user=user)
        shipping = get_object_or_404(Shipping, customer=customer)

        form = ShippingForm(instance=shipping)

        if form.is_valid():
            form.save()
            order_id = self.kwargs.get('order_id')
            return redirect(reverse('payment_form', kwargs={'order_id': order_id}))
        
        context = {
            'form': form, 
            'order_id': self.kwargs.get('order_id'),
            'type': 'update default address',
        }

        return render(request, self.template_name, context)

# profile for vendor 
class CompanyProfile(View):
    """Shows vendor's own details, as well as low stock and top selling products. Vendor view."""
    template_name = 'users/customer_detail.html'

    def get(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, user=request.user)
        vendor = get_object_or_404(Vendor, profile=customer)

        top_products = Product.objects.filter(vendor=vendor).annotate(
            total_sales=Sum('order_details__quantity')
        ).filter(total_sales__gt=0).order_by('-total_sales')[:5]

        low_stock_products = Product.objects.filter(
            vendor=vendor,
            stock__lte=50
        )

        context = {
            'vendor': vendor, 
            'low_stock_products': low_stock_products, 
            'top_products': top_products,
            'type': 'vendor profile'
        }

        return render(request, self.template_name, context)

# update vendor information 
class UpdateVendorProfile(UpdateView):
    """Update vendor information. Vendor view."""
    model = Vendor
    form_class = VendorForm
    template_name = 'users/customer_update_form.html'
    success_url = reverse_lazy('company_info')

    def get_object(self):
        customer = get_object_or_404(Customer, user = self.request.user)
        vendor = get_object_or_404(Vendor, profile=customer)
        return vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'update company'

        return context

# login 
class CustomLoginView(LoginView):
    """Handles log in."""
    form_class = CustomLoginForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.get_user()
        if user:
            login(self.request, user)

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'login'

        return context

# create user
class CreateUser(View):
    """Creates a user instance."""
    def get(self, request):
        user_form = UserForm()
        context = {
            'form': user_form, 
            'type': 'user creation'
        }
        return render(request, 'users/register.html', context)

    def post(self, request):
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save()
            #########
            is_vendor = user_form.cleaned_data.get('is_vendor')
            login(request, user)

            if is_vendor:
                # redirect to vendor form
                customer = Customer(user=user, is_vendor = True)
                customer.save()
                return redirect('create_vendor')

            else:
                # redirect to shipping form 
                customer = Customer(user=user, is_vendor = False)
                customer.save()
                return redirect('create_customer')
        else:
            
            context = {
                'form': user_form,
                'type': 'user creation'
            }
            return render(request, 'users/register.html', context)

# create customer
class CreateCustomer(View):
    """Creates a non-vendor customer"""
    def get(self, request):
        shipping_form = CreateCustomerForm()

        context = {
            'form': shipping_form,
            'type': 'customer profile creation',
            'shipping_fields': [shipping_form[field] for field in ['street_address', 'city', 'state_district', 'post_code', 'country']],
            'name_fields': [shipping_form[field] for field in ['first_name', 'last_name']]
        }


        return render(request, 'users/register.html', context)

    def post(self, request):
        shipping_form = CreateCustomerForm(request.POST)

        if shipping_form.is_valid():
            user = request.user
            shipping = shipping_form.save(commit=False)
            shipping.customer = Customer.objects.get(user=user)
            shipping.save()

            user.first_name = shipping_form.cleaned_data['first_name']
            user.last_name = shipping_form.cleaned_data['last_name']

            user.save()
            return redirect('all_products')
        
        context = {
            'form': shipping_form,
            'type': 'customer profile creation',
            'shipping_fields': [shipping_form[field] for field in ['street_address', 'city', 'state_district', 'post_code', 'country']],
            'name_fields': [shipping_form[field] for field in ['first_name', 'last_name']]
        }

        return redirect(request, 'users/register.html', context)

# create vendor 
class CreateVendor(View):
    """Creates a vendor"""
    def get(self, request):
        vendor_form = VendorForm()
        
        context = {
            'form': vendor_form, 
            'type': 'vendor profile creation'
        }

        print('get', context)
        return render(request, 'users/register.html', context)

    def post(self, request):
        vendor_form = VendorForm(request.POST)
        
        if vendor_form.is_valid():
            vendor = vendor_form.save(commit=False)
            vendor.profile = Customer.objects.get(user=request.user)
            vendor.save()
            return redirect('all_products')
        
        context = {
            'form': vendor_form, 
            'type': 'vendor profile creation'
        }
        print(context)
        return redirect(request, 'users/register.html', context)
