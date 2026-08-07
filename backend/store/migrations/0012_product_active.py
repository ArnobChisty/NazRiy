from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('store', '0011_unique_bkash_transaction_reference')]

    operations = [
        migrations.AddField(
            model_name='product',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
