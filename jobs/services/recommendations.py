from jobs.models import Job
from accounts.utils import calculate_job_match
from jobs.services.job_intelligence import analyze_candidate


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

    candidate_text = candidate_experience.lower()
    job_text = job_text.lower()

    if any(word in candidate_text for word in [
        "fresher",
        "0",
        "entry",
        "graduate",
    ]):

        if any(word in job_text for word in [
            "fresher",
            "entry level",
            "entry-level",
            "0-1",
            "0 - 1",
            "junior",
        ]):
            return 100

        if any(word in job_text for word in [
            "senior",
            "lead",
            "manager",
            "5+ years",
            "7+ years",
            "8+ years",
        ]):
            return 0

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