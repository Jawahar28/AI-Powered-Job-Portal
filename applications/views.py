from django.shortcuts import render, redirect, get_object_or_404
from jobs.models import Job
from .forms import ApplicationForm
from .models import Application
from django.contrib.auth.decorators import login_required

from accounts.utils import calculate_job_match, generate_resume_feedback, get_job_recommendations

def get_recommended_jobs_for_user(user):

    profile = user.profile

    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    applied_job_ids = user.applications.values_list(
        "job_id",
        flat=True
    )

    jobs = (
        Job.objects
        .exclude(id__in=applied_job_ids)
        .select_related("company")
    )

    recommended_jobs = []

    for job in jobs:

        match_res = calculate_job_match(
            candidate_skills,
            job.description
        )

        if match_res["match_score"] > 0:

            # Add temporary attributes to the Job object
            job.match_score = match_res["match_score"]
            job.matched_skills = match_res["matched_skills"]
            job.missing_skills = match_res["missing_skills"]

            recommended_jobs.append(job)

    recommended_jobs.sort(
        key=lambda job: job.match_score,
        reverse=True
    )

    return recommended_jobs

@login_required
def applicant_dashboard(request):

    applications = (
        request.user.applications
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    # Get AI recommended jobs
    recommended_jobs = get_recommended_jobs_for_user(
        request.user
    )

    context = {

        # Recent applications
        "applications": applications[:5],

        # Real application count
        "application_count": applications.count(),

        # Real AI recommendation count
        "recommendation_count": len(recommended_jobs),

        # Temporary values until those features are built
        "saved_jobs": 0,

        "interviews": 0,

        # We will calculate this dynamically in Step 2
        "profile_completion": 70,

    }

    return render(
        request,
        "applications/dashboard.html",
        context,
    )


@login_required
def apply_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    # Prevent duplicate applications
    if Application.objects.filter(user=request.user,job=job).exists():
        return redirect("job_detail", id=job.id)

    if request.method == "POST":

        form = ApplicationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            application = form.save(commit=False)

            application.job = job
            application.user = request.user

            # Automatically fill applicant details
            application.applicant_name = (
                request.user.get_full_name()
                or request.user.username
            )

            application.applicant_email = request.user.email

            # Use profile resume if no new resume uploaded
            if (
                not application.resume
                and hasattr(request.user, "profile")
                and request.user.profile.resume
            ):
                application.resume = request.user.profile.resume

            application.save()

            return redirect("job_detail", id=job.id)

    else:

        form = ApplicationForm()

    return render(
        request,
        "applications/application_form.html",
        {
            "form": form,
            "job": job,
        },
    )

@login_required
def my_applications(request):

    applications = (
        request.user.applications
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    profile = request.user.profile

    candidate_skills = [
        skill.strip()
        for skill in profile.skills.split(",")
        if skill.strip()
    ]

    # AI Match Score for Applied Jobs
    for app in applications:

        match_res = calculate_job_match(
            candidate_skills,
            app.job.description
        )

        app.match_score = match_res["match_score"]
        app.matched_skills = match_res["matched_skills"]
        app.missing_skills = match_res["missing_skills"]

    # Get all recommendations using the same helper
    recommendations = get_recommended_jobs_for_user(
        request.user
    )

    # Show only first 3
    recommended_jobs = recommendations[:3]

    context = {
        "applications": applications,
        "recommended_jobs": recommended_jobs,
        "has_more_recommendations": len(recommendations) > 3,
    }

    return render(
        request,
        "applications/my_applications.html",
        context
    )

@login_required
def recommended_jobs(request):

    recommendations = get_recommended_jobs_for_user(
        request.user
    )

    return render(
        request,
        "applications/recommended_jobs.html",
        {
            "recommendations": recommendations,
        }
    )