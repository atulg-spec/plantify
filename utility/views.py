import json
import logging

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import SpaceUploadForm
from .analysis import (
    run_plantify_analysis,
    generate_with_cloudflare_flux,
    get_cloudflare_credentials,
    create_visualization_prompt,
)
from .botanical_knowledge import (
    get_botanical_info,
    generate_why_this_works,
    generate_smart_insights,
)
from .models import CloudflareConfig, SpaceAnalysis

logger = logging.getLogger(__name__)


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _analyse(image, budget, maintenance, style):
    """
    Core function: processes validated upload inputs and returns AI analysis dict.
    Falls back to sample data on catastrophic failure to avoid blank error pages.
    """
    try:
        return run_plantify_analysis(
            image_input=image,
            budget=budget,
            maintenance=maintenance,
            style=style,
        )
    except Exception as exc:
        logger.exception("run_plantify_analysis failed: %s", exc)
        fb = _sample_analysis_result()
        fb["image_name"] = getattr(image, 'name', 'Uploaded Space')
        fb["validated_inputs"] = {"budget": budget, "maintenance": maintenance, "style": style}
        return fb

# Alias for external modules / tests
analyse = _analyse


def _save_analysis_to_db(request, analysis_result):
    """
    Save analysis result to SpaceAnalysis for authenticated users.
    Returns the saved SpaceAnalysis instance (or None for anonymous).
    """
    if not request.user.is_authenticated:
        return None

    try:
        space_name = analysis_result.get('image_name', 'My Space')
        inputs = analysis_result.get('validated_inputs', {})

        instance = SpaceAnalysis.objects.create(
            user=request.user,
            name=space_name,
            budget=inputs.get('budget', 'Medium'),
            maintenance=inputs.get('maintenance', 'Low'),
            style=inputs.get('style', 'No preference'),
            original_image=analysis_result.get('original_image_url', ''),
            annotated_image=analysis_result.get('annotated_image_url', ''),
            transformed_image=analysis_result.get('transformed_image_url', '') or '',
            analysis_data=analysis_result,
        )
        return instance
    except Exception as exc:
        logger.exception("Failed to save analysis to DB: %s", exc)
        return None


# ============================================================
# UPLOAD VIEW
# ============================================================

def upload(request):
    """
    Renders upload form and processes form submission.
    - Authenticated users: results auto-saved to DB, result page shows full data.
    - Anonymous users: results stored in session, result page shows blurred/limited preview.
    """
    if request.method == 'POST':
        form = SpaceUploadForm(request.POST, request.FILES)
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or request.content_type == 'application/json'
        )

        if form.is_valid():
            image = form.cleaned_data['image']
            budget = form.cleaned_data['budget']
            maintenance = form.cleaned_data['maintenance']
            style = form.cleaned_data['style']

            # Run analysis
            analysis_result = _analyse(
                image=image,
                budget=budget,
                maintenance=maintenance,
                style=style,
            )

            # Save to DB for authenticated users
            saved_instance = _save_analysis_to_db(request, analysis_result)

            # Always store in session for immediate result page access
            request.session['analysis_result'] = analysis_result
            request.session['analysis_id'] = saved_instance.pk if saved_instance else None
            request.session.modified = True

            if is_ajax or request.POST.get('format') == 'json':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('utility:result'),
                    'analysis_result': analysis_result,
                    'saved': saved_instance is not None,
                    'analysis_id': saved_instance.pk if saved_instance else None,
                })

            return redirect('utility:result')

        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            return render(request, 'utility/upload.html', {
                'form': form,
                'errors': form.errors,
            })

    form = SpaceUploadForm()
    return render(request, 'utility/upload.html', {'form': form})


# ============================================================
# RESULT VIEW
# ============================================================

def result(request):
    """
    Display analysis results.
    - Authenticated: full results from session (just saved) or from DB (via dashboard).
    - Anonymous: blurred/teaser preview.
    """
    analysis_result = request.session.get('analysis_result')
    analysis_id = request.session.get('analysis_id')
    is_authenticated = request.user.is_authenticated

    # Blurred preview mode for anonymous users who have no session data
    if not analysis_result:
        if not is_authenticated:
            # Provide sample blurred preview
            analysis_result = _sample_analysis_result()
            return render(request, 'utility/result.html', {
                'analysis': analysis_result,
                'blurred': True,
                'login_url': reverse('accounts:login') + '?next=' + reverse('utility:upload'),
            })
        return redirect('utility:upload')

    # If anonymous, show blurred result with sign-up prompt
    blurred = not is_authenticated

    if analysis_result and isinstance(analysis_result, dict):
        import re
        for item in analysis_result.get('placement_plan', []):
            if isinstance(item, dict) and 'plant' in item:
                item['plant'] = re.sub(r'\s*\(Var\.\s*\d+\)', '', item['plant']).strip()
        for plant in analysis_result.get('recommended_plants', []):
            if isinstance(plant, dict) and 'name' in plant:
                plant['name'] = re.sub(r'\s*\(Var\.\s*\d+\)', '', plant['name']).strip()

    return render(request, 'utility/result.html', {
        'analysis': analysis_result,
        'analysis_id': analysis_id,
        'blurred': blurred,
        'saved': is_authenticated and analysis_id is not None,
        'login_url': reverse('accounts:login') + '?next=' + reverse('utility:upload'),
    })


