"""
missions.py – Predefined mission library for TerraQuest AI.

These missions are used in Offline-Friendly Mode when no AI provider is
configured or when the AI request fails. They are clearly labelled as
predefined and are never presented as AI-generated content.

Safety constraints are embedded at this layer and are not delegated to
the AI model.
"""

from __future__ import annotations
import uuid
from typing import Any

# ---------------------------------------------------------------------------
# Hazard exclusion list (enforced in mission templates, not only in prompts)
# ---------------------------------------------------------------------------

PROHIBITED_ITEMS = [
    "broken glass", "medical waste", "batteries", "chemicals",
    "sharp objects", "unknown substances", "needles", "syringes",
]

PROHIBITED_AREAS = [
    "roads", "drains", "restricted areas", "private property",
    "construction sites",
]

# ---------------------------------------------------------------------------
# Predefined NatureQuest missions
# ---------------------------------------------------------------------------

_NATUREQUEST_MISSIONS: list[dict[str, Any]] = [
    {
        "id": "nq-flower-detective",
        "title": "Flower Detective",
        "category": "NatureQuest",
        "description": "Observe a hibiscus or any open flower from directly above and study how its petals are arranged.",
        "task": "Find an open flower. Crouch or stand above it and photograph the petal arrangement from directly overhead.",
        "evidence": "A photograph showing the flower from above with petals clearly visible.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Stay on paths or in your garden. Do not pick, pull, or touch the flower.",
        "tags": ["flower", "nature"],
    },
    {
        "id": "nq-leaf-explorer",
        "title": "Leaf Explorer",
        "category": "NatureQuest",
        "description": "Find two different leaves and compare their shapes, edges, or visible vein patterns.",
        "task": "Collect or photograph two leaves that look visibly different. Note what makes them distinct.",
        "evidence": "A photograph of the two leaves side by side.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Pick only fallen or detached leaves. Do not strip foliage from living plants without permission.",
        "tags": ["flower", "nature"],
    },
    {
        "id": "nq-squirrel-scout",
        "title": "Squirrel Scout",
        "category": "NatureQuest",
        "description": "Observe a squirrel in its natural surroundings. Photograph it if one appears naturally.",
        "task": "Sit quietly near trees or a park area for up to five minutes. If a squirrel appears and begins climbing, photograph it from a respectful distance.",
        "evidence": "A photograph of the squirrel, or a written note if none appeared.",
        "difficulty": "Moderate",
        "duration_minutes": 15,
        "points": 35,
        "safety": "Keep a respectful distance. Do not feed, chase, or disturb the squirrel.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-butterfly-watch",
        "title": "Butterfly Watch",
        "category": "NatureQuest",
        "description": "Find a butterfly resting on a flower or leaf and observe it without disturbing it.",
        "task": "Walk slowly through a garden or park. When you spot a butterfly at rest, photograph it from at least one metre away.",
        "evidence": "A photograph of the butterfly at rest on a surface.",
        "difficulty": "Moderate",
        "duration_minutes": 15,
        "points": 35,
        "safety": "Do not touch, trap, or disturb the butterfly. Use your phone's zoom rather than approaching.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-tiny-explorer",
        "title": "Tiny Explorer",
        "category": "NatureQuest",
        "description": "Observe ants from a safe distance and photograph one carrying food if that behaviour occurs naturally.",
        "task": "Find an ant trail or nest entrance. Observe patiently for two to three minutes. Photograph an ant that is visibly carrying something.",
        "evidence": "A close-up photograph of one or more ants. Written observation if no suitable behaviour was observed.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Do not disturb the trail, poke the nest, or pick up ants. Some ants bite.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-birdwatcher",
        "title": "Birdwatcher",
        "category": "NatureQuest",
        "description": "Observe a bird's natural behaviour and photograph it from a respectful distance.",
        "task": "Stand or sit quietly outdoors. When you spot a bird, observe what it is doing for at least thirty seconds, then photograph it.",
        "evidence": "A photograph of the bird in its natural setting.",
        "difficulty": "Moderate",
        "duration_minutes": 15,
        "points": 35,
        "safety": "Stay well away from nests. Do not make loud noises or sudden movements that would flush the bird.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-spider-study",
        "title": "Spider Study",
        "category": "NatureQuest",
        "description": "Find a spider's web or a resting spider and study its structure without disturbing it.",
        "task": "Locate a spider or intact web in a corner, on a fence, or between plants. Photograph the web structure or the spider.",
        "evidence": "A photograph showing the web or spider clearly.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Do not touch the spider or destroy its web. Keep a safe distance; some spiders bite.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-bee-observer",
        "title": "Bee Observer",
        "category": "NatureQuest",
        "description": "Observe bees visiting flowers and photograph one in the act of pollinating if possible.",
        "task": "Find flowering plants with bee activity. Observe quietly for a few minutes. Photograph a bee on a flower.",
        "evidence": "A photograph of a bee on or near a flower.",
        "difficulty": "Moderate",
        "duration_minutes": 15,
        "points": 35,
        "safety": "Stay calm and still near bees. Do not swat, spray, or disturb them. Move away if you feel threatened. If you are allergic to bee stings, skip this mission.",
        "tags": ["wildlife", "nature"],
    },
    {
        "id": "nq-sunflower-study",
        "title": "Sunflower Study",
        "category": "NatureQuest",
        "description": "Examine a sunflower up close and observe the arrangement of seeds in its centre disc.",
        "task": "Find a sunflower in a garden or park. Photograph the central disc in detail.",
        "evidence": "A close-up photograph of the sunflower's centre disc.",
        "difficulty": "Easy",
        "duration_minutes": 5,
        "points": 20,
        "safety": "Do not pick or damage the flower.",
        "tags": ["flower", "nature"],
    },
    {
        "id": "nq-morning-dew",
        "title": "Morning Dew Hunter",
        "category": "NatureQuest",
        "description": "Find water droplets on leaves or grass and photograph the way they reflect or distort light.",
        "task": "Go outside in the morning and find dew or water droplets on a leaf or blade of grass. Photograph the droplets at close range.",
        "evidence": "A photograph showing the droplets clearly.",
        "difficulty": "Challenging",
        "duration_minutes": 15,
        "points": 50,
        "safety": "Watch your step on wet surfaces.",
        "tags": ["nature"],
    },
]

