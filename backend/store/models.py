from decimal import Decimal
import uuid
from urllib.parse import unquote_plus
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils.text import slugify

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True); slug=models.SlugField(max_length=120,unique=True,blank=True); description=models.TextField(blank=True); image=models.FileField(upload_to='categories/',blank=True); image_alt=models.CharField(max_length=180,blank=True); featured=models.BooleanField(default=True); sort_order=models.PositiveSmallIntegerField(default=0)
    class Meta: ordering=['sort_order','name']; verbose_name_plural='categories'
    def save(self,*args,**kwargs):
        if not self.slug:self.slug=slugify(self.name)
        super().save(*args,**kwargs)
    def __str__(self):return self.name

class Product(models.Model):
    category=models.ForeignKey(Category,related_name='products',on_delete=models.PROTECT); name=models.CharField(max_length=160); slug=models.SlugField(max_length=180,unique=True,blank=True); short_description=models.CharField(max_length=240,blank=True); description=models.TextField(); price=models.DecimalField(max_digits=10,decimal_places=2); primary_image=models.FileField(upload_to='products/primary/',blank=True); available_sizes=models.JSONField(default=list,blank=True); available_colors=models.JSONField(default=list,blank=True); stock_quantity=models.PositiveIntegerField(default=0); active=models.BooleanField(default=True); featured=models.BooleanField(default=False); tone=models.CharField(max_length=30,default='sand'); shape=models.CharField(max_length=40,default='vase-shape'); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
    def save(self,*args,**kwargs):
        if not self.slug:
            base=slugify(self.name); slug=base; counter=2
            while Product.objects.exclude(pk=self.pk).filter(slug=slug).exists():slug=f'{base}-{counter}';counter+=1
            self.slug=slug
        super().save(*args,**kwargs)
    @property
    def in_stock(self):return self.stock_quantity>0
    def __str__(self):return self.name

class ProductImage(models.Model):
    product=models.ForeignKey(Product,related_name='images',on_delete=models.CASCADE); image=models.FileField(upload_to='products/gallery/'); alt_text=models.CharField(max_length=180,blank=True); position=models.PositiveSmallIntegerField(default=0)
    class Meta: ordering=['position','id']
    def __str__(self):return f'{self.product.name} image {self.position+1}'


class ProductSizeMeasurement(models.Model):
    product = models.ForeignKey(Product, related_name='size_chart', on_delete=models.CASCADE)
    size = models.CharField(max_length=12)
    garment_bust = models.DecimalField(max_digits=5, decimal_places=1, help_text='Finished garment bust in inches.')
    length = models.DecimalField(max_digits=5, decimal_places=1, help_text='Top length in inches.')
    recommended_bust = models.CharField(max_length=20, help_text='Recommended body bust range in inches, for example 32-34.')
    pant_length = models.DecimalField(max_digits=5, decimal_places=1, help_text='Pant length in inches.')
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['product', 'size'], name='unique_product_size_measurement'),
        ]
        verbose_name = 'size measurement'
        verbose_name_plural = 'size measurements'

    def __str__(self):
        return f'{self.product.name} - {self.size}'

class TopProduct(models.Model):
    product=models.OneToOneField(Product,related_name='homepage_placement',on_delete=models.CASCADE); showcase_image=models.FileField(upload_to='top-products/',blank=True,help_text='Optional homepage image. Leave blank to use the product primary image.'); image_alt=models.CharField(max_length=180,blank=True); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','id']; verbose_name='top product'; verbose_name_plural='top products'
    def __str__(self):return self.product.name

class NavigationLink(models.Model):
    label=models.CharField(max_length=60); url=models.CharField(max_length=240,help_text='Use a site path such as /products or /#about.'); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); open_in_new_tab=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','id']; verbose_name='navigation link'; verbose_name_plural='navigation links'
    @staticmethod
    def canonical_url(label, url):
        """Keep legacy Women links compatible with the product catalogue."""
        decoded = unquote_plus((url or '').strip()).lower()
        if (label or '').strip().casefold() == 'women' and decoded.startswith('/products') and 'category=' in decoded:
            return '/products?view=women'
        return url
    def save(self,*args,**kwargs):
        self.url=self.canonical_url(self.label,self.url)
        super().save(*args,**kwargs)
    def __str__(self):return self.label

