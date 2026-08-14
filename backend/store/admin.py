from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q, Sum
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Banner, Category, DiscountCampaign, NavigationLink, Order, OrderEmailLog, OrderItem, Payment, Product, ProductImage, ProductSizeMeasurement, TopProduct, WebsiteTheme
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


class ProductAdminForm(forms.ModelForm):
    available_sizes = forms.CharField(
        required=False,
        label='Available sizes',
        help_text='Enter sizes separated by commas, for example: S, M, L, XL',
        widget=forms.TextInput(attrs={'placeholder': 'S, M, L, XL'}),
    )
    available_colors = forms.CharField(
        required=False,
        label='Available colours',
        help_text='Enter colours separated by commas, for example: Black, Rose, Ivory',
        widget=forms.TextInput(attrs={'placeholder': 'Black, Rose, Ivory'}),
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['available_sizes'] = ', '.join(self.instance.available_sizes or [])
            self.initial['available_colors'] = ', '.join(self.instance.available_colors or [])

    @staticmethod
    def _comma_separated_values(value):
        return list(dict.fromkeys(item.strip() for item in value.split(',') if item.strip()))

    def clean_available_sizes(self):
        return self._comma_separated_values(self.cleaned_data.get('available_sizes', ''))

    def clean_available_colors(self):
        return self._comma_separated_values(self.cleaned_data.get('available_colors', ''))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_thumbnail', 'name', 'product_total', 'featured', 'sort_order')
    list_display_links = ('category_thumbnail', 'name')
    list_editable = ('featured', 'sort_order')
    search_fields = ('name', 'description')
    search_help_text = 'Search categories by name or description.'
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('category_image_preview',)
    fieldsets = (
        ('Category details', {'fields': ('name', 'description')}),
        ('Category image', {'fields': ('category_image_preview', 'image', 'image_alt'), 'description': 'Use a clear landscape or square image. Add descriptive alternative text for accessibility.'}),
        ('Storefront placement', {'fields': ('featured', 'sort_order'), 'description': 'Featured categories can appear on the homepage. Lower numbers appear first.'}),
        ('Search-friendly URL', {'fields': ('slug',), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(admin_product_count=Count('products'))

    @admin.display(description='Image')
    def category_thumbnail(self, category):
        return self._image(category.image if category else None, 'nz-catalogue-thumb')

    @admin.display(description='Current image')
    def category_image_preview(self, category):
        return self._image(category.image if category else None, 'nz-catalogue-preview')

    @staticmethod
    def _image(image, css_class):
        if not image:
            return format_html('<span class="nz-image-placeholder">{}</span>', 'No image')
        return format_html('<img class="{}" src="{}" alt="">', css_class, image.url)

    @admin.display(description='Products')
    def product_total(self, category):
        return category.admin_product_count


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
    form = ProductAdminForm
    list_display = ('product_thumbnail', 'name', 'category', 'price_display', 'stock_quantity', 'stock_state', 'active', 'featured', 'updated_at')
    list_display_links = ('product_thumbnail', 'name')
    list_filter = ('category', StockLevelFilter, 'active', 'featured')
    search_fields = ('name', 'short_description', 'description', 'slug')
    search_help_text = 'Search by product name, description, or URL slug.'
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('stock_quantity', 'active', 'featured')
    readonly_fields = ('primary_image_preview', 'created_at', 'updated_at')
    fieldsets = (
        ('Product essentials', {'fields': ('name', 'category', 'price', 'stock_quantity', 'active'), 'description': 'The essential information needed to sell this product.'}),
        ('Storefront description', {'fields': ('short_description', 'description')}),
        ('Main product image', {'fields': ('primary_image_preview', 'primary_image'), 'description': 'Upload the main image here. Add extra product photos in the gallery section below.'}),
        ('Customer options', {'fields': ('available_sizes', 'available_colors'), 'description': 'Type each option separated by a comma. No JSON formatting is required.'}),
        ('Homepage and catalogue', {'fields': ('featured',), 'description': 'Featured products may be highlighted in storefront sections.'}),
        ('Advanced display settings', {'fields': ('tone', 'shape', 'slug', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    inlines = [ProductSizeMeasurementInline, ProductImageInline]
    actions = ('make_active', 'make_inactive', 'make_featured', 'remove_featured')

    @admin.display(description='Image')
    def product_thumbnail(self, product):
        if not product or not product.primary_image:
            return format_html('<span class="nz-image-placeholder">{}</span>', 'No image')
        return format_html('<img class="nz-catalogue-thumb" src="{}" alt="">', product.primary_image.url)

    @admin.display(description='Current main image')
    def primary_image_preview(self, product):
        if not product or not product.primary_image:
            return format_html('<span class="nz-image-placeholder large">{}</span>', 'Upload a main product image below')
        return format_html('<img class="nz-catalogue-preview" src="{}" alt="">', product.primary_image.url)

    @admin.display(description='Price', ordering='price')
    def price_display(self, product):
        return format_html('<strong class="nz-catalogue-price">{}</strong>', f'৳{product.price:,.2f}')

    @admin.display(description='Stock status', ordering='stock_quantity')
    def stock_state(self, product):
        if product.stock_quantity == 0:
            state, label = 'out', 'Out of stock'
        elif product.stock_quantity <= 5:
            state, label = 'low', 'Low stock'
        else:
            state, label = 'healthy', 'In stock'
        return format_html('<span class="nz-stock-badge nz-stock-badge--{}">{}</span>', state, label)

    @admin.action(description='Make selected products visible')
    def make_active(self, request, queryset):
        self.message_user(request, f'{queryset.update(active=True)} product(s) made visible.', level=messages.SUCCESS)

    @admin.action(description='Hide selected products from customers')
    def make_inactive(self, request, queryset):
        self.message_user(request, f'{queryset.update(active=False)} product(s) hidden.', level=messages.SUCCESS)

    @admin.action(description='Feature selected products')
    def make_featured(self, request, queryset):
        self.message_user(request, f'{queryset.update(featured=True)} product(s) featured.', level=messages.SUCCESS)

    @admin.action(description='Remove selected products from featured sections')
    def remove_featured(self, request, queryset):
        self.message_user(request, f'{queryset.update(featured=False)} product(s) removed from featured sections.', level=messages.SUCCESS)


@admin.register(TopProduct)
class TopProductAdmin(admin.ModelAdmin):
    list_display = ('showcase_thumbnail', 'product', 'product_category', 'sort_order', 'active', 'updated_at')
    list_display_links = ('showcase_thumbnail', 'product')
    list_editable = ('sort_order', 'active')
    list_filter = ('active',)
    search_fields = ('product__name',)
    search_help_text = 'Search homepage products by product name.'
    autocomplete_fields = ('product',)
    ordering = ('sort_order', 'id')
    readonly_fields = ('showcase_image_preview',)
    fieldsets = (
        ('Homepage product', {'fields': ('product', 'active', 'sort_order'), 'description': 'Choose the product, turn it on, and use a lower display order to show it earlier.'}),
        ('Optional homepage image', {'fields': ('showcase_image_preview', 'showcase_image', 'image_alt'), 'description': 'Leave this blank to automatically use the product’s main image.'}),
    )

    @admin.display(description='Preview')
    def showcase_thumbnail(self, placement):
        image = placement.showcase_image or placement.product.primary_image
        if not image:
            return format_html('<span class="nz-image-placeholder">{}</span>', 'No image')
        return format_html('<img class="nz-catalogue-thumb" src="{}" alt="">', image.url)

    @admin.display(description='Current homepage image')
    def showcase_image_preview(self, placement):
        if not placement or not placement.pk:
            return format_html('<span class="nz-image-placeholder large">{}</span>', 'Choose a product or upload a custom image')
        image = placement.showcase_image or placement.product.primary_image
        if not image:
            return format_html('<span class="nz-image-placeholder large">{}</span>', 'This product has no image yet')
        return format_html('<img class="nz-catalogue-preview" src="{}" alt="">', image.url)

    @admin.display(description='Category', ordering='product__category__name')
    def product_category(self, placement):
        return placement.product.category


@admin.register(NavigationLink)
class NavigationLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'sort_order', 'active', 'open_in_new_tab', 'updated_at')
    list_editable = ('sort_order', 'active', 'open_in_new_tab')
    list_filter = ('active', 'open_in_new_tab')
    search_fields = ('label', 'url')
    ordering = ('sort_order', 'id')
    fieldsets = (
        ('Menu item', {'fields': ('label', 'url'), 'description': 'Use a simple website path such as /products, /account, or /#about.'}),
        ('Display settings', {'fields': ('active', 'sort_order', 'open_in_new_tab'), 'description': 'Lower display-order numbers appear first in the website menu.'}),
    )

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
    fields = (
        'method', 'amount', 'status', 'provider_reference', 'failure_reason',
        'attempts', 'created_at', 'updated_at', 'idempotency_key',
    )
    readonly_fields = (
        'method', 'amount', 'idempotency_key', 'provider_reference',
        'failure_reason', 'attempts', 'created_at', 'updated_at',
    )
    verbose_name = 'Payment review'
    verbose_name_plural = 'Payment review'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/store/order/change_list.html'
    list_display = (
        'order_number', 'customer_summary', 'order_total', 'payment_method_badge',
        'payment_status_badge', 'transaction_reference', 'fulfilment_status_badge',
        'created_display',
    )
    list_display_links = ('order_number', 'customer_summary')
    list_filter = ('status', 'payment__status', 'payment__method', 'city', 'created_at')
    search_fields = ('=id', 'name', 'email', 'phone', 'address', 'payment__provider_reference')
    search_help_text = 'Search by order number, customer, phone, address, or bKash transaction ID.'
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = (
        'user', 'name', 'email', 'phone', 'address', 'city', 'postal_code',
        'subtotal', 'delivery_charge', 'discount_campaign', 'discount_code', 'discount_amount',
        'total', 'inventory_restored', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Fulfilment workflow', {'fields': ('status',), 'description': 'Update the delivery stage here. Payment review is available below on the same page.'}),
        ('Customer and delivery', {'fields': ('user', 'name', 'email', 'phone', 'address', 'city', 'postal_code')}),
        ('Order totals', {'fields': ('subtotal', 'delivery_charge', 'discount_campaign', 'discount_code', 'discount_amount', 'total')}),
        ('Audit', {'fields': ('inventory_restored', 'created_at', 'updated_at')}),
    )
    inlines = [OrderItemInline, PaymentInline]
    actions = (
        'verify_bkash_payments', 'reject_bkash_payments', 'mark_as_shipped',
        'mark_as_delivered', 'cancel_orders', 'resend_confirmation_email',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment', 'user').prefetch_related('items', 'email_logs')

    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and request.POST.get('_quick_fulfilment'):
            return self._quick_fulfilment(request)
        if request.method == 'POST' and request.POST.get('_quick_payment'):
            return self._quick_payment(request)

        totals = self.get_queryset(request).aggregate(
            total_orders=Count('id'),
            paid_revenue=Sum('total', filter=Q(payment__status='paid')),
            pending_payments=Count('id', filter=Q(payment__status='pending')),
            awaiting_fulfilment=Count('id', filter=Q(status__in=('confirmed', 'shipped'))),
        )
        extra_context = {
            **(extra_context or {}),
            'order_stats': {
                **totals,
                'paid_revenue': f"৳{(totals['paid_revenue'] or 0):,.2f}",
            },
        }
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='Order', ordering='id')
    def order_number(self, order):
        item_count = order.items.count()
        return format_html('<strong class="nz-order-number">#{}</strong><small>{} item{}</small>', f'{order.id:04d}', item_count, '' if item_count == 1 else 's')

    @admin.display(description='Customer', ordering='name')
    def customer_summary(self, order):
        return format_html('<strong class="nz-order-customer">{}</strong><small>{}<br>{}</small>', order.name, order.email, order.phone)

    @admin.display(description='Total', ordering='total')
    def order_total(self, order):
        return format_html('<strong class="nz-payment-amount">{}</strong>', f'৳{order.total:,.2f}')

    @admin.display(description='Method', ordering='payment__method')
    def payment_method_badge(self, order):
        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return format_html('<span class="nz-payment-reference muted">{}</span>', 'Not created')
        return format_html('<span class="nz-payment-method nz-payment-method--{}">{}</span>', payment.method, payment.get_method_display())

    @admin.display(description='Payment', ordering='payment__status')
    def payment_status_badge(self, order):
        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return format_html('<span class="nz-payment-status nz-payment-status--cancelled"><i></i>{}</span>', 'Not created')
        badge = format_html(
            '<span class="nz-payment-status nz-payment-status--{}"><i></i>{}</span>',
            payment.status,
            payment.get_status_display(),
        )
        if order.status == 'cancelled' or payment.status not in {'pending', 'failed'}:
            return badge
        if payment.method == 'cash_on_delivery':
            action, label = 'collect', 'Paid'
        elif payment.method == 'bkash' and payment.provider_reference:
            action, label = 'verify', 'Verify'
        else:
            return badge
        return format_html(
            '<span class="nz-payment-control">{}<button type="submit" '
            'name="_quick_payment" value="{}:{}" aria-label="{} payment for order {}">{}</button></span>',
            badge,
            action,
            order.pk,
            label,
            order.pk,
            label,
        )

    @admin.display(description='Transaction', ordering='payment__provider_reference')
    def transaction_reference(self, order):
        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return '—'
        if payment.method == 'cash_on_delivery':
            return format_html('<span class="nz-payment-reference muted">{}</span>', 'Not required')
        if payment.provider_reference:
            return format_html('<code class="nz-payment-reference">{}</code>', payment.provider_reference)
        return format_html('<span class="nz-payment-reference waiting">{}</span>', 'Awaiting ID')

    @admin.display(description='Fulfilment', ordering='status')
    def fulfilment_status_badge(self, order):
        badge = format_html(
            '<span class="nz-order-status nz-order-status--{}"><i></i>{}</span>',
            order.status,
            order.get_status_display(),
        )
        next_action = {
            'confirmed': ('ship', 'Ship'),
            'shipped': ('deliver', 'Deliver'),
        }.get(order.status)
        if not next_action:
            return badge
        action, label = next_action
        return format_html(
            '<span class="nz-fulfilment-control">{}<button type="submit" '
            'name="_quick_fulfilment" value="{}:{}" aria-label="{} order {}">{}</button></span>',
            badge,
            action,
            order.pk,
            label,
            order.pk,
            label,
        )

    @admin.display(description='Placed', ordering='created_at')
    def created_display(self, order):
        return format_html('<time datetime="{}">{}</time><small>{}</small>', order.created_at.isoformat(), order.created_at.strftime('%d %b %Y'), order.created_at.strftime('%I:%M %p'))

    @admin.display(description='Email')
    def confirmation_email(self, order):
        latest = order.email_logs.order_by('-created_at').first()
        return latest.get_status_display() if latest else 'Not sent'

    def _change_order_status(self, request, queryset, target, source_statuses, label):
        updated = skipped = 0
        for order in queryset:
            if order.status not in source_statuses:
                skipped += 1
                continue
            order.status = target
            try:
                order.save()
                updated += 1
            except ValidationError:
                skipped += 1
        self.message_user(request, f'{updated} order(s) marked {label}.' + (f' {skipped} skipped because their current stage does not allow this action.' if skipped else ''), level=messages.WARNING if skipped else messages.SUCCESS)

    def _quick_fulfilment(self, request):
        try:
            action, raw_order_id = request.POST['_quick_fulfilment'].split(':', 1)
            order_id = int(raw_order_id)
        except (KeyError, TypeError, ValueError):
            self.message_user(request, 'That fulfilment action was not valid.', level=messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

        order = self.get_queryset(request).filter(pk=order_id).first()
        transitions = {
            ('ship', 'confirmed'): ('shipped', 'shipped'),
            ('deliver', 'shipped'): ('delivered', 'delivered'),
        }
        transition = transitions.get((action, order.status if order else None))
        if not order or not self.has_change_permission(request, order) or not transition:
            self.message_user(request, 'This order cannot move to that fulfilment stage.', level=messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())

        target, label = transition
        order.status = target
        try:
            order.save()
        except ValidationError:
            self.message_user(request, 'This order cannot move to that fulfilment stage.', level=messages.WARNING)
        else:
            self.message_user(request, f'Order #{order.pk} marked {label}.', level=messages.SUCCESS)
        return HttpResponseRedirect(request.get_full_path())

    def _quick_payment(self, request):
        try:
            action, raw_order_id = request.POST['_quick_payment'].split(':', 1)
            order_id = int(raw_order_id)
        except (KeyError, TypeError, ValueError):
            self.message_user(request, 'That payment action was not valid.', level=messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

        order = self.get_queryset(request).filter(pk=order_id).first()
        try:
            payment = order.payment if order else None
        except Payment.DoesNotExist:
            payment = None

        can_collect = (
            action == 'collect'
            and payment
            and payment.method == 'cash_on_delivery'
            and payment.status in {'pending', 'failed'}
        )
        can_verify = (
            action == 'verify'
            and payment
            and payment.method == 'bkash'
            and bool(payment.provider_reference)
            and payment.status in {'pending', 'failed'}
        )
        if (
            not order
            or not payment
            or order.status == 'cancelled'
            or not self.has_change_permission(request, order)
            or not (can_collect or can_verify)
        ):
            self.message_user(request, 'This payment cannot be marked as paid.', level=messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())

        payment.status = 'paid'
        payment.failure_reason = ''
        try:
            payment.save()
        except ValidationError:
            self.message_user(request, 'This payment cannot be marked as paid.', level=messages.WARNING)
        else:
            self.message_user(request, f'Payment for order #{order.pk} marked paid.', level=messages.SUCCESS)
        return HttpResponseRedirect(request.get_full_path())

    @admin.action(description='Payment: verify selected bKash transactions')
    def verify_bkash_payments(self, request, queryset):
        updated = skipped = 0
        for order in queryset:
            try:
                payment = order.payment
            except Payment.DoesNotExist:
                skipped += 1
                continue
            if payment.method == 'bkash' and payment.provider_reference and payment.status in {'pending', 'failed'} and order.status != 'cancelled':
                payment.status = 'paid'
                payment.failure_reason = ''
                payment.save()
                updated += 1
            else:
                skipped += 1
        self.message_user(request, f'{updated} bKash payment(s) verified.' + (f' {skipped} skipped.' if skipped else ''), level=messages.WARNING if skipped else messages.SUCCESS)

    @admin.action(description='Payment: reject selected bKash transactions')
    def reject_bkash_payments(self, request, queryset):
        updated = skipped = 0
        for order in queryset:
            try:
                payment = order.payment
            except Payment.DoesNotExist:
                skipped += 1
                continue
            if payment.method == 'bkash' and payment.status == 'pending':
                payment.status = 'failed'
                payment.failure_reason = 'The submitted bKash transaction could not be verified.'
                payment.save()
                updated += 1
            else:
                skipped += 1
        self.message_user(request, f'{updated} bKash payment(s) rejected.' + (f' {skipped} skipped.' if skipped else ''), level=messages.WARNING if skipped else messages.SUCCESS)

    @admin.action(description='Fulfilment: mark selected orders as shipped')
    def mark_as_shipped(self, request, queryset):
        self._change_order_status(request, queryset, 'shipped', {'confirmed'}, 'as shipped')

    @admin.action(description='Fulfilment: mark selected orders as delivered')
    def mark_as_delivered(self, request, queryset):
        self._change_order_status(request, queryset, 'delivered', {'shipped'}, 'as delivered')

    @admin.action(description='Fulfilment: cancel selected confirmed orders')
    def cancel_orders(self, request, queryset):
        self._change_order_status(request, queryset, 'cancelled', {'confirmed'}, 'as cancelled')

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
        'provider_reference', 'provider_payment_id', 'provider_invoice',
        'provider_redirect_url', 'provider_payload', 'failure_reason', 'attempts',
        'created_at', 'updated_at',
    )
    fieldsets = (
        ('Payment overview', {'fields': ('order_summary', 'customer_summary', 'method_display', 'amount_display', 'status')}),
        ('Provider verification', {'fields': (
            'provider_reference', 'provider_payment_id', 'provider_invoice',
            'provider_redirect_url', 'provider_payload', 'failure_reason', 'attempts',
        )}),
        ('System audit', {
            'fields': ('idempotency_key', 'last_request_id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ('mark_bkash_verified', 'mark_bkash_rejected')

    def get_model_perms(self, request):
        # Payments are managed from the unified Orders & payments workspace.
        # Keep these URLs registered for bookmarks and backwards compatibility.
        return {}

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
    list_display = ('banner_thumbnail', 'title', 'placement', 'schedule_status', 'theme', 'sort_order', 'active', 'updated_at')
    list_display_links = ('banner_thumbnail', 'title')
    list_filter = ('placement', 'theme', 'active')
    search_fields = ('title', 'eyebrow', 'description')
    search_help_text = 'Search banners by title or message.'
    list_editable = ('sort_order', 'active')
    ordering = ('placement', 'sort_order')
    readonly_fields = ('desktop_image_preview',)
    fieldsets = (
        ('Visibility and placement', {'fields': ('placement', 'active', 'sort_order', 'theme'), 'description': 'Turn the banner on and choose where it belongs. Lower order numbers appear first.'}),
        ('Customer message', {'fields': ('eyebrow', 'title', 'description')}),
        ('Banner images', {'fields': ('desktop_image_preview', 'desktop_image', 'mobile_image', 'image_alt', 'object_position'), 'description': 'Desktop image is required. Mobile image is optional but recommended.'}),
        ('Buttons', {'fields': ('primary_button_label', 'primary_button_link', 'secondary_button_label', 'secondary_button_link')}),
        ('Automatic schedule', {'fields': ('starts_at', 'ends_at'), 'description': 'Leave blank to keep the banner available without a time limit.'}),
    )

    @admin.display(description='Preview')
    def banner_thumbnail(self, banner):
        if not banner or not banner.desktop_image:
            return format_html('<span class="nz-image-placeholder">{}</span>', 'No image')
        return format_html('<img class="nz-banner-thumb" src="{}" alt="">', banner.desktop_image.url)

    @admin.display(description='Current desktop image')
    def desktop_image_preview(self, banner):
        if not banner or not banner.desktop_image:
            return format_html('<span class="nz-image-placeholder large">{}</span>', 'Upload a desktop banner image below')
        return format_html('<img class="nz-banner-preview" src="{}" alt="">', banner.desktop_image.url)

    @admin.display(description='Schedule', ordering='starts_at')
    def schedule_status(self, banner):
        now = timezone.now()
        if not banner.active:
            state, label = 'inactive', 'Inactive'
        elif banner.starts_at and banner.starts_at > now:
            state, label = 'scheduled', 'Scheduled'
        elif banner.ends_at and banner.ends_at < now:
            state, label = 'ended', 'Ended'
        else:
            state, label = 'live', 'Live now'
        return format_html('<span class="nz-campaign-state nz-campaign-state--{}">{}</span>', state, label)


@admin.register(DiscountCampaign)
class DiscountCampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_preview', 'name', 'display_badge', 'customer_offer', 'schedule_status', 'sort_order', 'active', 'updated_at')
    list_display_links = ('campaign_preview', 'name')
    list_filter = ('display_type', 'discount_type', 'theme', 'active')
    search_fields = ('name', 'title', 'message', 'discount_code')
    search_help_text = 'Search by campaign name, customer message, or discount code.'
    list_editable = ('sort_order', 'active')
    readonly_fields = ('campaign_image_preview', 'created_at', 'updated_at')
    fieldsets = (
        ('Campaign setup', {'fields': ('name', 'display_type', 'active', 'theme', 'sort_order'), 'description': 'Choose announcement banner for a slim site-wide message or popup for a larger promotion.'}),
        ('Customer offer', {'fields': ('title', 'message', 'discount_code'), 'description': 'Codes are case-insensitive and must be unique.'}),
        ('Discount rules', {'fields': ('discount_type', 'discount_value', 'minimum_order_amount', 'maximum_discount_amount', 'usage_limit', 'per_customer_limit'), 'description': 'Configure the server-enforced discount and customer usage limits. Discount value is ignored for free delivery.'}),
        ('Action button', {'fields': ('button_label', 'button_link')}),
        ('Campaign image', {'fields': ('campaign_image_preview', 'image', 'image_alt'), 'description': 'Optional for announcement banners; recommended for promotional popups.'}),
        ('Automatic schedule', {'fields': ('starts_at', 'ends_at'), 'description': 'Leave blank to run immediately without an end date.'}),
        ('Popup behaviour', {'fields': ('popup_delay_seconds', 'show_once_per_session'), 'description': 'These settings only affect popup campaigns.'}),
        ('Audit information', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Preview')
    def campaign_preview(self, campaign):
        if campaign and campaign.image:
            return format_html('<img class="nz-banner-thumb" src="{}" alt="">', campaign.image.url)
        return format_html('<span class="nz-campaign-swatch nz-campaign-swatch--{}">%</span>', campaign.theme if campaign else 'burgundy')

    @admin.display(description='Current campaign image')
    def campaign_image_preview(self, campaign):
        if not campaign or not campaign.image:
            return format_html('<span class="nz-image-placeholder large">{}</span>', 'Optional campaign image')
        return format_html('<img class="nz-banner-preview" src="{}" alt="">', campaign.image.url)

    @admin.display(description='Format', ordering='display_type')
    def display_badge(self, campaign):
        return format_html('<span class="nz-display-badge nz-display-badge--{}">{}</span>', campaign.display_type, campaign.get_display_type_display())

    @admin.display(description='Offer')
    def customer_offer(self, campaign):
        if campaign.discount_code:
            return format_html('<strong>{}</strong><small>Code: <code>{}</code></small>', campaign.title, campaign.discount_code)
        return format_html('<strong>{}</strong><small>{}</small>', campaign.title, campaign.message or 'No discount code')

    @admin.display(description='Schedule', ordering='starts_at')
    def schedule_status(self, campaign):
        now = timezone.now()
        if not campaign.active:
            state, label = 'inactive', 'Inactive'
        elif campaign.starts_at and campaign.starts_at > now:
            state, label = 'scheduled', 'Scheduled'
        elif campaign.ends_at and campaign.ends_at < now:
            state, label = 'ended', 'Ended'
        else:
            state, label = 'live', 'Live now'
        return format_html('<span class="nz-campaign-state nz-campaign-state--{}">{}</span>', state, label)


@admin.register(WebsiteTheme)
class WebsiteThemeAdmin(admin.ModelAdmin):
    change_list_template = 'admin/store/websitetheme/change_list.html'
    list_display = ('theme_preview', 'updated_at')
    readonly_fields = ('updated_at',)
    fields = ('theme', 'updated_at')

    def get_urls(self):
        custom_urls = [
            path(
                'set/<str:theme>/',
                self.admin_site.admin_view(self.set_theme),
                name='store_websitetheme_set_theme',
            ),
        ]
        return custom_urls + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        context = {
            'active_theme': WebsiteTheme.active_theme(),
            'theme_choices': WebsiteTheme.THEME_CHOICES,
            **(extra_context or {}),
        }
        return super().changelist_view(request, extra_context=context)

    def set_theme(self, request, theme):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        if not self.has_change_permission(request):
            raise PermissionDenied
        valid_themes = dict(WebsiteTheme.THEME_CHOICES)
        if theme not in valid_themes:
            self.message_user(request, 'That website theme is not available.', level=messages.ERROR)
        else:
            setting = WebsiteTheme(theme=theme)
            setting.save()
            self.message_user(
                request,
                f'Website theme changed to {valid_themes[theme]}.',
                level=messages.SUCCESS,
            )
        return HttpResponseRedirect(reverse('admin:store_websitetheme_changelist'))

    @admin.display(description='Current website theme', ordering='theme')
    def theme_preview(self, setting):
        colors = {
            'dark': ('#151311', '#f5efe6'),
            'white': ('#ffffff', '#27352e'),
            'pink': ('#f8dce6', '#6e2945'),
        }
        background, foreground = colors[setting.theme]
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:10px">'
            '<i style="width:28px;height:28px;border-radius:50%;background:{};border:1px solid #aaa"></i>'
            '<strong style="color:{}">{}</strong></span>',
            background,
            foreground,
            setting.get_theme_display(),
        )

    def has_add_permission(self, request):
        return not WebsiteTheme.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'NazRiy administration'
admin.site.site_title = 'NazRiy admin'
admin.site.index_title = 'Orders, inventory and content'
admin.site.index_template = 'admin/nazriy_index.html'
