from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length= 100)
    location = models.CharField(max_length = 100)
    website = models.URLField()
    created_at = models.DateTimeField(auto_now=True)