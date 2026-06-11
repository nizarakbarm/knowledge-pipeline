---
name: open-notebook
version: "2.0"
description: Self-hosted, open-source alternative to Google NotebookLM for AI-powered research and document analysis. Use when organizing research materials into notebooks, ingesting diverse content sources (PDFs, videos, audio, web pages, Office documents), generating AI-powered notes and summaries, creating multi-speaker podcasts from research, chatting with documents using context-aware AI, searching across materials with full-text and vector search, or running custom content transformations. Supports 16+ AI providers including OpenAI, Anthropic, Google, Ollama, Groq, and Mistral with complete data privacy through self-hosting.
license: MIT
metadata:
  version: "2.0"
  skill-author: K-Dense Inc.
  adapted-by: Nizar Akbar
  deployment: Production (OpenResty + SSL + Ansible)
  domain: <your-domain.com>
---

# Open Notebook - Production Deployment

## Overview

Open Notebook is an open-source, self-hosted alternative to Google's NotebookLM that enables researchers to organize materials, generate AI-powered insights, create podcasts, and have context-aware conversations with their documents — all while maintaining complete data privacy.

**Key advantages over NotebookLM:**
- Full REST API for programmatic access and automation
- Choice of 16+ AI providers (not locked to Google models)
- Multi-speaker podcast generation with 1-4 customizable speakers
- Complete data sovereignty through self-hosting
- Open source and fully extensible (MIT license)

**Repository:** https://github.com/lfnovo/open-notebook

## Production Architecture

```
Internet
    |
    v
┌─────────────────────────────┐
│ OpenResty (Nginx)           │  80/443 (HTTP/2, HTTP/3)
│ SSL/TLS 1.3, Let's Encrypt  │
│ Security headers, WAF         │
└─────────────┬───────────────┘
              |
    ┌─────────┴──────────┐
    |                    |
┌───┴───┐          ┌─────┴──────┐
│ 8502  │          │ 5055       │
│Next.js│          │ FastAPI    │
│(UI)   │          │ (API)      │
└───┬───┘          └─────┬──────┘
    |                    |
┌───┴────────────────────┴───┐
│ Docker Network               │
│  - Open Notebook             │
│  - SurrealDB (:8000)         │
│  - Ollama (:11434)           │
└─────────────────────────────┘
```

**Components:**
- **OpenResty**: Reverse proxy, SSL termination, security headers
- **Docker Compose**: Container orchestration
- **Ansible**: Automated deployment
- **Let's Encrypt**: SSL certificates via DNS-01 (Cloudflare)
- **UFW**: Firewall (ports 22/80/443 allowed)

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Python 3.8+ with `requests` and `python-dotenv`
- Access to production URL: `https://<your-domain.com>`
- Valid password (set during deployment)

### Python Client Setup

```bash
# Clone repository
git clone <repository-url>
cd open-notebook

# Setup virtual environment and dependencies
./setup.sh

# Activate environment
source venv/bin/activate

# Configure credentials
cp .env.example .env
# Edit .env:
# OPEN_NOTEBOOK_URL=https://<your-domain.com>
# OPEN_NOTEBOOK_PASSWORD=your-secure-password
```

### Available Scripts

All scripts are in `scripts/` directory:

```bash
# Notebook management
python scripts/notebook_management.py

# Source ingestion (URLs, files, text)
python scripts/source_ingestion.py

# Chat interaction
python scripts/chat_interaction.py

# Complete workflow example
python scripts/workflow_example.py
```

## Authentication

**All API requests require authentication.** Set credentials via environment or `.env` file.

### Environment Variables

```bash
export OPEN_NOTEBOOK_URL="https://<your-domain.com>"
export OPEN_NOTEBOOK_PASSWORD="your-secure-password"
```

### Using Config Module

```python
from scripts.config import get_config

config = get_config()
# config['base_url']   # https://<your-domain.com>
# config['api_url']    # https://<your-domain.com>/api
# config['password']   # your-password
```

