from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name='home'),
    path("jobs/", views.job_list, name='job_list'),
    path("jobs/<int:id>/", views.job_detail, name='job_detail'),
    path("jobs/<int:id>/save/", views.save_job, name="save_job"),
    path("saved-jobs/", views.saved_jobs, name="saved_jobs"),
    path("jobs/<int:id>/unsave/", views.unsave_job, name="unsave_job"),
    path("jobs/<int:id>/cover-letter/", views.generate_cover_letter_view, name="generate_cover_letter"),
    path("recommended/", views.recommended_jobs, name="recommended_jobs"),

]
