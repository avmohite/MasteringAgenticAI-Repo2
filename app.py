"""
AmsBot — Amsterdam Municipality Virtual Assistant
Streamlit entry point.

Architecture:
  User → Streamlit (this file) → POST to n8n webhook
       → n8n RAG (Pinecone + Groq LLaMA 3.3 70B)
       → cited answer → Streamlit renders response

Streamlit is the frontend only; no AI/RAG logic lives here.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import TypedDict

import streamlit as st

from components.chat import (
    render_bot_message,
    render_error_message,
    render_user_message,
)
from components.header import render_header
from components.sidebar import render_sidebar
from config import settings
from services.n8n_client import (
    N8nClientError,
    N8nConnectionError,
    N8nTimeoutError,
    send_message_sync,
)


# ── Types ─────────────────────────────────────────────────────────────────────


class ChatMessage(TypedDict):
    """A single entry in the conversation history."""

    role: str           # "user" or "assistant"
    content: str
    timestamp: str      # ISO-format string for serialisation


# ── Page configuration ────────────────────────────────────────────────────────


def _configure_page() -> None:
    """Set Streamlit page metadata and inject custom CSS."""
    st.set_page_config(
        page_title=f"{settings.app_title} — Gemeente Amsterdam",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with css_path.open() as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── Session state initialisation ─────────────────────────────────────────────


def _init_session() -> None:
    """Initialise session state keys on first load."""
    if "messages" not in st.session_state:
        st.session_state.messages: list[ChatMessage] = []

    if "session_id" not in st.session_state:
        # Unique per browser tab; passed to n8n so the RAG chain maintains
        # per-user conversation memory across turns.
        st.session_state.session_id: str = str(uuid.uuid4())

    if "language" not in st.session_state:
        st.session_state.language: str = "EN"

    if "pending_question" not in st.session_state:
        # Set by sidebar quick-question buttons; consumed once on next rerun.
        st.session_state.pending_question: str | None = None


# ── Language toggle ───────────────────────────────────────────────────────────


def _render_language_toggle() -> None:
    """Render the EN/NL toggle button aligned to the top-right of the page."""
    col_spacer, col_btn = st.columns([8, 1])
    with col_btn:
        current = st.session_state.language
        next_lang = "NL" if current == "EN" else "EN"
        label = f"🌐 {next_lang}"
        if st.button(label, key="lang_toggle", help="Switch language"):
            st.session_state.language = next_lang
            st.rerun()


# ── Message history rendering ─────────────────────────────────────────────────


def _render_chat_history() -> None:
    """Render all messages in ``st.session_state.messages``."""
    for msg in st.session_state.messages:
        ts = datetime.fromisoformat(msg["timestamp"])
        if msg["role"] == "user":
            render_user_message(msg["content"], ts)
        else:
            render_bot_message(msg["content"], ts)


# ── Welcome message ───────────────────────────────────────────────────────────


def _render_welcome() -> None:
    """Show a welcome card when the conversation is empty."""
    lang = st.session_state.language
    if lang == "NL":
        greeting = (
            "Hallo! Ik ben **AmsBot**, de virtuele assistent van Gemeente Amsterdam. "
            "Ik kan u helpen met vragen over gemeentelijke diensten, vergunningen, "
            "afval, parkeren, uitkeringen en meer.\n\n"
            "Hoe kan ik u vandaag helpen?"
        )
    else:
        greeting = (
            "Hello! I'm **AmsBot**, the virtual assistant for the City of Amsterdam. "
            "I can help you with questions about municipal services, permits, "
            "waste collection, parking, benefits, and more.\n\n"
            "How can I help you today?"
        )

    welcome_msg: ChatMessage = {
        "role": "assistant",
        "content": greeting,
        "timestamp": datetime.now().isoformat(),
    }
    render_bot_message(welcome_msg["content"], datetime.now())


# ── Send a message ────────────────────────────────────────────────────────────


def _handle_user_input(user_input: str) -> None:
    """Process a user message: append to history, call n8n, append reply.

    Args:
        user_input: The message text to send.
    """
    now = datetime.now()

    # Record user message
    st.session_state.messages.append(
        ChatMessage(role="user", content=user_input, timestamp=now.isoformat())
    )
    render_user_message(user_input, now)

    # Spinner at page level — avoids a ghost assistant bubble after completion
    reply: str | None = None
    error: str | None = None

    with st.spinner("AmsBot is thinking…"):
        try:
            reply = send_message_sync(user_input, st.session_state.session_id)
        except N8nTimeoutError:
            error = "The assistant is taking longer than usual. Please try again."
        except N8nClientError:
            error = "Something went wrong. Please visit amsterdam.nl or call 14 020."
        except N8nConnectionError:
            error = "Cannot reach the assistant right now. Please try again in a moment."
        except Exception:
            error = "An unexpected error occurred. Please refresh the page or call 14 020."

    response_ts = datetime.now()

    if error:
        render_error_message(error)
        st.session_state.messages.append(
            ChatMessage(
                role="assistant",
                content=f"[ERROR] {error}",
                timestamp=response_ts.isoformat(),
            )
        )
    else:
        assert reply is not None
        st.session_state.messages.append(
            ChatMessage(
                role="assistant",
                content=reply,
                timestamp=response_ts.isoformat(),
            )
        )
        render_bot_message(reply, response_ts)


# ── Sidebar controls ──────────────────────────────────────────────────────────


def _render_sidebar_controls() -> None:
    """Add the clear-conversation button and delegate to the sidebar component."""
    with st.sidebar:
        st.markdown(
            f'<p class="sidebar-section-title">💬 {settings.app_title}</p>',
            unsafe_allow_html=True,
        )
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        st.markdown("---")

    render_sidebar()


# ── Startup validation ────────────────────────────────────────────────────────


def _check_config() -> bool:
    """Return False and show a config error if the webhook URL is missing."""
    if not settings.n8n_webhook_url:
        st.error(
            "**Configuration error:** `N8N_WEBHOOK_URL` is not set.  \n"
            "Copy `.env.example` to `.env` and add your n8n webhook URL, "
            "then restart the app.",
            icon="⚙️",
        )
        return False
    return True


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    """Application entry point."""
    _configure_page()
    _init_session()

    _render_sidebar_controls()

    # Main content area
    render_header()

    if not _check_config():
        st.stop()

    _render_language_toggle()

    # Render existing conversation or welcome screen
    if not st.session_state.messages:
        _render_welcome()
    else:
        _render_chat_history()

    # Handle quick-question from sidebar (set by sidebar button click)
    pending = st.session_state.pop("pending_question", None)
    if pending:
        _handle_user_input(pending)
        st.rerun()

    # Main chat input — Streamlit's built-in chat_input auto-scrolls to bottom
    lang = st.session_state.language
    placeholder = (
        "Stel uw vraag over gemeentelijke diensten…"
        if lang == "NL"
        else "Ask about Amsterdam municipal services…"
    )

    if user_msg := st.chat_input(placeholder):
        _handle_user_input(user_msg)


if __name__ == "__main__":
    main()
