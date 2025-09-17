from django.core.management.base import BaseCommand
from space_app.models import Skill

class Command(BaseCommand):
    help = 'Removes a specific, hardcoded list of unwanted skills from the database.'

    def handle(self, *args, **options):
        unwanted_skill_names = [
            'Onepiece and jujutsu',
            'Still idc',
        ]

        self.stdout.write(self.style.SUCCESS('--- Deleting Exact Unwanted Skills ---'))

        for skill_name in unwanted_skill_names:
            try:
                skill_to_delete = Skill.objects.get(name__iexact=skill_name)
                skill_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted skill: "{skill_name}"'))
            except Skill.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Skill not found, could not delete: "{skill_name}"'))

        self.stdout.write(self.style.SUCCESS('--- Finished Deletion Process ---'))
