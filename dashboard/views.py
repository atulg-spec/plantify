from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from utility.models import SpaceAnalysis, FavoritePlant, UserProfile


@login_required
def index(request):
    """Main user dashboard — overview of activity and quick actions."""
    from utility.models import UserProfile

    # Get or create profile
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    # Recent analyses (last 6)
    recent_analyses = SpaceAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')[:6]

    # Favorite plants (last 6)
    favorite_plants = FavoritePlant.objects.filter(
        user=request.user
    ).order_by('-saved_at')[:6]

    # Stats
    total_analyses = SpaceAnalysis.objects.filter(user=request.user).count()
    total_favorites = FavoritePlant.objects.filter(user=request.user).count()

    context = {
        'profile': profile_obj,
        'recent_analyses': recent_analyses,
        'favorite_plants': favorite_plants,
        'total_analyses': total_analyses,
        'total_favorites': total_favorites,
        'is_new_user': total_analyses == 0,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def history(request):
    """Paginated list of all user's space analyses."""
    analyses_qs = SpaceAnalysis.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(analyses_qs, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/history.html', {
        'page_obj': page_obj,
        'total_count': analyses_qs.count(),
    })


@login_required
def analysis_detail(request, pk):
    """View a saved space analysis — enforces user ownership."""
    analysis_obj = get_object_or_404(SpaceAnalysis, pk=pk, user=request.user)
    data = dict(analysis_obj.analysis_data or {})

    # Ensure image URLs are populated from model fields if missing in JSON
    if not data.get('original_image_url') and analysis_obj.original_image:
        data['original_image_url'] = analysis_obj.original_image
    if not data.get('annotated_image_url') and analysis_obj.annotated_image:
        data['annotated_image_url'] = analysis_obj.annotated_image
    if not data.get('transformed_image_url') and analysis_obj.transformed_image:
        data['transformed_image_url'] = analysis_obj.transformed_image

    if data and isinstance(data, dict):
        import re
        from utility.botanical_knowledge import (
            get_botanical_info,
            generate_why_this_works,
            generate_smart_insights,
        )

        if not data.get('why_this_works'):
            data['why_this_works'] = generate_why_this_works(data)
        if not data.get('smart_insights'):
            data['smart_insights'] = generate_smart_insights(data)

        for item in data.get('placement_plan', []):
            if isinstance(item, dict) and 'plant' in item:
                item['plant'] = re.sub(r'\s*\(Var\.\s*\d+\)', '', item['plant']).strip()
                if not item.get('why_placed_here'):
                    b_info = get_botanical_info(item['plant'], zone_name=item.get('zone'))
                    item['why_placed_here'] = b_info.get('why_placed_here')
                    item['placement_advantages'] = b_info.get('placement_advantages')
                    item['botanical_name'] = item.get('botanical_name') or b_info.get('botanical_name')

        for plant in data.get('recommended_plants', []):
            if isinstance(plant, dict) and 'name' in plant:
                plant['name'] = re.sub(r'\s*\(Var\.\s*\d+\)', '', plant['name']).strip()
                if not plant.get('why_this_plant'):
                    b_info = get_botanical_info(plant['name'])
                    plant['botanical_name'] = plant.get('botanical_name') or b_info.get('botanical_name')
                    plant['description'] = plant.get('description') or b_info.get('design_contribution')
                    plant['why_this_plant'] = b_info.get('why_this_plant')
                    plant['placement_advantages'] = plant.get('placement_advantages') or b_info.get('placement_advantages')
                    plant['benefits'] = plant.get('benefits') or b_info.get('benefits', [])
                    plant['key_benefits'] = plant.get('key_benefits') or b_info.get('benefits', [])
                    plant['care_intelligence'] = plant.get('care_intelligence') or b_info.get('care_intelligence', {})
                    plant['things_to_consider'] = plant.get('things_to_consider') or b_info.get('things_to_consider', [])
                    plant['design_contribution'] = plant.get('design_contribution') or b_info.get('design_contribution')
                    plant['image'] = plant.get('image') or ''

    return render(request, 'utility/result.html', {
        'analysis': data,
        'analysis_obj': analysis_obj,
        'saved': True,
    })


@login_required
@require_POST
def rename_analysis(request, pk):
    """Rename a saved analysis via AJAX POST."""
    analysis_obj = get_object_or_404(SpaceAnalysis, pk=pk, user=request.user)
    new_name = request.POST.get('name', '').strip()
    if not new_name:
        return JsonResponse({'success': False, 'error': 'Name cannot be empty.'}, status=400)
    if len(new_name) > 200:
        return JsonResponse({'success': False, 'error': 'Name too long (max 200 chars).'}, status=400)
    analysis_obj.name = new_name
    analysis_obj.save(update_fields=['name'])
    return JsonResponse({'success': True, 'name': analysis_obj.name})


@login_required
@require_POST
def delete_analysis(request, pk):
    """Delete a saved space analysis with all associated files."""
    import os
    from django.conf import settings

    analysis_obj = get_object_or_404(SpaceAnalysis, pk=pk, user=request.user)

    # Clean up media files
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    for field_path in [analysis_obj.original_image, analysis_obj.annotated_image, analysis_obj.transformed_image]:
        if field_path:
            # Strip URL prefix to get relative path
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            relative = field_path.lstrip('/')
            if relative.startswith(media_url.lstrip('/')):
                relative = relative[len(media_url.lstrip('/')):]
            full_path = os.path.join(media_root, relative)
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                except OSError:
                    pass

    analysis_obj.delete()
    messages.success(request, "Space analysis deleted. 🗑️")
    return redirect('dashboard:history')


@login_required
def favorites(request):
    """Paginated list of all user's saved favorite plants."""
    favorites_qs = FavoritePlant.objects.filter(user=request.user).order_by('-saved_at')
    paginator = Paginator(favorites_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/favorites.html', {
        'page_obj': page_obj,
        'total_count': favorites_qs.count(),
    })


@login_required
@require_POST
def toggle_favorite(request):
    """Add or remove a plant from favorites via AJAX POST."""
    import json
    try:
        body = json.loads(request.body)
    except (ValueError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)

    plant_name = body.get('plant_name', '').strip()
    if not plant_name:
        return JsonResponse({'success': False, 'error': 'Plant name required.'}, status=400)

    existing = FavoritePlant.objects.filter(user=request.user, plant_name=plant_name).first()
    if existing:
        existing.delete()
        return JsonResponse({'success': True, 'action': 'removed', 'plant_name': plant_name})
    else:
        FavoritePlant.objects.create(
            user=request.user,
            plant_name=plant_name,
            botanical_name=body.get('botanical_name', ''),
            plant_image=body.get('plant_image', ''),
            plant_tag=body.get('plant_tag', ''),
            price=body.get('price', ''),
        )
        return JsonResponse({'success': True, 'action': 'added', 'plant_name': plant_name})


@login_required
@require_POST
def remove_favorite(request, pk):
    """Remove a specific favorite plant by its pk."""
    fav = get_object_or_404(FavoritePlant, pk=pk, user=request.user)
    fav.delete()
    messages.success(request, f"Removed {fav.plant_name} from favorites.")
    return redirect('dashboard:favorites')
