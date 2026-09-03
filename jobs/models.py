from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length= 100)

    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Company"
        verbose_name_plural = "Companies"

class Job(models.Model):

    class Status(models.TextChoices):
        OPEN = "O", "Open"
        CLOSED = "C", "Closed"
        DRAFT = "D", "Draft"

    class JobType(models.TextChoices):
        FULL_TIME = "FT", "Full Time"
        PART_TIME = "PT", "Part Time"
        INTERNSHIP = "IN", "Internship"

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()

    required_skills = models.TextField(blank=True, help_text="Separate skills using commas")

    location = models.CharField(max_length=100)

    salary = models.PositiveIntegerField()

    job_type = models.CharField(
        max_length=2,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
    )

    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.OPEN,
    )

    posted_at = models.DateTimeField(default=timezone.now)

    source = models.CharField(max_length=180, blank=True)
    external_url = models.URLField(blank=True)
    external_job_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class SavedJob(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_jobs"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
    
