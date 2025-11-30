"""Lightweight CLI helpers (kept for future extension)."""
from __future__ import annotations

from importlib import metadata


def version() -> str:
    try:
        return metadata.version("manifold_ultra_bot")
    except Exception:
        return "0.0.0"
