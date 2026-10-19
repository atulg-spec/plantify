import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from utility.models import SpaceAnalysis, FavoritePlant, UserProfile


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')
        UserProfile.objects.create(user=self.user1)
        UserProfile.objects.create(user=self.user2)

        # Create space for user1
        self.space1 = SpaceAnalysis.objects.create(
            user=self.user1,
            name='Living Room Window',
            budget='Medium',
            maintenance='Low',
            style='Modern',
            analysis_data={
                'scores': {'overall_compatibility': '95%'},
                'recommended_plants': [{'name': 'Snake Plant'}]
            }
        )

        # Create space for user2
        self.space2 = SpaceAnalysis.objects.create(
            user=self.user2,
            name='User2 Study Desk',
            budget='Low',
            maintenance='Low',
            style='Minimal',
            analysis_data={'scores': {'overall_compatibility': '90%'}}
        )

    def test_dashboard_login_required(self):
        resp = self.client.get(reverse('dashboard:index'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp.url)

    def test_dashboard_index_authenticated(self):
        self.client.login(username='user1', password='Password123!')
        resp = self.client.get(reverse('dashboard:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dashboard/index.html')
        self.assertContains(resp, 'Living Room Window')
        self.assertNotContains(resp, 'User2 Study Desk')

    def test_history_data_isolation(self):
        self.client.login(username='user1', password='Password123!')
        resp = self.client.get(reverse('dashboard:history'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Living Room Window')
        self.assertNotContains(resp, 'User2 Study Desk')

    def test_analysis_detail_ownership_enforced(self):
        # User 1 viewing own space -> 200
        self.client.login(username='user1', password='Password123!')
        resp = self.client.get(reverse('dashboard:analysis_detail', args=[self.space1.pk]))
        self.assertEqual(resp.status_code, 200)

        # User 1 attempting to view User 2's space -> 404 (ownership check)
        resp = self.client.get(reverse('dashboard:analysis_detail', args=[self.space2.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_rename_analysis(self):
        self.client.login(username='user1', password='Password123!')
        resp = self.client.post(
            reverse('dashboard:rename_analysis', args=[self.space1.pk]),
            {'name': 'Renamed Window Sanctuary'}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['name'], 'Renamed Window Sanctuary')
        self.space1.refresh_from_db()
        self.assertEqual(self.space1.name, 'Renamed Window Sanctuary')

    def test_delete_analysis(self):
        self.client.login(username='user1', password='Password123!')
        resp = self.client.post(reverse('dashboard:delete_analysis', args=[self.space1.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(SpaceAnalysis.objects.filter(pk=self.space1.pk).exists())

    def test_favorites_toggle_and_remove(self):
        self.client.login(username='user1', password='Password123!')

        # Add to favorites
        resp = self.client.post(
            reverse('dashboard:toggle_favorite'),
            data=json.dumps({
                'plant_name': 'Monstera Deliciosa',
                'botanical_name': 'Monstera deliciosa',
                'price': '₹1,500',
                'plant_tag': 'Statement Plant'
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'added')
        self.assertTrue(FavoritePlant.objects.filter(user=self.user1, plant_name='Monstera Deliciosa').exists())

        # Toggle again -> should remove
        resp2 = self.client.post(
            reverse('dashboard:toggle_favorite'),
            data=json.dumps({'plant_name': 'Monstera Deliciosa'}),
            content_type='application/json'
        )
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2['action'], 'removed')
        self.assertFalse(FavoritePlant.objects.filter(user=self.user1, plant_name='Monstera Deliciosa').exists())
