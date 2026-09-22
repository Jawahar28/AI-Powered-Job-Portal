from django.contrib.auth.models import User

from jobs.models import Job, Notification
from jobs.services.recommendations import (
    calculate_job_match_for_user,
    is_experience_eligible,
)


MATCH_THRESHOLD = 60


def match_new_jobs_to_candidates(fetch_run):
    matches = []

    jobs = (
        Job.objects
        .filter(
            fetch_run=fetch_run,
            status=Job.Status.OPEN,
        )
        .select_related("company")
    )

    users = (
        User.objects
        .filter(profile__resume_text__isnull=False)
        .exclude(profile__resume_text="")
    )

    for job in jobs:
        for user in users:

            profile = user.profile

            if user.applications.filter(job=job).exists():
                continue

            if not is_experience_eligible(
                profile.experience,
                job.intelligence,
            ):
                continue

            result = calculate_job_match_for_user(
                user,
                job,
            )

            if result["match_score"] >= MATCH_THRESHOLD:

                matches.append({
                    "user": user,
                    "job": job,
                    "match_score": result["match_score"],
                    "matched_skills": result["matched_skills"],
                    "missing_skills": result["missing_skills"],
                })

                Notification.objects.get_or_create(
                    user=user,
                    job=job,
                    defaults={
                        "title": "New Job Match",
                        "message": (
                            f"{job.title} at {job.company.name} "
                            f"matches your profile with a "
                            f"{result['match_score']}% match."
                        ),
                    },
                )

    return matches