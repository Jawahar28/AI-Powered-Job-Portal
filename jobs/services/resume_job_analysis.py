from jobs.services.recommendations import (
    calculate_job_match_for_user,
    is_experience_eligible,
)


def analyze_resume_for_job(user, job):
    """
    Compare a candidate's profile/resume against a specific job.

    Reuses JOBCode's existing recommendation engine rather than
    creating a second skill-matching system.
    """

    profile = user.profile

    # Existing JOBCode matching logic
    match_result = calculate_job_match_for_user(user, job)

    match_score = match_result["match_score"]
    matched_skills = match_result["matched_skills"]
    missing_skills = match_result["missing_skills"]

    # Experience eligibility
    experience_eligible = is_experience_eligible(
        profile.experience,
        job.intelligence,
    )

    # Resume availability
    has_resume = bool(profile.resume_text)

    # Resume completeness
    resume_completeness = 100 if has_resume else 0

    # Application readiness
    #
    # We intentionally keep this separate from the existing match score.
    # Match score = how well the candidate matches the job.
    # Readiness = whether the candidate appears ready to apply.
    readiness_score = 0

    # Job match contributes the largest portion.
    readiness_score += match_score * 0.60

    # Experience eligibility.
    if experience_eligible:
        readiness_score += 20

    # Resume availability.
    if has_resume:
        readiness_score += 10

    # Required skills coverage.
    required_skills = job.intelligence.get("required_skills", [])

    if required_skills:
        skill_coverage = (
            len(matched_skills) / len(required_skills)
        ) * 100
    else:
        skill_coverage = 0

    readiness_score += skill_coverage * 0.10

    readiness_score = round(min(readiness_score, 100))

    # Human-readable reasons
    strengths = []
    improvements = []

    if matched_skills:
        strengths.append(
            f"Your profile matches {len(matched_skills)} "
            f"of the identified job skills."
        )

    if experience_eligible:
        strengths.append(
            "Your experience level is eligible for this role."
        )
    else:
        improvements.append(
            "Your current experience level does not meet "
            "the detected experience requirements."
        )

    if missing_skills:
        improvements.append(
            "Consider strengthening these skills: "
            + ", ".join(missing_skills)
        )

    if not has_resume:
        improvements.append(
            "Upload a resume to improve application readiness."
        )

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "preference_score": match_result.get("preference_score", 0),
        "experience_eligible": experience_eligible,
        "has_resume": has_resume,
        "resume_completeness": resume_completeness,
        "skill_coverage": round(skill_coverage),
        "readiness_score": readiness_score,
        "strengths": strengths,
        "improvements": improvements,
    }