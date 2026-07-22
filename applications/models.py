from django.db import models
from django.utils import timezone
from jobs.models import Job, Company
from django.contrib.auth.models import User

# Create your models here.
STATUS_CHOICES = [
    ("A", "Applied"),
    ("UR ", "Under Review"),
    ("S", "Shortlisted"),
    ("R", "Rejected"),
    ("H", "Hired"),
]
class Application(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')


    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length = 5,
        choices=STATUS_CHOICES,
        default="A"
    )


    @property
    def badge_class(self):
        mapping = {
            "Applied" : "bg-primary",
            "Under Review" : "bg-warning text-dark",
            "Shortlisted" : "bg-success",
            "Rejected" : "bg-danger",
            "Hired" : "bg-success"
        }

        return mapping.get(
            self.status, "bg-secondary"
        )

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title}"