from django.contrib.auth import authenticate
from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Address


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('09123456789', 'strong-password')
        self.user.email = 'user@example.com'
        self.user.save()

    def test_inactive_user_cannot_login_by_phone_or_email(self):
        self.user.is_active = False
        self.user.save()
        for username in [self.user.phone, self.user.email]:
            self.assertIsNone(authenticate(username=username, password='strong-password'))

    def test_email_login_works_for_active_user(self):
        self.assertEqual(authenticate(username=self.user.email, password='strong-password'), self.user)

    def test_address_requires_login_and_belongs_to_request_user(self):
        url = reverse('account:add_address')
        data = {'fullname': 'آرمان', 'phone': self.user.phone, 'address': 'آدرس نمونه', 'postcode': '1234567890'}
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertFalse(Address.objects.exists())
        self.client.force_login(self.user)
        self.client.post(url, data)
        self.assertEqual(Address.objects.get().user, self.user)

    def test_duplicate_registration_shows_error(self):
        response = self.client.post(reverse('account:register'), {'phone': self.user.phone, 'password': 'password123', 'password2': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'قبلاً ثبت شده')

    def test_logout_requires_post_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.get(reverse('account:logout')).status_code, 405)
        self.assertEqual(client.post(reverse('account:logout')).status_code, 403)
        response = client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        csrf_token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(reverse('account:logout'), {'csrfmiddlewaretoken': csrf_token}).status_code, 302)
        self.assertNotIn('_auth_user_id', client.session)

    def test_email_session_stops_working_after_deactivation(self):
        self.client.force_login(self.user, backend='account.authentication.EmailBackend')
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.client.get(reverse('account:add_address')).status_code, 302)

    def test_regular_user_has_no_admin_permissions(self):
        self.assertFalse(self.user.has_perm('account.change_user'))
        self.user.is_admin = True
        self.assertTrue(self.user.has_perm('account.change_user'))
        self.user.is_active = False
        self.assertFalse(self.user.has_perm('account.change_user'))

    def test_registration_checks_password_and_hashes_valid_password(self):
        url = reverse('account:register')
        self.client.post(url, {'phone': '09123456780', 'password': '123', 'password2': '123'})
        self.assertEqual(User.objects.count(), 1)
        response = self.client.post(url, {'phone': '09123456780', 'password': 'new-Strong-Password-52', 'password2': 'new-Strong-Password-52'})
        self.assertRedirects(response, reverse('account:login'))
        self.assertTrue(User.objects.get(phone='09123456780').check_password('new-Strong-Password-52'))

    def test_admin_can_create_phone_based_user(self):
        admin = User.objects.create_superuser('09123456781', 'strong-password')
        self.client.force_login(admin)
        response = self.client.post(reverse('admin:account_user_add'), {
            'phone': '09123456782', 'password1': 'new-Strong-Password-52',
            'password2': 'new-Strong-Password-52', '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone='09123456782').exists())