class Banner(models.Model):
    PLACEMENTS=[('hero','Homepage hero'),('promotion','Promotional banner'),('category','Category banner')]
    THEMES=[('forest','Forest'),('burgundy','Burgundy'),('sage','Sage'),('neutral','Neutral')]
    placement=models.CharField(max_length=20,choices=PLACEMENTS,default='hero'); eyebrow=models.CharField(max_length=100,blank=True); title=models.CharField(max_length=180); description=models.TextField(blank=True); desktop_image=models.FileField(upload_to='banners/desktop/'); mobile_image=models.FileField(upload_to='banners/mobile/',blank=True); image_alt=models.CharField(max_length=180); primary_button_label=models.CharField(max_length=60,default='Shop now'); primary_button_link=models.CharField(max_length=240,default='/products'); secondary_button_label=models.CharField(max_length=60,blank=True); secondary_button_link=models.CharField(max_length=240,blank=True); theme=models.CharField(max_length=20,choices=THEMES,default='forest'); object_position=models.CharField(max_length=40,default='center center',help_text='CSS object-position, for example: center 42%'); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); starts_at=models.DateTimeField(blank=True,null=True); ends_at=models.DateTimeField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:ordering=['sort_order','id']
    def __str__(self):return f'{self.get_placement_display()}: {self.title}'


class DiscountCampaign(models.Model):
    DISPLAY_CHOICES = [
        ('announcement', 'Discount announcement banner'),
        ('popup', 'Discount popup'),
    ]
    THEME_CHOICES = [
        ('forest', 'Forest green'),
        ('burgundy', 'Burgundy'),
        ('pink', 'Soft pink'),
        ('black', 'Black'),
    ]
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage off'),
        ('fixed', 'Fixed amount off'),
        ('free_delivery', 'Free delivery'),
    ]

    name = models.CharField(max_length=100, help_text='Internal name for staff, for example Eid sale 2026.')
    display_type = models.CharField(max_length=20, choices=DISPLAY_CHOICES, default='announcement')
    title = models.CharField(max_length=140)
    message = models.CharField(max_length=280, blank=True)
    discount_code = models.CharField(max_length=40, blank=True, help_text='Optional code customers can copy, for example EID20.')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'), help_text='Percentage or fixed BDT amount. Ignored for free delivery.')
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Optional cap for percentage discounts.')
    usage_limit = models.PositiveIntegerField(blank=True, null=True, help_text='Maximum successful checkouts across all customers. Leave blank for unlimited.')
    per_customer_limit = models.PositiveSmallIntegerField(default=1, help_text='Maximum non-cancelled orders per customer.')
    button_label = models.CharField(max_length=50, blank=True, default='Shop now')
    button_link = models.CharField(max_length=240, blank=True, default='/products')
    image = models.FileField(upload_to='discount-campaigns/', blank=True, help_text='Optional. Most useful for popup campaigns.')
    image_alt = models.CharField(max_length=180, blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='burgundy')
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    popup_delay_seconds = models.PositiveSmallIntegerField(default=3, help_text='Only used for popups. Recommended: 3 to 8 seconds.')
    show_once_per_session = models.BooleanField(default=True, help_text='Prevents the same popup repeatedly interrupting one visitor.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'discount campaign'
        verbose_name_plural = 'discount campaigns'
        constraints = [
            models.UniqueConstraint(
                Lower('discount_code'),
                condition=~Q(discount_code=''),
                name='unique_discount_campaign_code_ci',
            ),
        ]

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at': 'The end time must be after the start time.'})
        self.discount_code = self.discount_code.strip().upper()
        if self.discount_code:
            duplicate = type(self).objects.filter(discount_code__iexact=self.discount_code).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError({'discount_code': 'This promo code is already used by another campaign.'})
        if self.discount_type == 'percentage' and not Decimal('0') < self.discount_value <= Decimal('100'):
            raise ValidationError({'discount_value': 'Percentage discounts must be greater than 0 and no more than 100.'})
        if self.discount_type == 'fixed' and self.discount_value <= 0:
            raise ValidationError({'discount_value': 'Fixed discounts must be greater than 0.'})
        if self.maximum_discount_amount is not None and self.maximum_discount_amount <= 0:
            raise ValidationError({'maximum_discount_amount': 'The maximum discount must be greater than 0.'})

    def __str__(self):
        return f'{self.get_display_type_display()}: {self.name}'


class WebsiteTheme(models.Model):
    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('white', 'White'),
        ('pink', 'Pink'),
    ]

    theme = models.CharField(max_length=12, choices=THEME_CHOICES, default='dark')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'website theme'
        verbose_name_plural = 'website theme'

    def save(self, *args, **kwargs):
        # One global record controls the public website. Keeping a fixed key
        # prevents administrators from accidentally creating conflicting themes.
        self.pk = 1
        if type(self).objects.filter(pk=1).exists():
            kwargs.pop('force_insert', None)
        super().save(*args, **kwargs)

    @classmethod
    def active_theme(cls):
        return cls.objects.filter(pk=1).values_list('theme', flat=True).first() or 'dark'

    def __str__(self):
        return f'{self.get_theme_display()} website theme'

