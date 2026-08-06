from pathlib import Path

from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = 'Restore a trusted JSON backup produced by backup_database.'

    def add_arguments(self, parser):
        parser.add_argument('input', help='Path to the trusted JSON backup.')
        parser.add_argument('--flush', action='store_true', help='Clear application data before restoring.')
        parser.add_argument('--yes', action='store_true', help='Confirm the destructive --flush operation.')

    def handle(self, *args, **options):
        source = Path(options['input']).expanduser().resolve()
        if not source.is_file() or source.suffix.lower() != '.json':
            raise CommandError('Provide an existing .json backup file.')
        if options['flush'] and not options['yes']:
            raise CommandError('--flush requires --yes to prevent accidental data deletion.')
        if options['flush']:
            call_command('flush', interactive=False)
        call_command('loaddata', str(source))
        self.stdout.write(self.style.SUCCESS(f'Restored backup: {source}'))
