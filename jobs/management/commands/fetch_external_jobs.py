from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from jobs.models import JobFetchRun

from jobs.services.sources.registry import get_source
from jobs.services.job_importer import import_job
from jobs.services.job_intelligence import analyze_candidate


class Command(BaseCommand):

    help = "Fetch jobs using unique candidate search keywords"

    def handle(self, *args, **options):

        fetch_run = JobFetchRun.objects.create(
            source="Adzuna"
        )

        jobs_found = 0
        imported_count = 0
        skipped_count = 0

        try:

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

            source = get_source("Adzuna")

            for keyword, location in unique_searches:

                self.stdout.write(
                    f"Searching: {keyword} in {location}"
                )

                jobs = source.fetch_jobs(
                    keyword=keyword,
                    location=location,
                    results_per_page=10,
                )

                jobs_found += len(jobs)

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

            # SUCCESS
            fetch_run.finished_at = timezone.now()
            fetch_run.jobs_found = jobs_found
            fetch_run.jobs_imported = imported_count
            fetch_run.jobs_skipped = skipped_count
            fetch_run.status = JobFetchRun.Status.SUCCESS

            fetch_run.save(
                update_fields=[
                    "finished_at",
                    "jobs_found",
                    "jobs_imported",
                    "jobs_skipped",
                    "status",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Finished. Imported: {imported_count}, "
                    f"Skipped: {skipped_count}"
                )
            )

        except Exception as e:

            # FAILED
            fetch_run.finished_at = timezone.now()
            fetch_run.jobs_found = jobs_found
            fetch_run.jobs_imported = imported_count
            fetch_run.jobs_skipped = skipped_count
            fetch_run.status = JobFetchRun.Status.FAILED
            fetch_run.error_message = str(e)

            fetch_run.save(
                update_fields=[
                    "finished_at",
                    "jobs_found",
                    "jobs_imported",
                    "jobs_skipped",
                    "status",
                    "error_message",
                ]
            )

            self.stdout.write(
                self.style.ERROR(
                    f"Job fetch failed: {e}"
                )
            )

            raise