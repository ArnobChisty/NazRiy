from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0010_replace_sandbox_with_bkash'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.UniqueConstraint(
                condition=models.Q(method='bkash') & ~models.Q(provider_reference=''),
                fields=('provider_reference',),
                name='unique_bkash_transaction_reference',
            ),
        ),
    ]
