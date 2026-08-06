from django.db import migrations, models


def seed_category_showcase(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Category.objects.update(featured=False, sort_order=20)
    showcase = [
        ('Womens Clothing', 'categories/womens-clothing.jpeg', "NazRiy women's floral clothing", 1),
        ('Textiles', 'categories/textiles.jpeg', 'NazRiy textile details', 2),
        ('Ceramics', 'categories/ceramics.jpeg', 'NazRiy curated ceramics and objects', 3),
        ('Home Fragrance', 'categories/home-fragrance.jpeg', 'NazRiy home fragrance collection', 4),
    ]
    for name, image, alt, order in showcase:
        Category.objects.filter(name__iexact=name).update(
            featured=True, sort_order=order, image=image, image_alt=alt,
        )


class Migration(migrations.Migration):
    dependencies = [('store', '0005_sprint4_order_tracking')]
    operations = [
        migrations.AddField(model_name='category', name='featured', field=models.BooleanField(default=True)),
        migrations.AddField(model_name='category', name='image', field=models.FileField(blank=True, upload_to='categories/')),
        migrations.AddField(model_name='category', name='image_alt', field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name='category', name='sort_order', field=models.PositiveSmallIntegerField(default=0)),
        migrations.AlterModelOptions(name='category', options={'ordering': ['sort_order', 'name'], 'verbose_name_plural': 'categories'}),
        migrations.RunPython(seed_category_showcase, migrations.RunPython.noop),
    ]
