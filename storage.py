"""
storage.py – Local JSON persistence for TerraQuest AI.
All user data remains on-device. No data is sent to external services.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path("data")
USER_PROFILE_PATH = DATA_DIR / "profile.json"
MISSION_HISTORY_PATH = DATA_DIR / "mission_history.json"
EVIDENCE_DIR = DATA_DIR / "evidence"

# ---------------------------------------------------------------------------
# Points / level configuration (single source of truth)
# ---------------------------------------------------------------------------

POINTS_BY_DIFFICULTY = {
    "Easy": 20,
    "Moderate": 35,
    "Challenging": 50,
}

LEVELS = [
    {"level": 1, "name": "Seedling",         "required": 0},
    {"level": 2, "name": "Explorer",         "required": 100},
    {"level": 3, "name": "Nature Guardian",  "required": 300},
    {"level": 4, "name": "Earth Champion",   "required": 600},
    {"level": 5, "name": "Planet Protector", "required": 1000},
]

# ---------------------------------------------------------------------------
# Badge definitions
# ---------------------------------------------------------------------------

BADGE_DEFINITIONS = {
    "First Quest":       "Complete your very first quest",
    "Flower Finder":     "Complete 3 NatureQuest flower missions",
    "Wildlife Watcher":  "Complete 3 NatureQuest wildlife missions",
    "Nature Observer":   "Complete 10 NatureQuest missions total",
    "Recycling Rookie":  "Complete your first EcoQuest recycling mission",
    "Cleanup Hero":      "Complete 3 EcoQuest cleanup missions",
    "Compost Champion":  "Complete 3 EcoQuest composting missions",
    "Nature Guardian":   "Reach Level 3",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    EVIDENCE_DIR.mkdir(exist_ok=True)


def _load_json(path: Path, default: Any) -> Any:
    _ensure_dirs()
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return default


def _save_json(path: Path, data: Any) -> None:
    _ensure_dirs()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    shutil.move(str(tmp), str(path))


# ---------------------------------------------------------------------------
# Default profile
# ---------------------------------------------------------------------------

def _default_profile() -> dict:
    return {
        "total_points": 0,
        "completed_mission_ids": [],
        "badges": [],
        "naturequest_count": 0,
        "ecoquest_count": 0,
        "cleanup_count": 0,
        "wildlife_obs_count": 0,
        "flower_mission_count": 0,
        "wildlife_mission_count": 0,
        "recycling_mission_count": 0,
        "compost_mission_count": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_profile() -> dict:
    profile = _load_json(USER_PROFILE_PATH, None)
    if profile is None:
        profile = _default_profile()
        _save_json(USER_PROFILE_PATH, profile)
    # Back-fill any keys added in later versions
    defaults = _default_profile()
    for k, v in defaults.items():
        profile.setdefault(k, v)
    return profile


def save_profile(profile: dict) -> None:
    _save_json(USER_PROFILE_PATH, profile)


def load_mission_history() -> list:
    return _load_json(MISSION_HISTORY_PATH, [])


def save_mission_history(history: list) -> None:
    _save_json(MISSION_HISTORY_PATH, history)


# ---------------------------------------------------------------------------
# Mission completion
# ---------------------------------------------------------------------------

def award_points(profile: dict, mission: dict) -> tuple[dict, int]:
    """
    Award points for a completed mission.
    Returns (updated_profile, points_awarded).
    Points are determined by difficulty in Python – AI values are ignored.
    Duplicate missions yield 0 points.
    """
    mission_id = mission.get("id", "")
    if mission_id in profile.get("completed_mission_ids", []):
        return profile, 0

    difficulty = mission.get("difficulty", "Easy")
    points = POINTS_BY_DIFFICULTY.get(difficulty, POINTS_BY_DIFFICULTY["Easy"])

    profile["total_points"] = profile.get("total_points", 0) + points
    profile.setdefault("completed_mission_ids", []).append(mission_id)

    # Category counters
    category = mission.get("category", "")
    if category == "NatureQuest":
        profile["naturequest_count"] = profile.get("naturequest_count", 0) + 1
        tags = mission.get("tags", [])
        if "flower" in tags:
            profile["flower_mission_count"] = profile.get("flower_mission_count", 0) + 1
        if "wildlife" in tags:
            profile["wildlife_mission_count"] = profile.get("wildlife_mission_count", 0) + 1
    elif category == "EcoQuest":
        profile["ecoquest_count"] = profile.get("ecoquest_count", 0) + 1
        tags = mission.get("tags", [])
        if "cleanup" in tags:
            profile["cleanup_count"] = profile.get("cleanup_count", 0) + 1
        if "recycling" in tags:
            profile["recycling_mission_count"] = profile.get("recycling_mission_count", 0) + 1
        if "composting" in tags:
            profile["compost_mission_count"] = profile.get("compost_mission_count", 0) + 1

    profile = _check_and_award_badges(profile)
    return profile, points


def _check_and_award_badges(profile: dict) -> dict:
    earned = set(profile.get("badges", []))
    total = profile.get("total_points", 0)
    level = get_level(total)["level"]

    rules = {
        "First Quest":      (profile.get("naturequest_count", 0) + profile.get("ecoquest_count", 0)) >= 1,
        "Flower Finder":    profile.get("flower_mission_count", 0) >= 3,
        "Wildlife Watcher": profile.get("wildlife_mission_count", 0) >= 3,
        "Nature Observer":  profile.get("naturequest_count", 0) >= 10,
        "Recycling Rookie": profile.get("recycling_mission_count", 0) >= 1,
        "Cleanup Hero":     profile.get("cleanup_count", 0) >= 3,
        "Compost Champion": profile.get("compost_mission_count", 0) >= 3,
        "Nature Guardian":  level >= 3,
    }

    for badge, condition in rules.items():
        if condition and badge not in earned:
            earned.add(badge)

    profile["badges"] = sorted(earned)
    return profile


# ---------------------------------------------------------------------------
# Mission history record
# ---------------------------------------------------------------------------

def record_mission_completion(mission: dict, observation: str, evidence_filename: str | None) -> None:
    history = load_mission_history()
    history.append({
        "mission_id":        mission.get("id"),
        "title":             mission.get("title"),
        "category":          mission.get("category"),
        "difficulty":        mission.get("difficulty"),
        "points":            POINTS_BY_DIFFICULTY.get(mission.get("difficulty", "Easy"), 20),
        "observation":       observation,
        "evidence_filename": evidence_filename,
        "completed_at":      datetime.utcnow().isoformat(),
    })
    save_mission_history(history)


# ---------------------------------------------------------------------------
# Level helpers
# ---------------------------------------------------------------------------

def get_level(total_points: int) -> dict:
    current = LEVELS[0]
    for lvl in LEVELS:
        if total_points >= lvl["required"]:
            current = lvl
    return current


def get_next_level(total_points: int) -> dict | None:
    for lvl in LEVELS:
        if total_points < lvl["required"]:
            return lvl
    return None


def level_progress_pct(total_points: int) -> float:
    current = get_level(total_points)
    next_lvl = get_next_level(total_points)
    if next_lvl is None:
        return 100.0
    span = next_lvl["required"] - current["required"]
    gained = total_points - current["required"]
    return min(100.0, (gained / span) * 100) if span > 0 else 100.0


# ---------------------------------------------------------------------------
# Evidence storage
# ---------------------------------------------------------------------------

def save_evidence(uploaded_file, mission_id: str) -> str | None:
    """
    Save an uploaded Streamlit UploadedFile to the local evidence directory.
    Returns the filename or None on failure.
    """
    try:
        _ensure_dirs()
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in mission_id)[:40]
        ext = Path(uploaded_file.name).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            ext = ".jpg"
        filename = f"{safe_id}_{ts}{ext}"
        dest = EVIDENCE_DIR / filename
        dest.write_bytes(uploaded_file.getvalue())
        return filename
    except Exception:
        return None
