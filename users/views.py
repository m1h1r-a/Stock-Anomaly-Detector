from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm


# Create your views here.
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request, username=data["username"], password=data["password"]
            )
            if user is not None:
                login(request, user)
                return render(request, "users/index.html")
            else:
                return render(request, "users/home.html")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def index(request):
    return render(request, "users/index.html")


def home(request):
    return render(request, "users/home.html")


def user_logout(request):
    logout(request)  # Logs out the user
    return render(request, "users/home.html")  # Response message after logout