# ---------------------------------------------------------------------------
# Predefined EcoQuest missions
# ---------------------------------------------------------------------------

_ECOQUEST_MISSIONS: list[dict[str, Any]] = [
    {
        "id": "eq-plastic-patrol",
        "title": "Plastic Patrol",
        "category": "EcoQuest",
        "description": "Collect a small amount of non-hazardous litter from a safe, accessible outdoor area.",
        "task": "Put on gloves if available. Walk along a path, pavement, or park area. Collect any non-hazardous litter you can safely reach and dispose of it in the nearest waste bin.",
        "evidence": "A photograph of the litter collected before disposal, or a photograph of the area after cleanup.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Wear gloves. Do not touch broken glass, sharp objects, medical waste, batteries, or any unknown substance. Do not enter roads, drains, or restricted areas. If an item appears hazardous, leave it and report it to your local council.",
        "tags": ["cleanup", "eco"],
    },
    {
        "id": "eq-paper-saver",
        "title": "Paper Saver",
        "category": "EcoQuest",
        "description": "Identify clean, dry paper at home or in a nearby area that may be accepted for paper recycling.",
        "task": "Look through your waste paper. Select items that are clean and dry (no food contamination, no shiny plastic coating, no sticky tape if avoidable). Separate them into a recycling bag or bin.",
        "evidence": "A photograph of the separated paper pile.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Check your local recycling guidelines. Not all paper is accepted in every collection scheme. When in doubt, check your council's waste guidance.",
        "tags": ["recycling", "eco"],
    },
    {
        "id": "eq-compost-champion",
        "title": "Compost Champion",
        "category": "EcoQuest",
        "description": "Identify fruit and vegetable scraps at home that are suitable for composting.",
        "task": "After preparing a meal, set aside fruit and vegetable peelings, cores, or stalks. Do not include cooked food, meat, fish, dairy, or oily scraps. Place them in a compost bin or a covered container for composting.",
        "evidence": "A photograph of the raw fruit and vegetable scraps in a container.",
        "difficulty": "Easy",
        "duration_minutes": 5,
        "points": 20,
        "safety": "Raw plant matter is safe to handle. Wash hands after. Do not compost meat, fish, dairy, or cooked oily food, as these can attract pests and create odour.",
        "tags": ["composting", "eco"],
    },
    {
        "id": "eq-waste-detective",
        "title": "Waste Detective",
        "category": "EcoQuest",
        "description": "Find a discarded item in your home or a safe accessible area and determine the correct disposal category for it.",
        "task": "Pick up one discarded or unwanted item. Research its material. Decide: Is it general waste, recyclable, compostable, or suitable for reuse? Dispose of it correctly or write down your reasoning.",
        "evidence": "A photograph of the item and a short written note explaining your disposal decision.",
        "difficulty": "Moderate",
        "duration_minutes": 10,
        "points": 35,
        "safety": "Handle only clean, non-hazardous items. Do not touch sharp objects, batteries, chemicals, medical waste, or unknown substances. Check your local recycling guidance; rules vary by area.",
        "tags": ["recycling", "eco"],
    },
    {
        "id": "eq-cleanup-hero",
        "title": "Cleanup Hero",
        "category": "EcoQuest",
        "description": "Complete a short, focused cleanup in a permitted outdoor area near you.",
        "task": "Choose a permitted outdoor area (your garden, a public park, or a local footpath). Spend five to ten minutes collecting safely accessible non-hazardous litter. Dispose of it in the appropriate bins.",
        "evidence": "A photograph of the area after the cleanup, or a photograph of the litter collected.",
        "difficulty": "Challenging",
        "duration_minutes": 30,
        "points": 50,
        "safety": "Wear gloves. Do not touch broken glass, sharp objects, medical waste, batteries, or any unknown substance. Do not enter roads, drains, or restricted areas. Stay in areas where you have permission to be.",
        "tags": ["cleanup", "eco"],
    },
    {
        "id": "eq-reuse-explorer",
        "title": "Reuse Explorer",
        "category": "EcoQuest",
        "description": "Find a suitable discarded household item and propose a practical, safe way to reuse it.",
        "task": "Look around your home for an unwanted item that is still structurally sound. Think of one practical alternative use for it. Photograph the item and write a short description of your reuse idea.",
        "evidence": "A photograph of the item and a written reuse proposal.",
        "difficulty": "Easy",
        "duration_minutes": 10,
        "points": 20,
        "safety": "Choose items that are clean and undamaged. Do not reuse items that have contained chemicals, pharmaceuticals, or other hazardous materials.",
        "tags": ["recycling", "eco"],
    },
    {
        "id": "eq-water-saver",
        "title": "Water Saver",
        "category": "EcoQuest",
        "description": "Identify one practical way to reduce water use in your daily routine.",
        "task": "Think about how you currently use water at home. Choose one specific change (shorter shower, turning off the tap while brushing, reusing cooking water for plants). Try it today.",
        "evidence": "A written note or photograph describing the change you made.",
        "difficulty": "Easy",
        "duration_minutes": 5,
        "points": 20,
        "safety": "No safety concerns for this mission.",
        "tags": ["eco"],
    },
    {
        "id": "eq-energy-audit",
        "title": "Energy Audit",
        "category": "EcoQuest",
        "description": "Walk through one room at home and identify devices left on standby or lights left on unnecessarily.",
        "task": "Go through one room. Switch off any lights, chargers, or devices that are not in use. Note what you found.",
        "evidence": "A photograph of the switched-off devices or a written list of what you turned off.",
        "difficulty": "Easy",
        "duration_minutes": 5,
        "points": 20,
        "safety": "Do not touch electrical outlets or exposed wiring. Only switch off devices using their normal controls.",
        "tags": ["eco"],
    },
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_predefined_missions() -> list[dict]:
    return _NATUREQUEST_MISSIONS + _ECOQUEST_MISSIONS


def get_predefined_by_category(category: str) -> list[dict]:
    return [m for m in get_all_predefined_missions() if m["category"] == category]


def filter_missions(
    missions: list[dict],
    environment: list[str],
    flora: list[str],
    fauna: list[str],
    category_preference: str,
    difficulty: str,
    completed_ids: list[str],
    max_count: int = 3,
) -> list[dict]:
    """
    Filter and rank predefined missions based on user context.
    Always excludes already-completed missions to prevent duplicate rewards.
    """
    # Category filter
    if category_preference == "NatureQuest":
        pool = [m for m in missions if m["category"] == "NatureQuest"]
    elif category_preference == "EcoQuest":
        pool = [m for m in missions if m["category"] == "EcoQuest"]
    else:
        pool = list(missions)

    # Remove already-completed
    pool = [m for m in pool if m["id"] not in completed_ids]

    # Difficulty filter (prefer requested, fall back to all)
    preferred = [m for m in pool if m["difficulty"] == difficulty]
    pool = preferred if preferred else pool

    # Simple fauna/flora relevance scoring
    scored: list[tuple[int, dict]] = []
    for m in pool:
        score = 0
        tags = m.get("tags", [])
        title_lower = m["title"].lower()
        desc_lower = m["description"].lower()

        for f in fauna:
            f_l = f.lower()
            if f_l in title_lower or f_l in desc_lower:
                score += 2
        for f in flora:
            f_l = f.lower()
            if f_l in title_lower or f_l in desc_lower:
                score += 1

        scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:max_count]]


