from django.db import models
from django.contrib.auth.models import User


class CloudflareConfig(models.Model):
    account_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cloudflare Account ID"
    )
    api_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cloudflare API / Access Token"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/Disable Cloudflare AI Transformation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cloudflare AI Configuration"
        verbose_name_plural = "Cloudflare AI Configurations"

    def __str__(self):
        return f"Cloudflare AI Config ({self.account_id[:8]}...)" if self.account_id else "Cloudflare AI Config"


class SpaceAnalysis(models.Model):
    """Stores a user's uploaded space and all analysis results persistently."""

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

    # Ownership — None means anonymous
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='space_analyses',
        null=True,
        blank=True,
    )

    # Space metadata
    name = models.CharField(
        max_length=200,
        default='My Space',
        help_text="User-given name for this space"
    )

    # User preferences at time of analysis
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='Medium')
    maintenance = models.CharField(max_length=20, choices=MAINTENANCE_CHOICES, default='Low')
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='No preference')

    # Image paths (relative to MEDIA_ROOT)
    original_image = models.CharField(max_length=500, blank=True, default='')
    annotated_image = models.CharField(max_length=500, blank=True, default='')
    transformed_image = models.CharField(max_length=500, blank=True, default='')

    # Analysis result stored as JSON
    analysis_data = models.JSONField(default=dict)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Space Analysis"
        verbose_name_plural = "Space Analyses"
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        owner = self.user.username if self.user else "Anonymous"
        return f"{owner} — {self.name} ({self.created_at.strftime('%Y-%m-%d') if self.created_at else 'N/A'})"

    def get_overall_score(self):
        """Return the overall compatibility score from analysis data."""
        return self.analysis_data.get('scores', {}).get('overall_compatibility', 'N/A')

    def get_plant_count(self):
        """Return number of recommended plants."""
        return len(self.analysis_data.get('recommended_plants', []))


class FavoritePlant(models.Model):
    """Allows authenticated users to save favorite plants by name."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_plants',
    )
    plant_name = models.CharField(max_length=200)
    botanical_name = models.CharField(max_length=200, blank=True, default='')
    plant_image = models.URLField(max_length=500, blank=True, default='')
    plant_tag = models.CharField(max_length=100, blank=True, default='')
    price = models.CharField(max_length=50, blank=True, default='')
    # Source analysis — optional link back
    analysis = models.ForeignKey(
        SpaceAnalysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='favorited_plants',
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']
        unique_together = [('user', 'plant_name')]
        verbose_name = "Favourite Plant"
        verbose_name_plural = "Favourite Plants"

    def __str__(self):
        return f"{self.user.username} ❤ {self.plant_name}"


class UserProfile(models.Model):
    """Extended profile with Plantify-specific preferences."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='plantify_profile',
    )
    bio = models.TextField(blank=True, default='')
    preferred_budget = models.CharField(
        max_length=20,
        choices=SpaceAnalysis.BUDGET_CHOICES,
        default='Medium'
    )
    preferred_maintenance = models.CharField(
        max_length=20,
        choices=SpaceAnalysis.MAINTENANCE_CHOICES,
        default='Low'
    )
    preferred_style = models.CharField(
        max_length=50,
        choices=SpaceAnalysis.STYLE_CHOICES,
        default='No preference'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile: {self.user.username}"
