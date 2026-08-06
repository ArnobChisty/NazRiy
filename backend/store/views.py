from django.conf import settings
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import CategoryRepository, ProductRepository
from .models import NavigationLink, TopProduct
from .serializers import CategorySerializer, NavigationLinkSerializer, ProductSerializer, TopProductSerializer


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except Exception:
            return Response(
                {'status': 'unavailable', 'database': 'unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            'status': 'ok',
            'database': connection.vendor,
            'media_storage': 'supabase' if settings.USE_SUPABASE_STORAGE else 'local',
        })


class CategoryListView(APIView):
    def get(self, request):
        categories = CategoryRepository.list_categories()
        return Response(CategorySerializer(categories, many=True, context={"request": request}).data)


class ProductListView(APIView):
    def get(self, request):
        products = ProductRepository.list_products(request.query_params)
        return Response(ProductSerializer(products, many=True, context={"request": request}).data)


class FeaturedProductListView(APIView):
    def get(self, request):
        products = ProductRepository.featured_products()
        return Response(ProductSerializer(products, many=True, context={"request": request}).data)


class TopProductListView(APIView):
    def get(self, request):
        placements = TopProduct.objects.filter(active=True, product__active=True).select_related("product__category").prefetch_related("product__images")
        return Response(TopProductSerializer(placements, many=True, context={"request": request}).data)


class NavigationLinkListView(APIView):
    def get(self, request):
        links = NavigationLink.objects.filter(active=True)
        return Response(NavigationLinkSerializer(links, many=True).data)


class ProductDetailView(APIView):
    def get(self, request, slug):
        product = ProductRepository.get_by_slug(slug)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product, context={"request": request}).data)
