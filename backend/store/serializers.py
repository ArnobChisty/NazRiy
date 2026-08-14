from rest_framework import serializers

from .media_urls import serialized_media_url
from .models import Category, DiscountCampaign, NavigationLink, Product, ProductSizeMeasurement, TopProduct


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        # Product cards only need category text. Avoid a duplicate signed URL
        # (and the fallback product query) in compact catalogue responses.
        if self.context.get('compact'):
            return ''
        if not obj.image:
            product = obj.products.exclude(primary_image='').first()
            if not product or not product.primary_image:
                return ''
            image = product.primary_image
        else:
            image = obj.image
        return serialized_media_url(image, self.context)

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
    size_chart = serializers.SerializerMethodField()

    def _absolute_url(self, file_field):
        return serialized_media_url(file_field, self.context)

    def get_primary_image(self, obj):
        return self._absolute_url(obj.primary_image)

    def get_additional_images(self, obj):
        if self.context.get('compact'):
            return []
        return [self._absolute_url(item.image) for item in obj.images.all()]

    def get_size_chart(self, obj):
        if self.context.get('compact'):
            return []
        return ProductSizeMeasurementSerializer(obj.size_chart.all(), many=True).data

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
        return serialized_media_url(image, self.context)

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


class DiscountCampaignSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if self.context.get('compact'):
            return ''
        if not obj.image:
            return ''
        return serialized_media_url(obj.image, self.context)

    class Meta:
        model = DiscountCampaign
        fields = (
            'id', 'display_type', 'title', 'message', 'discount_code',
            'discount_type', 'discount_value', 'minimum_order_amount',
            'button_label', 'button_link', 'image', 'image_alt', 'theme',
            'popup_delay_seconds', 'show_once_per_session',
        )
