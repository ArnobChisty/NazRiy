from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.text import slugify

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True); slug=models.SlugField(max_length=120,unique=True,blank=True); description=models.TextField(blank=True); image=models.FileField(upload_to='categories/',blank=True); image_alt=models.CharField(max_length=180,blank=True); featured=models.BooleanField(default=True); sort_order=models.PositiveSmallIntegerField(default=0)
    class Meta: ordering=['sort_order','name']; verbose_name_plural='categories'
    def save(self,*args,**kwargs):
        if not self.slug:self.slug=slugify(self.name)
        super().save(*args,**kwargs)
    def __str__(self):return self.name

class Product(models.Model):
    category=models.ForeignKey(Category,related_name='products',on_delete=models.PROTECT); name=models.CharField(max_length=160); slug=models.SlugField(max_length=180,unique=True,blank=True); short_description=models.CharField(max_length=240,blank=True); description=models.TextField(); price=models.DecimalField(max_digits=10,decimal_places=2); primary_image=models.FileField(upload_to='products/primary/',blank=True); available_sizes=models.JSONField(default=list,blank=True); available_colors=models.JSONField(default=list,blank=True); stock_quantity=models.PositiveIntegerField(default=0); featured=models.BooleanField(default=False); tone=models.CharField(max_length=30,default='sand'); shape=models.CharField(max_length=40,default='vase-shape'); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
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

class TopProduct(models.Model):
    product=models.OneToOneField(Product,related_name='homepage_placement',on_delete=models.CASCADE); showcase_image=models.FileField(upload_to='top-products/',blank=True,help_text='Optional homepage image. Leave blank to use the product primary image.'); image_alt=models.CharField(max_length=180,blank=True); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','id']; verbose_name='top product'; verbose_name_plural='top products'
    def __str__(self):return self.product.name

class NavigationLink(models.Model):
    label=models.CharField(max_length=60); url=models.CharField(max_length=240,help_text='Use a site path such as /products or /#about.'); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); open_in_new_tab=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','id']; verbose_name='navigation link'; verbose_name_plural='navigation links'
    def __str__(self):return self.label

class Banner(models.Model):
    PLACEMENTS=[('hero','Homepage hero'),('promotion','Promotional banner'),('category','Category banner')]
    THEMES=[('forest','Forest'),('burgundy','Burgundy'),('sage','Sage'),('neutral','Neutral')]
    placement=models.CharField(max_length=20,choices=PLACEMENTS,default='hero'); eyebrow=models.CharField(max_length=100,blank=True); title=models.CharField(max_length=180); description=models.TextField(blank=True); desktop_image=models.FileField(upload_to='banners/desktop/'); mobile_image=models.FileField(upload_to='banners/mobile/',blank=True); image_alt=models.CharField(max_length=180); primary_button_label=models.CharField(max_length=60,default='Shop now'); primary_button_link=models.CharField(max_length=240,default='/products'); secondary_button_label=models.CharField(max_length=60,blank=True); secondary_button_link=models.CharField(max_length=240,blank=True); theme=models.CharField(max_length=20,choices=THEMES,default='forest'); object_position=models.CharField(max_length=40,default='center center',help_text='CSS object-position, for example: center 42%'); sort_order=models.PositiveSmallIntegerField(default=0); active=models.BooleanField(default=True); starts_at=models.DateTimeField(blank=True,null=True); ends_at=models.DateTimeField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:ordering=['sort_order','id']
    def __str__(self):return f'{self.get_placement_display()}: {self.title}'

class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='cart'); updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):return f'Cart for {self.user}'

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items'); product=models.ForeignKey(Product,on_delete=models.CASCADE); size=models.CharField(max_length=60,blank=True); color=models.CharField(max_length=60,blank=True); quantity=models.PositiveIntegerField(default=1)
    class Meta: constraints=[models.UniqueConstraint(fields=['cart','product','size','color'],name='unique_cart_product_option')]

class Order(models.Model):
    STATUS_CHOICES=[('confirmed','Confirmed'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled')]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders'); name=models.CharField(max_length=160); email=models.EmailField(); phone=models.CharField(max_length=30); address=models.TextField(); city=models.CharField(max_length=100); postal_code=models.CharField(max_length=20); subtotal=models.DecimalField(max_digits=10,decimal_places=2); delivery_charge=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('80.00')); total=models.DecimalField(max_digits=10,decimal_places=2); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='confirmed'); inventory_restored=models.BooleanField(default=False,editable=False); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
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
