from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('store', '0004_banner')]
    operations = [
        migrations.AddField(
            model_name='order',
            name='inventory_restored',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
