from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request,  'accounts/register.html', {'form' : form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(
            request, data=request.POST
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

    return render(request, 'accounts/login.html',  {'form' : form})

def logout_view(request):
    logout(request)
    return redirect("login")

