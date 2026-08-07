"""Vercel entrypoint for the Django API.

Vercel executes this file as a Python function.  The repository's Django
project lives one directory above ``api`` and the ``store`` app lives next to
it, so add that directory explicitly before importing the WSGI application.
"""

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from backend.wsgi import application  # noqa: E402

app = application
