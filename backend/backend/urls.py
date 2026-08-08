"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import mimetypes
from pathlib import PurePosixPath

from django.contrib import admin
from django.contrib.staticfiles import finders
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, Http404
from django.urls import include, path


def admin_theme_css(request):
    """Serve the project-owned admin theme without Vercel static-file caching."""
    theme_file = settings.BASE_DIR / 'store' / 'static' / 'admin' / 'css' / 'nazriy_admin_global.css'
    response = FileResponse(theme_file.open('rb'), content_type='text/css')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    return response


def admin_static_asset(request, path):
    """Serve Django admin assets in Vercel's serverless Python runtime.

    Vercel does not execute ``collectstatic`` for ``@vercel/python`` builds.
    Restrict this fallback to the public ``admin/`` static namespace and let
    Django's configured static finders locate assets shipped by Django or the
    store app.
    """
    relative_path = f'admin/{path}'
    if '..' in PurePosixPath(relative_path).parts:
        raise Http404('Static asset not found.')

    asset_path = finders.find(relative_path)
    if not asset_path:
        raise Http404('Static asset not found.')

    content_type = mimetypes.guess_type(relative_path)[0] or 'application/octet-stream'
    response = FileResponse(open(asset_path, 'rb'), content_type=content_type)
    response['Cache-Control'] = 'public, max-age=86400'
    return response

urlpatterns = [
    path('admin-theme.css', admin_theme_css, name='admin-theme-css'),
    path('static/admin/<path:path>', admin_static_asset, name='admin-static-asset'),
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