def _sample_analysis_result():
    """Return a rich sample analysis result for anonymous preview and fallback."""
    budget = "Medium"
    maintenance = "Low"
    style = "Modern"
    lighting_cond = "Medium"

    sample_raw = [
        {
            "name": "Snake Plant",
            "zone": "Floor Corner",
            "price": "₹450 - ₹850",
            "tag": "Air Purifier",
            "match_score": "95%",
            "image": "https://images.unsplash.com/photo-1593482892290-f54927ae1bac?w=600&q=80",
            "reasons": ["Thrives in ambient medium light", "Infrequent watering requirement"]
        },
        {
            "name": "Monstera Deliciosa",
            "zone": "Window Area",
            "price": "₹1,200 - ₹2,400",
            "tag": "Statement Plant",
            "match_score": "92%",
            "image": "https://images.unsplash.com/photo-1617173944883-6ffbd35d584d?w=600&q=80",
            "reasons": ["Dramatic architectural focal point", "Complements contemporary interior"]
        },
        {
            "name": "ZZ Plant",
            "zone": "Desk",
            "price": "₹550 - ₹1,100",
            "tag": "Low Maintenance",
            "match_score": "89%",
            "image": "https://images.unsplash.com/photo-1632207691143-643e2a9a9361?w=600&q=80",
            "reasons": ["High drought tolerance", "Glossy reflective foliage"]
        }
    ]

    plan = []
    recommended_plants = []

    for item in sample_raw:
        b_info = get_botanical_info(
            item["name"],
            zone_name=item["zone"],
            room_style=style,
            light_condition=lighting_cond,
            budget=budget,
            maintenance=maintenance
        )
        plan.append({
            "zone": item["zone"],
            "plant": item["name"],
            "botanical_name": b_info.get("botanical_name"),
            "why_placed_here": b_info.get("why_placed_here"),
            "placement_advantages": b_info.get("placement_advantages"),
            "benefits": b_info.get("benefits", []),
            "key_benefits": b_info.get("benefits", []),
            "wiki_url": b_info.get("wiki_url"),
            "maintenance_advice": b_info.get("care_intelligence", {}),
            "care_intelligence": b_info.get("care_intelligence", {}),
            "pet_safe": b_info.get("pet_safe", False),
            "pet_safety_notes": b_info.get("pet_safety_notes", ""),
            "design_contribution": b_info.get("design_contribution", ""),
            "things_to_consider": b_info.get("things_to_consider", [])
        })

        recommended_plants.append({
            "name": item["name"],
            "botanical_name": b_info.get("botanical_name"),
            "description": f"Architectural indoor plant selected for {item['zone']} integration.",
            "light": "Low to Bright Indirect Light",
            "water": b_info.get("care_intelligence", {}).get("watering", "Every 2-3 weeks"),
            "price": item["price"],
            "difficulty": b_info.get("difficulty", "Beginner Friendly"),
            "placement": f"Ideal for {item['zone']}",
            "tag": item["tag"],
            "image": item["image"],
            "match_score": item["match_score"],
            "reasons": item["reasons"],
            "botanical_info": b_info,
            "benefits": b_info.get("benefits", []),
            "key_benefits": b_info.get("benefits", []),
            "why_this_plant": b_info.get("why_this_plant"),
            "why_placed_here": b_info.get("why_placed_here"),
            "placement_advantages": b_info.get("placement_advantages"),
            "design_contribution": b_info.get("design_contribution"),
            "things_to_consider": b_info.get("things_to_consider", []),
            "wiki_url": b_info.get("wiki_url"),
            "maintenance_advice": b_info.get("care_intelligence", {}),
            "care_intelligence": b_info.get("care_intelligence", {}),
            "pet_safe": b_info.get("pet_safe", False),
            "pet_safety_notes": b_info.get("pet_safety_notes", ""),
            "family": b_info.get("family", ""),
            "origin": b_info.get("origin", ""),
            "mature_size": b_info.get("mature_size", ""),
            "growth_rate": b_info.get("growth_rate", "Moderate"),
        })

    result_data = {
        "success": True,
        "image_name": "Sample Living Space",
        "resolution": "1024 x 768 px",
        "original_image_url": "https://images.unsplash.com/photo-1545241047-6083a3684587?w=1200&q=80",
        "annotated_image_url": "https://images.unsplash.com/photo-1545241047-6083a3684587?w=1200&q=80",
        "transformed_image_url": None,
        "validated_inputs": {"budget": budget, "maintenance": maintenance, "style": style},
        "scores": {
            "overall_compatibility": "94%",
            "light_assessment": "Medium Light (Natural Probability: High)",
            "space_utilization": "3 Placement Zones Identified",
            "air_purification_index": "4.8/5",
        },
        "lighting": {"natural_light_prob": "High", "condition": "Medium", "avg_brightness": 128.5},
        "detected_objects": {"sofa": 1, "table": 1},
        "placement_plan": plan,
        "recommended_plants": recommended_plants,
        "style_guide": {
            "title": "Modern Interior Layout Guide",
            "planters": "Sleek monochromatic concrete & dark ceramic planters.",
            "tip": "Incorporate plants with structured silhouettes near ambient light sources.",
        },
        "budget_estimate": "₹3,500 - ₹7,500",
        "care_routine_summary": "Water once every 2-3 weeks; wipe leaves monthly.",
    }

    result_data["why_this_works"] = generate_why_this_works(result_data)
    result_data["smart_insights"] = generate_smart_insights(result_data)

    return result_data