class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='cart'); updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):return f'Cart for {self.user}'

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items'); product=models.ForeignKey(Product,on_delete=models.CASCADE); size=models.CharField(max_length=60,blank=True); color=models.CharField(max_length=60,blank=True); quantity=models.PositiveIntegerField(default=1)
    class Meta: constraints=[models.UniqueConstraint(fields=['cart','product','size','color'],name='unique_cart_product_option')]

class Order(models.Model):
    STATUS_CHOICES=[('confirmed','Confirmed'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled')]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders'); name=models.CharField(max_length=160); email=models.EmailField(); phone=models.CharField(max_length=30); address=models.TextField(); city=models.CharField(max_length=100); postal_code=models.CharField(max_length=20); subtotal=models.DecimalField(max_digits=10,decimal_places=2); delivery_charge=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('80.00')); discount_campaign=models.ForeignKey(DiscountCampaign,on_delete=models.SET_NULL,blank=True,null=True,related_name='orders'); discount_code=models.CharField(max_length=40,blank=True); discount_amount=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00')); total=models.DecimalField(max_digits=10,decimal_places=2); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='confirmed'); inventory_restored=models.BooleanField(default=False,editable=False); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
    def clean(self):
        if not self.pk:return
        previous=Order.objects.filter(pk=self.pk).values_list('status',flat=True).first()
        allowed={'confirmed':{'confirmed','shipped','cancelled'},'shipped':{'shipped','delivered'},'delivered':{'delivered'},'cancelled':{'cancelled'}}
        if previous and self.status not in allowed.get(previous,{previous}):raise ValidationError({'status':f'Orders cannot move from {previous} to {self.status}.'})
    def save(self,*args,**kwargs):
        previous=Order.objects.filter(pk=self.pk).values_list('status',flat=True).first() if self.pk else None
        self.full_clean()
        super().save(*args,**kwargs)
        if self.status=='cancelled' and previous!='cancelled' and not self.inventory_restored:
            for item in self.items.all():Product.objects.filter(pk=item.product_id).update(stock_quantity=F('stock_quantity')+item.quantity)
            Order.objects.filter(pk=self.pk).update(inventory_restored=True)
            self.inventory_restored=True

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items'); product=models.ForeignKey(Product,on_delete=models.PROTECT); product_name=models.CharField(max_length=160); size=models.CharField(max_length=60,blank=True); color=models.CharField(max_length=60,blank=True); unit_price=models.DecimalField(max_digits=10,decimal_places=2); quantity=models.PositiveIntegerField(); line_total=models.DecimalField(max_digits=10,decimal_places=2)


class OrderEmailLog(models.Model):
    STATUS_CHOICES = [('sent', 'Sent'), ('failed', 'Failed')]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='email_logs')
    recipient = models.EmailField()
    subject = models.CharField(max_length=180)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    error_message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'order email'
        verbose_name_plural = 'order emails'

    def __str__(self):
        return f'Order #{self.order_id} confirmation: {self.get_status_display()}'


class Payment(models.Model):
    METHOD_CHOICES = [
        ('bkash', 'bKash'),
        ('cash_on_delivery', 'Cash on delivery'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=24, choices=METHOD_CHOICES, default='bkash')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    last_request_id = models.UUIDField(blank=True, null=True, editable=False)
    provider_reference = models.CharField(max_length=80, blank=True, editable=False)
    provider_payment_id = models.CharField(max_length=120, blank=True, editable=False)
    provider_invoice = models.CharField(max_length=120, blank=True, editable=False)
    provider_redirect_url = models.URLField(max_length=1000, blank=True, editable=False)
    provider_payload = models.JSONField(default=dict, blank=True, editable=False)
    failure_reason = models.CharField(max_length=240, blank=True, editable=False)
    attempts = models.PositiveSmallIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['provider_reference'],
                condition=models.Q(method='bkash') & ~models.Q(provider_reference=''),
                name='unique_bkash_transaction_reference',
            ),
        ]

    def clean(self):
        if self.order_id and self.amount != self.order.total:
            raise ValidationError({'amount': 'Payment amount must match the order total.'})
        if self.order_id and self.order.status == 'cancelled' and self.status == 'paid':
            raise ValidationError({'status': 'A cancelled order cannot be marked as paid.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Payment for order #{self.order_id}: {self.get_status_display()}'
