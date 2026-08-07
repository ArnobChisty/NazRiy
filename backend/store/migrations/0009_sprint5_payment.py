# Generated for NazRiy Sprint 5.

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0008_navigation_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('sandbox_card', 'Sandbox card'), ('cash_on_delivery', 'Cash on delivery')], default='sandbox_card', max_length=24)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=16)),
                ('idempotency_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('last_request_id', models.UUIDField(blank=True, editable=False, null=True)),
                ('provider_reference', models.CharField(blank=True, editable=False, max_length=80)),
                ('failure_reason', models.CharField(blank=True, editable=False, max_length=240)),
                ('attempts', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='store.order')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
