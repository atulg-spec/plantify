from django import forms
from django.core.exceptions import ValidationError

BUDGET_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]

MAINTENANCE_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]

STYLE_CHOICES = [
    ('Minimal', 'Minimal'),
    ('Modern', 'Modern'),
    ('Boho', 'Boho'),
    ('Traditional', 'Traditional'),
    ('No preference', 'No preference'),
]

class SpaceUploadForm(forms.Form):
    image = forms.ImageField(
        required=True,
        error_messages={
            'required': 'Please upload an image of your space.',
            'invalid_image': 'Uploaded file must be a valid image (JPG, PNG, WEBP).'
        }
    )
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=True,
        error_messages={'required': 'Please select a budget level.'}
    )
    maintenance = forms.ChoiceField(
        choices=MAINTENANCE_CHOICES,
        required=True,
        error_messages={'required': 'Please select a maintenance preference.'}
    )
    style = forms.ChoiceField(
        choices=STYLE_CHOICES,
        required=True,
        error_messages={'required': 'Please select a preferred style.'}
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file size should not exceed 10MB.")
            main_type = image.content_type.split('/')[0]
            if main_type != 'image':
                raise ValidationError("File uploaded must be a valid image file.")
        return image
