from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import CandidateProfile


class CandidateProfileTests(TestCase):

    def test_profile_created_for_new_user(self):
        user = User.objects.create_user(
            username="testuser",
            password="TestPass123!",
        )

        self.assertTrue(
            CandidateProfile.objects.filter(user=user).exists()
        )

    def test_new_profile_starts_empty(self):
        user = User.objects.create_user(
            username="emptyprofile",
            password="TestPass123!",
        )

        profile = user.profile

        self.assertEqual(profile.bio, "")
        self.assertEqual(profile.skills, "")
        self.assertEqual(profile.headline, "")

    def test_users_have_separate_profiles(self):
        user1 = User.objects.create_user(
            username="user1",
            password="TestPass123!",
        )

        user2 = User.objects.create_user(
            username="user2",
            password="TestPass123!",
        )

        user1.profile.bio = "Python developer"
        user1.profile.skills = "Python,Django"
        user1.profile.save()

        self.assertEqual(user1.profile.bio, "Python developer")
        self.assertEqual(user1.profile.skills, "Python,Django")

        self.assertEqual(user2.profile.bio, "")
        self.assertEqual(user2.profile.skills, "")

        self.assertNotEqual(
            user1.profile.pk,
            user2.profile.pk,
        )

    def test_skill_list(self):
        user = User.objects.create_user(
            username="skilluser",
            password="TestPass123!",
        )

        profile = user.profile
        profile.skills = "Python, Django, REST API, MySQL"
        profile.save()

        self.assertEqual(
            profile.skill_list,
            ["Python", "Django", "REST API", "MySQL"],
        )

    def test_empty_skill_list(self):
        user = User.objects.create_user(
            username="noskills",
            password="TestPass123!",
        )

        self.assertEqual(
            user.profile.skill_list,
            [],
        )