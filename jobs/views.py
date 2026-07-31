from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Job, Company
from django.contrib.auth.models import User

# Create your views here.
def home(request):

    latest_jobs = Job.objects.filter(
        status=Job.Status.OPEN
    ).order_by("-posted_at")[:6]

    context = {
        "latest_jobs": latest_jobs,
        "job_count": Job.objects.count(),
        "company_count": Company.objects.count(),
        "candidate_count": User.objects.count(),
    }

    return render(request, "jobs/home.html", context)


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
