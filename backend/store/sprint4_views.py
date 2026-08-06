from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import Order
from .sprint3_views import ProtectedView
from .sprint4_serializers import CustomerOrderSerializer


class CustomerOrderListView(ProtectedView):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        return Response(CustomerOrderSerializer(orders, many=True, context={'request': request}).data)


class CustomerOrderDetailView(ProtectedView):
    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related('items__product'), pk=pk, user=request.user,
        )
        return Response(CustomerOrderSerializer(order, context={'request': request}).data)
