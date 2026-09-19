from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Job, Company, SavedJob, CoverLetterGeneration
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.services.recommendations import get_new_recommended_jobs, get_recommended_jobs, analyze_job_fit
from jobs.services.cover_letter import generate_cover_letter
from django.views.decorators.http import require_POST
from django.utils import timezone


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

        applications = (
            request.user.applications
            .select_related(
                "job",
                "job__company"
            )
            .order_by("-applied_at")
        )

        recommended_jobs = get_recommended_jobs(request.user)

        new_recommended_jobs = get_new_recommended_jobs(request.user)

        context.update({
            "application_count": applications.count(),
            "recent_applications": applications[:5],
            "saved_jobs": request.user.saved_jobs.count(),
            "interviews": 0,
            "profile_completion": 70,
            "recommendation_count": len(recommended_jobs),
            "new_recommended_jobs": new_recommended_jobs,
            "new_recommendation_count": len(new_recommended_jobs),
        })

    return render(request,"jobs/home.html",context)


def job_list(request):
    # return HttpResponse("Welcome to AI-Powered Job Portal")
    query = request.GET.get("q")

    location= request.GET.get("location")

    job_type = request.GET.get("job_type")

    experience = request.GET.get("experience")


    jobs = Job.objects.select_related("company").filter(status = Job.Status.OPEN)

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

    if experience:
        jobs = jobs.filter(intelligence__experience_level = experience)

    
    context = {
            "jobs" : jobs,
            "query" : query,
            "location": location,
            "job_type": job_type,
            "experience" : experience,
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

    job_fit = None

    if request.user.is_authenticated:
        job_fit = analyze_job_fit(
            request.user,
            job
        )

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "related_jobs": related_jobs,
            "job_fit": job_fit,
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


@login_required
@require_POST
def generate_cover_letter_view(request, id):

    job = get_object_or_404(
        Job,
        id=id
    )

    today = timezone.localdate()

    generation_count = (
        CoverLetterGeneration.objects
        .filter(
            user=request.user,
            generated_at__date=today
        )
        .count()
    )

    DAILY_LIMIT = 5

    if generation_count >= DAILY_LIMIT:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "You have reached your daily "
                    "cover letter generation limit. "
                    "Please try again tomorrow."
                ),
            },
            status=429
        )

    try:

        cover_letter = generate_cover_letter(
            request.user,
            job
        )

        CoverLetterGeneration.objects.create(
            user=request.user,
            job=job
        )

        return JsonResponse(
            {
                "success": True,
                "cover_letter": cover_letter,
                "remaining_generations": (
                    DAILY_LIMIT
                    - generation_count
                    - 1
                ),
            }
        )

    except Exception as e:

        print(
            "Cover letter generation error:",
            e
        )

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Unable to generate your "
                    "cover letter right now. "
                    "Please try again later."
                ),
            },
            status=500
        )

@login_required
def recommended_jobs(request):
    recommendations = get_recommended_jobs(request.user)

    for job in recommendations:
        job.fit = analyze_job_fit(request.user, job)


    return render(request, "jobs/recommended_jobs.html",{"recommendations" : recommendations})