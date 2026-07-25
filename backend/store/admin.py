from django.contrib import admin

from .models import Banner, Cart, CartItem, Category, NavigationLink, Order, OrderItem, Product, ProductImage, TopProduct


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'position')
    ordering = ('position',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_total', 'featured', 'sort_order')
    list_editable = ('featured', 'sort_order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'image', 'image_alt', 'featured', 'sort_order')

    @admin.display(description='Products')
    def product_total(self, category):
        return category.products.count()


class StockLevelFilter(admin.SimpleListFilter):
    title = 'inventory level'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [('out', 'Out of stock'), ('low', 'Low stock (1–5)'), ('healthy', 'Healthy stock (6+)')]

    def queryset(self, request, queryset):
        if self.value() == 'out': return queryset.filter(stock_quantity=0)
        if self.value() == 'low': return queryset.filter(stock_quantity__range=(1, 5))
        if self.value() == 'healthy': return queryset.filter(stock_quantity__gte=6)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'stock_state', 'featured', 'updated_at')
    list_filter = ('category', StockLevelFilter, 'featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('stock_quantity', 'featured')
    inlines = [ProductImageInline]

    @admin.display(description='Stock status', ordering='stock_quantity')
    def stock_state(self, product):
        if product.stock_quantity == 0: return 'Out of stock'
        if product.stock_quantity <= 5: return 'Low stock'
        return 'In stock'


@admin.register(TopProduct)
class TopProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'sort_order', 'active', 'updated_at')
    list_editable = ('sort_order', 'active')
    list_filter = ('active',)
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)
    ordering = ('sort_order', 'id')
    fields = ('product', 'showcase_image', 'image_alt', 'sort_order', 'active')


@admin.register(NavigationLink)
class NavigationLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'sort_order', 'active', 'open_in_new_tab', 'updated_at')
    list_editable = ('sort_order', 'active', 'open_in_new_tab')
    list_filter = ('active', 'open_in_new_tab')
    search_fields = ('label', 'url')
    ordering = ('sort_order', 'id')
    fields = ('label', 'url', 'sort_order', 'active', 'open_in_new_tab')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'product_name', 'size', 'color', 'unit_price', 'quantity', 'line_total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'email', 'city', 'total', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('=id', 'name', 'email', 'phone', 'address')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    readonly_fields = (
        'user', 'name', 'email', 'phone', 'address', 'city', 'postal_code',
        'subtotal', 'delivery_charge', 'total', 'inventory_restored', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Order workflow', {'fields': ('status',)}),
        ('Customer and delivery', {'fields': ('user', 'name', 'email', 'phone', 'address', 'city', 'postal_code')}),
        ('Payment summary', {'fields': ('subtotal', 'delivery_charge', 'total')}),
        ('Audit', {'fields': ('inventory_restored', 'created_at', 'updated_at')}),
    )
    inlines = [OrderItemInline]

    @admin.display(description='Customer', ordering='name')
    def customer(self, order):
        return order.name


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement', 'theme', 'sort_order', 'active', 'starts_at', 'ends_at', 'updated_at')
    list_filter = ('placement', 'theme', 'active')
    search_fields = ('title', 'eyebrow', 'description')
    list_editable = ('sort_order', 'active')
    ordering = ('placement', 'sort_order')
    fieldsets = (
        (None, {'fields': ('placement', 'active', 'sort_order', 'theme')}),
        ('Content', {'fields': ('eyebrow', 'title', 'description')}),
        ('Images', {'fields': ('desktop_image', 'mobile_image', 'image_alt', 'object_position')}),
        ('Actions', {'fields': ('primary_button_label', 'primary_button_link', 'secondary_button_label', 'secondary_button_link')}),
        ('Schedule', {'fields': ('starts_at', 'ends_at'), 'classes': ('collapse',)}),
    )


admin.site.site_header = 'NazRiy administration'
admin.site.site_title = 'NazRiy admin'
admin.site.index_title = 'Orders, inventory and content'
admin.site.register([Cart, CartItem])
