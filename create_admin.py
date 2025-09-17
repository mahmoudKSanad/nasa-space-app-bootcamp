import os
import django
import getpass

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from space_app.models import User

def create_admin_user(email, password):
    """
    Creates an admin user with the given email and password.
    """
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_superuser(email=email, password=password)
        print(f"Admin user {email} created successfully.")
    else:
        print(f"User with email {email} already exists.")

if __name__ == "__main__":
    email = input("Enter admin email: ")
    password = getpass.getpass("Enter admin password: ")
    create_admin_user(email, password)
