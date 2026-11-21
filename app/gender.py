import numpy as np
import librosa

FEMALE_THRESHOLD_HZ = 165.0


def detect_gender(wav_path, start: float, end: float) -> str:
    """Pitch (F0) se male/female guess. Return 'male' ya 'female'."""
    try:
        y, sr = librosa.load(str(wav_path), sr=16000, offset=start, duration=max(end - start, 0.5))
        f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr)
        f0 = f0[~np.isnan(f0)]
        if len(f0) < 5:
            return "male"
        return "female" if float(np.median(f0)) > FEMALE_THRESHOLD_HZ else "male"
    except Exception:
        return "male"
