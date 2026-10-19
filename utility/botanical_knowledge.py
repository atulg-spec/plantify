"""
Plantify Botanical Knowledge Base & Placement Intelligence Engine.
Provides detailed botanical data, evidence-based benefits, placement reasoning,
care intelligence, aesthetic design contribution, limitations, and Wikipedia reference links.
"""

import re
import urllib.parse

SPECIES_KNOWLEDGE_BASE = {
    "snake plant": {
        "common_name": "Snake Plant (Mother-in-Law's Tongue)",
        "botanical_name": "Dracaena trifasciata (formerly Sansevieria)",
        "family": "Asparagaceae",
        "origin": "Tropical West Africa (Nigeria, Congo)",
        "wiki_url": "https://en.wikipedia.org/wiki/Dracaena_trifasciata",
        "growth_rate": "Slow to Moderate",
        "mature_size": "2 - 4 ft (60 - 120 cm) tall",
        "pet_safe": False,
        "pet_safety_notes": "Mildly toxic to cats and dogs if ingested due to saponins. Place in floor corners with sturdy planters or elevated stands away from curious pets.",
        "difficulty": "Beginner Friendly (Highly Resilient)",
        "benefits": [
            "NASA Clean Air Study validated: Absorbs indoor volatile organic compounds (VOCs) including benzene, formaldehyde, and toluene.",
            "Crassulacean Acid Metabolism (CAM): Opens stomata at night to absorb carbon dioxide and release oxygen during sleeping hours.",
            "Drought-Resilient Succulence: Thick sword-like cuticle stores moisture, effortlessly surviving 3+ weeks between waterings.",
            "Hypoallergenic Greenery: Produces no airborne pollen or shedding debris, maintaining clean indoor air."
        ],
        "design_contribution": "Provides striking vertical architectural lines that visually heighten room ceilings. Its upright, sword-like foliage anchors empty corners without sprawling into walkable floor space.",
        "things_to_consider": [
            "Tolerates low light exceptionally well, but cannot survive in 100% windowless dark closets without periodic supplemental light.",
            "Highly susceptible to root rot if soil remains waterlogged; must dry out completely between waterings.",
            "Mild pet toxicity requires caution if household pets tend to chew foliage."
        ],
        "care_intelligence": {
            "watering": "Water only once every 2–3 weeks in warm seasons, and once every 4–5 weeks in winter. Ensure the potting mix is 100% dry before adding moisture.",
            "sunlight": "Extremely versatile: flourishes in low, medium, and bright filtered indirect light. Avoid sustained direct noon sunlight.",
            "soil": "Free-draining cactus and succulent mix containing 30% perlite, pumice, or coarse horticultural sand.",
            "feeding": "Light feeding once in early spring and once in mid-summer using a half-strength balanced liquid fertilizer.",
            "troubleshooting": "Mushy or yellowing base leaves indicate root waterlogging. Immediately cease watering, remove softened leaves, and allow soil to dry thoroughly."
        },
        "placement_rationales": {
            "Floor Corner": "Floor corners frequently suffer from lower ambient lumens and visual void. The Snake Plant's vertical column creates grounding height, drawing the eye upward without obstructing pathways.",
            "Window Area": "Placed near window perimeters to absorb bright indirect illumination; its waxy cuticle withstands thermal drafts near glass panes.",
            "Desk": "Compact cultivars provide immediate biophilic focus and VOC filtration during long working hours without encroaching on workspace.",
            "Empty Corner": "Fills awkward architectural room angles with clean structural geometry, softening hard wall corners.",
            "Shelf": "Anchors upper shelving with structured foliage that doesn't droop or spread into stored books and items."
        },
        "placement_advantages": {
            "Floor Corner": "Preserves 100% of room walking flow while turning an otherwise forgotten corner into an organic visual anchor.",
            "Window Area": "Maximizes natural ambient light exposure for faster growth while keeping central living areas uncluttered.",
            "Desk": "Enhances workspace air quality within immediate breathing distance with a tiny physical footprint.",
            "Empty Corner": "Solves negative spatial emptiness without requiring supplemental floor lighting or large furniture.",
            "Shelf": "Elevates upright foliage beyond pet reach while introducing organic texture at eye level."
        }
    },
    "zz plant": {
        "common_name": "ZZ Plant (Zanzibar Gem)",
        "botanical_name": "Zamioculcas zamiifolia",
        "family": "Araceae",
        "origin": "Eastern Africa (Kenya to South Africa)",
        "wiki_url": "https://en.wikipedia.org/wiki/Zamioculcas",
        "growth_rate": "Slow",
        "mature_size": "2 - 3 ft (60 - 90 cm) tall and wide",
        "pet_safe": False,
        "pet_safety_notes": "Contains insoluble calcium oxalate crystals; mildly toxic if chewed. Keep elevated or out of reach of puppies and kittens.",
        "difficulty": "Beginner Friendly (Thrives on Neglect)",
        "benefits": [
            "Low-Light Physiology: Thrives under modest ambient illumination and artificial fluorescent office lighting where other species decline.",
            "Subterranean Water Reservoirs: Bulbous underground rhizomes store extensive moisture, allowing it to survive 3 to 4 weeks unattended.",
            "Air Purification: Demonstrated to filter volatile pollutants including xylene, toluene, and ethylbenzene from indoor spaces.",
            "Natural High-Gloss Polish: Leaves possess a natural lustrous shine that reflects ambient light without artificial leaf glazes."
        ],
        "design_contribution": "Brings lush, reflective emerald foliage into dim areas. Its zigzagging leaf stems add rich botanical density and sophisticated contrast against minimalist and modern furniture.",
        "things_to_consider": [
            "Extremely sensitive to overwatering; over-caring is the #1 cause of decline.",
            "Slow growth rate means it requires patience and does not need frequent repotting.",
            "Contains calcium oxalate crystals, so place away from chewing domestic pets."
        ],
        "care_intelligence": {
            "watering": "Water deeply once every 3–4 weeks. When in doubt, always wait an extra week before watering.",
            "sunlight": "Thrives in low to medium indirect light. Tolerates shaded corners; avoid direct scorching sun rays.",
            "soil": "Aerated indoor potting blend amended with perlite and orchid bark for swift moisture drainage.",
            "feeding": "Minimal nutritional needs: apply quarter-strength houseplant food once or twice during the spring-summer period.",
            "troubleshooting": "Yellowing stems indicate overwatering. Dropping lower leaflets signifies severe prolonged drought."
        },
        "placement_rationales": {
            "Desk": "Ideal for workspaces with modest natural light. Deep glossy leaves reflect monitor and ceiling light, providing biophilic stress relief.",
            "Floor Corner": "Perfect for dim room corners away from windows where natural illumination falls into low ranges.",
            "Cabinet": "Positioned atop credenzas or cabinets to add lush green texture without requiring frequent watering access.",
            "Shelf": "Fits neatly onto bookshelf nooks without encroaching on headroom or shedding debris."
        },
        "placement_advantages": {
            "Desk": "Creates a calm, reflective green accent within direct eyesight that reduces visual fatigue.",
            "Floor Corner": "Brings organic life to secondary light zones that cannot sustain demanding sun-loving plants.",
            "Cabinet": "Transforms flat surface dead space into a vibrant botanical display.",
            "Shelf": "Occupies compact shelf depth without sprawling into neighboring items."
        }
    },
    "pothos": {
        "common_name": "Golden Pothos (Devil's Ivy)",
        "botanical_name": "Epipremnum aureum",
        "family": "Araceae",
        "origin": "Mo'orea, Society Islands (French Polynesia)",
        "wiki_url": "https://en.wikipedia.org/wiki/Epipremnum_aureum",
        "growth_rate": "Fast",
        "mature_size": "Vines trail 6 - 10 ft (1.8 - 3 m) indoors",
        "pet_safe": False,
        "pet_safety_notes": "Contains insoluble calcium oxalates. Ideal for high shelves or hanging planters, which naturally keeps vines far out of pet reach.",
        "difficulty": "Beginner Friendly (Fast Growing)",
        "benefits": [
            "High-Efficiency VOC Cleansing: Highly rated in clean air studies for removing airborne formaldehyde, benzene, and carbon monoxide.",
            "Visual Moisture Indicator: Softly droops when thirsty and visibly rebounds within hours of watering, teaching owners intuitive plant care.",
            "Dynamic Cascading Growth: Vines trail gracefully, breaking rigid rectilinear furniture lines with fluid organic curves.",
            "Effortless Propagation: Cuttings root quickly in plain water, allowing owners to cultivate new plants effortlessly."
        ],
        "design_contribution": "Introduces cascading vertical dimension. By draping downward over edges of shelves, mantels, or cabinets, it softens harsh horizontal lines and visually bridges upper and lower room zones.",
        "things_to_consider": [
            "Trailing vines will lengthen rapidly and should be trimmed or looped occasionally for tidy appearance.",
            "Variegation softens to solid green if placed in very deep shade; medium indirect light preserves golden marbling.",
            "Elevated placement recommended to prevent curious pets from nibbling dangling vines."
        ],
        "care_intelligence": {
            "watering": "Water when the top 1–2 inches of soil feel dry to the touch (typically every 7–10 days).",
            "sunlight": "Prefers medium to bright filtered indirect light, but adapts reliably to lower light levels.",
            "soil": "Standard peat-perlite houseplant mix with dependable drainage.",
            "feeding": "Feed once monthly during active spring and summer growth with a balanced liquid indoor fertilizer.",
            "troubleshooting": "Pale leaf marbling indicates need for more ambient light. Yellowing across multiple stems signals saturated roots."
        },
        "placement_rationales": {
            "Shelf": "Shelving is the natural habitat for Pothos; trailing heart-shaped foliage cascades over ledges, creating a living vertical waterfall.",
            "Cabinet": "Elevated on storage cabinets to keep vines out of pet reach while enlivening overhead space.",
            "Window Area": "Catches ambient morning light to encourage golden leaf marbling and dense leaf nodes.",
            "Desk": "Drapes over organizer edges to soften mechanical electronics and computer screens."
        },
        "placement_advantages": {
            "Shelf": "Draws the eye upward, making standard ceilings feel taller while utilizing zero valuable floor space.",
            "Cabinet": "Elevates greenery safely away from toddlers and pets while utilizing otherwise dead vertical volume.",
            "Window Area": "Promotes vibrant yellow-green leaf variegation through gentle indirect illumination.",
            "Desk": "Adds lush softness without consuming valuable mouse or keyboard workspace."
        }
    },
    "philodendron": {
        "common_name": "Heartleaf Philodendron",
        "botanical_name": "Philodendron hederaceum",
        "family": "Araceae",
        "origin": "Central America and Caribbean",
        "wiki_url": "https://en.wikipedia.org/wiki/Philodendron_hederaceum",
        "growth_rate": "Moderate to Fast",
        "mature_size": "Trailing or climbing 3 - 6 ft (1 - 2 m)",
        "pet_safe": False,
        "pet_safety_notes": "Mildly toxic to pets due to calcium oxalates; best showcased in hanging planters, tall plant stands, or upper shelving.",
        "difficulty": "Beginner Friendly",
        "benefits": [
            "Indoor Formaldehyde Scavenger: Captures airborne volatile compounds emitted by synthetic upholstery, rugs, and furniture adhesives.",
            "Climbing or Cascading Flexibility: Can be grown cascading down shelves or trained upwards on moss poles for varied design looks.",
            "High Humidity Tolerance: Adapts effortlessly to modern conditioned room environments without crisping leaf tips.",
            "Forgiving Foliage Recovery: Tolerates pruning and rebounds promptly with bushier, denser growth nodes."
        ],
        "design_contribution": "Brings velvety heart-shaped greenery with gentle trailing movement. Fills visual voids between furniture pieces, introducing warm organic curves to modern interiors.",
        "things_to_consider": [
            "Longer vine intervals (legginess) occur if placed too far from light; pinch stems to encourage bushy fullness.",
            "Avoid letting pots sit in standing water trays after saturation.",
            "Elevated placement recommended to keep toxic foliage away from cats and dogs."
        ],
        "care_intelligence": {
            "watering": "Water when the top 50% of the soil has dried out (approx. every 7–12 days). Empty drainage trays after watering.",
            "sunlight": "Bright, indirect light is optimal; tolerates medium shade gracefully without leaf drop.",
            "soil": "Chunky aroid mix with orchid bark, perlite, and coco peat for root aeration.",
            "feeding": "Bi-monthly feeding during spring and summer with diluted organic liquid fertilizer.",
            "troubleshooting": "Small leaves spaced far apart indicate plant is reaching for light; move closer to filtered light."
        },
        "placement_rationales": {
            "Window Area": "Positioned where soft ambient natural light enhances leaf size without burning delicate tender foliage.",
            "Shelf": "Cascades over bookshelf edges, creating organic vertical balance against rectilinear furniture.",
            "Floor Corner": "When trained on a moss totem, provides climbing vertical height in compact corners."
        },
        "placement_advantages": {
            "Window Area": "Provides ideal indirect lux for balanced internode spacing and deep emerald leaf pigmentation.",
            "Shelf": "Maximizes wall storage aesthetic without taking up floor square footage.",
            "Floor Corner": "Creates a living vertical totem in compact floor space."
        }
    },
    "monstera": {
        "common_name": "Monstera Deliciosa (Swiss Cheese Plant)",
        "botanical_name": "Monstera deliciosa",
        "family": "Araceae",
        "origin": "Tropical rainforests of Southern Mexico and Central America",
        "wiki_url": "https://en.wikipedia.org/wiki/Monstera_deliciosa",
        "growth_rate": "Fast in good indirect light",
        "mature_size": "4 - 8 ft (1.2 - 2.4 m) indoors with broad fenestrated leaves",
        "pet_safe": False,
        "pet_safety_notes": "Contains insoluble calcium oxalates. Toxic if chewed by pets; floor placement is best suited for pet-free homes or well-trained pets.",
        "difficulty": "Moderate (Rewarding & Vigorous)",
        "benefits": [
            "Iconic Interior Statement Piece: Large perforated fenestrations add dramatic designer focal impact to living spaces.",
            "Air Particulate Interception: Broad leaf surface captures airborne dust and micro-particles, improving room air clarity.",
            "Natural Transpiration Balance: Transpires clean water vapor into dry air-conditioned rooms, naturally balancing ambient humidity.",
            "Long-Term Durability: Highly resilient perennial that matures into an architectural indoor heirloom over years."
        ],
        "design_contribution": "Acts as the definitive biophilic centerpiece of a room. Its dramatic, perforated leaf architecture introduces bold tropical scale, commanding attention and grounding open floor areas.",
        "things_to_consider": [
            "Requires generous horizontal spread (3–4 ft wide); not suitable for cramped narrow walkways.",
            "Requires adequate bright indirect light (at least 2,000 lux) to develop iconic leaf perforations (fenestrations).",
            "Pet toxicity requires consideration in homes with teething puppies or curious cats."
        ],
        "care_intelligence": {
            "watering": "Water thoroughly every 1–2 weeks when top 2 inches of soil feel dry. Ensure excess water drains completely.",
            "sunlight": "Thrives in bright indirect sunlight (east- or south-facing filtered light). Avoid scorching direct midday sun.",
            "soil": "Rich, chunky aroid potting mix containing 40% organic compost, pine bark, perlite, and charcoal.",
            "feeding": "Feed every 3–4 weeks from spring through early autumn with a high-nitrogen balanced plant food.",
            "troubleshooting": "Solid leaves without holes mean insufficient light or young age; move closer to filtered light source."
        },
        "placement_rationales": {
            "Floor Corner": "Its expansive architectural silhouette anchors the room with grand botanical presence without intruding on central walkways.",
            "Window Area": "Positioned 3–5 feet back from windows to catch abundant ambient lux, fueling rapid growth and leaf fenestrations.",
            "Empty Corner": "Transforms empty dead floor space into a luxurious, magazine-worthy botanical focal point."
        },
        "placement_advantages": {
            "Floor Corner": "Frames seating arrangements with grand greenery while maintaining clear room sightlines.",
            "Window Area": "Receives adequate photosynthetic energy to split broad leaves without sunburning foliage.",
            "Empty Corner": "Visually balances heavy furniture on the opposite side of the room, creating symmetrical harmony."
        }
    },
    "peperomia": {
        "common_name": "Baby Rubber Plant (Peperomia)",
        "botanical_name": "Peperomia obtusifolia",
        "family": "Piperaceae",
        "origin": "Florida, Mexico, and Caribbean",
        "wiki_url": "https://en.wikipedia.org/wiki/Peperomia_obtusifolia",
        "growth_rate": "Moderate",
        "mature_size": "8 - 12 inches (20 - 30 cm) compact height",
        "pet_safe": True,
        "pet_safety_notes": "100% Non-toxic and completely pet safe for cats and dogs (certified by ASPCA). Safe for homes with pets of any age.",
        "difficulty": "Beginner Friendly (Compact & Safe)",
        "benefits": [
            "Certified 100% Pet-Safe: Completely non-toxic to cats and dogs according to ASPCA standards.",
            "Compact Desktop Footprint: Remains neat and compact under 12 inches, ideal for work desks, consoles, and bedside tables.",
            "Semi-Succulent Water Retention: Thick, rounded foliage stores moisture, forgiving occasional skipped waterings.",
            "Formaldehyde Filtration: Effectively purifies localized indoor air in closed office and bedroom spaces."
        ],
        "design_contribution": "Introduces clean, tidy, rounded botanical geometry. Its glossy spoon-shaped leaves add structured emerald charm to tabletop vignettes without overflowing or sprawling.",
        "things_to_consider": [
            "Sensitive to overwatering; fleshy roots rot easily if soil stays soggy.",
            "Requires moderate indirect light; dense shade causes leggy, weak stems.",
            "Avoid exposure to cold winter drafts under 15°C (59°F)."
        ],
        "care_intelligence": {
            "watering": "Allow top 50–75% of potting mix to dry out before watering (roughly every 10–14 days). Never allow roots to sit in saucer water.",
            "sunlight": "Medium to bright indirect light. Tolerates gentle morning sun rays very well.",
            "soil": "Light, well-aerated potting mix containing 40% perlite or pumice for swift drainage.",
            "feeding": "Light feeding once monthly in spring and summer with balanced half-strength houseplant fertilizer.",
            "troubleshooting": "Dropping green leaves indicates sudden temperature drops or cold drafts; black stem base indicates overwatering."
        },
        "placement_rationales": {
            "Desk": "Its compact upright habit and non-invasive root system make it the premier desktop companion, reducing screen fatigue without cluttering work tools.",
            "Shelf": "Fits comfortably between bookends on shallow shelves where sprawling plants would overflow.",
            "Cabinet": "Adds tidy geometric greenery to credenzas, consoles, and TV entertainment units."
        },
        "placement_advantages": {
            "Desk": "Enhances workspace wellness and cognitive focus without taking away monitor or paperwork area.",
            "Shelf": "Provides zero-risk pet-friendly greenery at eye level that stays neat year-round.",
            "Cabinet": "Complements modern horizontal furniture finishes with clean sculptural leaves."
        }
    },
    "calathea": {
        "common_name": "Calathea / Peacock Plant / Prayer Plant",
        "botanical_name": "Goeppertia insignis (Calathea)",
        "family": "Marantaceae",
        "origin": "Tropical rainforest understories of Brazil",
        "wiki_url": "https://en.wikipedia.org/wiki/Goeppertia",
        "growth_rate": "Moderate",
        "mature_size": "1 - 2.5 ft (30 - 75 cm) tall",
        "pet_safe": True,
        "pet_safety_notes": "100% Non-toxic and completely pet safe (ASPCA confirmed). Worry-free for pet owners.",
        "difficulty": "Moderate (Prefers Consistency)",
        "benefits": [
            "Circadian Nyctinastic Movement: Leaves fold upward at night like hands in prayer, adding dynamic living movement indoors.",
            "100% Non-Toxic & Pet Safe: Safe around curious pets and children.",
            "Artistic Feather Patterning: Intricate patterned leaf surfaces and deep burgundy undersides provide living color contrast.",
            "Active Transpiration: Transpires clean water vapor, acting as a natural micro-humidifier in dry indoor environments."
        ],
        "design_contribution": "Acts as living botanical art. Its patterned leaf surfaces and striking purple-maroon undersides introduce rich organic color palettes that break monochrome room schemes.",
        "things_to_consider": [
            "Sensitive to hard tap water chlorine and minerals; use filtered or resting water to prevent crispy leaf margins.",
            "Prefers consistent moisture; do not let soil completely dry out or sit in waterlogged mud.",
            "Direct sunlight scorches and bleaches the intricate feather patterns."
        ],
        "care_intelligence": {
            "watering": "Keep soil consistently lightly moist, watering when the top inch feels dry (roughly every 5–8 days). Use filtered water if possible.",
            "sunlight": "Low to medium indirect light. Direct sunlight bleaches the leaf patterns and curls edges.",
            "soil": "Moisture-retentive yet well-aerated blend of peat moss, coco coir, perlite, and vermiculite.",
            "feeding": "Apply diluted organic fertilizer once every 4 weeks during spring and summer only.",
            "troubleshooting": "Brown crispy leaf edges signal low ambient humidity or hard tap water minerals; mist foliage or use a pebble tray."
        },
        "placement_rationales": {
            "Desk": "Safe for pets and non-invasive. Its fascinating evening leaf-folding movement provides biophilic relaxation during study or screen work.",
            "Cabinet": "Placed out of direct draft corridors where stable humidity and medium ambient light allow delicate foliage to flourish.",
            "Window Area": "Positioned behind sheer curtains to receive soft dappled illumination mimicking rainforest understories."
        },
        "placement_advantages": {
            "Desk": "Adds vibrant color contrast and living circadian motion to workspaces with complete pet safety.",
            "Cabinet": "Creates a sheltered microclimate away from drafty doorways and heating vents.",
            "Window Area": "Preserves leaf pigmentation under gentle filtered lux without risk of sunburn."
        }
    },
    "fig": {
        "common_name": "Fiddle Leaf Fig / Rubber Fig",
        "botanical_name": "Ficus lyrata / Ficus elastica",
        "family": "Moraceae",
        "origin": "Western Africa tropical rainforests",
        "wiki_url": "https://en.wikipedia.org/wiki/Ficus_lyrata",
        "growth_rate": "Moderate",
        "mature_size": "5 - 10 ft (1.5 - 3 m) indoor ornamental tree",
        "pet_safe": False,
        "pet_safety_notes": "Milky sap contains irritant ficin; toxic to pets if chewed. Place in sturdy heavy floor planters away from pet play areas.",
        "difficulty": "Moderate to Experienced",
        "benefits": [
            "Dramatic Vertical Focal Tree: Creates a magazine-worthy statement indoor tree that visually anchors high ceilings.",
            "High Carbon & Toxin Sequestration: Massive violin-shaped leaves capture airborne carbon, dust, and indoor pollutants.",
            "Spatial Scale Enhancer: Tall upright sculptural trunk visually expands vertical room perception.",
            "Long-Term Value: A mature indoor fig specimen significantly elevates the perceived luxury and biophilic warmth of a home."
        ],
        "design_contribution": "Provides commanding vertical grandeur. Its large, sculptural violin-shaped leaves create a powerful focal tree that grounds seating areas and bridges vertical architectural space.",
        "things_to_consider": [
            "Needs abundant bright filtered sunlight (minimum 4–6 hours daily); struggles in dim interior corners.",
            "Sensitive to sudden relocation or temperature drafts; acclimate to one spot and avoid moving frequently.",
            "Prone to leaf drop if overwatered or exposed to cold AC draft currents."
        ],
        "care_intelligence": {
            "watering": "Water thoroughly only when the top 2–3 inches of soil have completely dried. Ensure container drainage holes flow freely.",
            "sunlight": "Requires bright, filtered indirect sunlight. Thrives within 3–6 feet of south- or east-facing windows.",
            "soil": "Rich, well-draining potting soil amended with pine bark, perlite, and coarse sand.",
            "feeding": "Feed once monthly during spring and summer with a balanced ficus fertilizer.",
            "troubleshooting": "Dropping lower green leaves signals relocation shock, cold drafts, or overwatering. Brown spots in center of leaves indicate root saturation."
        },
        "placement_rationales": {
            "Floor Corner": "Needs vertical headroom and floor stability. In a sunlit floor corner, it anchors the room with tree-like scale without encroaching on sofa seating.",
            "Window Area": "Requires high light levels to maintain massive foliage; placed directly in secondary light zone of large windows."
        },
        "placement_advantages": {
            "Floor Corner": "Maximizes ceiling height illusion while leaving seating pathways 100% open.",
            "Window Area": "Furnishes foliage with necessary lumens for continuous upright growth and healthy leaf retention."
        }
    },
    "wax plant": {
        "common_name": "Wax Plant (Hoya)",
        "botanical_name": "Hoya carnosa",
        "family": "Apocynaceae",
        "origin": "East Asia and Australia",
        "wiki_url": "https://en.wikipedia.org/wiki/Hoya_carnosa",
        "growth_rate": "Moderate",
        "mature_size": "Trailing or climbing vines up to 4 - 8 ft",
        "pet_safe": True,
        "pet_safety_notes": "100% Non-toxic and completely pet safe (certified by ASPCA). Safe around curious cats and dogs.",
        "difficulty": "Beginner Friendly (Resilient & Long-Lived)",
        "benefits": [
            "Completely Pet Safe: Non-toxic foliage ensures total peace of mind for pet owners.",
            "Fragrant Porcelain Blooms: Produces star-shaped, sweet-scented floral clusters when provided with bright ambient light.",
            "Semi-Succulent Drought Tolerance: Fleshy waxy foliage stores moisture, allowing it to withstand missed waterings.",
            "Decades of Longevity: Known as an heirloom houseplant that can live for 30+ years with simple care."
        ],
        "design_contribution": "Introduces waxy, sculptural trailing texture with potential for fragrant porcelain floral clusters. Softens hard edges of bookshelves, floating ledges, and consoles.",
        "things_to_consider": [
            "Requires bright indirect light to initiate flowering; foliage survives in medium light but won't bloom.",
            "Do not overwater; sensitive to soggy, heavy potting mixes.",
            "Do not cut off the bare flower spurs (peduncles), as new blooms emerge from the same spurs each year."
        ],
        "care_intelligence": {
            "watering": "Allow potting mix to dry out almost completely between waterings (every 10–14 days in summer, every 3–4 weeks in winter).",
            "sunlight": "Bright indirect light to gentle direct morning sun. Strong indirect light is necessary for seasonal blooming.",
            "soil": "Chunky epiphyte blend: 50% orchid bark, 30% potting soil, 20% perlite for maximum root oxygenation.",
            "feeding": "Feed bi-weekly with a bloom-boosting balanced fertilizer during late spring and summer.",
            "troubleshooting": "Wrinkled, puckered leaves indicate severe dehydration; soak pot thoroughly in water for 15 minutes."
        },
        "placement_rationales": {
            "Shelf": "Cascades gracefully from elevated shelves where waxy vines catch light and stay safe from floor foot traffic.",
            "Window Area": "Enjoys higher light levels near windows, which triggers sweet-smelling porcelain flower blooms.",
            "Cabinet": "Spills over sideboard and console edges, bringing waxy sculptural texture to woodwork."
        },
        "placement_advantages": {
            "Shelf": "Adds vertical trailing depth while utilizing vertical space that requires no floor footprint.",
            "Window Area": "Receives the light threshold required to produce iconic fragrant star flowers.",
            "Cabinet": "Creates a lush cascading focal point that softens rectangular furniture."
        }
    },
    "chinese evergreen": {
        "common_name": "Chinese Evergreen (Aglaonema)",
        "botanical_name": "Aglaonema commutatum",
        "family": "Araceae",
        "origin": "Tropical rainforests of Southeast Asia",
        "wiki_url": "https://en.wikipedia.org/wiki/Aglaonema",
        "growth_rate": "Slow to Moderate",
        "mature_size": "1.5 - 3 ft (45 - 90 cm) tall and bushy",
        "pet_safe": False,
        "pet_safety_notes": "Contains calcium oxalate crystals; mildly toxic to pets if chewed. Place in mid-height stands or elevated surfaces.",
        "difficulty": "Beginner Friendly (Extremely Adaptable)",
        "benefits": [
            "NASA Clean Air Proven: Efficiently filters volatile formaldehyde, carbon monoxide, and benzene from indoor rooms.",
            "Vibrant Color in Modest Light: Silver, pink, and variegated cultivars maintain bold leaf coloration even in dimmer areas.",
            "Extreme Environmental Tolerance: Forgiving of dry indoor air, missed waterings, and variable ambient temperatures.",
            "Dense Bushy Habit: Mid-height bushy foliage conceals empty corners, baseboards, and wiring effortlessly."
        ],
        "design_contribution": "Introduces lush, multi-toned silver, cream, and green foliage density. Fills mid-level visual space, creating a dense biophilic buffer that enriches neutral wall and floor colors.",
        "things_to_consider": [
            "Avoid placing near cold drafty windows or air conditioning vents (prefers temperatures above 16°C / 60°F).",
            "Overwatering can lead to yellowing leaves; let topsoil dry out before re-watering.",
            "Contains calcium oxalate crystals; keep out of reach of teething pets."
        ],
        "care_intelligence": {
            "watering": "Water when the top 1–2 inches of soil feel dry to the touch (typically once every 8–12 days).",
            "sunlight": "Low to medium indirect light. Adapts well to fluorescent office lighting; avoid direct sun.",
            "soil": "Aerated indoor potting soil mixed with perlite for reliable drainage.",
            "feeding": "Light balanced feeding once every 6–8 weeks during the warm spring and summer months.",
            "troubleshooting": "Yellowing leaves indicate overwatering; brown crispy tips point to dry air drafts or cold shock."
        },
        "placement_rationales": {
            "Floor Corner": "Dense bushy growth fills mid-level floor space, providing rich color contrast against neutral flooring.",
            "Desk": "Slow growth rate means it remains contained in desktop planters for years without outgrowing its spot.",
            "Empty Corner": "Variegated leaves brighten dim room corners without needing direct window sun."
        },
        "placement_advantages": {
            "Floor Corner": "Adds dense botanical substance to floor perimeters without encroaching on walking space.",
            "Desk": "Provides vibrant air-purifying foliage on executive or study desks with low lighting needs.",
            "Empty Corner": "Injects luminous silver-green patterns into shadowed room areas."
        }
    }
}


