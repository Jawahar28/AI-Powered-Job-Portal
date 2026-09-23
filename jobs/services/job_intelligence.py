import re


def analyze_job_description(title, description):
    title_text = title.lower()
    text = description.lower()
    combined_text = title_text + " " + text

    result = {
        "role": None,
        "total_experience": None,
        "skill_experience": {},
        "required_skills": [],
        "preferred_skills": [],
        "experience_level": None,
    }

    known_skills = [
        "python",
        "django",
        "django rest framework",
        "fastapi",
        "flask",
        "rest api",
        "rest apis",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "redis",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "java",
        "c#",
        "machine learning",
        "deep learning",
        "scikit-learn",
        "pytorch",
        "tensorflow",
        "pandas",
        "numpy",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "linux",
        "git",
        "github",
        "html",
        "css",
    ]

    # -------------------------
    # Role
    # -------------------------

    role_patterns = [
        r"(?:senior\s+)?backend\s+developer",
        r"(?:senior\s+)?software\s+engineer",
        r"(?:senior\s+)?python\s+developer",
        r"(?:senior\s+)?django\s+developer",
        r"(?:senior\s+)?data\s+analyst",
        r"(?:senior\s+)?data\s+scientist",
        r"(?:senior\s+)?machine\s+learning\s+engineer",
        r"(?:senior\s+)?ml\s+engineer",
    ]

    for pattern in role_patterns:
        match = re.search(pattern, combined_text)

        if match:
            result["role"] = match.group(0).strip()
            break

    # ------------------------------------------
    # Total Experience
    # ------------------------------------------

    experience_patterns = [
        # 0-1 years / 2-4 years
        r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",

        # 0 to 2 years
        r"(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",

        # 3+ years experience
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
        r"\s*(?:of\s+)?(?:total\s+|overall\s+)?experience",

        # minimum 3 years
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)"
        r"\s*\+?\s*(?:years?|yrs?)",

        # 3 YOE / 3 YoE
        r"(\d+(?:\.\d+)?)\s*\+?\s*yoe\b",
    ]

    for pattern in experience_patterns:
        match = re.search(pattern, combined_text)

        if match:
            if match.lastindex == 2:
                result["total_experience"] = {
                    "min_years": float(match.group(1)),
                    "max_years": float(match.group(2)),
                }
            else:
                result["total_experience"] = {
                    "min_years": float(match.group(1)),
                    "max_years": None,
                }

            break

    # ------------------------------------------
    # Experience Level
    # ------------------------------------------

    # We prioritize the JOB TITLE because descriptions can
    # contain unrelated seniority terms.

    title_level = None

    # Management / executive signals in title
    if re.search(
        r"\b(director|vice president|vp|head|manager)\b",
        title_text,
    ):
        title_level = "management"

    # Lead / principal / staff signals in title
    elif re.search(
        r"\b(lead|principal|staff)\b",
        title_text,
    ):
        title_level = "lead"

    # Senior signals in title
    elif re.search(
        r"\b(senior|sr\.?)\b",
        title_text,
    ):
        title_level = "senior"

    # Junior signals in title
    elif re.search(
        r"\b(junior|jr\.?)\b",
        title_text,
    ):
        title_level = "junior"

    # Entry-level signals in title
    elif re.search(
        r"\b(fresher|freshers|entry[- ]level)\b",
        title_text,
    ):
        title_level = "entry"

    if title_level:
        experience_level = title_level

    else:
        # If the title does not contain a clear level,
        # inspect the full job text.

        if re.search(
            r"\b(fresher|freshers|entry[- ]level|no experience)\b",
            combined_text,
        ):
            experience_level = "entry"

        elif re.search(
            r"\b(director|vice president|vp|head|manager)\b",
            combined_text,
        ):
            experience_level = "management"

        elif re.search(
            r"\b(lead|principal|staff)\b",
            combined_text,
        ):
            experience_level = "lead"

        elif re.search(
            r"\b(senior|sr\.?)\b",
            combined_text,
        ):
            experience_level = "senior"

        elif re.search(
            r"\b(junior|jr\.?)\b",
            combined_text,
        ):
            experience_level = "junior"

        else:
            experience_level = None

    result["experience_level"] = experience_level

    # -------------------------
    # Skill-specific experience
    # -------------------------

    for skill in known_skills:
        pattern = (
            rf"(\d+)\+?\s*(?:years?|yrs?)"
            rf"(?:\s+of\s+experience)?"
            rf"\s+(?:in|with|using|working\s+with)\s+"
            rf"{re.escape(skill)}"
        )

        match = re.search(pattern, text)

        if match:
            result["skill_experience"][skill] = int(
                match.group(1)
            )

    # -------------------------
    # Required vs Preferred
    # -------------------------

    preferred_section = re.search(
        r"(preferred|nice to have|good to have|bonus|desired)"
        r"\s*:?\s*(.*?)(?=\n\s*"
        r"(?:requirements|required|qualifications|"
        r"responsibilities|benefits)"
        r"\s*:|$)",
        text,
        re.DOTALL,
    )

    preferred_text = ""

    if preferred_section:
        preferred_text = preferred_section.group(2).lower()

    for skill in known_skills:
        if re.search(
            rf"\b{re.escape(skill)}\b",
            combined_text,
        ) is None:
            continue

        if skill in preferred_text:
            result["preferred_skills"].append(skill)
        else:
            result["required_skills"].append(skill)

    return result


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
        "primary_roles": list(
            dict.fromkeys(primary_roles)
        ),
        "secondary_roles": list(
            dict.fromkeys(secondary_roles)
        ),
        "search_keywords": list(
            dict.fromkeys(
                primary_roles + secondary_roles
            )
        ),
    }