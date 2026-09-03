from django.core.management.base import BaseCommand

from jobs.services.sources.adzuna import fetch_jobs
from jobs.services.job_importer import import_job


class Command(BaseCommand):

    help = "Fetch and import jobs from Adzuna"

    def handle(self, *args, **options):

        jobs = fetch_jobs(
            keyword= "Python Django",
            location= "India",
            results_per_page= 10,
        )

        imported_count = 0
        skipped_count = 0

        for job_data in jobs:

            job, created = import_job(
                job_data,
                source="Adzuna"
            )

            if created:

                imported_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imported: {job.title}"
                    )
                )

            else:

                skipped_count += 1

                self.stdout.write(
                    f"Already exists: {job.title}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Imported: {imported_count}, "
                f"Skipped: {skipped_count}"
            )
        )