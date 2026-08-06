from django.db.models import Q, QuerySet

from .models import Category, Product


class CategoryRepository:
    @staticmethod
    def list_categories() -> QuerySet[Category]:
        return Category.objects.all()


class ProductRepository:
    ORDERING = {
        "newest": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }

    @classmethod
    def list_products(cls, params=None) -> QuerySet[Product]:
        params = params or {}
        products = Product.objects.select_related("category").prefetch_related("images").filter(active=True)

        search = params.get("search", "").strip()
        if search:
            products = products.filter(
                Q(name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(category__name__icontains=search)
            )

        category = params.get("category", "").strip()
        if category:
            products = products.filter(category__slug=category)

        min_price = params.get("min_price")
        max_price = params.get("max_price")
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        size = params.get("size", "").strip()
        color = params.get("color", "").strip()
        if size:
            products = products.filter(available_sizes__icontains=size)
        if color:
            products = products.filter(available_colors__icontains=color)

        ordering = cls.ORDERING.get(params.get("ordering", "newest"), "-created_at")
        return products.order_by(ordering)

    @staticmethod
    def featured_products() -> QuerySet[Product]:
        return Product.objects.select_related("category").prefetch_related("images").filter(active=True, featured=True).order_by("-created_at")

    @staticmethod
    def get_by_slug(slug: str):
        return Product.objects.select_related("category").prefetch_related("images").filter(active=True, slug=slug).first()
