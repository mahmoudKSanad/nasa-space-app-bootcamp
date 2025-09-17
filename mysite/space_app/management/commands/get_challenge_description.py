from django.core.management.base import BaseCommand
from space_app.models import Challenge

class Command(BaseCommand):
    help = 'Gets the description of a specific challenge.'

    def handle(self, *args, **options):
        challenge_title = "Fayrouz -- Echoes from Space"
        try:
            challenge = Challenge.objects.get(title=challenge_title)
            self.stdout.write(self.style.SUCCESS(f'--- Description for \"{challenge_title}\" ---'))
            self.stdout.write(challenge.description)
            self.stdout.write(self.style.SUCCESS('----------------------------------------------------'))
        except Challenge.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Challenge with title \"{challenge_title}\" not found.'))
