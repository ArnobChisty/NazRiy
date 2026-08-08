from django.db import migrations, models
import django.db.models.deletion


def repair_women_navigation(apps, schema_editor):
    NavigationLink = apps.get_model('store', 'NavigationLink')
    NavigationLink.objects.filter(label__iexact='Women').update(url='/products?view=women')


class Migration(migrations.Migration):
    dependencies = [('store', '0012_product_active')]

    operations = [
        migrations.CreateModel(
            name='OrderEmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=180)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed')], max_length=12)),
                ('error_message', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='store.order')),
            ],
            options={'verbose_name': 'order email', 'verbose_name_plural': 'order emails', 'ordering': ['-created_at']},
        ),
        migrations.RunPython(repair_women_navigation, migrations.RunPython.noop),
    ]
