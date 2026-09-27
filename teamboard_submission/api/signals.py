import secrets

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Company


@receiver(post_save, sender=User)
def create_company_profile(sender, instance, created, **kwargs):
    """
    Automatically create the B2B Company profile when a User is first created.

    The assignment asks for instance._state.adding as the creation-state
    indicator. In post_save, Django has already transitioned _state.adding
    to False, so the reliable post_save indicator is `created`. We retain
    the state check for clarity without using it as the sole condition.
    """
    is_first_save = bool(getattr(instance._state, "adding", False))

    if created or is_first_save:
        Company.objects.get_or_create(
            user=instance,
            defaults={
                "company_name": instance.email or instance.username,
                "api_key": secrets.token_urlsafe(32),
                "role": Company.Role.CLIENT,
            },
        )
