from celery import shared_task
from django.core.management import call_command

# @shared_task
# def test_celery_task():
#     return "JOBCode Celery is Working!"

@shared_task(
        bind = True,
        autoretry_for=(Exception,),
        retry_backoff = True,
        retry_kwargs = {"maz_retries" : 3},
)
def fetch_jobs_task(self):
    call_command("fetch_external_jobs")
    return "JOBCode job fetching completed successfully!"