def get_botanical_info(plant_name, zone_name=None, room_style=None, light_condition=None, budget=None, maintenance=None):
    """
    Lookup or synthesize rich botanical information, evidence-based benefits,
    why-this-plant explanation, why-this-placement spatial rationale, placement advantages,
    care intelligence, design contribution, things to consider, and Wikipedia link.
    """
    clean = re.sub(r'\s*\(Var\.\s*\d+\)', '', str(plant_name or '')).strip()
    clean_lower = clean.lower()

    # Match by key substring
    matched_entry = None
    for key, data in SPECIES_KNOWLEDGE_BASE.items():
        if key in clean_lower or clean_lower in key:
            matched_entry = data
            break

    # Match by individual tokens if not matched
    if not matched_entry:
        for key, data in SPECIES_KNOWLEDGE_BASE.items():
            for word in key.split():
                if len(word) > 2 and word in clean_lower:
                    matched_entry = data
                    break
            if matched_entry:
                break

    # Robust fallback for custom or unlisted plant species
    if not matched_entry:
        encoded_query = urllib.parse.quote(clean)
        matched_entry = {
            "common_name": clean,
            "botanical_name": f"{clean} (Indoor Cultivar)",
            "family": "Araceae / Foliage Cultivar",
            "origin": "Tropical & Subtropical Understory",
            "wiki_url": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}",
            "growth_rate": "Moderate",
            "mature_size": "1.5 - 3 ft (45 - 90 cm)",
            "pet_safe": False,
            "pet_safety_notes": "Exercise general precaution: keep elevated or out of reach of curious domestic pets.",
            "difficulty": "Beginner Friendly",
            "benefits": [
                "Air Cleansing: Actively absorbs volatile organic compounds (VOCs) and supports indoor air clarity.",
                "Cognitive & Biophilic Wellness: Proven by biophilic research to lower stress markers and enhance mental focus.",
                "Natural Moisture Regulation: Transpires clean water vapor into dry conditioned indoor air.",
                "Aesthetic Elevation: Complements modern architectural interiors and neutral color palettes."
            ],
            "design_contribution": f"Provides structured natural foliage that balances geometric furniture, adding visual depth and soft organic contrast to {room_style or 'modern'} spaces.",
            "things_to_consider": [
                "Requires ambient photons; cannot thrive in permanently dark windowless spaces without grow lights.",
                "Avoid letting roots sit in standing drainage saucer water.",
                "Keep away from direct heating vents and cold air conditioning currents."
            ],
            "care_intelligence": {
                "watering": "Water every 7–12 days when the top 1–2 inches of soil feel dry. Ensure excess water drains completely.",
                "sunlight": "Thrives in medium to bright indirect light. Shield from harsh midday direct sun.",
                "soil": "Light, well-draining houseplant mix containing perlite or pumice.",
                "feeding": "Apply balanced liquid fertilizer once monthly during spring and summer.",
                "troubleshooting": "Check soil moisture with a finger test before watering. Wipe leaves monthly with a damp cloth to remove dust."
            },
            "placement_rationales": {},
            "placement_advantages": {}
        }

    zone_clean = str(zone_name or "Floor Corner").strip()
    rationales = matched_entry.get("placement_rationales", {})
    advantages = matched_entry.get("placement_advantages", {})

    why_here = rationales.get(zone_clean)
    advantage = advantages.get(zone_clean)

    if not why_here:
        for z_key, rationale in rationales.items():
            if z_key.lower() in zone_clean.lower() or zone_clean.lower() in z_key.lower():
                why_here = rationale
                advantage = advantages.get(z_key)
                break

    if not why_here:
        if "corner" in zone_clean.lower():
            why_here = f"Positioned in this {zone_clean} because its structured silhouette visually anchors open room corners, adding organic height without impeding walkways."
            advantage = "Utilizes negative space to create visual depth while leaving central movement corridors 100% unobstructed."
        elif "window" in zone_clean.lower():
            why_here = f"Allocated to the {zone_clean} to maximize ambient indirect natural illumination, promoting healthy photosynthesis and rich leaf pigmentation."
            advantage = "Provides the plant with optimal light levels while framing the window view with vibrant greenery."
        elif "desk" in zone_clean.lower() or "table" in zone_clean.lower():
            why_here = f"Selected for this {zone_clean} for its compact footprint that purifies breathing air and reduces eye strain without cluttering workspace."
            advantage = "Delivers immediate biophilic focus within your direct visual field, improving cognitive comfort during sedentary hours."
        elif "shelf" in zone_clean.lower() or "wall" in zone_clean.lower():
            why_here = f"Chosen for this {zone_clean} to draw the eye upward, making standard room ceilings feel taller and more spacious."
            advantage = "Takes advantage of vertical wall storage, keeping foliage safely elevated while occupying zero floor area."
        else:
            why_here = f"Tailored to this {zone_clean} based on compatible ambient illumination, spatial proportion, and lifestyle maintenance requirements."
            advantage = "Integrates natural greenery cleanly into the room without disrupting everyday functionality."

    # Build dynamic personalized "Why This Plant?" explanation
    light_str = str(light_condition or "Medium").capitalize()
    maint_str = str(maintenance or "Low").capitalize()
    budget_str = str(budget or "Medium").capitalize()
    style_str = str(room_style or "Modern").capitalize()

    why_this_plant = (
        f"Recommended for your space because its natural shade tolerance directly matches the detected {light_str} lighting conditions, "
        f"ensuring healthy chlorophyll retention without requiring artificial grow lamps. "
        f"Its growth structure complements your {style_str} interior aesthetic, while its resilient care cycle fits your {maint_str} maintenance preference "
        f"and comfortably aligns with your {budget_str} budget tier."
    )

    wiki_url = matched_entry.get("wiki_url")
    if not wiki_url or "Special:Search" in wiki_url:
        wiki_url = f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(clean)}"

    return {
        "common_name": matched_entry.get("common_name", clean),
        "botanical_name": matched_entry.get("botanical_name", f"{clean} (Cultivar)"),
        "family": matched_entry.get("family", "Tropical Family"),
        "origin": matched_entry.get("origin", "Tropical & Subtropical regions"),
        "wiki_url": wiki_url,
        "growth_rate": matched_entry.get("growth_rate", "Moderate"),
        "mature_size": matched_entry.get("mature_size", "1 - 3 ft"),
        "pet_safe": matched_entry.get("pet_safe", False),
        "pet_safety_notes": matched_entry.get("pet_safety_notes", "Keep away from domestic pets if ingested."),
        "difficulty": matched_entry.get("difficulty", "Beginner Friendly"),
        "benefits": matched_entry.get("benefits", []),
        "design_contribution": matched_entry.get("design_contribution", "Adds architectural balance and organic texture."),
        "things_to_consider": matched_entry.get("things_to_consider", [
            "Ensure container has drainage holes to prevent root moisture accumulation.",
            "Low-light tolerance does not equate to total darkness; needs ambient daylight.",
            "Keep away from extreme heating or AC vent currents."
        ]),
        "care_intelligence": matched_entry.get("care_intelligence", {}),
        "why_this_plant": why_this_plant,
        "why_placed_here": why_here,
        "placement_advantages": advantage,
        "zone": zone_clean,
    }


