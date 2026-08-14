from django.db import migrations, models


def create_default_theme(apps, schema_editor):
    WebsiteTheme = apps.get_model('store', 'WebsiteTheme')
    WebsiteTheme.objects.get_or_create(pk=1, defaults={'theme': 'dark'})


class Migration(migrations.Migration):
    dependencies = [('store', '0014_product_size_measurement')]

    operations = [
        migrations.CreateModel(
            name='WebsiteTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('dark', 'Dark'), ('white', 'White'), ('pink', 'Pink')], default='dark', max_length=12)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'website theme',
                'verbose_name_plural': 'website theme',
            },
        ),
        migrations.RunPython(create_default_theme, migrations.RunPython.noop),
    ]
