from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import PlantifyRegistrationForm, PlantifyLoginForm, UserProfileForm


def register(request):
    """User registration view. Auto-creates UserProfile on success."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = PlantifyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-create UserProfile with default preferences
            from utility.models import UserProfile
            UserProfile.objects.get_or_create(user=user)

            login(request, user)
            messages.success(
                request,
                f"Welcome to Plantify, {user.first_name or user.username}! 🌿 "
                "Your account is ready. Upload your first space to get started."
            )
            return redirect('dashboard:index')
        else:
            # Pass field errors back to template
            pass
    else:
        form = PlantifyRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """Login view with redirect support."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = PlantifyLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! 🌿")

            # Redirect to next page or dashboard
            redirect_to = request.POST.get('next') or next_url or 'dashboard:index'
            try:
                return redirect(redirect_to)
            except Exception:
                return redirect('dashboard:index')
        # Form errors are shown in template
    else:
        form = PlantifyLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_http_methods(["POST"])
def user_logout(request):
    """Logout via POST only (CSRF-protected)."""
    logout(request)
    messages.info(request, "You've been logged out. See you soon! 👋")
    return redirect('home:index')


@login_required
def profile(request):
    """User profile and preferences management."""
    from utility.models import UserProfile, SpaceAnalysis, FavoritePlant

    # Get or create profile
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save(update_fields=['first_name', 'last_name'])

            # Update UserProfile fields
            profile_obj.bio = form.cleaned_data.get('bio', '')
            profile_obj.preferred_budget = form.cleaned_data['preferred_budget']
            profile_obj.preferred_maintenance = form.cleaned_data['preferred_maintenance']
            profile_obj.preferred_style = form.cleaned_data['preferred_style']
            profile_obj.save()

            messages.success(request, "Profile updated successfully! ✅")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'bio': profile_obj.bio,
            'preferred_budget': profile_obj.preferred_budget,
            'preferred_maintenance': profile_obj.preferred_maintenance,
            'preferred_style': profile_obj.preferred_style,
        })

    # Stats for profile page
    analysis_count = SpaceAnalysis.objects.filter(user=request.user).count()
    favorites_count = FavoritePlant.objects.filter(user=request.user).count()

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile_obj,
        'analysis_count': analysis_count,
        'favorites_count': favorites_count,
    })


@login_required
def change_password(request):
    """Password change view."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Password changed successfully! 🔒")
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def delete_account(request):
    """Soft account deletion — requires POST confirmation."""
    if request.method == 'POST':
        confirmation = request.POST.get('confirm', '')
        if confirmation == request.user.username:
            user = request.user
            logout(request)
            user.delete()
            messages.info(request, "Your account and all data have been permanently deleted.")
            return redirect('home:index')
        else:
            messages.error(request, "Username confirmation didn't match. Account not deleted.")

    return render(request, 'accounts/delete_account.html')
