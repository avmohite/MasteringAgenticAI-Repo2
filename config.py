"""
Application configuration loaded from environment variables.
All secrets and tunables live here — nothing is hardcoded elsewhere.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable settings object built from environment variables."""

    n8n_webhook_url: str = field(
        default_factory=lambda: os.environ.get("N8N_WEBHOOK_URL", "")
    )
    app_title: str = field(
        default_factory=lambda: os.environ.get("APP_TITLE", "AmsBot")
    )
    app_subtitle: str = field(
        default_factory=lambda: os.environ.get(
            "APP_SUBTITLE", "Gemeente Amsterdam · 24/7 Virtual Assistant"
        )
    )
    request_timeout: int = field(
        default_factory=lambda: int(
            os.environ.get("REQUEST_TIMEOUT_SECONDS", "30")
        )
    )

    # ── Branding constants (not configurable via .env by design) ─────────────
    color_primary: str = "#CC1414"      # Amsterdam red
    color_background: str = "#F5F2EC"  # warm off-white
    color_text: str = "#1A1A1A"
    color_accent: str = "#1B6CA8"      # canal blue for citations

    def validate(self) -> None:
        """Raise ValueError when required settings are missing."""
        if not self.n8n_webhook_url:
            raise ValueError(
                "N8N_WEBHOOK_URL is not set. "
                "Copy .env.example to .env and add your webhook URL."
            )


# Module-level singleton — import this everywhere
settings = Settings()
