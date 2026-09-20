from celery import shared_task
from django.core.management import call_command

# @shared_task
# def test_celery_task():
#     return "JOBCode Celery is Working!"

@shared_task
def fetch_jobs_task():
    call_command("fetch_external_jobs")
    return "JOBCode job fetching completed successfully!"