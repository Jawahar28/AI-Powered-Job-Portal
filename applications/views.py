from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from jobs.models import Job, SavedJob

from .forms import ApplicationForm
from .models import Application

from accounts.utils import calculate_profile_completion

from jobs.services.recommendations import (
    get_recommended_jobs,
    get_new_recommended_jobs,
    calculate_job_match_for_user
)


@login_required
def applicant_dashboard(request):

    applications = (
        request.user.applications
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    # Get AI recommended jobs
    recommended_jobs = get_recommended_jobs(request.user)

    new_recommended_jobs = get_new_recommended_jobs(request.user)

    profile_completion = calculate_profile_completion(request.user)

    context = {

    "applications": applications[:5],

    "application_count": applications.count(),

    "recommendation_count": len(recommended_jobs),

    "new_recommended_jobs": new_recommended_jobs,

    "new_recommendation_count": len(
        new_recommended_jobs
    ),

    "saved_jobs": request.user.saved_jobs.count(),

    "interviews": 0,

    "profile_completion": profile_completion,
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
    existing_application = Application.objects.filter(
        user=request.user,
        job=job
    ).first()

    if existing_application:
        if job.external_url:
            return redirect(job.external_url)

        return redirect("job_detail", id=job.id)

    # For external jobs, record the application immediately
    if job.external_url and request.method == "GET":

        application = Application.objects.create(
            user=request.user,
            job=job,
            applicant_name=(
                request.user.get_full_name()
                or request.user.username
            ),
            applicant_email=request.user.email,
            resume=(
                request.user.profile.resume
                if hasattr(request.user, "profile")
                and request.user.profile.resume
                else None
            ),
            status="A",
        )

        return redirect(job.external_url)

    # Internal application flow
    if request.method == "POST":

        form = ApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            application = form.save(commit=False)

            application.job = job
            application.user = request.user

            application.applicant_name = (
                request.user.get_full_name()
                or request.user.username
            )

            application.applicant_email = request.user.email

            if (
                not application.resume
                and hasattr(request.user, "profile")
                and request.user.profile.resume
            ):
                application.resume = request.user.profile.resume

            application.save()

            return redirect(
                "job_detail",
                id=job.id
            )

    else:
        form = ApplicationForm()

    return render(
        request,
        "applications/application_form.html",
        {
            "form": form,
            "job": job,
        }
    )

@login_required
def my_applications(request):

    applications = (
        request.user.applications
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    # AI Match Score for Applied Jobs
    for app in applications:

        match_res = calculate_job_match_for_user(request.user,app.job)

        app.match_score = match_res["match_score"]
        app.matched_skills = match_res["matched_skills"]
        app.missing_skills = match_res["missing_skills"]

    # Get all recommendations using the same helper
    recommendations = get_recommended_jobs(request.user)

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

    recommendations = get_recommended_jobs(
        request.user
    )

    return render(
        request,
        "applications/recommended_jobs.html",
        {
            "recommendations": recommendations,
        }
    )