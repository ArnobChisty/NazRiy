from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('store', '0016_discountcampaign')]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='provider_invoice',
            field=models.CharField(blank=True, editable=False, max_length=120),
        ),
        migrations.AddField(
            model_name='payment',
            name='provider_payload',
            field=models.JSONField(blank=True, default=dict, editable=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='provider_payment_id',
            field=models.CharField(blank=True, editable=False, max_length=120),
        ),
        migrations.AddField(
            model_name='payment',
            name='provider_redirect_url',
            field=models.URLField(blank=True, editable=False, max_length=1000),
        ),
    ]
