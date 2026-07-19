from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Job

# Create your views here.
def home(request):
    return render(request, 'jobs/home.html')


def job_list(request):
    # return HttpResponse("Welcome to AI-Powered Job Portal")
    jobs = Job.objects.all()

    return render(request,
                "jobs/job_list.html",
                {
                    'jobs': jobs
                }
            )

def job_detail(request,id):
    job = get_object_or_404(Job, id=id)

    return render(request,
            "jobs/job_detail.html",
                {
                    'job': job
                }    
            )
