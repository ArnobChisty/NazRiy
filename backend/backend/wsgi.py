"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Vercel may flatten the Django project package during its Python build. Keep
# both the normal local layout and the flattened deployment layout importable.
_project_dir = Path(__file__).resolve().parent
for _path in (_project_dir, _project_dir.parent, _project_dir / "backend"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
