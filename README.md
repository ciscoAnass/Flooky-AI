# FLooky / Flooky-AI

Flooky is a **Flask** web app that fronts **Anthropic Claude** to deliver a clean chat UI with light conversation memory and a set of modular helpers for bills, contracts, financial docs, videos, and HR workflows.

> Repo: `ciscoAnass/Flooky-AI` • License: **GPL-3.0** • Live site: **flooky.space**

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Layout](#project-layout)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Run & Operate](#run--operate)
- [Modules & Responsibilities](#modules--responsibilities)
- [Routes & Templates](#routes--templates)
- [Frontend (static/)](#frontend-static)
- [Error Handling & Logging](#error-handling--logging)
- [Security Checklist](#security-checklist)
- [Deployment (Azure Web App)](#deployment-azure-web-app)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- **Claude-powered chat** with a friendly tone and short-term **conversation memory**.
- **Processor helpers** for common document/video tasks (bills, contracts, finance, video summarization) and an **HR helper** for resume/cover prompts.
- **Clean, responsive UI** (HTML/CSS/JS) with About / Donation / Contact pages.
- **Config via `.env`** + a checked-in **`.env.example`** to make onboarding safe and fast.
- **Azure-ready**: includes a working Azure Pipelines YAML example for CI/CD.

---

## Architecture

```
Browser
  │  (fetch / render)
  ▼
Flask (app.py) ──► Claude Service (claude_service.py)
  │                 (Auth headers, model selection, retries)
  │
  ├─ Conversation (conversation.py)  → short-term memory (per session/request)
  ├─ Helpers (helpers.py)            → formatting, small utilities
  └─ Domain processors
      ├─ bill_processor.py
      ├─ contract_processor.py
      ├─ financial_processor.py
      ├─ video_analyzer.py
      └─ hr_helper.py
```

- **app.py** wires HTTP routes, renders templates, and invokes modules.
- **claude_service.py** encapsulates Anthropic API calls.
- **conversation.py** is a small in-process memory utility.
- **processors** are pure Python helpers — easy to test and extend.

> An editable system diagram lives in **`Flooky.AI.drawio`**.

---

## Project Layout

```
Flooky-AI/
├─ static/                        # CSS/JS assets
├─ templates/                     # Jinja2 HTML templates
├─ .env.example                   # safe template for required env vars
├─ .gitignore
├─ app.py
├─ bill_processor.py
├─ claude_service.py
├─ config.py                      # env loading & defaults
├─ contract_processor.py
├─ conversation.py
├─ financial_processor.py
├─ Flooky.AI.drawio               # architecture diagram
├─ helpers.py
├─ hr_helper.py
├─ LICENSE                        # GPL-3.0
├─ README.md                      # (this file)
├─ requirements.txt
└─ video_analyzer.py
```

---

## Getting Started

### Prereqs
- Python **3.10+**
- An **Anthropic API key**

### Setup
```bash
git clone https://github.com/ciscoAnass/Flooky-AI
cd Flooky-AI

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# create your local env file from the example
cp .env.example .env   # (Windows: copy .env.example .env)

# open .env and set your key(s)
# ANTHROPIC_API_KEY=sk-ant-...
```

### Run (dev)
```bash
python app.py
# visit http://localhost:5000
```

> For production, run behind a WSGI server like **gunicorn** (see Deployment).

---

## Configuration

All configuration is read from environment variables (loaded by `config.py`).

| Variable | Required | Default | Notes |
|---|:---:|---|---|
| `ANTHROPIC_API_KEY` | ✅ | — | Your Claude API key |
| `CLAUDE_MODEL` | ⛔ | `claude-3-5-haiku` | Adjust to your account/limits |
| `FLASK_ENV` | ⛔ | `development` | Use `production` in prod |
| `FLASK_DEBUG` | ⛔ | `1` | `0` in prod |
| `HOST` | ⛔ | `127.0.0.1` | Host bind for dev |
| `PORT` | ⛔ | `5000` | Port for dev |
| `TIMEOUT_SECONDS` | ⛔ | `30` | HTTP timeout for Claude calls |
| `MAX_TOKENS` | ⛔ | `1024` | Model output cap |
| `TEMPERATURE` | ⛔ | `0.5` | Sampling temperature |

---

## Run & Operate

### Dev server
- `python app.py` will start Flask in debug on `HOST:PORT` from env.

### Production
```bash
pip install gunicorn
gunicorn --bind=0.0.0.0:8000 app:app
```

### Minimal Health Check
```python
@app.get("/healthz")
def health():
    return {"status": "ok"}, 200
```

---

## Modules & Responsibilities

- **claude_service.py** → API wrapper, retries, model selection.
- **conversation.py** → ephemeral memory (per session).
- **helpers.py** → shared utils.
- **bill_processor.py** → parse bills.
- **contract_processor.py** → parse contracts.
- **financial_processor.py** → summarize financials.
- **video_analyzer.py** → video/URL analysis.
- **hr_helper.py** → HR resume/cover tools.

---

## Routes & Templates

- `/` → `index.html` (chat)
- `/about` → `about.html`
- `/donation` → `donation.html`
- `/contact` → `contact.html`

Chat POST endpoint calls `claude_service.py` with `conversation.py` memory.

---

## Frontend (static/)

- `static/css/styles.css` → UI styles.
- `static/js/chat.js` → handles fetch, rendering.

---

## Error Handling & Logging

- Return JSON errors with codes.
- Hide stack traces in prod.
- Suggest structured JSON logs.

---

## Security Checklist

- `.env` is git‑ignored; `.env.example` exists.
- Add timeouts/retries, CSRF, CORS, headers, rate limiting, file validation.

---

## Deployment (Azure Web App)

Startup command:
```bash
pip install -r requirements.txt && pip install gunicorn && gunicorn --bind=0.0.0.0:8000 app:app
```

Use Azure Pipelines YAML already included in repo.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| 404 model error | Model not available | Change `CLAUDE_MODEL` |
| 429 error | Rate limit | Add retries/backoff |
| Blank page | Missing startup command | Use gunicorn startup |
| CORS errors | Wrong origin | Fix CORS allowlist |

---

## Roadmap

- Streaming responses (SSE)
- JSON logging + request IDs
- Unit tests for processors
- `/metrics` endpoint
- Redis memory backend

---

## License

GPL‑3.0 — see `LICENSE`.
