
import json
from django.core.management.base import BaseCommand
from mysite.space_app.models import Challenge

class Command(BaseCommand):
    help = 'Import challenges from a JSON file'

    def handle(self, *args, **options):
        with open('mysite/space_app/data/challenges.json', 'r') as f:
            challenges = json.load(f)
            for challenge_data in challenges:
                challenge, created = Challenge.objects.update_or_create(
                    id=challenge_data['id'],
                    defaults={
                        'title': challenge_data['title'],
                        'category': challenge_data['category'],
                        'description': challenge_data['description'],
                        'difficulty': challenge_data['difficulty'],
                        'image': challenge_data['image'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created challenge "{challenge.title}"'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated challenge "{challenge.title}"'))
