from django.db import models
from django.utils import timezone
from jobs.models import Job, Company

# Create your models here.
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title}"