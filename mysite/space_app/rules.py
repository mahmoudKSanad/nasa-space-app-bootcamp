from impersonate.helpers import get_redir_path, get_redir_arg, get_real_user

def can_impersonate_check(request, impersonating_user):
    """ Returns True if the user is allowed to impersonate the given user.

    1. User must be a superuser or staff.
    2. User cannot impersonate another superuser.
    3. User cannot impersonate themself.
    """
    impersonator = get_real_user(request)

    if not (impersonator.is_superuser or impersonator.is_staff):
        # Must be a superuser or staff to impersonate.
        return False

    if impersonator.is_superuser and not impersonating_user.is_superuser:
        # Superusers can impersonate anyone but other superusers.
        return True

    if impersonator.is_staff and not impersonating_user.is_superuser and not impersonating_user.is_staff:
        # Staff can impersonate anyone but superusers and other staff.
        return True

    return False

def get_impersonatable_users(requesting_user):
    """Return a queryset of users that the requesting user can impersonate.

    This is used for the user selection list in the admin UI.
    """
    from .models import User

    if requesting_user.is_superuser:
        # Superusers can impersonate any user that is not a superuser
        return User.objects.filter(is_superuser=False).order_by('email')

    if requesting_user.is_staff:
        # Staff can impersonate any user that is not a superuser or staff
        return User.objects.filter(is_superuser=False, is_staff=False).order_by('email')

    # Otherwise, no one can be impersonated
    return User.objects.none()
