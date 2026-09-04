def analyze_candidate(profile):

    skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    skills_lower = {
        skill.lower()
        for skill in skills
    }

    primary_roles = []
    secondary_roles = []

    # -------------------------
    # Backend / Python
    # -------------------------

    if (
        "python" in skills_lower
        and (
            "django" in skills_lower
            or "django rest framework" in skills_lower
            or "rest api" in skills_lower
            or "rest apis" in skills_lower
        )
    ):
        primary_roles.extend([
            "Python Developer",
            "Django Developer",
            "Backend Developer",
        ])

    # -------------------------
    # Data
    # -------------------------

    if (
        "python" in skills_lower
        and (
            "pandas" in skills_lower
            or "numpy" in skills_lower
            or "sql" in skills_lower
        )
    ):
        secondary_roles.extend([
            "Data Analyst",
            "Python Data Analyst",
        ])

    # -------------------------
    # Machine Learning
    # -------------------------

    if (
        "machine learning" in skills_lower
        or "scikit-learn" in skills_lower
    ):
        secondary_roles.extend([
            "Machine Learning Engineer",
            "ML Engineer",
        ])

    return {
        "skills": skills,
        "primary_roles": list(dict.fromkeys(primary_roles)),
        "secondary_roles": list(dict.fromkeys(secondary_roles)),
        "search_keywords": list(
            dict.fromkeys(
                primary_roles + secondary_roles
            )
        ),
    }