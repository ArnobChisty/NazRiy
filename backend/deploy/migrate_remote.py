import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django

django.setup()

from django.core.management import call_command

call_command("migrate", interactive=False)
