from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import CandidateProfile


@receiver(post_save, sender=User)
def create_candidate_profile(sender, instance, created, **kwargs):

    print("Signal Fired: ", instance.username, created)

    if created:
        try:
            CandidateProfile.objects.create(user=instance)
            print("Profile Created")
        except Exception as e:
            print("Error")


@receiver(post_save, sender=User)
def save_candidate_profile(sender, instance, **kwargs):

    instance.profile.save()