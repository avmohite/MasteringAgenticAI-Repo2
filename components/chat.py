"""
Chat message rendering and citation parsing.

Uses Streamlit's native st.chat_message() contexts.
No custom HTML wrappers — avoids raw-tag bleed-through in older Streamlit builds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

import streamlit as st


_CITATION_PATTERN = re.compile(
    r"\[Source:\s*(?P<title>[^—\]]+?)\s*—\s*(?P<url>[^\]]+?)\s*\]"
)


@dataclass
class Citation:
    """A single parsed source citation."""

    title: str
    url: str

    @property
    def full_url(self) -> str:
        if self.url.startswith("http"):
            return self.url
        return f"https://{self.url}"


def parse_citations(text: str) -> tuple[str, list[Citation]]:
    """Strip ``[Source: title — url]`` markers from text and return them separately."""
    citations: list[Citation] = []
    seen: set[str] = set()

    for m in _CITATION_PATTERN.finditer(text):
        url = m.group("url").strip()
        if url not in seen:
            citations.append(Citation(title=m.group("title").strip(), url=url))
            seen.add(url)

    return _CITATION_PATTERN.sub("", text).strip(), citations


def render_user_message(content: str, timestamp: datetime) -> None:
    """Render a user message bubble."""
    with st.chat_message("user"):
        st.markdown(content)
        st.caption(timestamp.strftime("%H:%M"))


def render_bot_message(content: str, timestamp: datetime) -> None:
    """Render the assistant reply with optional citation badges."""
    # Strip internal [ERROR] prefix so it never leaks into the UI
    display = content.removeprefix("[ERROR] ")
    clean_text, citations = parse_citations(display)

    with st.chat_message("assistant", avatar="🏛️"):
        st.markdown(clean_text)
        if citations:
            _render_citation_badges(citations)
        st.caption(timestamp.strftime("%H:%M"))


def render_error_message(error_text: str) -> None:
    """Render a styled warning — never a raw exception."""
    with st.chat_message("assistant", avatar="🏛️"):
        st.warning(error_text)


# ── Private ───────────────────────────────────────────────────────────────────


def _render_citation_badges(citations: list[Citation]) -> None:
    badge_html = " ".join(
        f'<a href="{c.full_url}" target="_blank" class="citation-badge">📄 {c.title}</a>'
        for c in citations
    )
    st.markdown(
        f'<div class="citation-row">{badge_html}</div>',
        unsafe_allow_html=True,
    )
