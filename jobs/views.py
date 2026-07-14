from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def job_list(request):
    # return HttpResponse("Welcome to AI-Powered Job Portal")
    return render(request, "jobs/job_list.html")
