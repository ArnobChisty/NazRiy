from django.core.management.base import BaseCommand

from store.models import Category, Product


PRODUCTS = [
    ("Ceramics", "The Solace Vase", "A soft neutral vase for shelves, desks, and quiet corners.", 480, ["Small", "Medium", "Large"], ["Sand", "Clay"], "sand", "vase-shape", True),
    ("Textiles", "Linen Carryall", "A relaxed everyday carryall with a structured handmade feel.", 760, ["One Size"], ["Clay", "Olive"], "clay", "bag-shape", True),
    ("Tableware", "Quiet Morning Cup", "A warm ceramic cup made for tea, coffee, and slow mornings.", 340, ["250 ml", "350 ml"], ["Cream", "Sand"], "cream", "cup-shape", True),
    ("Home Fragrance", "Amber Glow Candle", "A gentle amber candle for cosy rooms and evening resets.", 590, ["Small", "Large"], ["Amber", "Sage"], "sage", "candle-shape", True),
    ("Ceramics", "Earthline Planter", "An earthy planter that brings a little softness to windows and desks.", 650, ["Small", "Medium"], ["Terracotta", "Cream"], "clay", "planter-shape", False),
    ("Textiles", "Woven Rest Cushion", "A tactile woven cushion cover made for relaxed corners.", 890, ["40 cm", "50 cm"], ["Oat", "Olive", "Rust"], "sand", "cushion-shape", False),
    ("Tableware", "Gather Serving Bowl", "A generous serving bowl with an organic hand-finished rim.", 980, ["Medium", "Large"], ["Cream", "Sage"], "sage", "bowl-shape", False),
    ("Home Fragrance", "Forest Quiet Diffuser", "A grounding blend of cedar, moss, and soft citrus.", 720, ["100 ml"], ["Forest", "Amber"], "cream", "diffuser-shape", False),
]


class Command(BaseCommand):
    help = "Create the demonstration categories and products used by the NazRiy frontend."

    def handle(self, *args, **options):
        for category_name, name, short, price, sizes, colors, tone, shape, featured in PRODUCTS:
            category, _ = Category.objects.get_or_create(name=category_name)
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "short_description": short,
                    "description": f"{short} Thoughtfully selected by NazRiy for useful, beautiful everyday living.",
                    "price": price,
                    "available_sizes": sizes,
                    "available_colors": colors,
                    "stock_quantity": 12,
                    "featured": featured,
                    "tone": tone,
                    "shape": shape,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} NazRiy products."))
