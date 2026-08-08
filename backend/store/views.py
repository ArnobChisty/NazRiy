from django.conf import settings
from django.db import connection
from django.db.models import Case, IntegerField, When
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import CategoryRepository, ProductRepository
from .models import NavigationLink, Product, TopProduct
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
        placements = TopProduct.objects.filter(active=True, product__active=True).select_related("product__category").prefetch_related("product__images", "product__size_chart")
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


class RecommendationListView(APIView):
    """Return explainable, rule-based recommendations from the product catalog."""

    permission_classes = [AllowAny]

    def get(self, request):
        slug = request.query_params.get("product", "").strip()
        current = ProductRepository.get_by_slug(slug) if slug else None
        category_id = current.category_id if current else None
        size = request.query_params.get("size", "").strip()
        color = request.query_params.get("color", "").strip()
        try:
            limit = min(max(int(request.query_params.get("limit", 4)), 1), 12)
        except (TypeError, ValueError):
            limit = 4

        products = Product.objects.select_related("category").prefetch_related("images", "size_chart").filter(active=True)
        if current:
            products = products.exclude(pk=current.pk)
        products = products.annotate(
            category_score=Case(When(category_id=category_id, then=4) if category_id else When(featured=True, then=2), default=0, output_field=IntegerField()),
            size_score=Case(When(available_sizes__icontains=size, then=2) if size else When(stock_quantity__gt=0, then=1), default=0, output_field=IntegerField()),
            color_score=Case(When(available_colors__icontains=color, then=2) if color else When(featured=True, then=1), default=0, output_field=IntegerField()),
        ).order_by("-category_score", "-size_score", "-color_score", "-featured", "-created_at")[:limit]
        return Response(ProductSerializer(products, many=True, context={"request": request}).data)


class RelatedProductListView(RecommendationListView):
    def get(self, request, slug):
        request.query_params._mutable = True
        request.query_params["product"] = slug
        return super().get(request)
