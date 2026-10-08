from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from product.models import Product
from .cart_module import Cart, CHECKOUT_SESSION_ID
from .forms import CartAddForm, DiscountForm
from .models import Order, OrderItem, Discount


class CartDetailView(View):
    def get(self, request):
        return render(request, 'cart/cart_detail.html', {'cart': Cart(request)})


class CartAddView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        try:
            Cart(request).add(product, request.POST.get('quantity'), request.POST.get('color'), request.POST.get('size'))
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
            return redirect('product:product_detial', pk=pk)
        return redirect('cart:cart_detail')


class CartDeleteView(View):
    def post(self, request, id):
        Cart(request).remove(id)
        return redirect('cart:cart_detail')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related('items__product'), id=pk, user=request.user)
        return render(request, 'cart/order.html', {'order': order})


class OrderCreationView(LoginRequiredMixin, View):
    def post(self, request):
        cart = Cart(request)
        items = list(cart)
        if not items:
            messages.error(request, 'سبد خرید شما خالی است.')
            return redirect('cart:cart_detail')
        # Recheck catalog options and quantity, including carts from older sessions.
        for item in items:
            form = CartAddForm(item, product=item['product'])
            if not form.is_valid():
                messages.error(request, 'گزینه‌های سبد خرید تغییر کرده‌اند؛ محصول را دوباره به سبد اضافه کنید.')
                return redirect('cart:cart_detail')
        token = request.session[CHECKOUT_SESSION_ID]
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user, checkout_token=token,
                    total_price=sum((item['total'] for item in items), Decimal('0.00')),
                )
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, product=item['product'], quantity=item['quantity'],
                              price=item['price'], color=item['color'], size=item['size'])
                    for item in items
                ])
        except IntegrityError:
            # The unique token prevents replays of the same cart creating two orders.
            order = Order.objects.filter(checkout_token=token, user=request.user).first()
            if order is None:
                raise
        cart.remove_cart()
        return redirect('cart:order_detail', pk=order.pk)


class ApplyDiscountView(LoginRequiredMixin, View):
    def post(self, request, pk):
        form = DiscountForm(request.POST)
        get_object_or_404(Order, pk=pk, user=request.user)
        try:
            if not form.is_valid():
                raise ValidationError('کد تخفیف معتبر وارد کنید.')
            with transaction.atomic():
                order = Order.objects.select_for_update().get(pk=pk, user=request.user)
                if order.is_paid or order.discount_applied:
                    raise ValidationError('امکان اعمال تخفیف روی این سفارش وجود ندارد.')
                discount = Discount.objects.filter(name=form.cleaned_data['discount_code']).first()
                if discount is None:
                    raise ValidationError('کد تخفیف معتبر نیست.')
                # Conditional updates protect both counters even without row locks.
                used = Discount.objects.filter(pk=discount.pk, quantity__gt=0).update(quantity=F('quantity') - 1)
                if not used:
                    raise ValidationError('ظرفیت کد تخفیف تمام شده است.')
                total = (order.total_price * (100 - discount.discount) / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                updated = Order.objects.filter(
                    pk=pk, user=request.user, is_paid=False, discount_applied=False,
                ).update(total_price=total, applied_discount=discount, discount_applied=True)
                if not updated:
                    raise ValidationError('امکان اعمال تخفیف روی این سفارش وجود ندارد.')
            messages.success(request, 'کد تخفیف اعمال شد.')
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
        return redirect('cart:order_detail', pk=pk)
