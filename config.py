"""Configuration de l'application : chemins, constantes métier, lecture de la clé API."""
from pathlib import Path

from dotenv import load_dotenv, set_key
import os
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Charge les variables du fichier .env s'il existe déjà (usage local uniquement — ne fait rien sinon).
load_dotenv(ENV_PATH)

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_MAX_CONCURRENT_REQUESTS = 5

DESIGNATIONS = ["alimentaire", "technologie", "service", "à vérifier manuellement"]

# Marqueurs affichés directement dans les cases du tableau (Streamlit ne permet pas de colorer
# une case précise dans un tableau modifiable — ces textes/emoji servent de repère visuel à la place).
MISSING_TEXT_MARKER = "🔴 À remplir"
MISSING_SELECT_MARKER = "🔴 À choisir"

DEPARTEMENTS = [MISSING_SELECT_MARKER, "Bar-Restaurant", "Bar à vin", "Boulangerie"]

APP_TITLE = "Automatisation factures O2 COCO"


def _get_secret(name: str) -> str | None:
    """Lit une valeur dans st.secrets (Streamlit Community Cloud) si disponible."""
    try:
        return st.secrets[name]
    except Exception:
        return None


def is_cloud_deployment() -> bool:
    """Vrai si des secrets Streamlit Cloud sont configurés (indique un déploiement hébergé)."""
    try:
        return len(st.secrets) > 0
    except Exception:
        return False


def get_api_key() -> str | None:
    return _get_secret("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or None


def get_model() -> str:
    return _get_secret("CLAUDE_MODEL") or os.environ.get("CLAUDE_MODEL") or DEFAULT_MODEL


def get_max_concurrent_requests() -> int:
    raw = _get_secret("MAX_CONCURRENT_REQUESTS") or os.environ.get("MAX_CONCURRENT_REQUESTS")
    try:
        value = int(raw) if raw else DEFAULT_MAX_CONCURRENT_REQUESTS
        return value if value > 0 else DEFAULT_MAX_CONCURRENT_REQUESTS
    except ValueError:
        return DEFAULT_MAX_CONCURRENT_REQUESTS


def save_api_key(api_key: str) -> None:
    """Enregistre la clé dans le .env local (usage local uniquement, voir setup.py)."""
    if not ENV_PATH.exists():
        ENV_PATH.write_text("", encoding="utf-8")
    set_key(str(ENV_PATH), "ANTHROPIC_API_KEY", api_key)
    os.environ["ANTHROPIC_API_KEY"] = api_key
