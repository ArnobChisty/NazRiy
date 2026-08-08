from django.contrib import admin
from django.db.models import Count, Q, Sum
from django.urls import reverse
from django.utils.html import format_html

from .models import Banner, Category, NavigationLink, Order, OrderEmailLog, OrderItem, Payment, Product, ProductImage, ProductSizeMeasurement, TopProduct
from .order_emails import send_order_confirmation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'position')
    ordering = ('position',)


class ProductSizeMeasurementInline(admin.TabularInline):
    model = ProductSizeMeasurement
    extra = 0
    fields = ('size', 'garment_bust', 'length', 'recommended_bust', 'pant_length', 'sort_order')
    ordering = ('sort_order', 'id')
    verbose_name = 'Size chart row'
    verbose_name_plural = 'Size chart (all measurements in inches)'


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
    list_display = ('name', 'category', 'price', 'stock_quantity', 'stock_state', 'active', 'featured', 'updated_at')
    list_filter = ('category', StockLevelFilter, 'active', 'featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('stock_quantity', 'active', 'featured')
    inlines = [ProductSizeMeasurementInline, ProductImageInline]

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

    def save_model(self, request, obj, form, change):
        obj.url = NavigationLink.canonical_url(obj.label, obj.url)
        super().save_model(request, obj, form, change)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'product_name', 'size', 'color', 'unit_price', 'quantity', 'line_total')


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = (
        'method', 'amount', 'status', 'idempotency_key', 'provider_reference',
        'failure_reason', 'attempts', 'created_at', 'updated_at',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'email', 'city', 'total', 'payment_status', 'confirmation_email', 'status', 'created_at')
    list_filter = ('status', 'payment__status', 'payment__method', 'city', 'created_at')
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
    inlines = [OrderItemInline, PaymentInline]
    actions = ('resend_confirmation_email',)

    @admin.display(description='Customer', ordering='name')
    def customer(self, order):
        return order.name

    @admin.display(description='Payment', ordering='payment__status')
    def payment_status(self, order):
        try:
            return order.payment.get_status_display()
        except Payment.DoesNotExist:
            return 'Not created'

    @admin.display(description='Email')
    def confirmation_email(self, order):
        latest = order.email_logs.order_by('-created_at').first()
        return latest.get_status_display() if latest else 'Not sent'

    @admin.action(description='Resend order confirmation email')
    def resend_confirmation_email(self, request, queryset):
        sent = sum(1 for order in queryset if send_order_confirmation(order.id))
        failed = queryset.count() - sent
        message = f'{sent} confirmation email(s) sent.'
        if failed:
            message += f' {failed} failed; see Order emails for details.'
        self.message_user(request, message, level='warning' if failed else 'success')


