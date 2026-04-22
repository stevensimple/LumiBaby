import numpy as np
from scipy.signal import medfilt

def preprocess_csi(raw_csi: list) -> np.ndarray:
    arr = np.array(raw_csi, dtype=np.float32)
    if len(arr) == 0:
        return np.array([], dtype=np.float32)
    if len(arr) % 2 == 0:
        real = arr[0::2]
        imag = arr[1::2]
        amplitude = np.sqrt(real**2 + imag**2)
    else:
        amplitude = np.abs(arr)
    if len(amplitude) >= 3:
        amplitude = medfilt(amplitude, kernel_size=3)
    return amplitude
