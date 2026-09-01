from PyPDF2 import PdfReader
from jobs.models import Job

SKILL_ALIASES = {

    "python": "Python",

    "django": "Django",

    "django rest framework": "Django REST Framework",
    "drf": "Django REST Framework",

    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    "mysql": "MySQL",

    "sql": "SQL",

    "html": "HTML",

    "css": "CSS",

    "javascript": "JavaScript",
    "js": "JavaScript",

    "git": "Git",

    "github": "GitHub",

    "postman": "Postman",

    "vs code": "VS Code",
    "visual studio code": "VS Code",

    "pycharm": "PyCharm",

    "pandas": "Pandas",

    "numpy": "NumPy",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "keras": "Keras",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    "data structures": "Data Structures",

    "algorithms": "Algorithms",

    "object-oriented programming": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",

    "flask": "Flask",

    "xgboost": "XGBoost",

    "bootstrap": "Bootstrap",

}

def normalize_skill(skill):
    skill = skill.strip().lower()

    return SKILL_ALIASES.get(skill, skill.title())

def extract_text_from_resume(resume_file):
    try:
        reader = PdfReader(resume_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
        return text

    except Exception as e:
        return ""


# def normalize_skill(skill):
#     skill = skill.lower().strip()

#     skill_mapping = {
#         "rest apis" : "rest api",
#         "rest api" : "rest api",

#         "js" :  "javascript",
#         "javascript" : "javascript",

#         "oop" : "object-oriented programming",
#         "object oriented programming" : "object-oriented programming",
#         "object-oriented programming" : "object-oriented programming",

#         "django rest framework" : "django rest framework",

#         "scikit learn" : "scikit-learn",
#         "scikit-learn" : "scikit-learn",
#     }

#     return skill_mapping.get(skill, skill)


def extract_skills_from_resume(resume_text):

    known_skills = [

        "Python",
        "Django",
        "Django REST Framework",

        "REST API",
        "REST APIs",

        "MySQL",
        "SQL",

        "HTML",
        "CSS",

        "JavaScript",
        "JS",

        "Git",
        "GitHub",

        "Postman",
        "VS Code",
        "PyCharm",

        "Pandas",
        "NumPy",

        "Scikit-learn",
        "Keras",

        "Machine Learning",
        "Deep Learning",

        "Data Structures",
        "Algorithms",

        "Object-Oriented Programming",
        "OOP",

        "Flask",
        "XGBoost",

        "Bootstrap",
    ]

    extracted_skills = []

    resume_text_lower = resume_text.lower()

    for skill in known_skills:

        if skill.lower() in resume_text_lower:

            normalized_skill = normalize_skill(skill)

            if normalized_skill not in extracted_skills:

                extracted_skills.append(normalized_skill)

    return extracted_skills

    
def calculate_job_match(candidate_skills, job_description):

    job_skills = extract_skills_from_resume(job_description)


    # Normalize candidate skills
    normalized_candidate_skills = set()

    for skill in candidate_skills:

        normalized_skill = normalize_skill(skill)

        normalized_candidate_skills.add(
            normalized_skill
        )


    # Normalize job skills
    normalized_job_skills = set()

    for skill in job_skills:

        normalized_skill = normalize_skill(skill)

        normalized_job_skills.add(
            normalized_skill
        )


    # Find matched skills
    matched_skills = normalized_candidate_skills.intersection(
        normalized_job_skills
    )


    # Find missing skills
    missing_skills = normalized_job_skills.difference(
        normalized_candidate_skills
    )


    # If no skills were detected in job description
    if not normalized_job_skills:

        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": []
        }


    # Calculate match percentage
    match_score = (
        len(matched_skills)
        / len(normalized_job_skills)
    ) * 100


    return {
        "match_score": round(match_score),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }

def generate_resume_feedback(
    match_score,
    matched_skills,
    missing_skills
):

    if match_score >= 80:

        feedback = (
            "Excellent match! Your profile strongly aligns with "
            "this job. Make sure your resume clearly highlights "
            "your relevant experience and projects."
        )

    elif match_score >= 60:

        feedback = (
            "Strong match! You already have many of the required "
            "skills. Highlight your matched skills and relevant "
            "projects prominently in your resume."
        )

    elif match_score >= 40:

        feedback = (
            "Moderate match. You have a good foundation, but "
            "developing some additional required skills could "
            "strengthen your application."
        )

    else:

        feedback = (
            "Low match. Your current skills have limited overlap "
            "with this job. Focus on learning the important "
            "missing skills and building projects using them."
        )

    if missing_skills:

        skills_text = ", ".join(missing_skills)

        if match_score >= 60:

            feedback += (
                f" Consider improving your knowledge of "
                f"{skills_text}."
            )

        else:

            feedback += (
                f" Focus on developing experience with "
                f"{skills_text}."
            )

    return feedback

def get_job_recommendations(candidate_skills, jobs):
    recommendations = []

    for job in jobs:
        match_res = calculate_job_match(candidate_skills, job.description)

        recommendations.append( {
            "job" : job,
            "match_score" : match_res["match_score"],
            "matched_skills" : match_res["matched_skills"],
        })

    recommendations.sort(key = lambda item: item["match_score"],reverse=True)

    return recommendations

    