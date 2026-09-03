from jobs.models import Job, Company

def import_job(job_data, source):
    external_job_id = job_data["external_job_id"]

    existing_job = Job.objects.filter(
        source = source,
        external_job_id = external_job_id
    ).first()

    if existing_job:
        return existing_job, False

    company, created = Company.objects.get_or_create(name=job_data["company"])

    job = Job.objects.create(
        company = company,
        title = job_data["title"],
        description = job_data["description"],
        required_skills = job_data.get("required_skills", ""),
        location = job_data["location"],
        salary = job_data["salary"],
        job_type = job_data["job_type"],
        source = source,
        external_url = job_data["external_url"],
        external_job_id = external_job_id,
    )

    return job, True