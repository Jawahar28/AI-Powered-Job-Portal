import re

from jobs.models import Job
from accounts.utils import calculate_job_match
from jobs.services.job_intelligence import analyze_candidate

def is_experience_eligible(candidate_experience, job_text):

    if not candidate_experience:
        return True

    candidate_text = candidate_experience.lower().strip()
    job_text = job_text.lower()

    # Fresher / 0 years
    if candidate_text in [
        "0",
        "0 years",
        "fresher",
        "freshers",
    ]:

        # Explicit senior-level keywords
        senior_keywords = [
            "senior",
            "sr.",
            "sr ",
            "lead",
            "manager",
            "principal",
        ]

        if any(
            keyword in job_text
            for keyword in senior_keywords
        ):
            return False

        # Detect requirements such as:
        # 2 years
        # 3+ years
        # 5 years
        # 7 YoE
        # 8+ YoE
        experience_matches = re.findall(
            r'(\d+)\s*(?:\+)?\s*(?:years?|yoe)',
            job_text
        )

        for years in experience_matches:

            if int(years) > 1:
                return False

    return True


def get_recommended_jobs(user):

    profile = user.profile

    analysis = analyze_candidate(profile)

    candidate_roles = analysis["roles"]

    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    applied_job_ids = user.applications.values_list(
        "job_id",
        flat=True
    )

    jobs = (
        Job.objects
        .filter(status=Job.Status.OPEN)
        .exclude(id__in=applied_job_ids)
        .select_related("company")
    )

    recommendations = []

    for job in jobs:

        job_text = job.title + " " + job.description

        if not is_experience_eligible(profile.experience, job_text):
            continue

        skill_match = calculate_job_match(
            candidate_skills,
            job.description
        )

        role_score = calculate_role_score(
            job.title,
            candidate_roles
        )

        experience_score = calculate_experience_score(
            profile.experience,
            job.title + " " + job.description
        )

        final_score = (
            skill_match["match_score"] * 0.7
            + role_score * 0.2
            + experience_score * 0.1
        )

        if skill_match["match_score"] > 0 or role_score > 0:

            job.match_score = round(final_score)

            job.matched_skills = (
                skill_match["matched_skills"]
            )

            job.missing_skills = (
                skill_match["missing_skills"]
            )

            recommendations.append(job)

    recommendations.sort(
        key=lambda job: job.match_score,
        reverse=True
    )

    return recommendations


def calculate_experience_score(
    candidate_experience,
    job_text
):
    if not candidate_experience:
        return 0

    candidate_text = candidate_experience.lower().strip()
    job_text = job_text.lower()

    # Candidate is a fresher
    if candidate_text in ["0", "0 years", "fresher", "freshers"]:
        if any(word in job_text for word in [
            "fresher",
            "entry level",
            "entry-level",
            "0-1 years",
            "0 - 1 years",
            "0-1 years",
            "junior",
            "intern",
            "internship",
        ]):
            return 100

        if any(word in job_text for word in [
            "senior",
            "sr.",
            "lead",
            "manager",
            "5+ years",
            "6+ years",
            "7+ years",
            "8+ years",
            "10+ years",
        ]):
            return 0

        # Experience requirement isn't clearly stated
        return 50

    return 50


def calculate_role_score(job_title, candidate_roles):

    title = job_title.lower()

    role_keywords = {
        "python developer": ["python", "developer"],
        "django developer": ["django", "developer"],
        "backend developer": ["backend", "developer"],
        "data analyst": ["data", "analyst"],
        "python data analyst": ["python", "data", "analyst"],
        "machine learning engineer": [
            "machine learning",
            "engineer"
        ],
        "ml engineer": ["ml", "engineer"],
    }

    best_score = 0

    for role in candidate_roles:

        keywords = role_keywords.get(
            role.lower(),
            []
        )

        if not keywords:
            continue

        matched = sum(
            keyword in title
            for keyword in keywords
        )

        if matched == len(keywords):
            score = 100

        elif matched > 0:
            score = 50

        else:
            score = 0

        best_score = max(best_score, score)

    return best_score