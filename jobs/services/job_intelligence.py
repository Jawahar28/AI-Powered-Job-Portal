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
    }

    known_skills = [
        "python",
        "django",
        "django rest framework",
        "sql",
        "mysql",
        "javascript",
        "react",
        "java",
        "c#",
        "machine learning",
        "deep learning",
        "pandas",
        "numpy",
        "aws",
        "azure",
        "gcp",
        "php",
        "css",
    ]

    # -------------------------
    # Role
    # -------------------------

    role_patterns = [
        r"(senior\s+)?backend\s+developer",
        r"(senior\s+)?software\s+engineer",
        r"(senior\s+)?python\s+developer",
        r"(senior\s+)?django\s+developer",
        r"(senior\s+)?data\s+analyst",
        r"(senior\s+)?data\s+scientist",
        r"(senior\s+)?machine\s+learning\s+engineer",
        r"(senior\s+)?ml\s+engineer",
    ]

    for pattern in role_patterns:

        match = re.search(pattern, combined_text)

        if match:
            result["role"] = match.group(0).strip()
            break

    # -------------------------
    # Total experience
    # -------------------------

        # ------------------------------------------
    # Total Experience
    # ------------------------------------------

    experience_patterns = [

    # ------------------------------------------
    # Ranges must come FIRST
    # ------------------------------------------

    # 0-1 years / 2–4 years
    r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)"
    r"\s*(?:years?|yrs?)",

    # 0 to 2 years
    r"(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)"
    r"\s*(?:years?|yrs?)",

    # ------------------------------------------
    # Single minimum experience
    # ------------------------------------------

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

        match = re.search(
            pattern,
            combined_text
        )

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

    experience_level = None

    if re.search(
        r"\b(fresher|freshers|entry[- ]level|"
        r"no experience|0\s*[-–]\s*1\s*years?)\b",
        combined_text
    ):
        experience_level = "entry"

    elif re.search(
        r"\b(junior|jr\.?|associate)\b",
        combined_text
    ):
        experience_level = "junior"

    elif re.search(
        r"\b(senior|sr\.?)\b",
        combined_text
    ):
        experience_level = "senior"

    elif re.search(
        r"\b(lead|principal|staff)\b",
        combined_text
    ):
        experience_level = "lead"

    elif re.search(
        r"\b(manager|director|head)\b",
        combined_text
    ):
        experience_level = "management"

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
    r"(preferred|nice to have|good to have|bonus|desired)\s*:?\s*(.*?)(?=\n\s*(?:requirements|required|qualifications|responsibilities|benefits)\s*:|$)",
    text,
    re.DOTALL
)

    preferred_text = ""

    if preferred_section:
        preferred_text = preferred_section.group(2)

    for skill in known_skills:

        if re.search(rf"\b{re.escape(skill)}\b",combined_text) is None:
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
        "primary_roles": list(dict.fromkeys(primary_roles)),
        "secondary_roles": list(dict.fromkeys(secondary_roles)),
        "search_keywords": list(
            dict.fromkeys(
                primary_roles + secondary_roles
            )
        ),
    }