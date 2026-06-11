# AmsBot — Amsterdam Municipality Virtual Assistant

AmsBot is a production-quality Streamlit frontend for the Gemeente Amsterdam
chatbot. It connects to an existing **n8n RAG backend** (Pinecone + Groq
LLaMA 3.3 70B) via webhook. All AI logic lives in n8n; Streamlit only sends
the message and renders the response.

```
User → Streamlit → POST n8n webhook → RAG (Pinecone + Groq) → cited answer → Streamlit
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| uv | latest (`pip install uv` or `brew install uv`) |

---

## Quick start

```bash
# 1. Clone / navigate to the project directory
cd Amsbot

# 2. Create virtual environment with uv
uv venv

# 3. Activate it
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell

# 4. Install dependencies
uv pip install -e .

# 5. Configure environment
cp .env.example .env
# Open .env and set N8N_WEBHOOK_URL to your n8n endpoint

# 6. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `N8N_WEBHOOK_URL` | Yes | Full URL of your n8n chat webhook |
| `APP_TITLE` | No | Browser tab / header title (default: `AmsBot`) |
| `APP_SUBTITLE` | No | Header subtitle (default: `Gemeente Amsterdam · 24/7 Virtual Assistant`) |
| `REQUEST_TIMEOUT_SECONDS` | No | HTTP timeout in seconds (default: `30`) |

---

## Project structure

```
Amsbot/
├── app.py                 # Streamlit entry point
├── config.py              # Settings loaded from .env
├── services/
│   └── n8n_client.py      # Async webhook POST + response parsing
├── components/
│   ├── header.py          # Amsterdam branded header
│   ├── chat.py            # Message rendering + citation parser
│   └── sidebar.py         # Quick questions + service categories
├── assets/
│   └── style.css          # Amsterdam red custom CSS
├── .env.example           # Template — copy to .env
└── pyproject.toml         # uv project config
```

---

## n8n webhook contract

AmsBot sends a JSON POST body:

```json
{
  "chatInput": "How do I book a grofvuil pickup?",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

The response must include one of these keys (checked in order):

```json
{ "output": "..." }
{ "text":   "..." }
{ "message": "..." }
{ "answer": "..." }
```

### Citation format

To render source badges in the UI, include citation markers in the response:

```
[Source: Grofvuil Guide — amsterdam.nl/afval]
```

These are stripped from the visible text and rendered as clickable blue badges.

---

## Features

- Full-width chat interface with Amsterdam branding
- Right-aligned red user bubbles / left-aligned white bot cards
- Animated typing indicator while waiting for n8n
- Clickable citation badges (canal blue) parsed from bot responses
- EN / NL language toggle (top-right)
- Quick-question sidebar buttons that auto-send
- Collapsible service categories (10 categories)
- Clear conversation button (resets session ID)
- Styled error messages — never raw exceptions
- Timestamps on every message

---

## Branding

| Token | Value |
|-------|-------|
| Primary (Amsterdam red) | `#CC1414` |
| Background (warm off-white) | `#F5F2EC` |
| Text | `#1A1A1A` |
| Accent / citations (canal blue) | `#1B6CA8` |
| Font | Inter, system-ui, sans-serif |

---

## Contact

For questions about Amsterdam municipal services:

- Web: [amsterdam.nl](https://amsterdam.nl)
- Phone: **14 020** (Mon–Fri 08:00–18:00)
