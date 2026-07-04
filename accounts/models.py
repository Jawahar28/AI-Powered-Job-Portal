from django.db import models

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

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    
    class Status(models.TextChoices):
        OPEN = "O", "Open"
        CLOSED = "C", "Closed"
        DRAFT = "D", "Draft"

    
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.OPEN
    )

    def __str__(self):
        return self.title
    