"""
n8n webhook client.

Sends user messages to the n8n RAG pipeline and returns the assistant
response.  All AI logic (Pinecone vector search + Groq LLaMA 3.3 70B)
runs inside n8n — this module is a thin HTTP layer only.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)


class N8nClientError(Exception):
    """Raised when the n8n webhook returns a non-2xx status."""


class N8nTimeoutError(N8nClientError):
    """Raised when the request exceeds the configured timeout."""


class N8nConnectionError(N8nClientError):
    """Raised when the n8n host is unreachable."""


async def send_message(message: str, session_id: str) -> str:
    """Send a user message to the n8n webhook and return the bot reply.

    Args:
        message: The raw user input string.
        session_id: UUID string that identifies the conversation session.
                    n8n uses this to maintain per-user memory in the RAG chain.

    Returns:
        The assistant's response text (may contain citation markers).

    Raises:
        N8nTimeoutError: Request exceeded ``settings.request_timeout`` seconds.
        N8nClientError: n8n returned a 4xx or 5xx status code.
        N8nConnectionError: Network-level failure reaching n8n.
    """
    payload: dict[str, str] = {
        "chatInput": message,
        "sessionId": session_id,
    }

    logger.debug("→ n8n payload: %s", payload)

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout)
        ) as client:
            response = await client.post(
                settings.n8n_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise N8nTimeoutError("Request to n8n timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise N8nClientError(
            f"n8n returned {exc.response.status_code}: {exc.response.text[:200]}"
        ) from exc
    except httpx.RequestError as exc:
        raise N8nConnectionError(f"Cannot reach n8n: {exc}") from exc

    data: dict = response.json()
    logger.debug("← n8n response: %s", data)

    # n8n can return the answer in several shapes depending on workflow config
    reply = (
        data.get("output")
        or data.get("text")
        or data.get("message")
        or data.get("answer")
        or str(data)
    )
    return reply.strip()


def send_message_sync(message: str, session_id: str) -> str:
    """Synchronous wrapper around ``send_message`` for Streamlit's event loop.

    Streamlit runs in a synchronous context; this helper creates a temporary
    event loop so the async HTTP call can be awaited correctly.
    """
    return asyncio.run(send_message(message, session_id))
