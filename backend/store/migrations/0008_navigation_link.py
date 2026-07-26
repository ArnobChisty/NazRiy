from django.db import migrations, models


def seed_navigation(apps, schema_editor):
    NavigationLink = apps.get_model('store', 'NavigationLink')
    links = [
        ('Shop all', '/products', 1),
        ('New arrivals', '/products?ordering=newest', 2),
        ('Women', '/products?category=womens-clothing', 3),
        ('Our story', '/#about', 4),
    ]
    for label, url, sort_order in links:
        NavigationLink.objects.get_or_create(
            label=label,
            defaults={'url': url, 'sort_order': sort_order, 'active': True},
        )


class Migration(migrations.Migration):
    dependencies = [('store', '0007_top_product')]
    operations = [
        migrations.CreateModel(
            name='NavigationLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=60)),
                ('url', models.CharField(help_text='Use a site path such as /products or /#about.', max_length=240)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('open_in_new_tab', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'navigation link', 'verbose_name_plural': 'navigation links', 'ordering': ['sort_order', 'id']},
        ),
        migrations.RunPython(seed_navigation, migrations.RunPython.noop),
    ]
