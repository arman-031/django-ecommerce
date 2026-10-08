from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError

from product.models import Product
from .forms import CartAddForm

CART_SESSION_ID = 'cart'
CHECKOUT_SESSION_ID = 'checkout_token'


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(CART_SESSION_ID, {})
        if self.cart and not self.session.get(CHECKOUT_SESSION_ID):
            self.session[CHECKOUT_SESSION_ID] = str(uuid4())

    def __iter__(self):
        # Work on new dictionaries: model objects must never enter session JSON.
        products = Product.objects.in_bulk([item['id'] for item in self.cart.values()])
        for key, stored in list(self.cart.items()):
            product = products.get(stored['id'])
            if product is None:
                self.remove(key)
                continue
            yield {
                **stored,
                'product': product,
                'price': product.price,
                'total': product.price * stored['quantity'],
                'unique_id': key,
            }

    def remove_cart(self):
        self.session.pop(CART_SESSION_ID, None)
        self.session.pop(CHECKOUT_SESSION_ID, None)
        self.cart = {}
        self.session.modified = True

    def unique_id_generator(self, id, color, size):
        return f'{id}-{color}-{size}'

    def add(self, product, quantity, color, size):
        form = CartAddForm(
            {'quantity': quantity, 'color': color or '', 'size': size or ''},
            product=product,
        )
        if not form.is_valid():
            raise ValidationError([error for errors in form.errors.values() for error in errors])
        data = form.cleaned_data
        key = self.unique_id_generator(product.id, data['color'], data['size'])
        quantity = self.cart.get(key, {}).get('quantity', 0) + data['quantity']
        if quantity > 99:
            raise ValidationError('تعداد هر محصول در سبد خرید حداکثر ۹۹ است.')
        self.cart[key] = {
            'id': product.id, 'quantity': quantity, 'price': str(product.price),
            'color': data['color'], 'size': data['size'],
        }
        self.save()

    def total(self):
        return sum((item['total'] for item in self), Decimal('0.00'))

    def remove(self, id):
        if id in self.cart:
            del self.cart[id]
            self.save()

    def save(self):
        # A changed cart represents a new checkout attempt.
        self.session[CHECKOUT_SESSION_ID] = str(uuid4())
        self.session.modified = True
