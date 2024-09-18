from typing import Any
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView, DetailView, FormView
from django.views import View
from products.models import Product
from users.models import Shipping
from .models import Order, OrderDetail, Payment
from products.models import Product
from .forms import CardForm, TemporaryShippingForm
from users.forms import ShippingForm
from products.forms import AddToCartForm
from users.models import Customer

# list of all previous orders 
class PreviousOrderList(ListView):
    model = Order
    template_name = 'orders/previous_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        previous_orders = Order.objects.filter(customer = customer, is_in_cart = False). order_by('-order_date')
        return previous_orders
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = context['orders']

        order_details = []
        total_sum = 0
        total_items = 0

        for order in orders:
            details = OrderDetail.objects.filter(order=order)

            total_sum += sum(detail.unit_price * detail.quantity for detail in details)
            total_items += sum(detail.quantity for detail in details)

            order_details.append({
                'order': order,
                'details': details,
                'total_sum': total_sum,
                'total_items': total_items
            })
        
        context['order_details'] = order_details

        return context

# current cart detail info 
class CurrentOrderDetail(DetailView):
    model = Order
    template_name = 'orders/current_order.html'
    context_object_name = 'order'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_details = OrderDetail.objects.filter(order=order)
        context['order_details'] = order_details

        total_sum = sum(detail.unit_price * detail.quantity for detail in order_details)
        context['total_sum'] = total_sum

        total_items = sum(detail.quantity for detail in order_details)
        context['total_items'] = total_items

        return context
    def object_order(self):
        user = self.request.user
        customer = get_object_or_404(Customer, user=user)
        order, created = Order.objects.get_or_create(
            customer=customer,
            is_in_cart=True
        )
        return order 
    
    def get_object(self):
        user = self.request.user

        customer = get_object_or_404(Customer, user=user)
        order, created = Order.objects.get_or_create(
            customer = customer,
            is_in_cart=True
        )

        return order

# for past order details
class OrderDetails(DetailView):
    model = Order
    template_name = 'current_order.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_details'] = OrderDetail.objects.filter(order=self.object)
        return context
    
    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id, is_in_cart=True)
    
# make payment with card
class MakePaymentView(View):
    template_name = 'orders/make_payment.html'

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')

        billing_address = request.session.get('billing_address', {})
        print('billing_address: ', billing_address)

        form = CardForm()
        billing_address_form = ShippingForm(initial={
            'street_address': billing_address.get('street_adr', None),
            'city': billing_address.get('city', None),
            'state_district': billing_address.get('state_district', None),
            'post_code': billing_address.get('post_code', None),
            'country': billing_address.get('country', None)
        })

        context = {
            'form': form,
            'billing_address_form': billing_address_form,
            'order_id': order_id
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = CardForm(request.POST)
        billing_address_form = ShippingForm(request.POST)
        order_id = kwargs.get('order_id')

        if form.is_valid() and billing_address_form.is_valid():
            request.session['billing_address'] = {
                'street_adr': billing_address_form.cleaned_data['street_address'],
                'city': billing_address_form.cleaned_data['city'],
                'state_district': billing_address_form.cleaned_data['state_district'],
                'post_code': billing_address_form.cleaned_data['post_code'],
                'country': billing_address_form.cleaned_data['country']
            }

            order = get_object_or_404(Order, id=order_id)
            payment_id = form.cleaned_data['method']
            payment = get_object_or_404(Payment, id=payment_id)

            order.make_order(payment)
            return redirect('all_products')
        else:
            print(f'form error: {form.errors}')
            print(f'shipping form error: {billing_address_form.errors}')
            context = {
                'form': form,
                'billing_address_form': billing_address_form,
                'order_id': order_id
            }

            return render(request, self.template_name, context)
        
# remove cart
class RemoveCartItem(View):
    def post(self, request, order_detail_id):
        order_detail = get_object_or_404(OrderDetail, id=order_detail_id)

        order_detail.delete()

        return redirect('cart')


# update cart
class UpdateCartQuantityView(View):
    def post(self, request, order_detail_id):
        order_detail = get_object_or_404(OrderDetail, id=order_detail_id)
        product = order_detail.product
        new_quantity = int(request.POST.get('quantity'))

        previous_quantity = order_detail.quantity
        delta_quantity = new_quantity - previous_quantity

        # if remnoving stock, check first if able to do so
        if delta_quantity > 0:
            if product.stock < delta_quantity:
                messages.error(request, 'Not enough stock available')
                return redirect('cart')

        order_detail.quantity = new_quantity
        order_detail.unit_price = order_detail.product.price
        order_detail.save()

        return redirect('cart')


# add item to cart
class AddToCartView(View):
    def post(self, request, product_id):
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            product = get_object_or_404(Product, id=product_id)
            customer = get_object_or_404(Customer, user=request.user)

            if product.stock < quantity: 
                messages.error(request, 'Sorry, there is not enough stock for your request')
                return redirect('product_detail', product_id=product_id)

            order, created = Order.objects.get_or_create(
                customer=customer,
                is_in_cart = True
            )

            try: 
                order_detail = OrderDetail.objects.get(order=order, product=product)
                order_detail.quantity += quantity
                order_detail.unit_price = product.price
                order_detail.save()
            
            except OrderDetail.DoesNotExist:
                order_detail = OrderDetail.objects.create(
                    order = order,
                    product = product,
                    quantity = quantity,
                    unit_price = product.price
                )

            finally: 
                return redirect('cart')
        return redirect('product_detail', product_id=product_id)

# for temporary shipping form 
class TemporaryShippingView(View):
    template_name = 'orders/temporary_shipping.html'

    def get(self, request, *args, **kwargs):
        form = TemporaryShippingForm()
        context = {
            'form': form,
            'order_id': self.kwargs.get('order_id'),
            'type': 'temporary shipping',
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = TemporaryShippingForm(request.POST)
        order_id = self.kwargs.get('order_id')
        context = {
            'form': form,
            'order_id': order_id,
            'type': 'temporary shipping',
        }

        if form.is_valid():
            order_id = order_id
            order = get_object_or_404(Order, order_id)

            special_shipping = form.save(commit=False)
            special_shipping.order = order
            special_shipping.save()

            return redirect('payment_form', order_id=order_id)
        
        return render(request, self.template_name, context)

# default shipping info from payment screen 
class ShippingAddressView(DetailView):
    model = Shipping
    template_name = 'orders/confirm_shipping.html'
    context_object_name = 'shipping'

    def get_object(self, queryset=None):
        customer = get_object_or_404(Customer, user=self.request.user)
        shipping = get_object_or_404(Shipping, customer=customer)
        return shipping
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = get_object_or_404(Customer, user=self.request.user)
        context['order_id'] = self.kwargs.get('order_id')
        context['customer'] = customer

        return context
