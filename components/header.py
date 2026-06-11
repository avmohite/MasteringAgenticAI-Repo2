"""
Amsterdam-branded page header component.

Renders the three-crosses (✕✕✕) logo, the AmsBot title and the
Gemeente Amsterdam subtitle using the official red/off-white palette.
"""

from __future__ import annotations

import streamlit as st

from config import settings


def render_header() -> None:
    """Inject the AmsBot branded header into the Streamlit page."""

    st.markdown(
        f"""
        <div class="ams-header">
            <div class="ams-header-logo">
                <span class="ams-crosses">✕✕✕</span>
            </div>
            <div class="ams-header-text">
                <h1 class="ams-title">{settings.app_title}</h1>
                <p class="ams-subtitle">{settings.app_subtitle}</p>
            </div>
            <div class="ams-header-badge">
                <span class="ams-badge">BETA</span>
            </div>
        </div>
        <hr class="ams-divider" />
        """,
        unsafe_allow_html=True,
    )