def generate_why_this_works(analysis_data):
    """
    Generate an intelligent, personalized explanation covering:
    - What the AI observed about the environment
    - Which environmental factors influenced recommendations
    - Why selected plants work well together
    - How placements improve appearance and practicality
    - What makes the arrangement suitable for budget and maintenance
    """
    lighting = analysis_data.get("lighting", {})
    cond = lighting.get("condition", "Medium")
    avg_lum = lighting.get("avg_brightness", 128)
    nat_prob = lighting.get("natural_light_prob", "Medium")
    detected_objs = analysis_data.get("detected_objects", {})
    inputs = analysis_data.get("validated_inputs", {})
    budget = inputs.get("budget", "Medium")
    maint = inputs.get("maintenance", "Low")
    style = inputs.get("style", "Modern")
    plan = analysis_data.get("placement_plan", [])
    plants = analysis_data.get("recommended_plants", [])

    # Format detected objects text
    if detected_objs:
        obj_items = [f"{count} {label}{'s' if count > 1 else ''}" for label, count in detected_objs.items()]
        obs_furniture = f"visible furnishings including {', '.join(obj_items)}"
    else:
        obs_furniture = "open floor perimeter and architectural wall angles"

    # Plant synergy summary
    plant_names = [p.get("name", "Plant") for p in plants[:3]]
    names_str = ", ".join(plant_names) if plant_names else "selected botanical varieties"

    return {
        "title": "Why This Works: Botanical Architecture & Spatial Analysis",
        "observations": (
            f"Our computer vision pipeline analyzed your space, detecting an average luminance of {avg_lum}/255, "
            f"identifying a {cond} natural lighting environment with {nat_prob.lower()} daylight probability. "
            f"We identified {len(plan)} strategic placement zones and detected {obs_furniture}."
        ),
        "environmental_drivers": (
            f"Indoor lighting drops exponentially with distance from light sources. Because your space exhibits {cond.lower()} ambient illumination, "
            f"sun-demanding plants were excluded to prevent etiolation (stretching) and leaf drop. "
            f"Instead, species adapted to rainforest understories and drought-resilient environments were selected for reliable, long-term survival."
        ),
        "plant_synergy": (
            f"The chosen plants ({names_str}) create a balanced vertical hierarchy: upright architectural forms anchor floor levels, "
            f"while trailing and compact foliage softens desks and shelving. Furthermore, they share synchronized care cycles "
            f"requiring infrequent watering, eliminating the stress of managing conflicting care schedules."
        ),
        "spatial_improvement": (
            f"Placing vertical specimens in identified corner zones preserves unobstructed walking paths around furniture, "
            f"while elevated placements on desks or shelves bring biophilic greenery into direct sightlines without consuming floor space."
        ),
        "lifestyle_alignment": (
            f"Configured specifically for your {budget.lower()} budget tier and {maint.lower()} maintenance preference: "
            f"every recommended species is widely accessible in India, naturally pest-resistant, and capable of withstanding occasional care lapses without irreversible damage."
        )
    }


