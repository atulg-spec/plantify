import os
import sys
import uuid
import random
import csv
import ast
import json
import re
import requests
import numpy as np
import cv2
from pathlib import Path
from django.conf import settings

try:
    from utility.botanical_knowledge import (
        get_botanical_info,
        generate_why_this_works,
        generate_smart_insights,
    )
except (ImportError, ValueError):
    from .botanical_knowledge import (
        get_botanical_info,
        generate_why_this_works,
        generate_smart_insights,
    )

# Try to import ultralytics YOLO (optional)
YOLO_AVAILABLE = False
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


# ============================================================
# 1. IMAGE LOADING FROM DJANGO FILE OR PATH
# ============================================================
def load_image_from_input(image_input):
    """
    Load image from Django file object, path, or bytes.
    Returns (img_bgr, img_rgb, h, w, image_name)
    """
    image_name = "uploaded_space.jpg"
    
    if hasattr(image_input, 'read'):
        image_name = getattr(image_input, 'name', 'uploaded_space.jpg')
        file_bytes = np.frombuffer(image_input.read(), np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if hasattr(image_input, 'seek'):
            image_input.seek(0)
    elif isinstance(image_input, (str, Path)) and os.path.exists(str(image_input)):
        image_name = os.path.basename(str(image_input))
        img_bgr = cv2.imread(str(image_input))
    elif isinstance(image_input, np.ndarray):
        img_bgr = image_input
    else:
        raise ValueError("Invalid image input provided to Plantify analysis.")

    if img_bgr is None or img_bgr.size == 0:
        raise ValueError("Could not decode image array.")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img_bgr.shape[:2]

    return img_bgr, img_rgb, h, w, image_name


# ============================================================
# 2. LIGHTING ANALYSIS
# ============================================================
def analyze_lighting(img_bgr):
    """Estimate brightness and natural-light probability."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    avg_brightness = float(np.mean(gray))
    median_brightness = float(np.median(gray))

    # Distribution
    dark_pct = float(np.sum(gray < 85) / gray.size * 100)
    medium_pct = float(np.sum((gray >= 85) & (gray < 170)) / gray.size * 100)
    bright_pct = float(np.sum(gray >= 170) / gray.size * 100)

    # Classify
    if avg_brightness < 50:
        condition = "Very Low"
    elif avg_brightness < 90:
        condition = "Low"
    elif avg_brightness < 140:
        condition = "Medium"
    elif avg_brightness < 190:
        condition = "Bright"
    else:
        condition = "Very Bright"

    # Natural light probability: high if many bright pixels and high contrast
    std_dev = float(np.std(gray))
    if bright_pct > 15 and std_dev > 50:
        natural = "High"
    elif bright_pct > 5:
        natural = "Medium"
    else:
        natural = "Low"

    return {
        "avg": avg_brightness,
        "median": median_brightness,
        "dark_pct": dark_pct,
        "medium_pct": medium_pct,
        "bright_pct": bright_pct,
        "condition": condition,
        "natural": natural,
        "std": std_dev,
    }


# ============================================================
# 3. LOCAL COMPUTER VISION (YOLO optional / OpenCV fallback)
# ============================================================
def detect_objects(img_bgr, img_rgb):
    """Detect objects using local YOLO if available; otherwise OpenCV heuristics."""
    h, w = img_bgr.shape[:2]
    detections = []  # list of dicts: {label, x, y, w, h, conf}

    if YOLO_AVAILABLE:
        try:
            model = YOLO("yolov8n.pt")
            results = model(img_rgb, verbose=False)[0]
            for box in results.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "label": label,
                    "x": x1, "y": y1,
                    "w": x2 - x1, "h": y2 - y1,
                    "conf": conf,
                })
        except Exception:
            detections = _fallback_object_detection(img_bgr, img_rgb)
    else:
        detections = _fallback_object_detection(img_bgr, img_rgb)

    # Summarize
    summary = {}
    for d in detections:
        summary[d["label"]] = summary.get(d["label"], 0) + 1

    return detections, summary


def _fallback_object_detection(img_bgr, img_rgb):
    """Lightweight heuristic detection using contours and color regions."""
    detections = []
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = img_bgr.shape[:2]
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < (w * h) * 0.02:  # ignore tiny
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        if bh > bw * 1.5 and y > h * 0.5:
            label = "cabinet"
        elif bw > bh * 1.5 and y > h * 0.4:
            label = "table"
        elif bw > bh * 1.2 and y < h * 0.6:
            label = "sofa"
        else:
            label = "object"
            
        detections.append({
            "label": label,
            "x": x, "y": y, "w": bw, "h": bh,
            "conf": 0.45,
        })
        
    detections = sorted(detections, key=lambda d: d["w"] * d["h"], reverse=True)[:5]
    return detections


# ============================================================
# 4. SPACE / PLACEMENT ZONE ANALYSIS
# ============================================================
def find_placement_zones(img_bgr, detections, lighting):
    """Heuristic placement zones based on empty regions, corners, light."""
    h, w = img_bgr.shape[:2]
    zones = []

    occupied = np.zeros((h, w), dtype=np.uint8)
    for d in detections:
        x, y, bw, bh = d["x"], d["y"], d["w"], d["h"]
        occupied[max(0, y):min(h, y + bh), max(0, x):min(w, x + bw)] = 255

    def is_empty(cx, cy, rw, rh):
        x1 = max(0, cx - rw // 2)
        y1 = max(0, cy - rh // 2)
        x2 = min(w, cx + rw // 2)
        y2 = min(h, cy + rh // 2)
        if x2 <= x1 or y2 <= y1:
            return False
        region = occupied[y1:y2, x1:x2]
        return np.mean(region) < 10

    candidates = [
        ("Floor Corner", int(w * 0.15), int(h * 0.80), int(w * 0.18), int(h * 0.25)),
        ("Floor Corner", int(w * 0.85), int(h * 0.80), int(w * 0.18), int(h * 0.25)),
        ("Window Area", int(w * 0.50), int(h * 0.25), int(w * 0.20), int(h * 0.20)),
        ("Desk",        int(w * 0.30), int(h * 0.65), int(w * 0.15), int(h * 0.10)),
        ("Table",       int(w * 0.70), int(h * 0.65), int(w * 0.15), int(h * 0.10)),
        ("Shelf",       int(w * 0.80), int(h * 0.40), int(w * 0.10), int(h * 0.15)),
        ("Empty Corner",int(w * 0.20), int(h * 0.40), int(w * 0.15), int(h * 0.20)),
        ("Wall Area",   int(w * 0.50), int(h * 0.15), int(w * 0.15), int(h * 0.15)),
    ]

    for zone_name, cx, cy, rw, rh in candidates:
        if is_empty(cx, cy, rw, rh):
            x1 = max(0, cx - rw // 2)
            y1 = max(0, cy - rh // 2)
            x2 = min(w, cx + rw // 2)
            y2 = min(h, cy + rh // 2)
            if x2 > x1 and y2 > y1:
                region_gray = cv2.cvtColor(img_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                local_avg = float(np.mean(region_gray))
                if local_avg < 50:
                    light = "Low"
                elif local_avg < 120:
                    light = "Medium"
                else:
                    light = "Bright"
            else:
                light = lighting["condition"]

            zones.append({
                "zone": zone_name,
                "x": cx, "y": cy,
                "width": rw, "height": rh,
                "light": light,
                "confidence": round(random.uniform(0.70, 0.94), 2),
            })

    if len(zones) < 3:
        fallback = [
            ("Floor Corner", int(w * 0.15), int(h * 0.85), int(w * 0.20), int(h * 0.25)),
            ("Window Area", int(w * 0.50), int(h * 0.30), int(w * 0.20), int(h * 0.20)),
            ("Empty Corner", int(w * 0.85), int(h * 0.50), int(w * 0.15), int(h * 0.20)),
        ]
        for name, cx, cy, rw, rh in fallback:
            if len(zones) >= 3:
                break
            zones.append({
                "zone": name,
                "x": cx, "y": cy,
                "width": rw, "height": rh,
                "light": lighting["condition"],
                "confidence": 0.65,
            })

    return zones


# ============================================================
# 5. INTERIOR STYLE ESTIMATION
# ============================================================
def estimate_style(img_bgr, detections):
    """Simple heuristic style guess based on color profile and detected objects."""
    h, w = img_bgr.shape[:2]
    b, g, r = cv2.split(img_bgr.astype(np.float32))
    rg = np.abs(r - g)
    yb = np.abs(0.5 * (r + g) - b)
    colorfulness = np.sqrt(np.std(rg) ** 2 + np.std(yb) ** 2) + 0.3 * np.sqrt(np.mean(rg) ** 2 + np.mean(yb) ** 2)

    labels = [d["label"] for d in detections]
    has_modern = any(l in labels for l in ["tv", "television", "laptop", "monitor"])
    has_natural = any(l in labels for l in ["plant", "potted plant", "flower"])

    if colorfulness > 40 and has_natural:
        return "Boho"
    elif has_modern and colorfulness < 25:
        return "Minimal"
    elif has_modern:
        return "Modern"
    elif colorfulness > 30:
        return "Natural"
    else:
        return "Traditional"


# ============================================================
# 6. PLANT DATABASE FROM CSV (plants-db.csv)
# ============================================================
def load_plant_database():
    """Load indoor plant database dynamically from plants-db.csv."""
    base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
    csv_path = os.path.join(base_dir, 'plants-db.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.getcwd(), 'plants-db.csv')
        
    plants = []
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse JSON or Python literal fields
                    try:
                        light = json.loads(row['light']) if row['light'].startswith('[') else [row['light']]
                    except Exception:
                        try:
                            light = ast.literal_eval(row['light']) if row['light'].startswith('[') else [row['light']]
                        except Exception:
                            light = [row['light']]

                    try:
                        locations = json.loads(row['locations']) if row['locations'].startswith('[') else [row['locations']]
                    except Exception:
                        try:
                            locations = ast.literal_eval(row['locations']) if row['locations'].startswith('[') else [row['locations']]
                        except Exception:
                            locations = [row['locations']]

                    try:
                        style = json.loads(row['style']) if row['style'].startswith('[') else [row['style']]
                    except Exception:
                        try:
                            style = ast.literal_eval(row['style']) if row['style'].startswith('[') else [row['style']]
                        except Exception:
                            style = [row['style']]

                    budget_val = row.get('budget', 'Medium')
                    price_map = {"Low": "₹350 - ₹650", "Medium": "₹700 - ₹1,400", "High": "₹1,500 - ₹3,500"}
                    growth_type = row.get('growth_type', 'Foliage')
                    raw_name = row.get('name', 'Indoor Plant')
                    clean_name = re.sub(r'\s*\(Var\.\s*\d+\)', '', raw_name).strip()
                    botanical_data = get_botanical_info(clean_name)

                    plants.append({
                        "name": clean_name,
                        "botanical_name": botanical_data.get("botanical_name", f"{growth_type} Variety"),
                        "description": f"Beautiful {growth_type.lower()} indoor plant ideal for {', '.join(locations[:2])}.",
                        "light": light,
                        "maintenance": row.get('maintenance', 'Low'),
                        "size": row.get('size', 'Medium'),
                        "locations": locations,
                        "budget": budget_val,
                        "pet_safe": str(row.get('pet_safe', '')).lower() == 'true',
                        "style": style,
                        "watering": f"Watering level: {row.get('watering', 'Low')}",
                        "price": price_map.get(budget_val, "₹600 - ₹1,200"),
                        "tag": growth_type,
                        "beginner": str(row.get('beginner', '')).lower() == 'true',
                        "image": row.get('image_url', 'https://images.unsplash.com/photo-1593482892290-f54927ae1bac?w=600&q=80')
                    })
        except Exception as err:
            print("Error loading plants-db.csv:", err)

    if not plants:
        # Fallback inline list if CSV is unreadable
        plants = [
            {
                "name": "Snake Plant",
                "botanical_name": "Sansevieria trifasciata",
                "description": "Hardy air-purifying indoor plant with upright architectural foliage.",
                "light": ["Low", "Medium", "Bright"],
                "maintenance": "Low",
                "size": "Medium",
                "locations": ["Floor Corner", "Window Area", "Empty Corner"],
                "budget": "Low",
                "pet_safe": False,
                "style": ["Modern", "Minimal"],
                "watering": "Every 2-3 weeks",
                "price": "$15 - $25",
                "tag": "Air Purifier",
                "beginner": True,
                "image": "https://images.unsplash.com/photo-1593482892290-f54927ae1bac?w=600&q=80"
            }
        ]

    return plants


# ============================================================
# 7. PLANT RECOMMENDATION ENGINE
# ============================================================
def calculate_plant_score(plant, lighting, zones, prefs, style):
    """Return 0–100 score and list of match reasons."""
    reasons = []
    score = 0.0

    # 1. Light compatibility (30%)
    light_score = 0.0
    if lighting["condition"] in plant["light"]:
        light_score = 1.0
        reasons.append(f"Works well with {lighting['condition'].lower()} light")
    elif any(l in plant["light"] for l in ["Medium", "Bright"]) and lighting["condition"] in ["Low", "Medium", "Bright"]:
        light_score = 0.7
        reasons.append(f"Tolerates {lighting['condition'].lower()} light")
    else:
        light_score = 0.3
        reasons.append(f"Adapts to ambient lighting")
    score += light_score * 30

    # 2. Placement compatibility (20%)
    zone_names = [z["zone"] for z in zones]
    if any(loc in zone_names for loc in plant["locations"]):
        matched = [loc for loc in plant["locations"] if loc in zone_names]
        place_score = 1.0
        reasons.append(f"Suitable for {matched[0]}")
    else:
        place_score = 0.4
        reasons.append("Adaptable room placement")
    score += place_score * 20

    # 3. Maintenance compatibility (15%)
    maint_pref = prefs["maintenance"]
    maint_map = {"Low": 0, "Medium": 1, "High": 2}
    plant_m = maint_map.get(plant["maintenance"], 1)
    pref_m = maint_map.get(maint_pref, 0)
    if plant_m <= pref_m:
        maint_score = 1.0
        reasons.append(f"{plant['maintenance']} maintenance requirement")
    elif plant_m == pref_m + 1:
        maint_score = 0.6
        reasons.append(f"Moderate care ({plant['maintenance']})")
    else:
        maint_score = 0.2
        reasons.append(f"Higher care demand")
    score += maint_score * 15

    # 4. Budget compatibility (15%)
    budget_pref = prefs["budget"]
    budget_map = {"Low": 0, "Medium": 1, "High": 2}
    plant_b = budget_map.get(plant["budget"], 1)
    pref_b = budget_map.get(budget_pref, 1)
    if plant_b <= pref_b:
        budget_score = 1.0
        reasons.append(f"Fits {budget_pref.lower()} budget tier")
    else:
        budget_score = 0.3
        reasons.append(f"Slightly above target budget")
    score += budget_score * 15

    # 5. Style compatibility (10%)
    style_pref = prefs["style"]
    if style_pref == "No preference" or style == "Unknown / Mixed":
        style_score = 0.8
    elif style_pref in plant["style"] or style in plant["style"]:
        style_score = 1.0
        reasons.append(f"Complements {style_pref.lower()} decor")
    else:
        style_score = 0.4
    score += style_score * 10

    # 6. Beginner friendliness (10%)
    if plant.get("beginner", True):
        beginner_score = 1.0
        reasons.append("Beginner friendly species")
    else:
        beginner_score = 0.5
        reasons.append("Requires experienced care")
    score += beginner_score * 10

    return round(score, 1), reasons


def recommend_plants(plants, lighting, zones, prefs, style, top_n=3):
    """Score and rank all plants from CSV, selecting distinct top species."""
    scored = []
    for p in plants:
        s, reasons = calculate_plant_score(p, lighting, zones, prefs, style)
        scored.append({"plant": p, "score": s, "reasons": reasons})
    
    scored.sort(key=lambda r: r["score"], reverse=True)

    results = []
    seen_base_names = set()

    for r in scored:
        name = r["plant"]["name"]
        # Extract base species name to ensure species variety
        base_name = name.split("'")[0].strip()
        if base_name not in seen_base_names:
            seen_base_names.add(base_name)
            results.append(r)
            if len(results) >= top_n:
                break

    if len(results) < top_n:
        for r in scored:
            if r not in results:
                results.append(r)
                if len(results) >= top_n:
                    break

    return results[:top_n]


# ============================================================
# 8. PLACEMENT RECOMMENDATIONS & ANNOTATION
# ============================================================
def placement_plan(zones, top_plants):
    """Assign distinct plant to each zone, prioritizing locations and avoiding duplicates."""
    plan = []
    used = set()
    for i, z in enumerate(zones, 1):
        best = None
        best_score = -1
        # 1. Best matching plant that fits this zone and has not yet been placed
        for r in top_plants:
            p = r["plant"]
            if p["name"] in used:
                continue
            if z["zone"] in p.get("locations", []):
                if r.get("score", 0) > best_score:
                    best_score = r["score"]
                    best = p

        # 2. If no zone-specific plant is unused, take the next highest-scoring unused plant
        if best is None:
            for r in top_plants:
                p = r["plant"]
                if p["name"] not in used:
                    best = p
                    break

        # 3. If all candidate plants have been used, cycle cleanly through available candidates
        if best is None and top_plants:
            best = top_plants[(i - 1) % len(top_plants)]["plant"]

        if best:
            used.add(best["name"])
            plan.append({"zone": z["zone"], "plant": best["name"], "zone_info": z})
    return plan


def create_annotated_image(img_bgr, detections, zones, plan):
    """Draw bounding boxes and placement markers, save to Django media directory."""
    out = img_bgr.copy()
    h, w = out.shape[:2]

    # Draw detected objects
    for d in detections:
        x, y, bw, bh = d["x"], d["y"], d["w"], d["h"]
        cv2.rectangle(out, (x, y), (x + bw, y + bh), (34, 197, 94), 2)
        label = f"{d['label']} ({int(d['conf']*100)}%)"
        cv2.putText(out, label, (x, max(20, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (34, 197, 94), 2)

    # Draw placement zones
    for i, z in enumerate(zones, 1):
        cx, cy = z["x"], z["y"]
        rw, rh = z["width"], z["height"]
        x1, y1 = cx - rw // 2, cy - rh // 2
        x2, y2 = cx + rw // 2, cy + rh // 2
        cv2.rectangle(out, (x1, y1), (x2, y2), (255, 140, 0), 2)
        cv2.circle(out, (cx, cy), 14, (0, 0, 220), -1)
        cv2.putText(out, str(i), (cx - 6, cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Draw plant labels
    for i, p in enumerate(plan, 1):
        z = p["zone_info"]
        cx, cy = z["x"], z["y"]
        name = p["plant"]
        label = f"[{i}] {name}"
        cv2.putText(out, label, (cx - 50, cy - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(out, label, (cx - 50, cy - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Save into Django MEDIA directory under 'annotated/'
    media_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(getattr(settings, 'BASE_DIR', os.getcwd()), 'static', 'media'))
    annotated_folder = os.path.join(media_dir, 'annotated')
    os.makedirs(annotated_folder, exist_ok=True)
    
    unique_filename = f"plantify_annotated_{uuid.uuid4().hex[:8]}.jpg"
    full_path = os.path.join(annotated_folder, unique_filename)
    cv2.imwrite(full_path, out)

    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    relative_url = os.path.join(media_url, 'annotated', unique_filename).replace('\\', '/')
    return relative_url


def save_original_image(img_bgr):
    """Save the original uploaded image into Django media directory."""
    media_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(getattr(settings, 'BASE_DIR', os.getcwd()), 'static', 'media'))
    uploads_folder = os.path.join(media_dir, 'uploads')
    os.makedirs(uploads_folder, exist_ok=True)
    
    unique_filename = f"plantify_original_{uuid.uuid4().hex[:8]}.jpg"
    full_path = os.path.join(uploads_folder, unique_filename)
    cv2.imwrite(full_path, img_bgr)

    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    relative_url = os.path.join(media_url, 'uploads', unique_filename).replace('\\', '/')
    return relative_url, full_path


def get_cloudflare_credentials():
    """Fetch Cloudflare Account ID and API Token from DB admin model or fallback."""
    try:
        from .models import CloudflareConfig
        config = CloudflareConfig.objects.filter(is_active=True).first()
        if config and config.account_id and config.api_token:
            return config.account_id, config.api_token
    except Exception as e:
        print("Notice: Could not query CloudflareConfig table:", e)
    
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', ''))
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", getattr(settings, 'CLOUDFLARE_API_TOKEN', ''))
    return account_id, api_token




def create_visualization_prompt(analysis_data):
    """
    Creates strict image-editing visualization prompt matching Plantify design specs.
    """
    style = analysis_data.get("validated_inputs", {}).get("style", "Modern")
    lighting = analysis_data.get("lighting", {})
    space_type = analysis_data.get("detected_style", "Indoor Room")
    placement_plan = analysis_data.get("placement_plan", [])
    recommendations = analysis_data.get("recommended_plants", [])

    lines = []
    if placement_plan:
        for index, item in enumerate(placement_plan[:5], start=1):
            plant_name = item.get("plant", "Indoor Plant")
            zone_info = item.get("zone_info", {})
            zone_name = item.get("zone", "Floor Corner")
            
            x = zone_info.get("x", 0)
            y = zone_info.get("y", 0)
            w = zone_info.get("width", 0)
            h = zone_info.get("height", 0)
            light = zone_info.get("light", "Medium")
            
            lines.append(
                f"PLANT {index}\n"
                f"Plant: {plant_name}\n"
                f"Placement zone: {zone_name}\n"
                f"Approximate image position:\n"
                f"x={x}, y={y}\n"
                f"zone width={w}, zone height={h}\n"
                f"Estimated local light: {light}\n"
                f"Recommended plant size: Medium\n"
            )
    elif recommendations:
        for index, p in enumerate(recommendations[:5], start=1):
            p_name = p.get("name", "Indoor Plant")
            p_place = p.get("placement", "Floor Corner")
            lines.append(
                f"PLANT {index}\n"
                f"Plant: {p_name}\n"
                f"Placement zone: {p_place}\n"
            )
    else:
        lines.append("PLANT 1\nPlant: Snake Plant\nPlacement zone: Floor Corner\n")

    plant_instructions = "\n".join(lines)

    light_cond = lighting.get("condition", "Medium") if isinstance(lighting, dict) else str(lighting)
    light_nat = lighting.get("natural_light_prob", "Medium") if isinstance(lighting, dict) else "Medium"

    plants = [plant.get("name") for plant in recommendations]


    prompt = f"""
EDIT THE PROVIDED ROOM PHOTO.
You are Plantify's photorealistic interior plant
visualization engine.

ROOM TYPE:
{space_type}

RECOMMENDED PLANTS:
{plants}

PLACEMENT PLAN:
{plant_instructions}

The provided image is the ORIGINAL ROOM.
Grass mats, Lightings and some accessories
Preserve the original room as accurately as possible.

PRESERVE:
- walls
- windows
- doors
- floor
- ceiling
- furniture
- room architecture
- room proportions
- camera position
- camera perspective
- existing lighting
- existing colors
- existing furniture arrangement

ONLY ADD THE RECOMMENDED PLANTS.

The plants should look like they were physically placed
inside the real room.

PLANT REQUIREMENTS:
- realistic botanical appearance
- realistic size
- realistic pots
- realistic perspective
- realistic shadows
- realistic contact with floor/furniture
- realistic lighting
- appropriate placement
- appropriate scale

PLACEMENT:
Use the Plantify placement plan as the primary instruction.

Do NOT randomly move plants to attractive locations.

Do NOT redesign the room.

DO NOT:
- remove furniture
- move furniture
- add furniture
- change walls
- change flooring
- change windows
- add decorations
- add people
- add text
- add labels
- add arrows
- add UI
- add diagrams
- add excessive plants
- create floating plants
- create oversized plants

The final image must look like a real photograph
of the SAME ROOM after adding the recommended plants.

Make the smallest possible modification to the original image.

Output only the edited photorealistic room image.
"""

    print(prompt)
    return prompt









CF_CONNECT_TIMEOUT = 15          # seconds to establish TCP connection
CF_READ_TIMEOUT    = 180         # seconds to wait for full response body
CF_MAX_RETRIES     = 3           # attempts per model before giving up
CF_RETRY_BACKOFF   = [5, 15, 30] # wait (seconds) between retry attempts
# FLUX.2 Klein hard limit — do NOT increase beyond 512
CF_MAX_IMAGE_SIDE  = 512
CF_JPEG_QUALITY    = 92          # JPEG encode quality sent to Cloudflare



# ============================================================
# MAIN ENTRY POINT FOR DJANGO VIEWS
# ============================================================
def run_plantify_analysis(image_input, budget="Medium", maintenance="Low", style="No preference"):
    """
    Main function invoked by Django view. Reads plants-db.csv, runs vision analysis,
    lighting assessment, placement zone finding, plant scoring, and saves annotated image.
    """
    # 1. Load Image
    img_bgr, img_rgb, h, w, image_name = load_image_from_input(image_input)

    # 1b. Save original uploaded image
    original_url, original_path = save_original_image(img_bgr)

    # 2. Analyze Lighting
    lighting = analyze_lighting(img_bgr)

    # 3. Detect Objects
    detections, summary = detect_objects(img_bgr, img_rgb)

    # 4. Find Placement Zones
    zones = find_placement_zones(img_bgr, detections, lighting)

    # 5. Estimate Style
    detected_style = estimate_style(img_bgr, detections)
    chosen_style = style if style != "No preference" else detected_style

    # 6. Load Plant Database from plants-db.csv
    plants = load_plant_database()
    prefs = {"budget": budget, "maintenance": maintenance, "style": chosen_style}

    # 7. Recommendations (retrieve enough candidate plants to populate all detected zones with distinct species)
    needed_candidates = max(len(zones), 6)
    candidate_recommendations = recommend_plants(plants, lighting, zones, prefs, chosen_style, top_n=needed_candidates)

    # 8. Placement Plan (uses candidate_recommendations so each zone gets a unique plant)
    plan = placement_plan(zones, candidate_recommendations)
    for item in plan:
        b_info = get_botanical_info(
            item["plant"],
            zone_name=item["zone"],
            room_style=chosen_style,
            light_condition=lighting["condition"],
            budget=budget,
            maintenance=maintenance
        )
        item["botanical_info"] = b_info
        item["why_placed_here"] = b_info["why_placed_here"]
        item["placement_advantages"] = b_info["placement_advantages"]
        item["benefits"] = b_info["benefits"]
        item["key_benefits"] = b_info["benefits"]
        item["wiki_url"] = b_info["wiki_url"]
        item["maintenance_advice"] = b_info["care_intelligence"]
        item["care_intelligence"] = b_info["care_intelligence"]
        item["pet_safe"] = b_info["pet_safe"]
        item["pet_safety_notes"] = b_info["pet_safety_notes"]
        item["botanical_name"] = b_info["botanical_name"]
        item["design_contribution"] = b_info["design_contribution"]
        item["things_to_consider"] = b_info["things_to_consider"]

    # Display top recommendations
    top_recommendations = candidate_recommendations[:6] if len(candidate_recommendations) >= 6 else candidate_recommendations

    # 9. Create Annotated Image Output
    annotated_url = create_annotated_image(img_bgr, detections, zones, plan)

    # Prepare recommended plant data for output
    formatted_plants = []
    for r in top_recommendations:
        p = r["plant"]
        loc_zone = p['locations'][0] if isinstance(p.get('locations'), list) and p['locations'] else p.get('locations', 'Floor Corner')
        b_info = get_botanical_info(
            p["name"],
            zone_name=loc_zone,
            room_style=chosen_style,
            light_condition=lighting["condition"],
            budget=budget,
            maintenance=maintenance
        )
        formatted_plants.append({
            "name": p["name"],
            "botanical_name": b_info.get("botanical_name") or p.get("botanical_name"),
            "description": p["description"],
            "light": f"{p['light'][0]} to {p['light'][-1]} Light" if isinstance(p['light'], list) else str(p['light']),
            "water": p["watering"],
            "price": p["price"],
            "difficulty": b_info.get("difficulty", "Beginner Friendly" if p.get("beginner") else "Moderate Care"),
            "placement": f"Ideal for {loc_zone}",
            "tag": p["tag"],
            "image": p["image"],
            "match_score": f"{r['score']:.0f}%",
            "reasons": r["reasons"],
            "botanical_info": b_info,
            "benefits": b_info["benefits"],
            "key_benefits": b_info["benefits"],
            "why_this_plant": b_info["why_this_plant"],
            "why_placed_here": b_info["why_placed_here"],
            "placement_advantages": b_info["placement_advantages"],
            "design_contribution": b_info["design_contribution"],
            "things_to_consider": b_info["things_to_consider"],
            "wiki_url": b_info["wiki_url"],
            "maintenance_advice": b_info["care_intelligence"],
            "care_intelligence": b_info["care_intelligence"],
            "pet_safe": b_info["pet_safe"],
            "pet_safety_notes": b_info["pet_safety_notes"],
            "family": b_info["family"],
            "origin": b_info["origin"],
            "mature_size": b_info["mature_size"],
            "growth_rate": b_info["growth_rate"],
        })

    overall_score = int(top_recommendations[0]["score"]) if top_recommendations else 92

    output_result = {
        "success": True,
        "image_name": image_name,
        "original_image_url": original_url,
        "annotated_image_url": annotated_url,
        "transformed_image_url": None,
        "resolution": f"{w} x {h} px",
        "total_database_plants": len(plants),
        "validated_inputs": {
            "budget": budget,
            "maintenance": maintenance,
            "style": chosen_style,
        },
        "lighting": {
            "avg_brightness": round(lighting["avg"], 1),
            "condition": lighting["condition"],
            "natural_light_prob": lighting["natural"],
            "dark_pct": round(lighting["dark_pct"], 1),
            "medium_pct": round(lighting["medium_pct"], 1),
            "bright_pct": round(lighting["bright_pct"], 1),
        },
        "detected_objects": summary,
        "detected_style": detected_style,
        "scores": {
            "overall_compatibility": f"{overall_score}%",
            "light_assessment": f"{lighting['condition']} Light ({lighting['natural']} Natural Light Probability)",
            "space_utilization": f"{len(zones)} Placement Zones Identified",
            "air_purification_index": "4.8/5"
        },
        "recommended_plants": formatted_plants,
        "placement_plan": plan,
        "style_guide": {
            "title": f"{chosen_style} Interior Layout Guide",
            "planters": "Matte ceramic, terracotta, or woven seagrass planters." if chosen_style == "Boho" else "Sleek monochromatic concrete & dark ceramic planters.",
            "tip": f"Arrange plants in {chosen_style.lower()} style taking advantage of identified placement zones."
        },
        "budget_estimate": {
            "Low": "₹1,200 - ₹3,500 Total room greening",
            "Medium": "₹3,500 - ₹7,500 Curated botanical arrangement",
            "High": "₹8,000+ Premium designer botanical setup"
        }.get(budget, "₹3,500 - ₹7,500"),
        "care_routine_summary": {
            "Low": "Water once every 2-3 weeks; wipe leaves monthly.",
            "Medium": "Water weekly when top inch of soil feels dry.",
            "High": "Frequent misting and weekly soil moisture check with seasonal feeding."
        }.get(maintenance, "Weekly watering check.")
    }

    # Generate dynamic, personalized "Why This Works" and "Smart Insights"
    output_result["why_this_works"] = generate_why_this_works(output_result)
    output_result["smart_insights"] = generate_smart_insights(output_result)

    return output_result



import requests


def generate_with_cloudflare_flux(
    account_id,
    access_token,
    prompt,
    image,
    width=1024,
    height=768,
):
    """
    Generate/edit an image using Cloudflare Workers AI
    FLUX.2 Klein 4B.

    Args:
        account_id: Cloudflare Account ID
        access_token: Cloudflare API token
        prompt: Text prompt
        image: Django UploadedFile object (request.FILES["image"])
        width: Output width
        height: Output height

    Returns:
        bytes: Generated image bytes
    """

    MODEL = "@cf/black-forest-labs/flux-2-klein-4b"

    url = (
        f"https://api.cloudflare.com/client/v4/"
        f"accounts/{account_id}/ai/run/{MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Make sure we're at the beginning of the uploaded file
    image.seek(0)

    # Multipart form data
    files = {
        "input_image_0": (
            image.name,
            image,
            image.content_type or "image/jpeg",
        )
    }

    data = {
        "prompt": prompt,
        "width": str(width),
        "height": str(height),
    }

    response = requests.post(
        url,
        headers=headers,
        data=data,
        files=files,
        timeout=180,
    )

    if not response.ok:
        raise RuntimeError(
            f"Cloudflare AI Error "
            f"(HTTP {response.status_code}): {response.text}"
        )

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            f"Cloudflare AI failed: {result}"
        )

    # Cloudflare returns generated image as base64
    import base64

    image_base64 = result["result"]["image"]

    return base64.b64decode(image_base64)