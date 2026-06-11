"""
Sidebar component: quick-question buttons, service categories, and footer.

Quick-question buttons inject the question directly into the chat flow by
setting ``st.session_state.pending_question``, which app.py picks up on the
next rerun.
"""

from __future__ import annotations

import streamlit as st


# ── Data ─────────────────────────────────────────────────────────────────────

_QUICK_QUESTIONS: list[tuple[str, str]] = [
    ("🗑️", "How do I book a grofvuil pickup?"),
    ("📋", "How much does a passport cost in Amsterdam?"),
    ("💸", "What is the afvalstoffenheffing in 2025?"),
    ("🌱", "What solar panel subsidies are available?"),
    ("🚗", "How do I get a resident parking permit?"),
    ("💰", "Am I eligible for the Stadspas?"),
]

_SERVICE_CATEGORIES: list[tuple[str, str]] = [
    ("🏠", "Housing & Living"),
    ("📄", "Permits & Licences"),
    ("🗑️", "Waste & Recycling"),
    ("🚌", "Transport & Parking"),
    ("💶", "Benefits & Financial Aid"),
    ("🌿", "Environment & Sustainability"),
    ("🎓", "Education & Childcare"),
    ("🏥", "Health & Social Care"),
    ("🏗️", "Construction & Planning"),
    ("🎉", "Events & Public Space"),
]


# ── Render ────────────────────────────────────────────────────────────────────


def render_sidebar() -> None:
    """Render the full sidebar: quick questions, categories, and footer."""
    with st.sidebar:
        _render_quick_questions()
        st.markdown("---")
        _render_service_categories()
        st.markdown("---")
        _render_language_note()
        _render_footer()


def _render_quick_questions() -> None:
    """Render clickable quick-question buttons.

    Clicking a button sets ``st.session_state.pending_question`` so that
    app.py can treat it exactly like a typed user message.
    """
    st.markdown(
        '<p class="sidebar-section-title">⚡ Quick Questions</p>',
        unsafe_allow_html=True,
    )

    for icon, question in _QUICK_QUESTIONS:
        button_label = f"{icon} {question}"
        if st.button(
            button_label,
            key=f"quick_{question[:20]}",
            use_container_width=True,
        ):
            st.session_state.pending_question = question
            st.rerun()


def _render_service_categories() -> None:
    """Render the collapsible service categories list."""
    with st.expander("📂 Service Categories", expanded=False):
        for icon, name in _SERVICE_CATEGORIES:
            st.markdown(
                f'<div class="category-item">{icon} {name}</div>',
                unsafe_allow_html=True,
            )


def _render_language_note() -> None:
    """Render a small note about language toggling."""
    lang = st.session_state.get("language", "EN")
    st.markdown(
        f'<p class="sidebar-lang-note">🌐 Current language: <strong>{lang}</strong><br>'
        "Use the toggle in the top-right to switch.</p>",
        unsafe_allow_html=True,
    )


def _render_footer() -> None:
    """Render contact details and branding footer."""
    st.markdown(
        """
        <div class="sidebar-footer">
            <p>🌐 <a href="https://amsterdam.nl" target="_blank">amsterdam.nl</a></p>
            <p>📞 <strong>14 020</strong><br>
               <span class="footer-hours">Mon–Fri 8:00–18:00</span></p>
            <p class="footer-brand">Gemeente Amsterdam</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
