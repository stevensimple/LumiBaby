import numpy as np
import scipy.signal
from typing import Optional

def detect_signal_pattern(csi_buffer: np.ndarray, sample_rate: float = 20.0) -> dict:
    """
    Detect a rhythmic low-frequency pattern (0.1-0.5 Hz) in the CSI signal.
    This is experimental and makes NO health or medical claims.
    Returns: {rhythmic, confidence, note}
    """
    min_samples = int(sample_rate * 8)
    if len(csi_buffer) < min_samples:
        return {"rhythmic": False, "confidence": 0.0, "note": "experimental"}

    signal = np.mean(np.abs(csi_buffer[-int(sample_rate * 30):]), axis=1) if csi_buffer.ndim > 1 else csi_buffer[-int(sample_rate * 30):]
    nyq = sample_rate / 2
    low_norm = 0.1 / nyq
    high_norm = min(0.5 / nyq, 0.99)
    b, a = scipy.signal.butter(3, [low_norm, high_norm], btype="band")
    try:
        filtered = scipy.signal.filtfilt(b, a, signal)
    except Exception:
        return {"rhythmic": False, "confidence": 0.0, "note": "experimental"}

    fft_vals = np.abs(np.fft.rfft(filtered))
    freqs = np.fft.rfftfreq(len(filtered), d=1.0 / sample_rate)
    mask = (freqs >= 0.1) & (freqs <= 0.5)
    if not mask.any():
        return {"rhythmic": False, "confidence": 0.0, "note": "experimental"}

    band_fft = fft_vals[mask]
    peak_power = float(band_fft[np.argmax(band_fft)])
    noise_floor = float(np.median(fft_vals)) + 1e-9
    snr = peak_power / noise_floor
    confidence = round(min(snr / 12.0, 0.90), 3)
    rhythmic = snr > 4.0

    return {"rhythmic": rhythmic, "confidence": confidence, "note": "experimental"}
