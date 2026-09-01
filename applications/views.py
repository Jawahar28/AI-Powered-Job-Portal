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

    # Jobs already applied by the user
    applied_job_ids = user.applications.values_list(
        "job_id",
        flat=True
    )

    # Get jobs the user has not applied to
    jobs = Job.objects.exclude(
        id__in=applied_job_ids
    ).select_related("company")

    recommended_jobs = []

    for job in jobs:

        match_res = calculate_job_match(
            candidate_skills,
            job.skills
        )

        # Only recommend jobs with some match
        if match_res["match_score"] > 0:

            job.match_score = match_res["match_score"]

            job.matched_skills = match_res["matched_skills"]

            job.missing_skills = match_res["missing_skills"]

            recommended_jobs.append(job)

    # Highest match score first
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

    context = {

        "applications": applications[:5],

        "application_count": applications.count(),

        # We'll replace these with real models later
        "saved_jobs": 0,

        "interviews": 0,

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


    # ==========================================
    # Better Job Recommendations
    # ==========================================

    applied_job_ids = applications.values_list(
        "job_id",
        flat=True
    )

    available_jobs = (
        Job.objects
        .exclude(id__in=applied_job_ids)
        .select_related("company")
    )

    recommendations = []

    for job in available_jobs:

        match_res = calculate_job_match(
            candidate_skills,
            job.description
        )

        # Only recommend jobs where skills were detected
        if match_res["match_score"] > 0:

            recommendations.append({
                "job": job,
                "match_score": match_res["match_score"],
                "matched_skills": match_res["matched_skills"],
                "missing_skills": match_res["missing_skills"],
            })


    # Highest matching jobs first
    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )


    # Show maximum 3 jobs
    recommended_jobs = recommendations[:3]

    context = {

        "applications": applications,

        "recommended_jobs": recommended_jobs,

        # Show View All only if more than 3 exist
        "has_more_recommendations": len(recommendations) > 3,

    }

    return render(
        request,
        "applications/my_applications.html",
        context
    )

@login_required
def recommended_jobs(request):

    recommended_jobs = get_recommended_jobs_for_user(
        request.user
    )

    return render(
        request,
        "applications/recommended_jobs.html",
        {
            "recommended_jobs": recommended_jobs,
        }
    )