from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from product.models import Product
from .cart_module import Cart
from .models import Order, OrderItem, Discount


class CartDetailView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'cart/cart_detail.html', {'cart': cart})


class CartAddView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        color = request.POST.get('color')
        size = request.POST.get('size')
        quantity = request.POST.get('quantity')

        cart = Cart(request)
        cart.add(product, quantity, color, size)

        return redirect('cart:cart_detail')


class CartDeleteView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.remove(id)

        return redirect('cart:cart_detail')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(
            Order,
            id=pk,
            user=request.user
        )

        return render(
            request,
            'cart/order.html',
            {'order': order}
        )


class OrderCreationView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)

        if not cart.cart:
            return redirect('cart:cart_detail')

        order = Order.objects.create(
            user=request.user,
            total_price=cart.total()
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=int(float(item["price"])),
                color=item["color"],
                size=item["size"]
            )

        cart.remove_cart()

        return redirect(
            'cart:order_detail',
            order.id
        )


class ApplyDiscountView(LoginRequiredMixin, View):
    def post(self, request, pk):
        code = request.POST.get('discount_code')

        order = get_object_or_404(
            Order,
            id=pk,
            user=request.user
        )

        discount_code = get_object_or_404(
            Discount,
            name=code
        )

        if discount_code.quantity == 0:
            return redirect(
                'cart:order_detail',
                order.id
            )

        order.total_price -= (
            order.total_price *
            discount_code.discount / 100
        )

        order.save()

        discount_code.quantity -= 1
        discount_code.save()

        return redirect(
            'cart:order_detail',
            order.id
        )