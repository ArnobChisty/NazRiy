from django.db import migrations, models
import django.db.models.deletion


def seed_top_product(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    TopProduct = apps.get_model('store', 'TopProduct')
    product = Product.objects.filter(slug='nazz-dress').first()
    if product:
        TopProduct.objects.get_or_create(
            product=product,
            defaults={
                'showcase_image': 'categories/womens-clothing.jpeg',
                'image_alt': "Women's Ethnic Top Set (Red)",
                'sort_order': 1,
                'active': True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [('store', '0006_category_showcase')]
    operations = [
        migrations.CreateModel(
            name='TopProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('showcase_image', models.FileField(blank=True, help_text='Optional homepage image. Leave blank to use the product primary image.', upload_to='top-products/')),
                ('image_alt', models.CharField(blank=True, max_length=180)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='homepage_placement', to='store.product')),
            ],
            options={'verbose_name': 'top product', 'verbose_name_plural': 'top products', 'ordering': ['sort_order', 'id']},
        ),
        migrations.RunPython(seed_top_product, migrations.RunPython.noop),
    ]
