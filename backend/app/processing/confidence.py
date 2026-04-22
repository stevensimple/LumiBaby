def compute_activity_score(movement_level: str, presence_conf: float, presence_detected: bool, inactivity_minutes: float) -> int:
    """
    Activity score 0-100. Higher = calmer/more at rest.
    NOT a health metric — only reflects signal activity level.
    """
    if not presence_detected:
        return 0

    base = {"calm": 95, "light": 70, "agitated": 35, "very_agitated": 10}
    score = base.get(movement_level, 50)

    # Boost score when baby has been calm for a while (but cap at 99 — never claim perfection)
    if movement_level == "calm" and inactivity_minutes > 5:
        score = min(score + int(inactivity_minutes * 0.5), 99)

    # Adjust slightly by confidence
    score = int(score * (0.7 + 0.3 * presence_conf))
    return max(0, min(score, 99))
