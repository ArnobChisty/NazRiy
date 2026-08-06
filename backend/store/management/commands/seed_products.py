from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Category, NavigationLink, Product


PRODUCTS = [
    {
        'name': "Women's Ethnic Top Set (Red)",
        'short_description': 'A three-piece floral set finished with deep maroon lace and gold-tone buttons.',
        'description': 'A coordinated printed top, wide-leg trouser and lightweight dupatta designed for festive gatherings and polished everyday wear.',
        'price': Decimal('5000.00'),
        'sizes': ['Medium', 'Large'],
        'colors': ['Red', 'Maroon'],
        'tone': 'burgundy',
    },
    {
        'name': "Women’s Ethnic Top Set (Yellow)",
        'short_description': 'A soft floral three-piece set in warm yellow, blush pink and powder blue.',
        'description': 'A breathable printed top and trouser pairing with a flowing pink dupatta, detailed borders and delicate lace finishing.',
        'price': Decimal('5000.00'),
        'sizes': ['Medium', 'Large'],
        'colors': ['Yellow', 'Blush Pink'],
        'tone': 'sand',
    },
]


class Command(BaseCommand):
    help = 'Create or refresh the clothing-only NazRiy demonstration catalogue.'

    def handle(self, *args, **options):
        category, _ = Category.objects.update_or_create(
            slug='womens-clothing',
            defaults={
                'name': 'Womens Clothing',
                'description': 'Printed ethnic top sets and coordinated clothing by NazRiy.',
                'image_alt': 'NazRiy women’s clothing collection',
                'featured': True,
                'sort_order': 1,
            },
        )
        for index, item in enumerate(PRODUCTS):
            product, _ = Product.objects.get_or_create(name=item['name'], defaults={'category': category, 'description': item['description'], 'price': item['price']})
            product.category = category
            product.short_description = item['short_description']
            product.description = item['description']
            product.price = item['price']
            product.available_sizes = item['sizes']
            product.available_colors = item['colors']
            product.tone = item['tone']
            product.shape = 'apparel'
            product.active = True
            product.featured = True
            if not product.stock_quantity:
                product.stock_quantity = 8
            product.save()

        links = [
            ('Shop all', '/products'),
            ('New arrivals', '/products?ordering=newest'),
            ('Women', '/products?category=womens-clothing'),
            ('Our story', '/#about'),
        ]
        for position, (label, url) in enumerate(links, start=1):
            NavigationLink.objects.update_or_create(label=label, defaults={'url': url, 'sort_order': position, 'active': True})
        self.stdout.write(self.style.SUCCESS(f'Refreshed {len(PRODUCTS)} clothing products and {len(links)} navigation links.'))
