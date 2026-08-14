from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('store', '0015_websitetheme')]

    operations = [
        migrations.CreateModel(
            name='DiscountCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Internal name for staff, for example Eid sale 2026.', max_length=100)),
                ('display_type', models.CharField(choices=[('announcement', 'Discount announcement banner'), ('popup', 'Discount popup')], default='announcement', max_length=20)),
                ('title', models.CharField(max_length=140)),
                ('message', models.CharField(blank=True, max_length=280)),
                ('discount_code', models.CharField(blank=True, help_text='Optional code customers can copy, for example EID20.', max_length=40)),
                ('button_label', models.CharField(blank=True, default='Shop now', max_length=50)),
                ('button_link', models.CharField(blank=True, default='/products', max_length=240)),
                ('image', models.FileField(blank=True, help_text='Optional. Most useful for popup campaigns.', upload_to='discount-campaigns/')),
                ('image_alt', models.CharField(blank=True, max_length=180)),
                ('theme', models.CharField(choices=[('forest', 'Forest green'), ('burgundy', 'Burgundy'), ('pink', 'Soft pink'), ('black', 'Black')], default='burgundy', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('starts_at', models.DateTimeField(blank=True, null=True)),
                ('ends_at', models.DateTimeField(blank=True, null=True)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('popup_delay_seconds', models.PositiveSmallIntegerField(default=3, help_text='Only used for popups. Recommended: 3 to 8 seconds.')),
                ('show_once_per_session', models.BooleanField(default=True, help_text='Prevents the same popup repeatedly interrupting one visitor.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'discount campaign', 'verbose_name_plural': 'discount campaigns', 'ordering': ['sort_order', '-created_at']},
        ),
    ]
