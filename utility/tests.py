from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from utility.forms import SpaceUploadForm
from utility.views import analyse

class UtilityUploadFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
            b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

    def test_analyse_function_directly(self):
        """Test that analyse function executes with validated inputs."""
        uploaded_image = SimpleUploadedFile("test_room.jpg", self.small_gif, content_type="image/jpeg")
        result = analyse(
            image=uploaded_image,
            budget='Low',
            maintenance='Medium',
            style='Minimal'
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['validated_inputs']['budget'], 'Low')
        self.assertEqual(result['validated_inputs']['maintenance'], 'Medium')
        self.assertEqual(result['validated_inputs']['style'], 'Minimal')
        self.assertIn('recommended_plants', result)
        self.assertIn('style_guide', result)
        self.assertIn('why_this_works', result)
        self.assertIn('smart_insights', result)
        
        # Verify why_this_works contents
        wtw = result['why_this_works']
        self.assertIn('observations', wtw)
        self.assertIn('environmental_drivers', wtw)
        self.assertIn('plant_synergy', wtw)
        self.assertIn('spatial_improvement', wtw)
        self.assertIn('lifestyle_alignment', wtw)

        # Verify smart_insights contents
        si = result['smart_insights']
        self.assertIn('light_compatibility', si)
        self.assertIn('space_optimization', si)
        self.assertIn('maintenance_forecast', si)
        self.assertIn('design_harmony', si)
        self.assertIn('potential_challenges', si)
        self.assertIn('practical_recommendations', si)

        # Verify first plant enriched fields
        p = result['recommended_plants'][0]
        self.assertIn('why_this_plant', p)
        self.assertIn('key_benefits', p)
        self.assertIn('placement_advantages', p)
        self.assertIn('design_contribution', p)
        self.assertIn('things_to_consider', p)
        self.assertIn('care_intelligence', p)

    def test_space_upload_form_valid(self):
        """Test SpaceUploadForm with valid inputs."""
        uploaded_image = SimpleUploadedFile("test.png", self.small_gif, content_type="image/png")
        data = {
            'budget': 'Medium',
            'maintenance': 'Low',
            'style': 'Boho'
        }
        files = {'image': uploaded_image}
        form = SpaceUploadForm(data=data, files=files)
        self.assertTrue(form.is_valid())

    def test_upload_view_get(self):
        """Test GET request to upload view."""
        response = self.client.get(reverse('utility:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'utility/upload.html')

    def test_result_view_get(self):
        """Test GET request to result view and verify all 7 sections render."""
        response = self.client.get(reverse('utility:result'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'utility/result.html')
        self.assertContains(response, 'green-space-analysis')
        self.assertContains(response, 'recommended-plants')
        self.assertContains(response, 'why-this-works')
        self.assertContains(response, 'smart-placement-guide')
        self.assertContains(response, 'plant-care-guide')
        self.assertContains(response, 'design-wellness-insights')
        self.assertContains(response, 'things-to-watch-out-for')

    def test_upload_view_post_ajax(self):
        """Test AJAX POST request to upload view which triggers analyse and returns redirect URL."""
        uploaded_image = SimpleUploadedFile("room.jpg", self.small_gif, content_type="image/jpeg")
        data = {
            'budget': 'High',
            'maintenance': 'High',
            'style': 'Modern'
        }
        response = self.client.post(
            reverse('utility:upload'),
            data={'image': uploaded_image, **data},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['redirect_url'], reverse('utility:result'))
