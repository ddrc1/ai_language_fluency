from django.core.management.base import BaseCommand
from django.core import management

from apps.language_practice.models import Language, Vocabulary

class Command(BaseCommand):
    """
    Command to populate specific tables:
    - Language
    - Vocabulary

    Note: This command should be considered when the application is
    deployed in Docker, or it is running for the first time.
    """

    help = 'Populate specific tables for the first time.'

    def handle(self, *args, **kwargs):
        if Language.objects.exists():
            self.stdout.write('Language already populated.')
        else:
            management.call_command('loaddata', 'language', format='json', verbosity=0)
            self.stdout.write('Successfully populated Language!')

        if Vocabulary.objects.exists():
            self.stdout.write('Vocabulary already populated.')
        else:
            management.call_command(
                'loaddata', 'vocabulary', format='json', verbosity=0
            )
            self.stdout.write('Successfully populated Vocabulary!')
