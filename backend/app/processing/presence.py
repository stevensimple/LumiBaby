import numpy as np

def detect_presence(csi_buffer: np.ndarray, baseline_variance: float = None) -> tuple[bool, float]:
    if len(csi_buffer) == 0:
        return False, 0.0
    variance = float(np.var(csi_buffer, axis=0).mean())
    if baseline_variance is None or baseline_variance < 1e-6:
        threshold = 0.5
        detected = variance > threshold
        confidence = min(variance / (threshold * 3), 1.0) if detected else max(0.0, 1.0 - variance / threshold)
    else:
        ratio = variance / baseline_variance
        detected = ratio > 2.5
        confidence = min((ratio - 1.0) / 4.0, 0.98) if detected else max(0.0, 1.0 - ratio / 2.5)
    return detected, round(float(confidence), 3)