def validate_ai_mission(raw: dict) -> dict | None:
    """
    Validate and sanitise a mission dict returned by the AI.
    Enforce allowed values in Python, not via prompts.
    Returns a cleaned dict or None if validation fails.
    """
    from storage import POINTS_BY_DIFFICULTY  # avoid circular import at module level

    ALLOWED_CATEGORIES = {"NatureQuest", "EcoQuest"}
    ALLOWED_DIFFICULTIES = set(POINTS_BY_DIFFICULTY.keys())
    ALLOWED_DURATIONS = {5, 10, 15, 30}

    try:
        category = raw.get("category", "")
        if category not in ALLOWED_CATEGORIES:
            return None

        difficulty = raw.get("difficulty", "Easy")
        if difficulty not in ALLOWED_DIFFICULTIES:
            difficulty = "Easy"

        points = POINTS_BY_DIFFICULTY[difficulty]  # always override AI value

        duration = int(raw.get("duration_minutes", 10))
        if duration not in ALLOWED_DURATIONS:
            # Round to nearest allowed
            duration = min(ALLOWED_DURATIONS, key=lambda d: abs(d - duration))

        title = str(raw.get("title", "")).strip()[:80]
        description = str(raw.get("description", "")).strip()[:500]
        task = str(raw.get("task", "")).strip()[:500]
        evidence = str(raw.get("evidence", "")).strip()[:300]
        safety = str(raw.get("safety", "")).strip()[:400]

        if not title or not description:
            return None

        # Enforce safety constraints: reject missions containing prohibited items
        combined_text = (title + description + task).lower()
        for prohibited in PROHIBITED_ITEMS + PROHIBITED_AREAS:
            if f"handle {prohibited}" in combined_text or f"pick up {prohibited}" in combined_text:
                return None

        return {
            "id":               f"ai-{uuid.uuid4().hex[:8]}",
            "title":            title,
            "category":         category,
            "description":      description,
            "task":             task,
            "evidence":         evidence,
            "difficulty":       difficulty,
            "duration_minutes": duration,
            "points":           points,
            "safety":           safety,
            "tags":             raw.get("tags", []),
            "ai_generated":     True,
        }
    except Exception:
        return None
