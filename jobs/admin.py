from django.contrib import admin
from .models import Company,Job, SavedJob

# Register your models here.
admin.site.register(Company)
admin.site.register(Job)
admin.site.register(SavedJob)