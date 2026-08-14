from rest_framework import serializers

from .models import Order, OrderItem
from .sprint5_serializers import PaymentSerializer


class OrderDetailItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_slug', 'product_image', 'size', 'color', 'unit_price', 'quantity', 'line_total']

    def get_product_image(self, obj):
        if not obj.product.primary_image:
            return ''
        request = self.context.get('request')
        return request.build_absolute_uri(obj.product.primary_image.url) if request else obj.product.primary_image.url


class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderDetailItemSerializer(many=True, read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city', 'postal_code',
            'subtotal', 'delivery_charge', 'discount_code', 'discount_amount', 'total', 'status', 'status_label',
            'created_at', 'updated_at', 'items', 'payment',
        ]