### Manual Request with Auth

```python
import requests

headers = {
    'Authorization': 'Bearer your-password',
    'Content-Type': 'application/json',
}

response = requests.get(
    'https://<your-domain.com>/api/notebooks',
    headers=headers
)
```

## Core Features

### Notebooks

```python
from scripts.notebook_management import create_notebook, list_notebooks

# Create
nb = create_notebook(
    name="Cancer Genomics Research",
    description="Literature review on tumor mutational burden"
)

# List all
notebooks = list_notebooks()
```

### Sources

```python
from scripts.source_ingestion import (
    add_url_source,
    add_text_source,
    upload_file_source,
    wait_for_processing
)

# Add URL
source = add_url_source(
    notebook_id="your-notebook-id",
    url="https://arxiv.org/abs/2301.00001"
)

# Add text
source = add_text_source(
    notebook_id="your-notebook-id",
    title="Research Notes",
    text="Your text content here..."
)

# Upload file
source = upload_file_source(
    notebook_id="your-notebook-id",
    file_path="paper.pdf"
)

# Wait for processing
wait_for_processing(source["id"])
```

### Chat

```python
from scripts.chat_interaction import (
    create_chat_session,
    send_chat_message,
    search_knowledge_base,
    ask_question
)

# Create session
session = create_chat_session(
    notebook_id="your-notebook-id",
    title="Research Discussion"
)

# Send message
result = send_chat_message(
    session["id"],
    "What are the key biomarkers?"
)

# Search
results = search_knowledge_base(
    "checkpoint inhibitor efficacy"
)

# Ask standalone question
answer = ask_question(
    "What is the role of PD-L1 in cancer immunotherapy?"
)
```

### Notes

Create and manage notes within notebooks.

```python
from scripts.notebook_management import create_note, list_notes, get_note

# Create a note
note = create_note(
    notebook_id="your-notebook-id",
    content="Key findings from the CRISPR study...",
    title="CRISPR Summary",
    note_type="human"
)

# List all notes
notes = list_notes(notebook_id="your-notebook-id")

# Get a specific note
note = get_note(note_id="your-note-id")
```

### Source Insights

Generate AI insights from sources using transformations.

```python
from scripts.source_ingestion import (
    get_source_insights,
    create_source_insight,
    list_transformations
)

# List available transformations
transformations = list_transformations()

# Generate insight
insight = create_source_insight(
    source_id="your-source-id",
    transformation_id="your-transformation-id",
    model_id="your-model-id"
)

# Get all insights for a source
insights = get_source_insights(source_id="your-source-id")
```

### Transformations

Create and execute custom AI transformations.

```python
from scripts.source_ingestion import create_transformation, execute_transformation

# Create transformation
transformation = create_transformation(
    name="extract_methods",
    title="Extract Methods",
    description="Extract methodology from research papers",
    prompt="Extract the methods section from this text:"
)

# Execute on text
result = execute_transformation(
    transformation_id=transformation["id"],
    input_text="Your research text here...",
    model_id="your-model-id"
)
print(result["output"])
```

### Save Insight as Note

```python
from scripts.source_ingestion import save_insight_as_note

# Save an insight as a note in a notebook
note = save_insight_as_note(
    insight_id="your-insight-id",
    notebook_id="your-notebook-id"
)
```

## AI Provider Configuration

Configure providers via the web UI or API:

```python
import requests

BASE_URL = "https://<your-domain.com>/api"
headers = {
    'Authorization': 'Bearer your-password',
    'Content-Type': 'application/json',
}

# Add OpenAI credential
response = requests.post(
    f"{BASE_URL}/credentials",
    json={
        "provider": "openai",
        "name": "My OpenAI Key",
        "api_key": "sk-..."
    },
    headers=headers
)
credential = response.json()

# Discover models
response = requests.post(
    f"{BASE_URL}/credentials/{credential['id']}/discover",
    headers=headers
)
models = response.json()

# Register models
requests.post(
    f"{BASE_URL}/credentials/{credential['id']}/register-models",
    json={"model_ids": [m["id"] for m in models["models"]]},
    headers=headers
)
```

