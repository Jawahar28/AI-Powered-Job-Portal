from django.shortcuts import render, redirect, get_object_or_404
from jobs.models import Job
from .forms import ApplicationForm


def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
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