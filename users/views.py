from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from services.registration_service import create_depo_for_new_user
from .forms.forms import LoginForm, RegisterForm


def sign_up(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            create_depo_for_new_user(user)
            login(request, user)
            return redirect("/")
        else:
            return render(request, "users/register.html", {"form": form})


def sign_in(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd["username"], password=cd["password"])
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                return render(request, "users/login.html", {"form": form})

        else:
            return render(request, "users/login.html", {"form": form})


@login_required
def sign_out(request):
    if request.method == "GET":
        logout(request)
        return redirect("/")
