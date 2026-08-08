from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


SIZE_CHARTS = {
    'womens-ethnic-top-set-yellow': [
        ('S', '36', '30.5', '32-34', '38'),
        ('M', '40', '32', '35-38', '38'),
        ('L', '44', '33.5', '39-42', '40'),
    ],
    'womens-ethnic-top-set-red': [
        ('S', '36', '30.5', '32-34', '38'),
        ('M', '40', '32', '35-38', '38'),
        ('L', '44', '33.5', '39-42', '40'),
        ('XL', '48', '34', '44-46', '41'),
    ],
}


def add_florence_size_charts(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    ProductSizeMeasurement = apps.get_model('store', 'ProductSizeMeasurement')

    for slug, rows in SIZE_CHARTS.items():
        product = Product.objects.filter(slug=slug).first()
        if product is None:
            colour = 'yellow' if slug.endswith('yellow') else 'red'
            product = Product.objects.filter(name__icontains=colour).first()
        if product is None:
            continue

        product.available_sizes = [row[0] for row in rows]
        product.save(update_fields=['available_sizes'])
        ProductSizeMeasurement.objects.filter(product=product).delete()
        ProductSizeMeasurement.objects.bulk_create([
            ProductSizeMeasurement(
                product=product,
                size=size,
                garment_bust=Decimal(garment_bust),
                length=Decimal(length),
                recommended_bust=recommended_bust,
                pant_length=Decimal(pant_length),
                sort_order=position,
            )
            for position, (size, garment_bust, length, recommended_bust, pant_length)
            in enumerate(rows, start=1)
        ])


class Migration(migrations.Migration):
    dependencies = [('store', '0013_order_email_log_and_navigation_fix')]

    operations = [
        migrations.CreateModel(
            name='ProductSizeMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=12)),
                ('garment_bust', models.DecimalField(decimal_places=1, help_text='Finished garment bust in inches.', max_digits=5)),
                ('length', models.DecimalField(decimal_places=1, help_text='Top length in inches.', max_digits=5)),
                ('recommended_bust', models.CharField(help_text='Recommended body bust range in inches, for example 32-34.', max_length=20)),
                ('pant_length', models.DecimalField(decimal_places=1, help_text='Pant length in inches.', max_digits=5)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='size_chart', to='store.product')),
            ],
            options={
                'verbose_name': 'size measurement',
                'verbose_name_plural': 'size measurements',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='productsizemeasurement',
            constraint=models.UniqueConstraint(fields=('product', 'size'), name='unique_product_size_measurement'),
        ),
        migrations.RunPython(add_florence_size_charts, migrations.RunPython.noop),
    ]
