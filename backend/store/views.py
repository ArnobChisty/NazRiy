from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Case, IntegerField, When
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import CategoryRepository, ProductRepository
from .cache_keys import HOMEPAGE_CACHE_KEY
from .models import Banner, DiscountCampaign, NavigationLink, Product, TopProduct, WebsiteTheme
from .banner_serializers import BannerSerializer
from .serializers import CategorySerializer, DiscountCampaignSerializer, NavigationLinkSerializer, ProductSerializer, TopProductSerializer


class PublicCatalogView(APIView):
    """Public, edge-cacheable catalogue responses.

    Disabling session authentication prevents Django from adding ``Vary:
    Cookie`` to anonymous catalogue responses, which would otherwise stop
    Vercel from caching them at the edge.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    cache_seconds = 60

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response['Cache-Control'] = (
                f'public, max-age=0, s-maxage={self.cache_seconds}, '
                f'stale-while-revalidate={self.cache_seconds * 4}'
            )
        return response


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


class CategoryListView(PublicCatalogView):
    cache_seconds = 300
    def get(self, request):
        categories = CategoryRepository.list_categories()
        return Response(CategorySerializer(categories, many=True, context={"request": request}).data)


class ProductListView(PublicCatalogView):
    def get(self, request):
        products = ProductRepository.list_products(request.query_params)
        return Response(ProductSerializer(products, many=True, context={"request": request, 'compact': True}).data)


class FeaturedProductListView(PublicCatalogView):
    def get(self, request):
        products = ProductRepository.featured_products()
        return Response(ProductSerializer(products, many=True, context={"request": request, 'compact': True}).data)


class TopProductListView(PublicCatalogView):
    def get(self, request):
        placements = TopProduct.objects.filter(active=True, product__active=True).select_related("product__category").prefetch_related("product__images", "product__size_chart")
        return Response(TopProductSerializer(placements, many=True, context={"request": request, 'compact': True}).data)


class NavigationLinkListView(PublicCatalogView):
    cache_seconds = 300
    def get(self, request):
        links = NavigationLink.objects.filter(active=True)
        return Response(NavigationLinkSerializer(links, many=True).data)


class DiscountCampaignListView(PublicCatalogView):
    cache_seconds = 30

    def get(self, request):
        now = timezone.now()
        campaigns = (
            DiscountCampaign.objects.filter(active=True)
            .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
            .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        )
        return Response(DiscountCampaignSerializer(campaigns, many=True, context={'request': request}).data)


class ProductDetailView(PublicCatalogView):
    def get(self, request, slug):
        product = ProductRepository.get_by_slug(slug)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product, context={"request": request}).data)


class ProductAvailabilityView(APIView):
    """Return current stock without browser or edge caching."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = Product.objects.filter(slug=slug, active=True).only('id', 'slug', 'stock_quantity').first()
        if product is None:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        response = Response({
            'id': product.id,
            'slug': product.slug,
            'stock_quantity': product.stock_quantity,
            'in_stock': product.stock_quantity > 0,
        })
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response


class HomepageView(PublicCatalogView):
    """Return all database-managed homepage content in one serverless call."""

    cache_seconds = 300

    def get(self, request):
        if not settings.IS_RUNNING_TESTS:
            cached_homepage = cache.get(HOMEPAGE_CACHE_KEY)
            if cached_homepage is not None:
                return Response(cached_homepage)

        now = timezone.now()
        banners = (
            Banner.objects.filter(active=True, placement='hero')
            .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
            .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        )
        placements = (
            TopProduct.objects.filter(active=True, product__active=True)
            .select_related('product__category')
        )
        featured = Product.objects.filter(active=True, featured=True).select_related('category').order_by('-created_at')[:8]
        links = NavigationLink.objects.filter(active=True)
        context = {'request': request, 'compact': True}
        homepage = {
            'site_theme': WebsiteTheme.active_theme(),
            'banners': BannerSerializer(banners, many=True, context=context).data,
            'top_products': TopProductSerializer(placements, many=True, context=context).data,
            'featured_products': ProductSerializer(featured, many=True, context=context).data,
            'navigation_links': NavigationLinkSerializer(links, many=True).data,
        }
        if not settings.IS_RUNNING_TESTS:
            cache.set(HOMEPAGE_CACHE_KEY, homepage, timeout=self.cache_seconds)
        return Response(homepage)


class WebsiteThemeView(APIView):
    """Return the single admin-selected public website theme."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        response = Response({'theme': WebsiteTheme.active_theme()})
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response


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
        return Response(ProductSerializer(products, many=True, context={"request": request, 'compact': True}).data)


class RelatedProductListView(RecommendationListView):
    def get(self, request, slug):
        request.query_params._mutable = True
        request.query_params["product"] = slug
        return super().get(request)
