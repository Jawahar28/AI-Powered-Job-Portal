from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, CandidateProfileForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .utils import extract_text_from_resume, extract_skills_from_resume

def register(request):

    # Prevent logged-in users from accessing register page
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/auth/register.html',
        {
            'form': form
        }
    )


def login_view(request):

    # Prevent logged-in users from accessing login page
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

    else:

        form = LoginForm()

    return render(
        request,
        'accounts/auth/login.html',
        {
            'form': form
        }
    )


def logout_view(request):

    logout(request)

    return redirect("login")



@login_required
def profile(request):
    profile = request.user.profile

    return render(request, "accounts/candidate/profile.html", {"profile":profile},)

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":

        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )

        profile_form = CandidateProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            if profile.resume:
                resume_text = extract_text_from_resume(profile.resume)

                profile.resume_text = resume_text

                skills = extract_skills_from_resume(resume_text)

                profile.skills = ", ".join(skills)

                profile.save()

                print(resume_text)


            return redirect("profile")

    else:

        user_form = UserUpdateForm(
            instance=request.user
        )

        profile_form = CandidateProfileForm(
            instance=profile
        )

    context = {
        "user_form": user_form,
        "form": profile_form,
        "profile": profile,
    }

    return render(
        request,
        "accounts/candidate/edit_profile.html",
        context
    )

