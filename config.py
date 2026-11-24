import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

GOOGLE_ENABLED = os.getenv("GOOGLE_ENABLED", "false").lower() == "true"
USER_ID = os.getenv("USER_ID", "default")
USER_DIR = DATA_DIR / "users" / USER_ID
USER_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "jarvis.db"
APPS_FILE = ROOT / "apps.json"
GOOGLE_CLIENT_FILE = ROOT / "google_client.json"
GOOGLE_TOKEN = USER_DIR / "google_token.json"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

OWNER_NAME = os.getenv("OWNER_NAME", "Boss")
BUTLER_NAME = os.getenv("BUTLER_NAME", "Prometheus")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

LLM_MODEL = os.getenv("LLM_MODEL", "google/gemini-2.5-flash")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
STT_MODEL = os.getenv("STT_MODEL", "nova-3")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "deepgram").lower()
TTS_VOICE = os.getenv("TTS_VOICE", "")
ELEVEN_MODEL = os.getenv("ELEVEN_MODEL", "eleven_flash_v2_5")

WAKE_ENABLED = os.getenv("WAKE_ENABLED", "true").lower() == "true"
WAKE_TIMEOUT = float(os.getenv("WAKE_TIMEOUT", "60"))
WAKE_WORDS = [w.strip().lower() for w in os.getenv("WAKE_WORDS", "prometheus,promethius,prometheous,prometheos,prometeus").split(",") if w.strip()]

NUDGES_ENABLED = os.getenv("NUDGES_ENABLED", "true").lower() == "true"
NUDGE_INTERVAL = float(os.getenv("NUDGE_INTERVAL", "60"))
NUDGE_LEAD_MINUTES = int(os.getenv("NUDGE_LEAD_MINUTES", "30"))
NUDGE_COOLDOWN_HOURS = float(os.getenv("NUDGE_COOLDOWN_HOURS", "6"))
QUIET_START = int(os.getenv("QUIET_START", "22"))
QUIET_END = int(os.getenv("QUIET_END", "7"))

DEEP_MODEL = os.getenv("DEEP_MODEL", "~anthropic/claude-sonnet-latest")
DEEP_MAX_TOKENS = int(os.getenv("DEEP_MAX_TOKENS", "4000"))
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR") or str(ROOT / "workspace")).expanduser()
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
READ_DIRS = [Path(p).expanduser() for p in os.getenv("READ_DIRS", "").split(";") if p.strip()]
CODE_DIRS = [Path(p).expanduser() for p in os.getenv("CODE_DIRS", "").split(";") if p.strip()]
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "120"))
MAX_FIX_FILES = int(os.getenv("MAX_FIX_FILES", "6"))

REMINDERS_ENABLED = os.getenv("REMINDERS_ENABLED", "true").lower() == "true"
REMINDER_INTERVAL = float(os.getenv("REMINDER_INTERVAL", "15"))
DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "233").lstrip("+")

MIND_ENABLED = os.getenv("MIND_ENABLED", "true").lower() == "true"
MIND_INTERVAL = float(os.getenv("MIND_INTERVAL", "600"))
MIND_SUMMARIZE = os.getenv("MIND_SUMMARIZE", "true").lower() == "true"


def require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name} in .env")
    return value
