from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from utility.models import UserProfile, SpaceAnalysis, FavoritePlant


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='plantlover',
            email='lover@example.com',
            password='TestPassword123!',
            first_name='Green',
            last_name='Thumb'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            preferred_budget='Medium',
            preferred_maintenance='Low',
            preferred_style='Modern'
        )

    def test_registration_view_get(self):
        resp = self.client.get(reverse('accounts:register'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/register.html')

    def test_registration_success(self):
        resp = self.client.post(reverse('accounts:register'), {
            'first_name': 'Aarav',
            'last_name': 'Mehta',
            'username': 'aaravm',
            'email': 'aarav@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard:index'))
        self.assertTrue(User.objects.filter(username='aaravm').exists())
        # Profile should be auto-created
        new_user = User.objects.get(username='aaravm')
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_login_and_logout(self):
        # Login
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'plantlover',
            'password': 'TestPassword123!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard:index'))

        # Logout (requires POST)
        resp = self.client.post(reverse('accounts:logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('home:index'))

    def test_profile_update(self):
        self.client.login(username='plantlover', password='TestPassword123!')
        resp = self.client.post(reverse('accounts:profile'), {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'bio': 'Urban balcony gardener',
            'preferred_budget': 'High',
            'preferred_maintenance': 'Medium',
            'preferred_style': 'Boho'
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.profile.preferred_budget, 'High')
        self.assertEqual(self.profile.preferred_style, 'Boho')

    def test_change_password(self):
        self.client.login(username='plantlover', password='TestPassword123!')
        resp = self.client.post(reverse('accounts:change_password'), {
            'old_password': 'TestPassword123!',
            'new_password1': 'BrandNewPass123!',
            'new_password2': 'BrandNewPass123!'
        })
        self.assertEqual(resp.status_code, 302)
        # Login with new password
        self.client.logout()
        success = self.client.login(username='plantlover', password='BrandNewPass123!')
        self.assertTrue(success)

    def test_delete_account(self):
        self.client.login(username='plantlover', password='TestPassword123!')
        resp = self.client.post(reverse('accounts:delete_account'), {
            'confirm': 'plantlover'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(User.objects.filter(username='plantlover').exists())
