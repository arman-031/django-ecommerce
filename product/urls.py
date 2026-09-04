from django.urls import path
from . import views

app_name = 'product'
urlpatterns = [
    path('<int:pk>', views.ProductDetailView.as_view(), name='product_detial'),
    path('navbar', views.NavbarPartialView.as_view(), name='navbar'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:slug>/', views.CategoryProductView.as_view(), name='category_products'),

]
