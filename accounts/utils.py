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

    
