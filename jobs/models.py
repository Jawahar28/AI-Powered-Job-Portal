from django.db import models
from django.utils import timezone

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

    title = models.CharField(max_length=100)
    description = models.TextField()

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

    def __str__(self):
        return self.title
    
