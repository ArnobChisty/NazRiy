from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from .authentication import SignedTokenAuthentication
from .discounts import DiscountValidationError, delivery_charge_for, quote_discount
from .models import Cart,CartItem,Order,OrderItem,Payment,Product
from .order_emails import send_order_confirmation
from .sprint3_serializers import CartItemSerializer,CheckoutSerializer,OrderSerializer

class ProtectedView(APIView):
    authentication_classes=[SignedTokenAuthentication];permission_classes=[permissions.IsAuthenticated]
class CartView(ProtectedView):
    def cart(self,user):return Cart.objects.get_or_create(user=user)[0]
    def get(self,request):return Response(CartItemSerializer(self.cart(request.user).items.select_related('product'),many=True).data)
    def post(self,request):
        serializer=CartItemSerializer(data=request.data);serializer.is_valid(raise_exception=True);data=serializer.validated_data;cart=self.cart(request.user);item,created=CartItem.objects.update_or_create(cart=cart,product=data['product'],size=data.get('size',''),color=data.get('color',''),defaults={'quantity':data['quantity']});return Response(CartItemSerializer(item).data,status=201 if created else 200)
class CartItemView(ProtectedView):
    def patch(self,request,pk):
        item=get_object_or_404(CartItem,pk=pk,cart__user=request.user);serializer=CartItemSerializer(item,data=request.data,partial=True);serializer.is_valid(raise_exception=True);serializer.save();return Response(serializer.data)
    def delete(self,request,pk):get_object_or_404(CartItem,pk=pk,cart__user=request.user).delete();return Response(status=204)
class CheckoutView(ProtectedView):
    @transaction.atomic
    def post(self,request):
        serializer=CheckoutSerializer(data=request.data);serializer.is_valid(raise_exception=True);data=serializer.validated_data
        idempotency_key=data.pop('idempotency_key');payment_method=data.pop('payment_method');promo_code=data.pop('promo_code','')
        existing=Payment.objects.select_related('order').filter(idempotency_key=idempotency_key).first()
        if existing:
            if existing.order.user_id != request.user.id:return Response({'detail':'That checkout request belongs to another customer.'},status=409)
            return Response(OrderSerializer(existing.order).data,status=status.HTTP_200_OK)
        items=data.pop('items');lines=[];subtotal=Decimal('0');reserved_quantities={};locked_products={}
        for entry in items:
            product=get_object_or_404(Product.objects.select_for_update(),pk=entry.get('product_id'));quantity=int(entry.get('quantity',0));size=entry.get('size','');color=entry.get('color','').strip()
            if color.lower() == 'default':
                color = product.available_colors[0] if product.available_colors else ''
            if quantity < 1:
                return Response({'detail': f'Choose at least one {product.name}.'}, status=400)
            if product.stock_quantity < 1:
                return Response({'detail': f'{product.name} is out of stock.'}, status=400)
            if quantity > product.stock_quantity:
                return Response({'detail': f'Only {product.stock_quantity} of {product.name} remain in stock.'}, status=400)
            reserved_quantities[product.pk]=reserved_quantities.get(product.pk,0)+quantity
            if reserved_quantities[product.pk] > product.stock_quantity:
                return Response({'detail': f'Only {product.stock_quantity} of {product.name} remain in stock across the selected options.'}, status=400)
            locked_products[product.pk]=product
            if size and size not in product.available_sizes:return Response({'detail':f'Invalid size for {product.name}.'},status=400)
            if color and color not in product.available_colors:return Response({'detail':f'Invalid colour for {product.name}.'},status=400)
            subtotal+=product.price*quantity;lines.append((product,quantity,size,color))
        delivery=delivery_charge_for(subtotal);discount_amount=Decimal('0.00');discount_campaign=None;normalized_code=''
        if promo_code:
            try:
                quote=quote_discount(code=promo_code,subtotal=subtotal,user=request.user,lock=True)
            except DiscountValidationError as error:
                return Response({'detail':str(error)},status=400)
            delivery=quote.delivery_charge;discount_amount=quote.discount_amount;discount_campaign=quote.campaign;normalized_code=quote.code;total=quote.total
        else:
            total=subtotal+delivery
        order=Order.objects.create(user=request.user,subtotal=subtotal,delivery_charge=delivery,discount_campaign=discount_campaign,discount_code=normalized_code,discount_amount=discount_amount,total=total,**data)
        for product,quantity,size,color in lines:
            OrderItem.objects.create(order=order,product=product,product_name=product.name,size=size,color=color,unit_price=product.price,quantity=quantity,line_total=product.price*quantity)
        for product_id,quantity in reserved_quantities.items():
            product=locked_products[product_id];product.stock_quantity-=quantity;product.save(update_fields=['stock_quantity'])
        Payment.objects.create(order=order,method=payment_method,amount=order.total,idempotency_key=idempotency_key)
        Cart.objects.filter(user=request.user).delete()
        transaction.on_commit(lambda order_id=order.id: send_order_confirmation(order_id))
        return Response(OrderSerializer(order).data,status=status.HTTP_201_CREATED)
class OrderListView(ProtectedView):
    def get(self,request):return Response(OrderSerializer(Order.objects.filter(user=request.user).prefetch_related('items'),many=True).data)
