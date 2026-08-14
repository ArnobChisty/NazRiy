from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response

from .discounts import DiscountValidationError, quote_discount
from .models import Product
from .sprint3_serializers import PromoValidationSerializer
from .sprint3_views import ProtectedView


class PromoCodeValidationView(ProtectedView):
    """Return a server-calculated promo quote without creating an order."""

    def post(self, request):
        serializer = PromoValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        subtotal = Decimal('0.00')
        requested_quantities = {}

        for entry in data['items']:
            try:
                product_id = int(entry.get('product_id'))
                quantity = int(entry.get('quantity'))
            except (TypeError, ValueError):
                return Response({'detail': 'The cart contains an invalid item.'}, status=status.HTTP_400_BAD_REQUEST)
            if quantity < 1:
                return Response({'detail': 'Cart quantities must be at least one.'}, status=status.HTTP_400_BAD_REQUEST)
            requested_quantities[product_id] = requested_quantities.get(product_id, 0) + quantity
            try:
                product = Product.objects.get(pk=product_id, active=True)
            except Product.DoesNotExist:
                return Response({'detail': 'A product in the cart is no longer available.'}, status=status.HTTP_400_BAD_REQUEST)
            if requested_quantities[product_id] > product.stock_quantity:
                return Response({'detail': f'Only {product.stock_quantity} of {product.name} remain in stock.'}, status=status.HTTP_400_BAD_REQUEST)
            subtotal += product.price * quantity

        try:
            quote = quote_discount(code=data['code'], subtotal=subtotal, user=request.user)
        except DiscountValidationError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'code': quote.code,
            'title': quote.campaign.title,
            'discount_type': quote.campaign.discount_type,
            'subtotal': f'{subtotal:.2f}',
            'delivery_charge': f'{quote.delivery_charge:.2f}',
            'discount_amount': f'{quote.discount_amount:.2f}',
            'total': f'{quote.total:.2f}',
            'message': 'Promo code applied successfully.',
        })
