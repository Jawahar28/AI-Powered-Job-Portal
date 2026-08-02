from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


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