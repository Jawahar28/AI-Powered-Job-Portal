from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("list/", views.job_list, name='job_list'),
]
