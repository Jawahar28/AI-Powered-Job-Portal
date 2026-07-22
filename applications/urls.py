from django.urls import path

from . import views

urlpatterns = [
    path("jobs/<int:job_id>/apply/",views.apply_job,name = "apply_job",),
    path("my-applications/", views.my_applications, name="my_applications",),
]
