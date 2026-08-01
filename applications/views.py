from django.shortcuts import render, redirect, get_object_or_404
from jobs.models import Job
from .forms import ApplicationForm
from .models import Application
from django.contrib.auth.decorators import login_required


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

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)


            application.job = job
            application.user = request.user


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
    applications = request.user.applications.all().order_by('-applied_at')

    return render(request, 
                  "applications/my_applications.html",
                  {

                      'applications' : applications,
                  },
                )