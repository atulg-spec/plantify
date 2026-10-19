
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from PIL import Image, UnidentifiedImageError


# -------------------- CONFIGURATION --------------------

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "image4.png"
OUTPUT_PATH = BASE_DIR / "plantify_output.json"
CACHE_DIR = BASE_DIR / ".plantify_cache"

ACCOUNT_ID = "ca6c0ef3ff8cad6eb02c315bcde7d569"
API_TOKEN = "cfut_TxJgn47WCGYYZKONdWVJtgMbwwKsVieV22TJP5pa12bbc24c"

VISION_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct"
TEXT_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"

API_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/"
)

MAX_IMAGE_SIDE = 1280
TIMEOUT = (15, 180)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

CACHE_DIR.mkdir(exist_ok=True)


# -------------------- CLOUDFLARE API --------------------

def run_model(
    model: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Run a Cloudflare Workers AI model."""

    response = requests.post(
        API_URL + model,
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT,
    )

    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError("Cloudflare returned a non-JSON response.")

    if not response.ok or not data.get("success", False):
        errors = data.get("errors", [])
        raise RuntimeError(
            f"Cloudflare AI request failed ({response.status_code}): "
            f"{json.dumps(errors or data, ensure_ascii=False)}"
        )

    return data.get("result", {})


def extract_text(result: Any) -> str:
    """Extract generated text from common Workers AI response shapes."""

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        for key in ("response", "generated_text", "output", "text"):
            value = result.get(key)
            if isinstance(value, str):
                return value

        choices = result.get("choices")
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, str):
                return content

    raise ValueError(
        f"Could not extract model text. Response: {str(result)[:1000]}"
    )


# -------------------- IMAGE PROCESSING --------------------

def prepare_image() -> tuple[str, str]:
    """
    Validate image4.png, create an optimized JPEG data URL,
    and return it with a hash of the original image.
    """

    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(
            f"Input image not found: {IMAGE_PATH}"
        )

    original_bytes = IMAGE_PATH.read_bytes()
    image_hash = hashlib.sha256(original_bytes).hexdigest()

    try:
        with Image.open(IMAGE_PATH) as source:
            source.verify()

        with Image.open(IMAGE_PATH) as source:
            image = source.convert("RGB")
            image.thumbnail(
                (MAX_IMAGE_SIDE, MAX_IMAGE_SIDE),
                Image.Resampling.LANCZOS,
            )

            from io import BytesIO

            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=85,
                optimize=True,
            )
            encoded = base64.b64encode(
                buffer.getvalue()
            ).decode("ascii")

    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("image4.png is not a valid readable image.") from exc

    return f"data:image/jpeg;base64,{encoded}", image_hash


# -------------------- VISION ANALYSIS --------------------

VISION_PROMPT = """
Analyze the supplied photograph for a plant recommendation system.

Return a detailed, factual description of the visible environment.

Cover:
- Likely space type and its visible characteristics.
- Visible light sources, openings, shadows and obstructions.
- Possible direct sun, partial sun, bright indirect light or shade.
- Areas that could accommodate floor pots, hanging pots, shelves or planters.
- Approximate usable space and placement constraints.
- Visible exposure to heat, wind or rain, if reasonably inferable.
- Relevant environmental uncertainties.

Separate direct visual observations from estimates.
Do not invent exact sunlight hours, temperature, humidity or dimensions.
If the photograph cannot establish a condition, mark it as unknown.

Return plain text. Do not recommend plants yet.
"""


def analyze_area(image_url: str) -> str:
    result = run_model(
        VISION_MODEL,
        {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You analyze photographs carefully. "
                        "Never present guesses as observations."
                    ),
                },
                {
                    "role": "user",
                    "content": VISION_PROMPT,
                },
            ],
            "image": image_url,
            "max_tokens": 1200,
            "temperature": 0.2,
        },
    )

    return extract_text(result)


# -------------------- PLANT RECOMMENDATIONS --------------------

def build_recommendations(area_analysis: str) -> dict[str, Any]:
    prompt = f"""
You are Plantify, a plant-selection and space-planning assistant.

Analyze this area description and produce a comprehensive, practical
plant recommendation dataset.

AREA ANALYSIS:
{area_analysis}

REQUIREMENTS:

1. Recommend every genuinely suitable plant variety worth considering.
   Do not impose an arbitrary limit such as 3, 5 or 10 plants.
   Include alternatives across relevant categories when appropriate.
   Do not add unsuitable or repetitive plants merely to lengthen the list.

2. Prioritize low maintenance, realistic survival, suitable lighting,
   beginner-friendly care, and affordability in India.

3. Never assume that a shaded space can support full-sun plants.
   Explain uncertainty when the photograph cannot establish actual
   sunlight duration or intensity.

4. Give common and scientific names. Explain each plant's suitability,
   lighting, watering, maintenance, mature size, placement, pot and
   soil needs, approximate Indian price in INR, and visual contribution.

5. Watering frequency must be approximate and conditional on soil
   moisture, weather, pot size and growing conditions. Do not prescribe
   rigid watering schedules as universally correct.

6. Include a practical arrangement, suggested quantities and spacing,
   alternatives that can be substituted for each other, and a
   low-maintenance care plan.

7. Estimate the setup budget with plant costs and optional accessories
   separated. Clearly label prices as estimates, not live quotations.

8. Do not claim that a plant is available locally or that a price is
   verified. Flag pet/child toxicity where relevant.

9. Use valid JSON only. Do not wrap it in Markdown fences.
   Include every field defined below. Use arrays for collections.
   Use null for unavailable numerical estimates and explain uncertainty.

Return this structure:

{{
  "schema_version": "1.0",
  "area_analysis": {{
    "space_type": "",
    "observations": [],
    "estimated_light_conditions": "",
    "light_confidence": "low",
    "sunlight_uncertainties": [],
    "placement_opportunities": [],
    "space_constraints": []
  }},
  "plants": [
    {{
      "id": "stable-slug",
      "common_name": "",
      "scientific_name": "",
      "category": "",
      "suitability_reason": "",
      "light_requirement": "",
      "light_match": "",
      "watering_guidance": "",
      "maintenance_level": "low",
      "mature_height_cm": null,
      "mature_spread_cm": null,
      "placement": "",
      "pot_size_cm": null,
      "soil_requirements": "",
      "estimated_price_inr": null,
      "price_notes": "",
      "visual_contribution": "",
      "toxicity_notes": "",
      "cautions": []
    }}
  ],
  "arrangement": {{
    "design_style": "",
    "design_rationale": "",
    "planting_zones": [
      {{
        "location": "",
        "plant_ids": [],
        "suggested_quantity": null,
        "spacing_guidance": "",
        "reason": ""
      }}
    ],
    "alternative_combinations": [],
    "overcrowding_warnings": []
  }},
  "budget": {{
    "currency": "INR",
    "plant_cost_estimate": null,
    "pot_and_soil_cost_estimate": null,
    "optional_accessory_cost_estimate": null,
    "total_estimated_cost": null,
    "assumptions": []
  }},
  "maintenance_plan": {{
    "routine": [],
    "watering_principles": [],
    "seasonal_care": [],
    "drainage_guidance": []
  }},
  "follow_up_questions": [],
  "limitations": []
}}

For light_confidence, use only high, medium or low.
For maintenance_level, use low, medium or high.
For light_match, describe the degree of compatibility and any
condition that must be confirmed.

Include as many appropriate plant records as necessary. The JSON
must be directly usable by a Python application.
"""

    result = run_model(
        TEXT_MODEL,
        {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You produce accurate, comprehensive plant plans "
                        "as structured JSON. Follow the requested format. "
                        "Never invent certainty."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "response_format": {
                "type": "json_object"
            },
            "max_tokens": 12000,
            "temperature": 0.2,
        },
    )

    text = extract_text(result).strip()

    # Defensive fallback for models that add surrounding whitespace.
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The model returned invalid JSON. "
            "Try again or reduce the requested output size.\n"
            f"Output excerpt: {text[:800]}"
        ) from exc

    validate_output(data)
    return data


# -------------------- VALIDATION --------------------

def validate_output(data: Any) -> None:
    """Check the basic output contract before saving."""

    if not isinstance(data, dict):
        raise ValueError("Output must be a JSON object.")

    required = {
        "schema_version",
        "area_analysis",
        "plants",
        "arrangement",
        "budget",
        "maintenance_plan",
        "follow_up_questions",
        "limitations",
    }

    missing = required - data.keys()
    if missing:
        raise ValueError(
            f"Output is missing required fields: {sorted(missing)}"
        )

    if not isinstance(data["plants"], list):
        raise ValueError("'plants' must be a JSON array.")

    for index, plant in enumerate(data["plants"]):
        if not isinstance(plant, dict):
            raise ValueError(f"Plant record {index} must be an object.")

        for key in ("common_name", "scientific_name"):
            if not plant.get(key):
                raise ValueError(
                    f"Plant record {index} is missing {key}."
                )

    ids = [p.get("id") for p in data["plants"]]
    ids = [value for value in ids if value]

    if len(ids) != len(set(ids)):
        raise ValueError("Plant IDs must be unique.")


def accept_vision_model_agreement() -> None:
    """Submit the required model agreement through Python."""

    url = API_URL + VISION_MODEL

    response = requests.post(
        url,
        headers=HEADERS,
        json={"prompt": "agree"},
        timeout=TIMEOUT,
    )

    try:
        result = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError(
            "Cloudflare returned a non-JSON agreement response."
        )

    if not response.ok or not result.get("success", False):
        raise RuntimeError(
            "Could not register the vision model agreement: "
            + json.dumps(
                result.get("errors", result),
                ensure_ascii=False,
            )
        )

    print("✅ Vision model agreement accepted by Cloudflare.")



# -------------------- MAIN PIPELINE --------------------

def main() -> None:
    if not ACCOUNT_ID or not API_TOKEN:
        raise EnvironmentError(
            "Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN "
            "before running Plantify."
        )

    print("🌿 Plantify: analyzing image4.png")

    print("Checking vision model access...")
    # accept_vision_model_agreement()



    image_url, image_hash = prepare_image()
    cache_file = CACHE_DIR / f"{image_hash}.json"

    # Reuse a previous result for an unchanged image.
    if cache_file.exists():
        print("Using cached analysis; no AI calls required.")

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        validate_output(data)

    else:
        print("1/2: Analyzing the area with the vision model...")
        area_analysis = analyze_area(image_url)

        print("2/2: Generating plant recommendations...")
        data = build_recommendations(area_analysis)

        data["metadata"] = {
            "input_image": IMAGE_PATH.name,
            "image_sha256": image_hash,
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "vision_model": VISION_MODEL,
            "recommendation_model": TEXT_MODEL,
        }

        # Save the cache only after validation succeeds.
        cache_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Write atomically to avoid leaving a partial JSON file.
    temporary_path = OUTPUT_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_path.replace(OUTPUT_PATH)

    print(f"\n✅ Saved: {OUTPUT_PATH}")
    print(f"🌱 Plant varieties returned: {len(data['plants'])}")
    print("📦 Output format: valid JSON")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, requests.RequestException) as exc:
        print(f"\n❌ Plantify failed: {exc}", file=sys.stderr)
        sys.exit(1)
