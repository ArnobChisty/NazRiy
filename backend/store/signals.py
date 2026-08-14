from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache_keys import HOMEPAGE_CACHE_KEY
from .models import Banner, Category, NavigationLink, Product, TopProduct, WebsiteTheme


@receiver(post_save, sender=Banner)
@receiver(post_delete, sender=Banner)
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
@receiver(post_save, sender=NavigationLink)
@receiver(post_delete, sender=NavigationLink)
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
@receiver(post_save, sender=TopProduct)
@receiver(post_delete, sender=TopProduct)
@receiver(post_save, sender=WebsiteTheme)
@receiver(post_delete, sender=WebsiteTheme)
def clear_homepage_cache(**kwargs):
    """Make admin catalogue changes visible immediately."""
    cache.delete(HOMEPAGE_CACHE_KEY)
