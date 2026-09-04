from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('add/address', views.AddAddressView.as_view(), name='add_address'),

]
