from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXERCISES_PATH = BASE_DIR / "data" / "exercises.json"
DEFAULT_RULES_PATH = BASE_DIR / "data" / "rules.json"


def load_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def condition_matches(profile: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    for key, expected in conditions.items():
        actual = profile.get(key)

        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False

    return True


def build_policy(profile: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    policy = {
        "prefer_tags": set(),
        "exclude_tags": set(),
        "max_intensity": 3,
        "allowed_equipment": None,
        "matched_rules": [],
    }

    for rule in rules:
        conditions = rule.get("when", {})

        if not condition_matches(profile, conditions):
            continue

        policy["matched_rules"].append(rule)
        effects = rule.get("effects", {})

        policy["prefer_tags"].update(effects.get("prefer_tags", []))
        policy["exclude_tags"].update(effects.get("exclude_tags", []))

        if "max_intensity" in effects:
            policy["max_intensity"] = min(
                policy["max_intensity"],
                int(effects["max_intensity"]),
            )

        if "allowed_equipment" in effects:
            allowed = set(effects["allowed_equipment"])

            if policy["allowed_equipment"] is None:
                policy["allowed_equipment"] = allowed
            else:
                policy["allowed_equipment"] &= allowed

    return policy


def equipment_is_compatible(
    exercise: Dict[str, Any],
    profile: Dict[str, Any],
    policy: Dict[str, Any],
) -> bool:
    exercise_equipment = set(exercise.get("equipment", ["none"]))
    allowed_equipment = policy["allowed_equipment"]

    if allowed_equipment is not None:
        return bool(exercise_equipment & allowed_equipment)

    selected_equipment = profile.get("equipment", "none")

    if selected_equipment == "mixed":
        return True

    return "none" in exercise_equipment or selected_equipment in exercise_equipment


def recommend(
    profile: Dict[str, Any],
    exercises: List[Dict[str, Any]] | None = None,
    rules: List[Dict[str, Any]] | None = None,
    limit: int = 5,
) -> Dict[str, Any]:
    if exercises is None:
        exercises = load_json(DEFAULT_EXERCISES_PATH)

    if rules is None:
        rules = load_json(DEFAULT_RULES_PATH)

    policy = build_policy(profile, rules)
    recommendations = []

    for exercise in exercises:
        tags = set(exercise.get("tags", []))

        if tags & policy["exclude_tags"]:
            continue

        intensity = int(exercise.get("intensity", 1))

        if intensity > policy["max_intensity"]:
            continue

        environments = exercise.get("environment", [])

        if profile.get("environment") not in environments:
            continue

        if not equipment_is_compatible(exercise, profile, policy):
            continue

        score = 0
        reasons = []
        objective = profile.get("objective")

        if objective in exercise.get("objectives", []):
            score += 5
            reasons.append(f"Correspond à l'objectif « {objective} ».")

        preferred_tags = sorted(tags & policy["prefer_tags"])

        if preferred_tags:
            score += 2 * len(preferred_tags)
            reasons.append(
                "Caractéristiques privilégiées : "
                + ", ".join(preferred_tags)
                + "."
            )

        if "low_impact" in tags:
            score += 1

        result = dict(exercise)
        result["score"] = score
        result["reasons"] = reasons if reasons else [
            "Compatible avec les contraintes saisies."
        ]

        recommendations.append(result)

    recommendations.sort(
        key=lambda item: (
            -item["score"],
            item["intensity"],
            item["name"],
        )
    )

    return {
        "recommendations": recommendations[:limit],
        "matched_rules": policy["matched_rules"],
        "policy": {
            "prefer_tags": sorted(policy["prefer_tags"]),
            "exclude_tags": sorted(policy["exclude_tags"]),
            "max_intensity": policy["max_intensity"],
            "allowed_equipment": (
                sorted(policy["allowed_equipment"])
                if policy["allowed_equipment"] is not None
                else None
            ),
        },
    }