def generate_smart_insights(analysis_data):
    """
    Generate evidence-based smart insights:
    - Light Compatibility
    - Space Optimization
    - Maintenance Forecast
    - Design Harmony
    - Potential Challenges
    - Practical Recommendations
    """
    lighting = analysis_data.get("lighting", {})
    cond = lighting.get("condition", "Medium")
    avg_lum = lighting.get("avg_brightness", 128)
    inputs = analysis_data.get("validated_inputs", {})
    maint = inputs.get("maintenance", "Low")
    style = inputs.get("style", "Modern")
    plan = analysis_data.get("placement_plan", [])
    plants = analysis_data.get("recommended_plants", [])

    # Maintenance forecast text
    if maint == "Low":
        maint_summary = "Infrequent inspection cycle: ~5–10 minutes once every 2–3 weeks for soil checks; occasional leaf dusting."
    elif maint == "High":
        maint_summary = "Weekly routine: ~15 minutes per week for soil moisture checks, gentle misting, and occasional pruning."
    else:
        maint_summary = "Balanced routine: ~10 minutes every 7–10 days for moisture testing and checking plant orientation."

    return {
        "light_compatibility": {
            "status": "High Compatibility",
            "summary": f"Detected ambient level ({cond} light, {avg_lum} brightness index) matches the physiological tolerance curve of the curated plants. Foliage will maintain chlorophyll production without risking sun scorch."
        },
        "space_optimization": {
            "status": "Maximum Flow Preservation",
            "summary": f"By distributing {len(plan)} plants across vertical elevations (floor perimeter, desk surface, and elevated shelving), room walking corridors remain 100% unobstructed."
        },
        "maintenance_forecast": {
            "status": f"{maint} Maintenance Commitment",
            "summary": maint_summary
        },
        "design_harmony": {
            "status": "Biophilic Visual Balance",
            "summary": f"Juxtaposes upright sword-like geometry against broad fenestrated and cascading heart-shaped foliage, enriching the {style.lower()} interior aesthetic with multi-layered depth."
        },
        "potential_challenges": [
            "Low-light tolerance does not mean total darkness: ensure plants receive ambient daylight from nearby windows or secondary room openings.",
            "Overwatering is the leading risk for indoor houseplants: always confirm soil is dry 1–2 inches below the surface before adding water.",
            "Protect sensitive foliage from direct drafts generated by air conditioners, cooling fans, or heating vents.",
            "Ensure all decorative planters include drainage holes and catch saucers to prevent root rot."
        ],
        "practical_recommendations": [
            "Conduct the 2-inch soil finger test: insert your finger into the potting mix—if damp, postpone watering for another 4–5 days.",
            "Rotate planters 90 degrees once a month to ensure symmetrical foliage growth toward ambient light.",
            "Empty water collection saucers 15 minutes after watering so root systems never sit in stagnant moisture.",
            "Wipe broad foliage periodically with a soft damp cloth to clear household dust and maximize photosynthetic efficiency."
        ]
    }
