---
created: 2026-08-14
up:
  - "[[Efforts]]"
related:
  - "[[Root-Me API Broken Access (IDOR)]]"
  - "[[Open Redirect (Improper Redirect Handling)]]"
  - "[[Root-Me Nginx - Alias Misconfiguration]]"
in:
  - "[[Efforts]]"
tags:
  - root-me
  - http
  - redirect
  - open-redirect
  - web-security
  - ctf
---

# Root-Me HTTP - Improper redirect

Challenge: [HTTP - Improper redirect](https://www.root-me.org/en/Challenges/Web-Server/HTTP-Improper-redirect) — Root-Me Web/Server challenge, topic: improper redirect handling.

> [!Milestone]+ Status: solved
> Solved with `curl --no-location` — don't follow the redirect; read the raw response.

## What is known

- **Profile:** 15 pts, Web - Server, author Arod (2014), challenge path `/web-serveur/ch32/`.
- **Topic:** the server serves the flag in the response and then redirects; a client that follows the redirect loses it. Fix the client, not the server.
- **Technique:** `curl --no-location` — prevents curl from following redirects, exposing the raw 3xx response where the flag sits.
- **Flag:** captured at solve; value kept out of the vault (don't copy flags).

> [!NOTE]- Access: Anubis anti-bot
> Challenge pages are served behind Anubis — scripted fetches return a bot-check page. Use a real browser session or hit the challenge host directly.

## How it was solved

1. Request the challenge endpoint with redirect-following disabled: `curl --no-location <url>`.
2. Read the raw response curl shows — the flag is there, before/at the redirect.
3. `--no-location` is the whole trick: see what the redirect was hiding.

## Post-solve pipeline

> [!COMMAND]- Learnings → vault Knowledge Pipeline (no custom tooling)
> 1. **Encounter Gate** — `skill://grill-me`: raw spark? → capture to `+/`; to promote, skip gate (`.omp/RULES.md` Steps 0–0b).
> 2. **Classify** knowledge type (Concept/Process/Entity/Principle) — `.omp/knowledge/knowledge-classification.md`.
> 3. **Distill → locate → link** — @sensemaker (atomic notes, own words) → @librarian (location) → @connector (`up:`/`related:`, duplicates, `needs-moc`). Destination `Atlas/` (`.omp/RULES.md` Steps 1–4). Logged via `bash .omp/scripts/knowledge-pipeline.sh`. Research: Open Notebook.
> 4. **Confidence** — ≥0.85 auto-run; 0.70–0.84 confirm; <0.70 options per step (`.omp/knowledge/workflows.md`). Fallbacks: @librarian fails → `+/`; @connector fails → linkless + flag.
> 5. **Frontmatter + validation** — `standards.md`, `output-standards.md`, Validation Checklist (`.omp/knowledge/workflows.md`).
> 6. **MOC Gate** — `skill://grill-me` + `skill://moc-workbench`; `scripts/validate_moc.py` (`.omp/RULES.md` Step 5; squeeze-point rule).

Never ingest challenge tokens/keys into notes — `.omp/RULES.md` Sensitive Data Protection (FATAL).
