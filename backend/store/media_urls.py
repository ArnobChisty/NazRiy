"""Fast, reusable media URLs for public API serializers."""

from hashlib import sha256

from django.conf import settings
from django.core.cache import cache


def serialized_media_url(file_field, context=None):
    """Return a media URL without repeatedly signing the same Supabase key."""
    if not file_field:
        return ""

    name = getattr(file_field, "name", "") or str(file_field)
    request_cache = None
    if context is not None:
        request_cache = context.setdefault("_nazriy_media_urls", {})
        if name in request_cache:
            return request_cache[name]

    cache_key = f"nazriy:media-url:{sha256(name.encode('utf-8')).hexdigest()}"
    url = cache.get(cache_key) if settings.USE_SUPABASE_STORAGE else None
    if not url:
        url = file_field.url
        if settings.USE_SUPABASE_STORAGE:
            signature_lifetime = int(getattr(settings, "SUPABASE_STORAGE_URL_EXPIRY", 3600))
            cache.set(cache_key, url, timeout=max(30, min(900, signature_lifetime // 2)))

    request = (context or {}).get("request")
    absolute_url = request.build_absolute_uri(url) if request else url
    if request_cache is not None:
        request_cache[name] = absolute_url
    return absolute_url
