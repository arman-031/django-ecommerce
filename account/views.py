from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, RegisterForm, AddressCreationForm
from .models import User
from django.db import IntegrityError, transaction
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['phone'], password=cd['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                form.add_error('phone', 'شماره همراه یا رمز عبور صحیح نیست.')
        else:
            form.add_error('phone', 'اطلاعات ورود معتبر نیست.')

        return render(request, 'account/login.html', {'form': form})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('account:login')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    User.objects.create_user(phone=cd['phone'], password=cd['password'])
            except IntegrityError:
                if not User.objects.filter(phone=cd['phone']).exists():
                    raise
                form.add_error('phone', 'این شماره همراه قبلاً ثبت شده است.')
            else:
                return redirect('account:login')
        return render(request, 'account/register.html', {'form': form})


class AddAddressView(LoginRequiredMixin, View):
    def post(self, request):
        form = AddressCreationForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('account:add_address')
        return render(request, 'account/add_address.html', {'form': form})

    def get(self, request):
        form = AddressCreationForm()
        return render(request, 'account/add_address.html', {'form': form})
