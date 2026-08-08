from rest_framework import serializers

from .models import Category, NavigationLink, Product, ProductSizeMeasurement, TopProduct


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if not obj.image:
            product = obj.products.exclude(primary_image='').first()
            if not product or not product.primary_image:
                return ''
            image = product.primary_image
        else:
            image = obj.image
        request = self.context.get('request')
        return request.build_absolute_uri(image.url) if request else image.url

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "image", "image_alt", "featured", "sort_order", "product_count")


class ProductSizeMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSizeMeasurement
        fields = ('id', 'size', 'garment_bust', 'length', 'recommended_bust', 'pant_length', 'sort_order')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True, required=False
    )
    in_stock = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    additional_images = serializers.SerializerMethodField()
    size_chart = ProductSizeMeasurementSerializer(many=True, read_only=True)

    def _absolute_url(self, file_field):
        if not file_field:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(file_field.url) if request else file_field.url

    def get_primary_image(self, obj):
        return self._absolute_url(obj.primary_image)

    def get_additional_images(self, obj):
        return [self._absolute_url(item.image) for item in obj.images.all()]

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "category", "category_id", "short_description",
            "description", "price", "primary_image", "additional_images",
            "available_sizes", "size_chart", "available_colors", "stock_quantity", "in_stock",
            "featured", "tone", "shape", "created_at", "updated_at",
        )


class TopProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        image = obj.showcase_image or obj.product.primary_image
        if not image:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(image.url) if request else image.url

    class Meta:
        model = TopProduct
        fields = ("id", "product", "image", "image_alt", "sort_order")


class NavigationLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return NavigationLink.canonical_url(obj.label, obj.url)

    class Meta:
        model = NavigationLink
        fields = ("id", "label", "url", "sort_order", "open_in_new_tab")
