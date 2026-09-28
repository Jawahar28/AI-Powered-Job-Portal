from django.test import TestCase

from jobs.services.recommendations import (
    is_experience_eligible,
    calculate_experience_score,
)

from django.contrib.auth.models import User
from accounts.models import CandidateProfile
from jobs.models import Company, Job, JobFetchRun, Notification

class ExperienceEligibilityTests(TestCase):

    def test_fresher_is_eligible_for_entry_level_job(self):
        job_intelligence = {
            "experience_level": "junior",
            "total_experience": {
                "min_years": 0,
            },
        }

        self.assertTrue(
            is_experience_eligible(
                "fresher",
                job_intelligence,
            )
        )

    def test_fresher_is_eligible_for_one_year_requirement(self):
        job_intelligence = {
            "experience_level": "junior",
            "total_experience": {
                "min_years": 1,
            },
        }

        self.assertTrue(
            is_experience_eligible(
                "0 years",
                job_intelligence,
            )
        )

    def test_fresher_is_not_eligible_for_senior_job(self):
        job_intelligence = {
            "experience_level": "senior",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertFalse(
            is_experience_eligible(
                "fresher",
                job_intelligence,
            )
        )

    def test_fresher_is_not_eligible_for_lead_job(self):
        job_intelligence = {
            "experience_level": "lead",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertFalse(
            is_experience_eligible(
                "0",
                job_intelligence,
            )
        )

    def test_experienced_candidate_meets_requirement(self):
        job_intelligence = {
            "experience_level": "mid",
            "total_experience": {
                "min_years": 2,
            },
        }

        self.assertTrue(
            is_experience_eligible(
                "3 years",
                job_intelligence,
            )
        )

    def test_experienced_candidate_does_not_meet_requirement(self):
        job_intelligence = {
            "experience_level": "mid",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertFalse(
            is_experience_eligible(
                "2 years",
                job_intelligence,
            )
        )

    def test_missing_job_experience_requirement_is_eligible(self):
        job_intelligence = {
            "experience_level": "junior",
        }

        self.assertTrue(
            is_experience_eligible(
                "2 years",
                job_intelligence,
            )
        )

    def test_missing_candidate_experience_is_eligible(self):
        job_intelligence = {
            "experience_level": "senior",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertTrue(
            is_experience_eligible(
                "",
                job_intelligence,
            )
        )


class ExperienceScoreTests(TestCase):

    def test_fresher_entry_level_score(self):
        job_intelligence = {
            "experience_level": "junior",
            "total_experience": {
                "min_years": 1,
            },
        }

        self.assertEqual(
            calculate_experience_score(
                "fresher",
                job_intelligence,
            ),
            100,
        )

    def test_fresher_senior_score(self):
        job_intelligence = {
            "experience_level": "senior",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertEqual(
            calculate_experience_score(
                "fresher",
                job_intelligence,
            ),
            0,
        )

    def test_experienced_candidate_meets_requirement(self):
        job_intelligence = {
            "experience_level": "mid",
            "total_experience": {
                "min_years": 2,
            },
        }

        self.assertEqual(
            calculate_experience_score(
                "3 years",
                job_intelligence,
            ),
            100,
        )

    def test_experienced_candidate_below_requirement(self):
        job_intelligence = {
            "experience_level": "mid",
            "total_experience": {
                "min_years": 5,
            },
        }

        self.assertEqual(
            calculate_experience_score(
                "2 years",
                job_intelligence,
            ),
            0,
        )

    def test_unknown_experience_requirement_score(self):
        job_intelligence = {
            "experience_level": "junior",
        }

        self.assertEqual(
            calculate_experience_score(
                "3 years",
                job_intelligence,
            ),
            50,
        )

class JobMatchTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="matchuser",
            password="TestPass123!",
        )

        self.profile = self.user.profile
        self.profile.skills = "Python, Django, MySQL, REST API"
        self.profile.experience = "2 years"
        self.profile.preferred_roles = "Python Developer, Backend Developer"
        self.profile.preferred_locations = "Hyderabad"
        self.profile.preferred_job_type = "FT"
        self.profile.work_mode = "ONSITE"
        self.profile.save()

        self.company = Company.objects.create(
            name="Test Company"
        )

    def create_job(self, **overrides):
        defaults = {
            "company": self.company,
            "title": "Python Backend Developer",
            "description": "Python Django backend development",
            "location": "Hyderabad",
            "salary": 800000,
            "job_type": Job.JobType.FULL_TIME,
            "status": Job.Status.OPEN,
            "intelligence": {
                "required_skills": [
                    "Python",
                    "Django",
                    "MySQL",
                ],
                "experience_level": "junior",
                "total_experience": {
                    "min_years": 1,
                },
            },
        }

        defaults.update(overrides)

        return Job.objects.create(**defaults)

    def test_match_returns_expected_keys(self):
        from jobs.services.recommendations import (
            calculate_job_match_for_user,
        )

        job = self.create_job()

        result = calculate_job_match_for_user(
            self.user,
            job,
        )

        expected_keys = {
            "match_score",
            "matched_skills",
            "missing_skills",
            "preference_score",
        }

        self.assertTrue(
            expected_keys.issubset(result.keys())
        )

    def test_matching_skills_are_detected(self):
        from jobs.services.recommendations import (
            calculate_job_match_for_user,
        )

        job = self.create_job()

        result = calculate_job_match_for_user(
            self.user,
            job,
        )

        self.assertIn(
            "Python",
            result["matched_skills"],
        )

        self.assertIn(
            "Django",
            result["matched_skills"],
        )

    def test_missing_skills_are_detected(self):
        from jobs.services.recommendations import (
            calculate_job_match_for_user,
        )

        job = self.create_job(
            intelligence={
                "required_skills": [
                    "Python",
                    "Django",
                    "Kubernetes",
                ],
                "experience_level": "junior",
                "total_experience": {
                    "min_years": 1,
                },
            }
        )

        result = calculate_job_match_for_user(
            self.user,
            job,
        )

        self.assertIn(
            "Kubernetes",
            result["missing_skills"],
        )

    def test_match_score_is_between_zero_and_hundred(self):
        from jobs.services.recommendations import (
            calculate_job_match_for_user,
        )

        job = self.create_job()

        result = calculate_job_match_for_user(
            self.user,
            job,
        )

        self.assertGreaterEqual(
            result["match_score"],
            0,
        )

        self.assertLessEqual(
            result["match_score"],
            100,
        )


class JobFitAnalysisTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="fituser",
            password="TestPass123!",
        )

        profile = self.user.profile
        profile.skills = "Python, Django, MySQL"
        profile.experience = "2 years"
        profile.preferred_roles = "Python Developer, Backend Developer"
        profile.preferred_locations = "Hyderabad"
        profile.preferred_job_type = "FT"
        profile.work_mode = "ONSITE"
        profile.save()

        self.company = Company.objects.create(
            name="Fit Test Company"
        )

    def create_job(self, **overrides):
        defaults = {
            "company": self.company,
            "title": "Python Backend Developer",
            "description": "Backend development using Python and Django",
            "location": "Hyderabad",
            "salary": 800000,
            "job_type": Job.JobType.FULL_TIME,
            "status": Job.Status.OPEN,
            "intelligence": {
                "required_skills": [
                    "Python",
                    "Django",
                    "MySQL",
                ],
                "experience_level": "junior",
                "total_experience": {
                    "min_years": 1,
                },
            },
        }

        defaults.update(overrides)
        return Job.objects.create(**defaults)

    def test_job_fit_returns_expected_fields(self):
        from jobs.services.recommendations import analyze_job_fit

        job = self.create_job()

        result = analyze_job_fit(
            self.user,
            job,
        )

        expected_keys = {
            "match_score",
            "matched_skills",
            "missing_skills",
            "skill_score",
            "role_score",
            "experience_score",
            "preference_score",
            "role_match",
            "experience_match",
            "preference_reasons",
            "eligible",
            "strengths",
            "gaps",
        }

        self.assertTrue(
            expected_keys.issubset(result.keys())
        )

    def test_matching_profile_is_eligible(self):
        from jobs.services.recommendations import analyze_job_fit

        job = self.create_job()

        result = analyze_job_fit(
            self.user,
            job,
        )

        self.assertTrue(result["role_match"])
        self.assertTrue(result["experience_match"])
        self.assertTrue(result["eligible"])

    def test_job_fit_score_is_between_zero_and_hundred(self):
        from jobs.services.recommendations import analyze_job_fit

        job = self.create_job()

        result = analyze_job_fit(
            self.user,
            job,
        )

        self.assertGreaterEqual(
            result["match_score"],
            0,
        )

        self.assertLessEqual(
            result["match_score"],
            100,
        )

    def test_missing_skill_creates_gap(self):
        from jobs.services.recommendations import analyze_job_fit

        job = self.create_job(
            intelligence={
                "required_skills": [
                    "Python",
                    "Django",
                    "Kubernetes",
                ],
                "experience_level": "junior",
                "total_experience": {
                    "min_years": 1,
                },
            }
        )

        result = analyze_job_fit(
            self.user,
            job,
        )

        self.assertIn(
            "Kubernetes",
            result["missing_skills"],
        )

        self.assertTrue(
            any(
                "Missing required skills" in gap
                for gap in result["gaps"]
            )
        )

class JobMatchingNotificationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="notifyuser",
            password="TestPass123!",
        )

        profile = self.user.profile
        profile.skills = "Python, Django, MySQL"
        profile.experience = "2 years"
        profile.preferred_roles = "Python Developer, Backend Developer"
        profile.preferred_locations = "Hyderabad"
        profile.resume_text = "Python Django backend developer with 2 years experience."
        profile.save()

        self.company = Company.objects.create(
            name="Notification Test Company"
        )

        self.fetch_run = JobFetchRun.objects.create(
            source="Adzuna",
            status=JobFetchRun.Status.SUCCESS,
        )

    def create_job(self, **overrides):
        defaults = {
            "company": self.company,
            "title": "Python Backend Developer",
            "description": "Python Django backend development",
            "location": "Hyderabad",
            "salary": 800000,
            "job_type": Job.JobType.FULL_TIME,
            "status": Job.Status.OPEN,
            "fetch_run": self.fetch_run,
            "intelligence": {
                "required_skills": [
                    "Python",
                    "Django",
                ],
                "experience_level": "junior",
                "total_experience": {
                    "min_years": 1,
                },
            },
        }

        defaults.update(overrides)

        return Job.objects.create(**defaults)

    def test_matching_job_creates_notification(self):
        from jobs.services.job_matching import (
            match_new_jobs_to_candidates,
        )

        job = self.create_job()

        matches = match_new_jobs_to_candidates(
            self.fetch_run
        )

        self.assertEqual(len(matches), 1)

        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                job=job,
            ).exists()
        )

    def test_notification_contains_job_match_message(self):
        from jobs.services.job_matching import (
            match_new_jobs_to_candidates,
        )

        job = self.create_job()

        match_new_jobs_to_candidates(
            self.fetch_run
        )

        notification = Notification.objects.get(
            user=self.user,
            job=job,
        )

        self.assertEqual(
            notification.title,
            "New Job Match",
        )

        self.assertIn(
            job.title,
            notification.message,
        )

        self.assertIn(
            self.company.name,
            notification.message,
        )

        self.assertIn(
            "% match",
            notification.message,
        )

    def test_running_matching_twice_does_not_duplicate_notification(self):
        from jobs.services.job_matching import (
            match_new_jobs_to_candidates,
        )

        job = self.create_job()

        match_new_jobs_to_candidates(
            self.fetch_run
        )

        match_new_jobs_to_candidates(
            self.fetch_run
        )

        self.assertEqual(
            Notification.objects.filter(
                user=self.user,
                job=job,
            ).count(),
            1,
        )

    def test_user_without_resume_is_not_matched(self):
        from jobs.services.job_matching import (
            match_new_jobs_to_candidates,
        )

        self.user.profile.resume_text = ""
        self.user.profile.save()

        job = self.create_job()

        matches = match_new_jobs_to_candidates(
            self.fetch_run
        )

        self.assertEqual(len(matches), 0)

        self.assertFalse(
            Notification.objects.filter(
                user=self.user,
                job=job,
            ).exists()
        )

    def test_already_applied_user_is_not_matched(self):
        from jobs.services.job_matching import (
            match_new_jobs_to_candidates,
        )
        from applications.models import Application

        job = self.create_job()

        Application.objects.create(
            user=self.user,
            job=job,
            applicant_name="Notify User",
            applicant_email="notify@example.com",
        )

        matches = match_new_jobs_to_candidates(
            self.fetch_run
        )

        self.assertEqual(len(matches), 0)

        self.assertFalse(
            Notification.objects.filter(
                user=self.user,
                job=job,
            ).exists()
        )