from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages

def login(request):
    """Log a user or show the webpage"""

    if request.method != "POST":
        form = UserForm()
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('finance:index')
        else:
            messages.error(request, 'Username or Password is incorrect!')
            return redirect('users:login')

    context = {'form': form}

    return render(request, 'users/login.html', context)

def logout(request):
    auth_logout(request)
    return redirect('users:login')