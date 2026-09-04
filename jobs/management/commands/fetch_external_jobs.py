from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from jobs.services.sources.adzuna import fetch_jobs
from jobs.services.job_importer import import_job
from jobs.services.job_intelligence import analyze_candidate


class Command(BaseCommand):

    help = "Fetch jobs using unique candidate search keywords"

    def handle(self, *args, **options):

        users = (
            User.objects
            .filter(profile__resume_text__isnull=False)
            .exclude(profile__resume_text="")
        )

        unique_searches = set()

        for user in users:

            analysis = analyze_candidate(
                user.profile
            )

            location = user.profile.location

            for keyword in analysis["search_keywords"]:

                unique_searches.add(
                    (keyword, location)
                )

        self.stdout.write(
            f"Unique searches: {len(unique_searches)}"
        )

        imported_count = 0
        skipped_count = 0

        for keyword, location in unique_searches:

            self.stdout.write(
                f"Searching: {keyword} in {location}"
            )

            jobs = fetch_jobs(
                keyword=keyword,
                location=location,
                results_per_page=10,
            )

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
            self.style.SUCCESS(
                f"Finished. Imported: {imported_count}, "
                f"Skipped: {skipped_count}"
            )
        )