from django.shortcuts import render
from django.http import HttpResponse
from .models import Job

# Create your views here.
def job_list(request):
    # return HttpResponse("Welcome to AI-Powered Job Portal")
    jobs = Job.objects.all()

    return render(request,
                "jobs/job_list.html",
                {
                    'jobs': jobs
                }
            )