## Supported AI Providers

| Provider | LLM | Embedding | Speech-to-Text | Text-to-Speech |
|----------|-----|-----------|----------------|----------------|
| OpenAI | Yes | Yes | Yes | Yes |
| Anthropic | Yes | No | No | No |
| Google GenAI | Yes | Yes | No | Yes |
| Vertex AI | Yes | Yes | No | Yes |
| Ollama | Yes | Yes | No | No |
| Groq | Yes | No | Yes | No |
| Mistral | Yes | Yes | No | No |
| Azure OpenAI | Yes | Yes | No | No |
| DeepSeek | Yes | No | No | No |
| xAI | Yes | No | No | No |
| OpenRouter | Yes | No | No | No |
| ElevenLabs | No | No | Yes | Yes |
| Perplexity | Yes | No | No | No |
| Voyage | No | Yes | No | No |

## Ollama Integration

Our deployment includes Ollama with `nomic-embed-text` for local embeddings:

```python
# In Open Notebook UI:
# Settings > API Keys > Add Ollama
# Base URL: http://ollama:11434
# Model: nomic-embed-text
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_NOTEBOOK_URL` | **Required.** Production URL | `https://<your-domain.com>` |
| `OPEN_NOTEBOOK_PASSWORD` | **Required.** Authentication password | None |
| `OPEN_NOTEBOOK_INSECURE` | Disable SSL verification (dev only) | `false` |

## API Endpoints

Base URL: `https://<your-domain.com>/api`

Interactive docs: `https://<your-domain.com>/api/docs`

Core endpoints:
- `/api/notebooks` - Notebook CRUD
- `/api/sources` - Source ingestion
- `/api/notes` - Note management
- `/api/chat/sessions` - Chat sessions
- `/api/chat/execute` - Chat messages
- `/api/search` - Full-text and vector search
- `/api/podcasts` - Podcast generation
- `/api/transformations` - Content transformations
- `/api/models` - AI model configuration
- `/api/credentials` - Provider credentials

## Architecture

- **Backend:** Python with FastAPI (port 5055, internal)
- **Frontend:** Next.js with React (port 8502, internal)
- **Database:** SurrealDB (port 8000, internal)
- **AI Local:** Ollama (port 11434, internal)
- **Proxy:** OpenResty (ports 80/443, public)
- **SSL:** Let's Encrypt via DNS-01 (Cloudflare)
- **Deployment:** Ansible + Docker Compose
- **Features:** Notebooks, Sources, Notes, Insights, Transformations, Chat

## Security Features

- SSL/TLS 1.3 with HTTP/2 and HTTP/3 (QUIC)
- Password authentication (Bearer token)
- API key encryption with Fernet
- UFW firewall blocking direct Docker ports
- Security headers (HSTS, CSP, X-Frame-Options)
- Auto-renewing SSL certificates
- Docker containers bound to localhost only

## Important Notes

- **Authentication required** for all API access
- **SSL enforced** in production (don't set `OPEN_NOTEBOOK_INSECURE`)
- **Password required** for UI access
- **Encryption key** must be kept consistent across restarts
- **Ollama** provides free local embeddings without API costs
- **Backups** should be configured for data directories

## Troubleshooting

### SSL Certificate Errors

If you see SSL errors:
```bash
# Only for testing - NEVER in production
export OPEN_NOTEBOOK_INSECURE=true
```

### Authentication Errors

If you get `{"detail":"Missing authorization header"}`:
- Verify `OPEN_NOTEBOOK_PASSWORD` is set
- Ensure you're using `https://` not `http://`
- Check the `Authorization: Bearer` header is included

### Connection Refused

If you cannot connect:
- Verify URL is `https://<your-domain.com>`
- Check OpenResty is running: `sudo systemctl status openresty`
- Check Docker containers: `docker ps`
- Verify firewall: `sudo ufw status`
