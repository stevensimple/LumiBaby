import numpy as np

# Thresholds tuned for baby monitoring (lower sensitivity)
THRESHOLDS = {"light": 0.06, "agitated": 0.25, "very_agitated": 0.8}

def detect_movement(csi_buffer: np.ndarray) -> tuple[str, float, float]:
    """Frame-to-frame energy → baby movement level."""
    if len(csi_buffer) < 2:
        return "calm", 0.0, 0.5
    diffs = np.diff(csi_buffer, axis=0)
    energy = float(np.sqrt(np.mean(diffs**2)))
    if energy < THRESHOLDS["light"]:
        return "calm", energy, round(min(1.0 - energy / THRESHOLDS["light"], 0.98), 3)
    elif energy < THRESHOLDS["agitated"]:
        return "light", energy, 0.75
    elif energy < THRESHOLDS["very_agitated"]:
        return "agitated", energy, 0.82
    else:
        return "very_agitated", energy, round(min(energy / 1.5, 0.95), 3)
