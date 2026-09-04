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

    roles = []
    search_keywords = []

    # Backend
    if (
        "python" in skills_lower
        and (
            "django" in skills_lower
            or "rest api" in skills_lower
            or "rest apis" in skills_lower
        )
    ):
        roles.extend([
            "Python Developer",
            "Django Developer",
            "Backend Developer",
        ])

        search_keywords.extend([
            "Python Django",
            "Python Backend",
            "Django REST",
        ])

    # Data
    if (
        "python" in skills_lower
        and (
            "pandas" in skills_lower
            or "numpy" in skills_lower
            or "sql" in skills_lower
        )
    ):
        roles.extend([
            "Data Analyst",
            "Python Data Analyst",
        ])

        search_keywords.extend([
            "Python Data Analyst",
            "Data Analyst Python",
        ])

    # Machine Learning
    if (
        "machine learning" in skills_lower
        or "scikit-learn" in skills_lower
    ):
        roles.extend([
            "Machine Learning Engineer",
            "ML Engineer",
        ])

        search_keywords.extend([
            "Machine Learning",
            "ML Engineer",
        ])

    return {
        "skills": skills,
        "roles": list(dict.fromkeys(roles)),
        "search_keywords": list(
            dict.fromkeys(search_keywords)
        ),
    }