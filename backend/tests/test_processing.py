import numpy as np
import pytest
from app.processing.preprocessing import preprocess_csi
from app.processing.presence import detect_presence
from app.processing.movement import detect_movement
from app.processing.respiration import detect_respiration
from app.processing.confidence import compute_room_score

def make_csi(n_frames=60, n_sub=52, amplitude=1.0, noise=0.1):
    return np.random.normal(amplitude, noise, (n_frames, n_sub)).astype(np.float32)

def test_preprocess_even():
    raw = [1.0, 0.0, 0.0, 1.0, -1.0, 0.0]
    result = preprocess_csi(raw)
    assert len(result) == 3
    assert result[0] == pytest.approx(1.0, abs=0.01)

def test_preprocess_odd():
    raw = [1.0, 2.0, 3.0]
    result = preprocess_csi(raw)
    assert len(result) == 3

def test_presence_no_baseline_empty():
    buf = np.zeros((20, 52))
    detected, conf = detect_presence(buf)
    assert detected is False
    assert 0.0 <= conf <= 1.0

def test_presence_high_variance():
    buf = make_csi(n_frames=20, amplitude=2.0, noise=2.0)
    detected, conf = detect_presence(buf)
    assert 0.0 <= conf <= 1.0

def test_presence_with_baseline():
    baseline_var = 0.01
    buf = make_csi(n_frames=20, noise=2.0)
    detected, conf = detect_presence(buf, baseline_var)
    assert isinstance(detected, bool)
    assert 0.0 <= conf <= 1.0

def test_movement_still():
    buf = np.ones((20, 52)) + np.random.normal(0, 0.001, (20, 52))
    level, energy, conf = detect_movement(buf)
    assert level in ("none", "low")

def test_movement_active():
    buf = make_csi(n_frames=20, noise=3.0)
    level, energy, conf = detect_movement(buf)
    assert level in ("none", "low", "medium", "high")
    assert energy >= 0

def test_respiration_too_short():
    buf = make_csi(n_frames=10, n_sub=52)
    detected, bpm, conf = detect_respiration(buf)
    assert detected is False
    assert bpm is None

def test_respiration_long_buffer():
    buf = make_csi(n_frames=300, n_sub=52, noise=0.05)
    detected, bpm, conf = detect_respiration(buf)
    assert isinstance(detected, bool)
    if detected:
        assert 6.0 <= bpm <= 30.0

def test_room_score_no_presence():
    score = compute_room_score(0.1, 0.5, 0.3, False)
    assert 0.0 <= score <= 1.0

def test_room_score_presence():
    score = compute_room_score(0.9, 0.8, 0.7, True)
    assert 0.0 <= score <= 1.0
