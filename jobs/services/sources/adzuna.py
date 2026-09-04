import os
import requests  # type: ignore[reportMissingModuleSource]

from accounts.utils import extract_skills_from_resume

BASE_URL = "https://api.adzuna.com/v1/api"

def fetch_jobs(
    keyword="Python Django",
    location="India",
    results_per_page=10,
):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    url = f"{BASE_URL}/jobs/in/search/1"

    params = {
    "app_id": app_id,
    "app_key": app_key,
    "results_per_page": results_per_page,
    "content-type": "application/json",
    }

    if keyword:
        params["what"] = keyword

    if location and location.lower() != "remote":
        params["where"] = location

    response = requests.get(url, params=params, timeout=10,)

    response.raise_for_status()

    data = response.json()

    jobs = []

    for item in data.get("results", []):
        job = {
            "external_job_id": str(item["id"]),

            "title": item.get(
                "title",
                ""
            ),

            "company": item.get(
                "company",
                {}
            ).get(
                "display_name",
                "Unknown"
            ),

            "description": item.get(
                "description",
                ""
            ),

            "location": item.get(
                "location",
                {}
            ).get(
                "display_name",
                "India"
            ),

            "required_skills": ", ".join(
                extract_skills_from_resume(
                    item.get("description", "")
                )
            ),

            "external_url": item.get(
                "redirect_url",
                ""
            ),

            "job_type": (
                "FT"
                if item.get("contract_time") == "full_time"
                else "PT"
            ),

            "salary": 0,
        }

        jobs.append(job)

    return jobs