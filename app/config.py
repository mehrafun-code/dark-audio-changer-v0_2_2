import os
import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)  # True jab PyInstaller .exe se chal raha ho

if FROZEN:
    BASE_DIR = Path(sys._MEIPASS)                  # bundled files (static, VERSION)
    APP_DIR = Path(sys.executable).resolve().parent  # .exe ka folder (data, .env yahan)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = BASE_DIR

DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
VERSION = (BASE_DIR / "VERSION").read_text().strip()


def _load_env(path: Path):
    """Simple .env loader (exe ke saath rakhi .env file padhta hai)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env(APP_DIR / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
VOICE_MALE = os.getenv("VOICE_MALE", "hi-IN-MadhurNeural")
VOICE_FEMALE = os.getenv("VOICE_FEMALE", "hi-IN-SwaraNeural")
TARGET_LANG = os.getenv("TARGET_LANG", "hi")
MAX_SPEEDUP = float(os.getenv("MAX_SPEEDUP", "1.5"))
