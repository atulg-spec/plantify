from django.contrib import admin
from .models import CloudflareConfig, SpaceAnalysis, FavoritePlant, UserProfile


@admin.register(CloudflareConfig)
class CloudflareConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'account_id', 'is_active', 'updated_at')
    fields = ('account_id', 'api_token', 'is_active')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(SpaceAnalysis)
class SpaceAnalysisAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'budget', 'maintenance', 'style', 'created_at')
    list_filter = ('budget', 'maintenance', 'style', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(FavoritePlant)
class FavoritePlantAdmin(admin.ModelAdmin):
    list_display = ('plant_name', 'user', 'saved_at')
    search_fields = ('plant_name', 'user__username')
    ordering = ('-saved_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_budget', 'preferred_maintenance', 'preferred_style', 'created_at')
    search_fields = ('user__username', 'user__email')
