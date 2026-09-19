import re

from jobs.models import Job, JobFetchRun
from jobs.services.job_intelligence import analyze_candidate

from django.utils import timezone
from datetime import timedelta

def is_experience_eligible(
    candidate_experience,
    job_intelligence
):

    if not candidate_experience:
        return True

    candidate_text = (
        candidate_experience
        .lower()
        .strip()
    )

    job_level = job_intelligence.get(
        "experience_level"
    )

    # ------------------------------------------
    # Fresher / Entry-level candidate
    # ------------------------------------------

    if candidate_text in [
        "0",
        "0 years",
        "fresher",
        "freshers",
        "entry level",
    ]:

        # Explicit seniority should reject
        # a fresher even if years weren't extracted.

        if job_level in [
            "senior",
            "lead",
            "management",
        ]:
            return False

        total_experience = job_intelligence.get(
            "total_experience"
        )

        if not total_experience:
            return True

        required_years = total_experience.get(
            "min_years",
            0
        )

        return required_years <= 1


    # ------------------------------------------
    # Experienced candidate
    # ------------------------------------------

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        candidate_text
    )

    if not match:
        return True

    candidate_years = float(
        match.group(1)
    )

    total_experience = job_intelligence.get(
        "total_experience"
    )

    if not total_experience:

        # We don't know the numerical requirement.
        # Don't reject solely because extraction failed.

        return True

    required_years = total_experience.get(
        "min_years",
        0
    )

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

    matched_skills = [
        skill
        for skill in required_skills
        if skill.lower() in candidate_skills_lower
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in matched_skills
    ]

    # Required skill coverage
    required_score = 0

    if required_skills:
        required_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

    # Preferred skill coverage
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

    # Base skill score
    skill_score = (
        required_score * 0.8
        + preferred_score * 0.2
    )

    # Depth bonus:
    # More matched required skills means stronger evidence
    if len(matched_skills) >= 5:
        skill_score += 10
    elif len(matched_skills) >= 4:
        skill_score += 7
    elif len(matched_skills) >= 3:
        skill_score += 5
    elif len(matched_skills) >= 2:
        skill_score += 3

    skill_score = min(round(skill_score), 100)

    return {
        "match_score": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


def calculate_job_match_for_user(user, job):
    profile = user.profile

    analysis = analyze_candidate(profile)

    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    skill_match = calculate_intelligence_skill_match(
        candidate_skills,
        job.intelligence
    )

    role_score = calculate_role_score(
        job.title,
        analysis["primary_roles"],
        analysis["secondary_roles"]
    )

    experience_score = calculate_experience_score(
        profile.experience,
        job.intelligence
    )

    preference_score = calculate_preference_score(
        profile,
        job
    )

    final_score = (
        skill_match["match_score"] * 0.55
        + role_score * 0.25
        + experience_score * 0.10
        + preference_score * 0.10
    )

    return {
        "match_score": round(final_score),
        "matched_skills": skill_match["matched_skills"],
        "missing_skills": skill_match["missing_skills"],
        "preference_score" : preference_score,
    }

def analyze_job_fit(user, job):
    profile = user.profile

    analysis = analyze_candidate(profile)

    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    # -------------------------
    # Skill analysis
    # -------------------------

    skill_match = calculate_intelligence_skill_match(
        candidate_skills,
        job.intelligence
    )

    # -------------------------
    # Role analysis
    # -------------------------

    role_score = calculate_role_score(
        job.title,
        analysis["primary_roles"],
        analysis["secondary_roles"]
    )

    # -------------------------
    # Experience analysis
    # -------------------------

    experience_score = calculate_experience_score(
        profile.experience,
        job.intelligence
    )

    preference_score = calculate_preference_score(
        profile,
        job
    )

    preference_reasons = get_preference_reasons(
    profile,
    job
    )

    # -------------------------
    # Final match score
    # -------------------------

    final_score = (
        skill_match["match_score"] * 0.6
        + role_score * 0.3
        + experience_score * 0.1
    )

    # -------------------------
    # Boolean match indicators
    # -------------------------

    role_match = role_score > 0
    total_experience = job.intelligence.get("total_experience")

    job_level = job.intelligence.get("experience_level")

    if (not total_experience and not job_level):
        experience_match = None
    else:
        experience_match = experience_score == 100

    # -------------------------
    # Strengths
    # -------------------------

    strengths = []

    if skill_match["matched_skills"]:
        strengths.append(
            f"You match {len(skill_match['matched_skills'])} required skill(s)."
        )

    if role_match:
        strengths.append(
            "Your profile matches the job role."
        )

    if experience_match:
        strengths.append(
            "Your experience matches the job requirements."
        )

    for reason in preference_reasons:
        strengths.append(reason)

    # -------------------------
    # Gaps
    # -------------------------

    gaps = []

    if skill_match["missing_skills"]:
        gaps.append(
            "Missing required skills: "
            + ", ".join(skill_match["missing_skills"])
        )

    if not role_match:
        gaps.append(
            "Your current profile does not strongly match the job role."
        )

    if experience_match is False:
        gaps.append(
            "Your experience does not fully match the job requirements."
        )

    

    return {
    "match_score": round(final_score),

    "matched_skills": skill_match["matched_skills"],
    "missing_skills": skill_match["missing_skills"],

    "skill_score": skill_match["match_score"],
    "role_score": role_score,
    "experience_score": experience_score,
    "preference_score": preference_score,

    "role_match": role_match,
    "experience_match": experience_match,

    "preference_reasons": preference_reasons,

    "eligible": (
        experience_match is not False
        and role_match
    ),

    "strengths": strengths,
    "gaps": gaps,
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

        experience_score = calculate_experience_score(
            profile.experience,
            job.intelligence
        )

        preference_score = calculate_preference_score(
            profile,
            job
        )

        final_score = (
            skill_match["match_score"] * 0.55
            + role_score * 0.25
            + experience_score * 0.10
            + preference_score * 0.10
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


def get_new_recommended_jobs(user, days = 1):
    """
    Return personalized recommendations that were
    imported into JOBCode recently.
    """

    latest_run = (JobFetchRun.objects.filter(source='Adzuna', status = JobFetchRun.Status.SUCCESS).order_by("-finished_at").first())

    if not latest_run:
        return []

    recommended_jobs = get_recommended_jobs(user)

    new_jobs = [job for job in recommended_jobs if job.fetch_run_id == latest_run.id]

    return new_jobs

def calculate_experience_score(
    candidate_experience,
    job_intelligence
):

    if not candidate_experience:
        return 50

    candidate_text = (
        candidate_experience
        .lower()
        .strip()
    )

    job_level = job_intelligence.get(
        "experience_level"
    )

    # Fresher
    if candidate_text in [
        "0",
        "0 years",
        "fresher",
        "freshers",
        "entry level",
    ]:

        if job_level in [
            "senior",
            "lead",
            "management",
        ]:
            return 0

        total_experience = job_intelligence.get(
            "total_experience"
        )

        if not total_experience:
            return 50

        required_years = total_experience.get(
            "min_years",
            0
        )

        if required_years <= 1:
            return 100

        return 0

    # Experienced candidate
    match = re.search(
        r"(\d+(?:\.\d+)?)",
        candidate_text
    )

    if not match:
        return 50

    candidate_years = float(
        match.group(1)
    )

    total_experience = job_intelligence.get(
        "total_experience"
    )

    if not total_experience:
        return 50

    required_years = total_experience.get(
        "min_years",
        0
    )

    if candidate_years >= required_years:
        return 100

    return 0


def calculate_role_score(
    job_title,
    primary_roles,
    secondary_roles
):
    title = job_title.lower()

    # Exact primary role phrase
    for role in primary_roles:
        role_text = role.lower()

        if role_text in title:
            return 100

    # Strong primary-role keyword combination
    for role in primary_roles:
        role_words = role.lower().split()

        matched_words = sum(
            1
            for word in role_words
            if word in title
        )

        if len(role_words) >= 2 and matched_words == len(role_words):
            return 90

    # Secondary role phrase
    for role in secondary_roles:
        role_text = role.lower()

        if role_text in title:
            return 70

    return 0


def _split_preferences(value):
    """
    Convert comma-separated profile preferences into
    normalized lowercase values.
    """
    if not value:
        return []

    return [
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    ]


def calculate_preference_score(profile, job):
    """
    Calculate how well a job matches the candidate's
    explicit career preferences.

    Maximum score: 100
    """

    scores = []

    # ------------------------------------------
    # Preferred roles
    # ------------------------------------------

    preferred_roles = _split_preferences(
        profile.preferred_roles
    )

    if preferred_roles:

        title = job.title.lower()

        role_match = any(
            role in title
            for role in preferred_roles
        )

        scores.append(100 if role_match else 0)

    # ------------------------------------------
    # Preferred locations
    # ------------------------------------------

    preferred_locations = _split_preferences(
        profile.preferred_locations
    )

    if preferred_locations:

        job_location = job.location.lower()

        location_match = any(
            location in job_location
            for location in preferred_locations
        )

        scores.append(100 if location_match else 0)

    # ------------------------------------------
    # Preferred job type
    # ------------------------------------------

    if profile.preferred_job_type:

        scores.append(
            100
            if job.job_type == profile.preferred_job_type
            else 0
        )

    # ------------------------------------------
    # Work mode
    # ------------------------------------------

    if profile.work_mode:

        job_text = (
            f"{job.title} "
            f"{job.location} "
            f"{job.description}"
        ).lower()

        if profile.work_mode == "REMOTE":

            mode_match = (
                "remote" in job_text
                or "work from home" in job_text
                or "wfh" in job_text
            )

        elif profile.work_mode == "HYBRID":

            mode_match = "hybrid" in job_text

        elif profile.work_mode == "ONSITE":

            mode_match = (
                "on-site" in job_text
                or "onsite" in job_text
                or "office" in job_text
            )

        else:
            mode_match = False

        scores.append(100 if mode_match else 0)

    # ------------------------------------------
    # Expected salary
    # ------------------------------------------

    if profile.expected_salary and job.salary:

        if job.salary >= profile.expected_salary:
            scores.append(100)
        else:
            # Give partial credit when salary is reasonably close.
            salary_ratio = (
                job.salary / profile.expected_salary
            ) * 100

            scores.append(
                max(0, min(round(salary_ratio), 100))
            )

    # ------------------------------------------
    # No preferences configured
    # ------------------------------------------

    if not scores:
        return 50

    return round(sum(scores) / len(scores))


def get_preference_reasons(profile, job):
    """
    Return human-readable reasons explaining how a job
    matches the candidate's career preferences.
    """

    reasons = []

    # ------------------------------------------
    # Preferred role
    # ------------------------------------------

    preferred_roles = _split_preferences(
        profile.preferred_roles
    )

    if preferred_roles:
        title = job.title.lower()

        matched_role = next(
            (
                role
                for role in preferred_roles
                if role in title
            ),
            None
        )

        if matched_role:
            reasons.append(
                f"'{job.title}' matches your preferred role "
                f"'{matched_role.title()}'."
            )

    # ------------------------------------------
    # Preferred location
    # ------------------------------------------

    preferred_locations = _split_preferences(
        profile.preferred_locations
    )

    if preferred_locations:
        job_location = job.location.lower()

        matched_location = next(
            (
                location
                for location in preferred_locations
                if location in job_location
            ),
            None
        )

        if matched_location:
            reasons.append(
                f"This job matches your preferred location "
                f"'{matched_location.title()}'."
            )

    # ------------------------------------------
    # Job type
    # ------------------------------------------

    if profile.preferred_job_type:

        if job.job_type == profile.preferred_job_type:
            reasons.append(
                f"This is a {job.get_job_type_display().lower()} "
                f"position, matching your preference."
            )

    # ------------------------------------------
    # Work mode
    # ------------------------------------------

    if profile.work_mode:

        job_text = (
            f"{job.title} "
            f"{job.location} "
            f"{job.description}"
        ).lower()

        if profile.work_mode == "REMOTE":

            if (
                "remote" in job_text
                or "work from home" in job_text
                or "wfh" in job_text
            ):
                reasons.append(
                    "This job supports remote work, "
                    "matching your preference."
                )

        elif profile.work_mode == "HYBRID":

            if "hybrid" in job_text:
                reasons.append(
                    "This job supports hybrid work, "
                    "matching your preference."
                )

        elif profile.work_mode == "ONSITE":

            if (
                "on-site" in job_text
                or "onsite" in job_text
                or "office" in job_text
            ):
                reasons.append(
                    "This job supports on-site work, "
                    "matching your preference."
                )

    # ------------------------------------------
    # Expected salary
    # ------------------------------------------

    if profile.expected_salary and job.salary:

        if job.salary >= profile.expected_salary:
            reasons.append(
                "The listed salary meets or exceeds "
                "your expected salary."
            )

    return reasons