from PyPDF2 import PdfReader

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

            extracted_skills.append(skill)

    return extracted_skills

    
def calculate_job_match(candidate_skills, job_description):
    job_skills = extract_skills_from_resume(job_description)

    candidate_skills_lower = [
        skill.lower()
        for skill in candidate_skills
    ]

    matched_skills = []

    for skill in job_skills:
        if skill.lower() in candidate_skills_lower:
            matched_skills.append(skill)

    if len(job_skills) == 0:
        return {
            "match_score" : 0,
            "matched_skills" : [],
            "missing_skills" : []
        }

    match_score = (
        len(matched_skills) / len(job_skills)
    ) * 100

    missing_skills = [
        skill for skill in job_skills
        if skill not in matched_skills
    ]

    return {
        "match_score" : round(match_score),
        "matched_skills" : matched_skills,
        "missing_skills" : missing_skills
    }