from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from .models import Profile


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwarg):
    user = instance

    # Add profile if user is created
    if created:
        Profile.objects.create(
            user=user,
        )
    else:
        # update allauth email address if exists
        try:
            email_address = EmailAddress.objects.get_primary(user)
            if email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False
                email_address.save()
        except:
            # if allauth email address doesn't exist create one
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False,
            )


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()
