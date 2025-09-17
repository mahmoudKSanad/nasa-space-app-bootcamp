
from django.db import migrations

from space_app.choices import SKILLS

def populate_skills(apps, schema_editor):
    Skill = apps.get_model('space_app', 'Skill')
    for skill_name, _ in SKILLS:
        Skill.objects.create(name=skill_name)

def delete_skills(apps, schema_editor):
    Skill = apps.get_model('space_app', 'Skill')
    Skill.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('space_app', '0004_skill_remove_user_skills_user_skills'),
    ]

    operations = [
        migrations.RunPython(populate_skills, delete_skills),
    ]
