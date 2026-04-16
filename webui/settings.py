"""Settings persistence for See-through UI."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

SETTINGS_FILE: Path = Path(__file__).resolve().parent / ".settings.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "mode": "NF4 Quantized (Recommended・VRAM ~7GB)",
    "resolution": 768,
    "inference_steps": 20,
    "seed": 42,
    "tblr_split": True,
    "cpu_offload": False,
}


def load_settings() -> Dict[str, Any]:
    """Load settings from file, return defaults if not found."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(saved)
            return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(**kwargs: Any) -> None:
    """Save settings to file."""
    current = load_settings()
    current.update(kwargs)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception:
        pass
