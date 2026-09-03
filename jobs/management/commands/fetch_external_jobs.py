from django.core.management.base import BaseCommand

from jobs.services.sources.wellfound import fetch_jobs
from jobs.services.job_importer import import_job

class Command(BaseCommand):
    help = "Fetch and import external jobs"

    def handle(self, *args, **options):
        jobs = fetch_jobs()

        imported_count = 0
        skipped_count = 0

        for job_data in jobs:
            job,created = import_job(job_data, source="Wellfound")

            if created:
                imported_count += 1

                self.stdout.write(self.style.SUCCESS(f"Imported: {job.title}"))

            else:
                skipped_count += 1

                self.stdout.write(f"Already exists: {job.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Imported: {imported_count},"
                f"Skipped: {skipped_count}"
            )
        )