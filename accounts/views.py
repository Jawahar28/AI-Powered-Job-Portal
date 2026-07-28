from django.shortcuts import render, redirect
from .forms import RegisterForm, AuthenticationForm
from django.contrib.auth import login

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
        form = AuthenticationForm(
            request, data=request.user
        )

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html',  {'form' : form})
