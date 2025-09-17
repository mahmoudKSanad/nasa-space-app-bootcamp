from django.core.management.base import BaseCommand
from space_app.models import Challenge

class Command(BaseCommand):
    help = 'Lists all challenges in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- All Challenges in Database ---'))
        all_challenges = Challenge.objects.all()
        if all_challenges.exists():
            for challenge in all_challenges:
                self.stdout.write(f'- "{challenge.title}" (ID: {challenge.id})')
        else:
            self.stdout.write(self.style.WARNING('No challenges found in the database.'))
        self.stdout.write(self.style.SUCCESS('------------------------------------'))
