
from django.core.management.base import BaseCommand
from space_app.models import Skill

class Command(BaseCommand):
    help = 'Lists all skills and then removes a list of unwanted skills from the database.'

    def handle(self, *args, **options):
        # 1. List all current skills
        self.stdout.write(self.style.SUCCESS('--- Current Skills in Database ---'))
        all_skills = Skill.objects.all()
        if all_skills.exists():
            for skill in all_skills:
                self.stdout.write(f'- "{skill.name}" (ID: {skill.id})')
        else:
            self.stdout.write(self.style.WARNING('No skills found in the database.'))
        self.stdout.write(self.style.SUCCESS('------------------------------------\n'))

        # 2. Attempt to delete unwanted skills
        self.stdout.write(self.style.SUCCESS('--- Attempting to Delete Unwanted Skills ---'))
        unwanted_skills = ['Onepiece', 'jujutsu', 'idc']

        for skill_name in unwanted_skills:
            skills_to_delete = Skill.objects.filter(name__iexact=skill_name.strip())
            
            if skills_to_delete.exists():
                deleted_count, _ = skills_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} skill(s) matching "{skill_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'No skill found matching "{skill_name}"'))
        self.stdout.write(self.style.SUCCESS('------------------------------------------'))