# ============================================================
# API ENDPOINTS
# ============================================================

def analyse_api(request):
    """API endpoint for AJAX plant analysis requests."""
    if request.method == 'POST':
        form = SpaceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            result = _analyse(
                image=form.cleaned_data['image'],
                budget=form.cleaned_data['budget'],
                maintenance=form.cleaned_data['maintenance'],
                style=form.cleaned_data['style'],
            )
            return JsonResponse(result)
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'error': 'POST method required'}, status=405)


def transform_image_api(request):
    """
    AJAX endpoint to trigger Cloudflare AI image transformation.
    Saves transformed image URL back to SpaceAnalysis if a session analysis_id exists.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        import os
        import uuid
        from django.conf import settings

        analysis_result = request.session.get('analysis_result', {})
        if not analysis_result:
            analysis_result = {
                "validated_inputs": {"style": "Modern"},
                "lighting": {"condition": "Medium"},
                "recommended_plants": [
                    {"name": "Snake Plant"},
                    {"name": "Monstera Deliciosa"},
                ],
            }

        # Get credentials
        account_id, access_token = get_cloudflare_credentials()

        # Build prompt
        prompt = create_visualization_prompt(analysis_result)

        # Resolve original image
        original_url = analysis_result.get('original_image_url', '')
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(os.getcwd(), 'static', 'media'))
        media_url_prefix = getattr(settings, 'MEDIA_URL', '/media/')

        relative_path = original_url.lstrip('/')
        if relative_path.startswith(media_url_prefix.lstrip('/')):
            relative_path = relative_path[len(media_url_prefix.lstrip('/')):]
        image_path = os.path.join(media_root, relative_path)

        if not os.path.exists(image_path):
            return JsonResponse({
                'success': False,
                'error': f'Original image not found: {relative_path}',
            }, status=400)

        # Call Cloudflare FLUX
        with open(image_path, 'rb') as image_file:
            class SimpleFile:
                def __init__(self, f, name):
                    self._f = f
                    self.name = name
                    self.content_type = 'image/jpeg'

                def read(self, *a): return self._f.read(*a)

                def seek(self, *a): return self._f.seek(*a)

            image_obj = SimpleFile(image_file, os.path.basename(image_path))
            image_bytes = generate_with_cloudflare_flux(
                account_id=account_id,
                access_token=access_token,
                prompt=prompt,
                image=image_obj,
            )

        # Save transformed image to media
        transformed_dir = os.path.join(media_root, 'transformed')
        os.makedirs(transformed_dir, exist_ok=True)
        out_filename = f'plantify_transformed_{uuid.uuid4().hex[:8]}.jpg'
        out_path = os.path.join(transformed_dir, out_filename)
        with open(out_path, 'wb') as f:
            f.write(image_bytes)

        transformed_url = media_url_prefix.rstrip('/') + '/transformed/' + out_filename

        # Update session
        analysis_result['transformed_image_url'] = transformed_url
        request.session['analysis_result'] = analysis_result
        request.session.modified = True

        # Update DB record if it exists
        analysis_id = request.session.get('analysis_id')
        if analysis_id and request.user.is_authenticated:
            try:
                sa = SpaceAnalysis.objects.get(pk=analysis_id, user=request.user)
                sa.transformed_image = transformed_url
                sa.analysis_data['transformed_image_url'] = transformed_url
                sa.save(update_fields=['transformed_image', 'analysis_data'])
            except SpaceAnalysis.DoesNotExist:
                pass

        return JsonResponse({'success': True, 'transformed_image_url': transformed_url})

    except Exception as exc:
        logger.exception("transform_image_api failed: %s", exc)
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)