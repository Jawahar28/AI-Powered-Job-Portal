import re

from jobs.models import Job
from jobs.services.job_intelligence import analyze_candidate

def is_experience_eligible(
    candidate_experience,
    job_intelligence
):

    if not candidate_experience:
        return True

    candidate_text = candidate_experience.lower().strip()

    total_experience = job_intelligence.get(
        "total_experience"
    )

    if not total_experience:
        return True

    required_years = total_experience.get(
        "min_years",
        0
    )

    # Fresher
    if candidate_text in [
        "0",
        "0 years",
        "fresher",
        "freshers",
    ]:
        return required_years <= 1

    # Extract candidate years
    match = re.search(
        r"(\d+(?:\.\d+)?)",
        candidate_text
    )

    if not match:
        return True

    candidate_years = float(match.group(1))

    return candidate_years >= required_years

def calculate_intelligence_skill_match(
    candidate_skills,
    job_intelligence
):
    candidate_skills_lower = {
        skill.lower().strip()
        for skill in candidate_skills
    }

    required_skills = job_intelligence.get(
        "required_skills",
        []
    )

    preferred_skills = job_intelligence.get(
        "preferred_skills",
        []
    )

    matched_skills = []

    for skill in required_skills:

        if skill.lower() in candidate_skills_lower:
            matched_skills.append(skill)

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in matched_skills
    ]

    required_score = 0

    if required_skills:
        required_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

    preferred_matched = [
        skill
        for skill in preferred_skills
        if skill.lower() in candidate_skills_lower
    ]

    preferred_score = 0

    if preferred_skills:
        preferred_score = (
            len(preferred_matched)
            / len(preferred_skills)
        ) * 100

    final_score = (
        required_score * 0.8
        + preferred_score * 0.2
    )

    return {
        "match_score": round(final_score),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


def get_recommended_jobs(user):

    profile = user.profile

    analysis = analyze_candidate(profile)

    primary_roles = analysis["primary_roles"]
    secondary_roles = analysis["secondary_roles"]

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
        if not is_experience_eligible(profile.experience, job.intelligence):
            continue

        skill_match = calculate_intelligence_skill_match(candidate_skills,job.intelligence)

        role_score = calculate_role_score(job.title,primary_roles,secondary_roles)

        experience_score = calculate_experience_score(profile.experience,job.intelligence)

        final_score = (skill_match["match_score"] * 0.6+ role_score * 0.3+ experience_score * 0.1)

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
    job_intelligence
):
    if not candidate_experience:
        return 0

    candidate_text = candidate_experience.lower().strip()

    total_experience = job_intelligence.get(
        "total_experience"
    )

    # Job does not specify experience
    if not total_experience:
        return 50

    required_years = total_experience.get(
        "min_years",
        0
    )

    # Fresher
    if candidate_text in [
        "0",
        "0 years",
        "fresher",
        "freshers",
    ]:
        if required_years <= 1:
            return 100

        return 0

    # Extract candidate years
    match = re.search(
        r"(\d+(?:\.\d+)?)",
        candidate_text
    )

    if not match:
        return 50

    candidate_years = float(match.group(1))

    if candidate_years >= required_years:
        return 100

    return 0


def calculate_role_score(
    job_title,
    primary_roles,
    secondary_roles
):

    title = job_title.lower()

    # Primary role match
    for role in primary_roles:
        role_words = role.lower().split()

        if all(word in title for word in role_words):
            return 100

    # Secondary role match
    for role in secondary_roles:
        role_words = role.lower().split()

        if all(word in title for word in role_words):
            return 70

    return 0