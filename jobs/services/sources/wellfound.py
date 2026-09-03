def fetch_jobs():
    """
    Return Jobs from the extenral source

    Later this function will fetch real data
    from an approved API/feed/source.
    """
    return [
        {
            "external_job_id" : "wellfound-test-002",
            "title" : "Python Backend Developer",
            "company" : "Example StartUp",
            "description" : (
                "We are looking for a Python Developer"
                "with experience in Django, REST APIs,"
                "SQL and Git"
            ),
            "required_skills" : (
                "Python, Django, REST API, SQL, Git"
            ),
            "location" : "Hyderbad",
            "salary" : 600000,
            "job_type" : "FT",
            "external_url" : "https://example.com/jobs/python-backend",
        }
    ]
    