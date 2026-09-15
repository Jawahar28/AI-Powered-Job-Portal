from django.core.management.base import BaseCommand

from jobs.models import Job
from jobs.services.job_intelligence import analyze_job_description

class Command(BaseCommand):
    help = "Refresh intelligence for existing jobs"

    def handle(self, *args, **options):
        jobs = Job.objects.all()

        updated_count = 0

        for job in jobs:
            intelligence = analyze_job_description(job.title, job.description)

            job.intelligence = intelligence

            job.save(update_fields=["intelligence"])

            updated_count+=1

            self.stdout.write(f"Updated: {job.title}")

        self.stdout.write(self.style.SUCCESS(
            f"Job Intelligence refresh complete."
            f"Updated : {updated_count}"
        ))