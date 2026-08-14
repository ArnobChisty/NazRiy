import uuid

from rest_framework import serializers
from .models import CartItem,Order,OrderItem,Payment,Product
from .sprint5_serializers import PaymentSerializer

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:model=Product;fields=['id','name','slug','price','stock_quantity']
class CartItemSerializer(serializers.ModelSerializer):
    product=CartProductSerializer(read_only=True);product_id=serializers.PrimaryKeyRelatedField(source='product',queryset=Product.objects.all(),write_only=True)
    class Meta:model=CartItem;fields=['id','product','product_id','size','color','quantity']
    def validate(self,data):
        product=data.get('product') or self.instance.product;quantity=data.get('quantity',getattr(self.instance,'quantity',1))
        if quantity<1:raise serializers.ValidationError('Quantity must be at least one.')
        if quantity>product.stock_quantity:raise serializers.ValidationError('Requested quantity exceeds available stock.')
        if data.get('size') and data['size'] not in product.available_sizes:raise serializers.ValidationError('Invalid size.')
        if data.get('color') and data['color'] not in product.available_colors:raise serializers.ValidationError('Invalid colour.')
        return data
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:model=OrderItem;fields=['product_name','size','color','unit_price','quantity','line_total']
class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    payment=PaymentSerializer(read_only=True)
    class Meta:model=Order;fields=['id','name','email','phone','address','city','postal_code','subtotal','delivery_charge','discount_code','discount_amount','total','status','created_at','items','payment']
class CheckoutSerializer(serializers.Serializer):
    name=serializers.CharField();email=serializers.EmailField();phone=serializers.RegexField(r'^[+\d][\d\s-]{7,}$');address=serializers.CharField();city=serializers.CharField();postal_code=serializers.CharField();items=serializers.ListField(child=serializers.DictField(),allow_empty=False)
    payment_method=serializers.ChoiceField(choices=Payment.METHOD_CHOICES,default='bkash')
    idempotency_key=serializers.UUIDField(required=False,default=uuid.uuid4)
    promo_code=serializers.CharField(required=False,allow_blank=True,max_length=40,trim_whitespace=True,default='')

class PromoValidationSerializer(serializers.Serializer):
    code=serializers.CharField(max_length=40,trim_whitespace=True)
    items=serializers.ListField(child=serializers.DictField(),allow_empty=False,max_length=100)
