import os

from google import genai

from jobs.services.recommendations import analyze_job_fit


PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.5-flash"


def generate_cover_letter(user, job):

    profile = user.profile

    job_fit = analyze_job_fit(
        user,
        job
    )

    candidate_name = (
        user.get_full_name()
        or user.username
    )

    prompt = f"""
You are an expert technical recruiter and professional
cover-letter writer.

Write a concise, professional cover letter for the candidate
applying to the job below.

IMPORTANT RULES:

1. Never invent experience, skills, projects, companies,
   achievements, education, or technologies.

2. Only use information explicitly provided in the candidate
   profile or resume.

3. Do not claim the candidate has experience with a technology
   simply because the job requires it.

4. Use the job-fit information to emphasize genuine strengths.

5. Do not mention the match score.

6. Do not mention missing skills unless genuinely relevant.

7. Keep the cover letter between 250 and 350 words.

8. Make the letter specific to this job.

9. Use a professional tone suitable for a software engineering
   application.

10. Return only the cover letter. Do not include explanations,
    headings such as "Cover Letter", or commentary.

CANDIDATE

Name:
{candidate_name}

Headline:
{profile.headline}

Skills:
{profile.skills}

Experience:
{profile.experience}

Education:
{profile.education}

Bio:
{profile.bio}

Resume:
{profile.resume_text}


JOB

Title:
{job.title}

Company:
{job.company.name}

Location:
{job.location}

Description:
{job.description}


JOB FIT ANALYSIS

Matched Skills:
{", ".join(job_fit["matched_skills"])}

Missing Skills:
{", ".join(job_fit["missing_skills"])}

Strengths:
{", ".join(job_fit["strengths"])}

Gaps:
{", ".join(job_fit["gaps"])}
"""

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt
        )

        return response.text.strip()

    except Exception as primary_error:

        # Only fall back for temporary Gemini availability errors.
        error_code = getattr(primary_error, "code", None)

        if error_code != 503:
            raise

        print(
            f"Primary Gemini model unavailable ({PRIMARY_MODEL}). "
            f"Trying fallback model ({FALLBACK_MODEL})."
        )

        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=prompt
        )

        return response.text.strip()