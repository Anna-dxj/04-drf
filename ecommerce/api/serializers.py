from rest_framework import serializers
from products.models import Product, Category
from users.models import Vendor, Customer, Shipping
from orders.models import Order, SpecialShipping, OrderDetail, Payment
from django.contrib.auth.models import User

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'method']
        read_only_fields=['id']


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ['id', 'street_address', 'city', 'state_district', 'post_code', 'country', 'customer']
        read_only_fields=['id', 'customer']

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'company_name', 'description', 'customer_service_email']
        read_only_fields=['id']
    
    def create(self, validated_data):
        customer = validated_data.get('profile')

        if Vendor.objects.filter(profile=customer).exists():
            raise serializers.ValidationError('Already associated with a vendor')

        return super().create(validated_data)

class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    shipping = ShippingSerializer(read_only=True)

    class Meta: 
        model = Customer
        fields = ['id', 'is_vendor', 'name', 'shipping']
    
    def get_name(self, obj):
        if hasattr(obj, 'vendor'):
            return obj.vendor.company_name
        elif obj.user:
            return f'{obj.user.first_name} {obj.user.last_name}'
        return None

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'is_staff', 'password']

    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer() 
    category = CategorySerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'vendor', 'stock']
        read_only_fields = ['id']

    def get_vendor(self, obj):
        return obj.vendor.company_name if obj.vendor else None

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class SpecialShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialShipping
        fields = '__all__'
        read_only_fields = ['id']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    product_info = ProductSerializer(read_only=True, source='product')
    class Meta:
        model = OrderDetail
        fields = ['id', 'product', 'product_info', 'quantity', 'unit_price', 'order']
        read_only_fields = ['id', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(read_only=True, many=True)
    shipping_info = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'order_date', 'is_in_cart', 'shipped_date', 'is_shipped', 'customer', 'payment', 'order_details', 'shipping_info']
        read_only_fields = ['id', 'order_date', 'shipping_info']

    def __init__(self, *args, **kwargs):
        self.request = kwargs['context'].get('request')
        super().__init__(*args,**kwargs)

        if not self.request.user.is_staff:
            self.fields['shipped_date'].read_only = True
            self.fields['is_shipped'].read_only=True
    
    def get_shipping_info(self, obj):
        try: 
            special_shipping = SpecialShipping.objects.get(order=obj)
            if special_shipping is not None: 
                return SpecialShippingSerializer(special_shipping).data
        except SpecialShipping.DoesNotExist:
            print(f'Ordr {obj.id} is not associated wiht a special shipping')
            if obj.is_in_cart == False:
                customer = obj.customer
                default_shipping = Shipping.objects.get(customer=customer)
                return ShippingSerializer(default_shipping).data 
            return None