@admin.register(OrderEmailLog)
class OrderEmailLogAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'recipient', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('=order__id', 'recipient', 'subject', 'error_message')
    readonly_fields = ('order', 'recipient', 'subject', 'status', 'error_message', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Order', ordering='order_id')
    def order_link(self, log):
        url = reverse('admin:store_order_change', args=(log.order_id,))
        return format_html('<a href="{}">Order #{}</a>', url, log.order_id)

    @admin.display(description='Delivery', ordering='status')
    def status_badge(self, log):
        return format_html(
            '<span class="nz-email-status nz-email-status--{}">{}</span>',
            log.status,
            log.get_status_display(),
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/store/payment/change_list.html'
    list_display = (
        'payment_order', 'customer_details', 'method_badge', 'amount_display',
        'status_badge', 'reference_display', 'updated_display',
    )
    list_display_links = ('payment_order',)
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('=order__id', 'order__email', 'provider_reference', 'idempotency_key')
    search_help_text = 'Search by order number, customer email, transaction ID, or idempotency key.'
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = (
        'order_summary', 'customer_summary', 'method_display', 'amount_display',
        'idempotency_key', 'last_request_id',
        'provider_reference', 'failure_reason', 'attempts', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Payment overview', {'fields': ('order_summary', 'customer_summary', 'method_display', 'amount_display', 'status')}),
        ('Provider verification', {'fields': ('provider_reference', 'failure_reason', 'attempts')}),
        ('System audit', {
            'fields': ('idempotency_key', 'last_request_id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ('mark_bkash_verified', 'mark_bkash_rejected')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        totals = self.get_queryset(request).aggregate(
            total=Count('id'),
            paid=Count('id', filter=Q(status='paid')),
            pending=Count('id', filter=Q(status='pending')),
            attention=Count('id', filter=Q(status__in=('failed', 'cancelled'))),
            paid_amount=Sum('amount', filter=Q(status='paid')),
        )
        extra_context = {
            **(extra_context or {}),
            'payment_stats': {
                **totals,
                'paid_amount': f"৳{(totals['paid_amount'] or 0):,.2f}",
            },
        }
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='Order', ordering='order__id')
    def payment_order(self, payment):
        return format_html(
            '<span class="nz-payment-order">Order #{}</span><small>{}</small>',
            payment.order_id,
            payment.order.name,
        )

    @admin.display(description='Customer', ordering='order__email')
    def customer_details(self, payment):
        return format_html(
            '<span class="nz-payment-customer">{}</span><small>{}</small>',
            payment.order.email,
            payment.order.phone,
        )

    @admin.display(description='Method', ordering='method')
    def method_badge(self, payment):
        return format_html(
            '<span class="nz-payment-method nz-payment-method--{}">{}</span>',
            payment.method,
            payment.get_method_display(),
        )

    @admin.display(description='Amount', ordering='amount')
    def amount_display(self, payment):
        return format_html('<strong class="nz-payment-amount">{}</strong>', f'৳{payment.amount:,.2f}')

    @admin.display(description='Status', ordering='status')
    def status_badge(self, payment):
        return format_html(
            '<span class="nz-payment-status nz-payment-status--{}"><i></i>{}</span>',
            payment.status,
            payment.get_status_display(),
        )

    @admin.display(description='Transaction')
    def reference_display(self, payment):
        if payment.method == 'cash_on_delivery':
            return format_html('<span class="nz-payment-reference muted">{}</span>', 'Not required')
        if payment.provider_reference:
            return format_html(
                '<code class="nz-payment-reference">{}</code><small>{} verification attempt{}</small>',
                payment.provider_reference,
                payment.attempts,
                '' if payment.attempts == 1 else 's',
            )
        return format_html('<span class="nz-payment-reference waiting">{}</span>', 'Awaiting transaction ID')

    @admin.display(description='Updated', ordering='updated_at')
    def updated_display(self, payment):
        return format_html(
            '<time datetime="{}">{}</time><small>{}</small>',
            payment.updated_at.isoformat(),
            payment.updated_at.strftime('%d %b %Y'),
            payment.updated_at.strftime('%I:%M %p'),
        )

    @admin.display(description='Order')
    def order_summary(self, payment):
        url = reverse('admin:store_order_change', args=(payment.order_id,))
        return format_html('<a class="nz-payment-summary-link" href="{}">Order #{} — {}</a>', url, payment.order_id, payment.order.name)

    @admin.display(description='Customer')
    def customer_summary(self, payment):
        return format_html('{}<br><a href="mailto:{}">{}</a><br>{}', payment.order.name, payment.order.email, payment.order.email, payment.order.phone)

    @admin.display(description='Payment method')
    def method_display(self, payment):
        return payment.get_method_display()

    @admin.action(description='Verify selected bKash payments')
    def mark_bkash_verified(self, request, queryset):
        updated = 0
        for payment in queryset.select_related('order'):
            if (
                payment.method == 'bkash'
                and payment.provider_reference
                and payment.status in {'pending', 'failed'}
                and payment.order.status != 'cancelled'
            ):
                payment.status = 'paid'
                payment.failure_reason = ''
                payment.save()
                updated += 1
        self.message_user(request, f'{updated} bKash payment(s) verified.')

    @admin.action(description='Reject selected bKash payments')
    def mark_bkash_rejected(self, request, queryset):
        updated = 0
        for payment in queryset:
            if payment.method == 'bkash' and payment.status == 'pending':
                payment.status = 'failed'
                payment.failure_reason = 'The submitted bKash transaction could not be verified.'
                payment.save()
                updated += 1
        self.message_user(request, f'{updated} bKash payment(s) rejected.')


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
admin.site.index_template = 'admin/nazriy_index.html'
