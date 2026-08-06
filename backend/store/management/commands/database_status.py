from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Verify the configured database connection and report its safe status.'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except Exception as exc:
            raise CommandError(f'Database connection failed: {exc}') from exc

        database = settings.DATABASES['default']
        self.stdout.write(self.style.SUCCESS('Database connection: OK'))
        self.stdout.write(f"Engine: {connection.vendor}")
        self.stdout.write(f"Name: {database.get('NAME')}")
        self.stdout.write(f"Host: {database.get('HOST') or 'local file'}")
        self.stdout.write(f"Port: {database.get('PORT') or '-'}")
        self.stdout.write(
            'Media storage: Supabase Storage'
            if settings.USE_SUPABASE_STORAGE
            else 'Media storage: local filesystem'
        )
