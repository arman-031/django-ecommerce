from urllib import request
from django.contrib.auth import authenticate , login, logout
from django.shortcuts import render,redirect
from django.views import View
from .forms import LoginForm

class LoginView(View):
    def get(self,request):
        form = LoginForm()
        return render(request,'account/login.html',{'form':form})

    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            user = authenticate(username=cd['phone'],password=cd['password'])
            if user is not None:
                login(request,user)
                return redirect('/')
            else:
                form.add_error('phone','invalid phone number')
        else:
            form.add_error('phone','invalid phone daita')

        return render(request,'account/login.html',{'form':form})