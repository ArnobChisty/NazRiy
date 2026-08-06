from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Create a timestamped JSON backup of application data.'

    def add_arguments(self, parser):
        parser.add_argument('--output', help='Optional backup output path.')

    def handle(self, *args, **options):
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        output = Path(options['output'] or settings.BASE_DIR / 'backups' / f'nazriy-{timestamp}.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        # Explicit UTF-8 keeps backups portable across Windows and Linux hosts.
        with output.open('w', encoding='utf-8', newline='\n') as stream:
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--indent', '2',
                '--exclude', 'contenttypes',
                '--exclude', 'auth.permission',
                '--exclude', 'sessions',
                stdout=stream,
            )
        self.stdout.write(self.style.SUCCESS(f'Backup created: {output}'))
