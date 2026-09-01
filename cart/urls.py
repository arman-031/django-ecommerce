from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('add/<int:pk>', views.CartAddView.as_view(), name='cart_add'),
    path('delete/<str:id>', views.CartDeleteView.as_view(), name='cart_del'),
    path('order/<int:pk>', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/add', views.OrderCreationView.as_view(), name='order_add'),
    path('applydiscount/<int:pk>', views.ApplyDiscountView.as_view(), name='discount'),

]
