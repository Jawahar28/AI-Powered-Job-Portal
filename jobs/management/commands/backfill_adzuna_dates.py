from django.core.management.base import BaseCommand
from jobs.models import Job
from jobs.services.sources.adzuna import AdzunaSource

class Command(BaseCommand):

    help = "Backfill posted_at for existing Adzuna jobs"

    def handle(self, *args, **options):
        source = AdzunaSource()

        jobs = Job.objects.filter(source="Adzuna")

        updated_count = 0

        for job in jobs:
            try:
                external_jobs = source.fetch_jobs(keyword=job.title,location=job.location, results_per_page=10,)

                for external_job in external_jobs:
                    if (external_job["external_job_id"] == job.external_job_id):
                        job.posted_at = external_job["posted_at"]

                        job.save(update_fields=["posted_at"])

                        updated_count+=1

                        self.stdout.write(self.style.SUCCESS(f"Updated: {job.title}"))
                        break

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed: {job.title} - {e}"
                    )
                )
        self.stdout.write(self.style.SUCCESS(f"Backfill Complete. Updated: {updated_count}"))

            