from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout,)
from .forms import UserLoginForm, UserRegisterForm

# Create your views here.

def login_view(request):
	form = UserLoginForm(request.POST or None)
	next_url = request.GET.get('next')
	if form.is_valid():
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		messages.success(request, "{} are successfully login.".format(username))
		login(request, user)
		if next_url:
			return redirect(next_url)
		return redirect('/')
	context = {
		'title': 'Login',
		'form': form,
		}
	return render(request, 'login-register.html', context)

def register_view(request):
	form = UserRegisterForm(request.POST or None)
	next_url = request.GET.get('next')
	if form.is_valid():
		user = form.save(commit=False)
		password = form.cleaned_data.get('password')
		user.set_password(password)
		user.save()
		new_user = authenticate(username=user.username, password=password)
		login(request, new_user)
		if next_url:
			return redirect(next_url)
		return redirect('/')
	context = {
		'title': 'Register',
		'form': form,
	}
	return render(request, 'login-register.html', context)

def logout_view(request):
	logout(request)
	return redirect('/')