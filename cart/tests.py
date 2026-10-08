from decimal import Decimal
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse

from account.models import User
from product.models import Product, Color, Size
from .cart_module import CART_SESSION_ID, CHECKOUT_SESSION_ID, Cart
from .models import Order, OrderItem, Discount


class CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('09123456789', 'strong-password')
        cls.other = User.objects.create_user('09123456780', 'strong-password')
        cls.product = Product.objects.create(title='کفش', description='نمونه', price='120.25', discount=0, image='products/test.jpg')
        cls.color = Color.objects.create(title='سفید')
        cls.size = Size.objects.create(title='XL')
        cls.product.color.add(cls.color)
        cls.product.size.add(cls.size)

    def setUp(self):
        self.client.force_login(self.user)

    def add(self, **kwargs):
        data = {'quantity': '2', 'color': 'سفید', 'size': 'XL'}
        data.update(kwargs)
        return self.client.post(reverse('cart:cart_add', args=[self.product.pk]), data)

    def checkout(self):
        return self.client.post(reverse('cart:order_add'))

    def test_checkout_keeps_exact_prices_and_clears_cart(self):
        self.add()
        response = self.checkout()
        order = Order.objects.get()
        self.assertRedirects(response, reverse('cart:order_detail', args=[order.pk]))
        self.assertEqual(order.total_price, Decimal('240.50'))
        self.assertEqual(order.items.get().total, Decimal('240.50'))
        self.assertNotIn(CART_SESSION_ID, self.client.session)

    def test_cart_render_does_not_put_models_in_session(self):
        self.add()
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '240.50')
        self.assertNotIn('product', next(iter(self.client.session[CART_SESSION_ID].values())))
        self.add(quantity=1)
        self.assertEqual(next(iter(self.client.session[CART_SESSION_ID].values()))['quantity'], 3)

    def test_invalid_cart_inputs_do_not_change_cart(self):
        for data in [{'quantity': '-1'}, {'quantity': '0'}, {'quantity': '100'}, {'quantity': 'abc'}, {'quantity': ''}, {'color': 'جعلی'}, {'size': 'جعلی'}, {'color': ''}, {'size': ''}]:
            with self.subTest(data=data):
                self.add(**data)
                self.assertFalse(self.client.session.get(CART_SESSION_ID))
        self.add(quantity=99)
        self.add(quantity=1)
        self.assertEqual(next(iter(self.client.session[CART_SESSION_ID].values()))['quantity'], 99)

    def test_product_without_options_can_be_added(self):
        self.product.color.clear()
        self.product.size.clear()
        self.add(color='', size='')
        self.assertEqual(len(self.client.session[CART_SESSION_ID]), 1)

    def test_checkout_uses_current_price(self):
        self.add()
        self.product.price = Decimal('10.15')
        self.product.save()
        self.checkout()
        self.assertEqual(Order.objects.get().total_price, Decimal('20.30'))

    def test_changed_catalog_options_block_checkout(self):
        self.add()
        self.product.color.clear()
        self.checkout()
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.client.session[CART_SESSION_ID])

    def test_missing_product_is_removed_from_cart(self):
        self.add()
        self.product.delete()
        self.assertEqual(self.client.get(reverse('cart:cart_detail')).status_code, 200)
        self.checkout()
        self.assertFalse(Order.objects.exists())

    def test_get_cannot_delete_or_create_order(self):
        self.add()
        key = next(iter(self.client.session[CART_SESSION_ID]))
        self.assertEqual(self.client.get(reverse('cart:cart_del', args=[key])).status_code, 405)
        self.assertEqual(self.client.get(reverse('cart:order_add')).status_code, 405)
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.client.session[CART_SESSION_ID])
        self.client.post(reverse('cart:cart_del', args=[key]))
        self.assertFalse(self.client.session[CART_SESSION_ID])

    def test_anonymous_checkout_requires_login(self):
        self.client.logout()
        response = self.checkout()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('account:login')))
        self.assertFalse(Order.objects.exists())

    def test_empty_checkout_has_no_order(self):
        self.checkout()
        self.assertFalse(Order.objects.exists())

    def test_order_failure_rolls_back_and_preserves_cart(self):
        self.add()
        with patch('cart.views.OrderItem.objects.bulk_create', side_effect=IntegrityError('simulated failure')):
            with self.assertRaises(IntegrityError):
                self.checkout()
        self.assertFalse(Order.objects.exists())
        self.assertFalse(OrderItem.objects.exists())
        self.assertTrue(self.client.session[CART_SESSION_ID])

    def test_replayed_checkout_token_does_not_duplicate_order(self):
        self.add()
        old_session = dict(self.client.session)
        self.checkout()
        session = self.client.session
        session[CART_SESSION_ID] = old_session[CART_SESSION_ID]
        session[CHECKOUT_SESSION_ID] = old_session[CHECKOUT_SESSION_ID]
        session.save()
        self.checkout()
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_other_user_cannot_read_order(self):
        self.add()
        self.checkout()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('cart:order_detail', args=[Order.objects.get().pk])).status_code, 404)

    def test_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        for url in [reverse('cart:cart_add', args=[self.product.pk]), reverse('cart:cart_del', args=['any']), reverse('cart:order_add')]:
            self.assertEqual(client.post(url).status_code, 403)

    def test_ordered_product_cannot_be_deleted(self):
        self.add()
        self.checkout()
        with self.assertRaises(IntegrityError):
            self.product.delete()


class DiscountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('09123456789', 'strong-password')
        self.client.force_login(self.user)
        self.order = Order.objects.create(user=self.user, total_price='120.25')
        self.discount = Discount.objects.create(name='SAVE', discount=10, quantity=2)
        self.url = reverse('cart:discount', args=[self.order.pk])

    def apply(self, code='SAVE'):
        return self.client.post(self.url, {'discount_code': code})

    def test_discount_applies_once_with_exact_rounding(self):
        self.apply()
        self.apply()
        self.order.refresh_from_db()
        self.discount.refresh_from_db()
        self.assertEqual(self.order.total_price, Decimal('108.23'))
        self.assertTrue(self.order.discount_applied)
        self.assertEqual(self.order.applied_discount_id, self.discount.pk)
        self.assertEqual(self.discount.quantity, 1)

    def test_expired_missing_and_paid_discounts_do_not_change_total(self):
        for code in ['', 'missing', 'x' * 11]:
            self.apply(code)
        self.discount.quantity = 0
        self.discount.save()
        self.apply()
        self.order.is_paid = True
        self.order.save()
        self.discount.quantity = 2
        self.discount.save()
        self.apply()
        self.order.refresh_from_db()
        self.discount.refresh_from_db()
        self.assertEqual(self.order.total_price, Decimal('120.25'))
        self.assertEqual(self.discount.quantity, 2)

    def test_failed_order_update_rolls_back_coupon_consumption(self):
        from django.db.models.query import QuerySet
        original = QuerySet.update

        def fail_order(queryset, **kwargs):
            return 0 if queryset.model is Order else original(queryset, **kwargs)

        with patch.object(QuerySet, 'update', fail_order):
            self.apply()
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.quantity, 2)

    def test_other_user_cannot_apply_discount(self):
        other = User.objects.create_user('09123456780', 'password')
        self.client.force_login(other)
        self.assertEqual(self.apply().status_code, 404)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.quantity, 2)

    def test_deleting_coupon_does_not_allow_second_discount(self):
        self.apply()
        self.discount.delete()
        Discount.objects.create(name='NEW', discount=20, quantity=1)
        self.apply('NEW')
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, Decimal('108.23'))

    def test_last_coupon_cannot_be_used_on_two_orders(self):
        self.discount.quantity = 1
        self.discount.save()
        self.apply()
        other_order = Order.objects.create(user=self.user, total_price='100.00')
        self.client.post(reverse('cart:discount', args=[other_order.pk]), {'discount_code': 'SAVE'})
        other_order.refresh_from_db()
        self.discount.refresh_from_db()
        self.assertEqual(other_order.total_price, Decimal('100.00'))
        self.assertEqual(self.discount.quantity, 0)
