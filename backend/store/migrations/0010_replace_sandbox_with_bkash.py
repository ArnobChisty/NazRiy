from django.db import migrations, models


def convert_sandbox_payments(apps, schema_editor):
    Payment = apps.get_model('store', 'Payment')
    for payment in Payment.objects.filter(method='sandbox_card'):
        payment.method = 'bkash'
        if payment.provider_reference.startswith('SBX-'):
            payment.provider_reference = ''
            if payment.status == 'paid':
                payment.status = 'pending'
            payment.failure_reason = 'A bKash transaction ID is required.'
        payment.save()


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0009_sprint5_payment'),
    ]

    operations = [
        migrations.RunPython(convert_sandbox_payments, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(
                choices=[
                    ('bkash', 'bKash'),
                    ('cash_on_delivery', 'Cash on delivery'),
                ],
                default='bkash',
                max_length=24,
            ),
        ),
    ]
