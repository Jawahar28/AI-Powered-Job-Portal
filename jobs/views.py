from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Job, Company, SavedJob
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

    if request.user.is_authenticated:

        applications = request.user.applications.select_related(
            "job",
            "job__company"
        ).order_by("-applied_at")

        context.update({
            "application_count": applications.count(),
            "recent_applications": applications[:5],
            "saved_jobs": 0,          # We'll replace later
            "interviews": 0,          # We'll replace later
            "profile_completion": 70, # We'll calculate later
        })

    return render(request, "jobs/home.html", context)


def job_list(request):
    # return HttpResponse("Welcome to AI-Powered Job Portal")
    query = request.GET.get("q")

    location= request.GET.get("location")

    job_type = request.GET.get("job_type")


    jobs = Job.objects.select_related("company").all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query) |
            Q(description__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    
    context = {
            "jobs" : jobs,
            "query" : query,
            "location": location,
            "job_type": job_type,
    }
    return render(request, "jobs/job_list.html", context)


def job_detail(request, id):
    job = get_object_or_404(Job, id=id)

    related_jobs = (
        Job.objects.filter(
            company=job.company,
            status=Job.Status.OPEN
        )
        .exclude(id=job.id)[:3]
    )

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "related_jobs": related_jobs,
        },
    )


@login_required
def save_job(request, id):

    job = get_object_or_404(Job, id=id)

    SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )

    return redirect("job_detail", id=id)


@login_required
def saved_jobs(request):

    saved_jobs = request.user.saved_jobs.select_related("job", "job__company")

    return render(
        request,
        "jobs/saved_jobs.html",
        {
            "saved_jobs": saved_jobs,
        },
    )

@login_required
def unsave_job(request, id):
    job = get_object_or_404(Job, id=id)

    SavedJob.objects.filter(user=request.user, job=job).delete()

    messages.success(request, "Job removed from your saved jobs.")

    return redirect("saved_jobs")
