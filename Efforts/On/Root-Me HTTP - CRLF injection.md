---
created: 2026-08-14
up:
  - "[[Efforts]]"
related:
  - "[[Root-Me HTTP - Improper redirect]]"
  - "[[Root-Me Nginx - Alias Misconfiguration]]"
  - "[[Root-Me Nginx - Root Location Misconfiguration]]"
  - "[[Root-Me API Broken Access (IDOR)]]"
  - "[[CRLF Injection (HTTP-CRLF)]]"
in:
  - "[[Efforts]]"
tags:
  - root-me
  - http
  - crlf
  - injection
  - log-injection
  - web-security
  - ctf
---

# Root-Me HTTP - CRLF injection

Challenge: [HTTP - CRLF injection](https://www.root-me.org/en/Challenges/Web-Server/HTTP-CRLF-injection) — Root-Me Web/Server challenge, path `/web-serveur/ch14/`, topic: CRLF injection in a reflected username → forged authentication-log line.

> [!Milestone]+ Status: solved
> Solved with `curl` — CRLF in the username parameter forges an `admin authenticated.` log line and the server hands over the flag.

## What is known

- **Profile:** 15 pts, Web - Server. Path `http://challenge01.root-me.org/web-serveur/ch14/`.
- **Topic:** the auth log builds `$username failed to authenticate.` from unescaped input. A `%0D%0A` (CRLF) in the username breaks out of the line and forges new log entries — the server's log check then grants the flag.
- **Flag:** captured at solve; value kept out of the vault (don't copy flags).

> [!NOTE]- Access: Anubis anti-bot
> Root-Me pages are served behind Anubis — the challenge instance itself responds directly to curl.

## How it was solved

1. **Recon:** `curl http://challenge01.root-me.org/web-serveur/ch14/` → GET login form + static auth log hint (`admin authenticated.` — credentials exist; log is not persistent, it's a fixed hint + the current attempt).
2. **Identify the flaw:** the log line reflects the submitted username verbatim — CRLF injection point.
3. **Payload:** `?username=admin%20authenticated.%0D%0Aadmin&password=admin` → the appended failure line contains a forged `admin authenticated.` line → response: `Well done, you can validate challenge with this password : <flag>`.

## Post-solve pipeline

> [!COMMAND]- Learnings → vault Knowledge Pipeline (no custom tooling)
> 1. **Encounter Gate** — `skill://grill-me`: raw spark? → capture to `+/`; to promote, skip gate (`.omp/RULES.md` Steps 0–0b).
> 2. **Classify** knowledge type (Concept/Process/Entity/Principle) — `.omp/knowledge/knowledge-classification.md`.
> 3. **Distill → locate → link** — @sensemaker (atomic notes, own words) → @librarian (location) → @connector (`up:`/`related:`, duplicates, `needs-moc`). Destination `Atlas/` (`.omp/RULES.md` Steps 1–4). Logged via `bash .omp/scripts/knowledge-pipeline.sh`. Research: Open Notebook.
> 4. **Confidence** — ≥0.85 auto-run; 0.70–0.84 confirm; <0.70 options per step (`.omp/knowledge/workflows.md`). Fallbacks: @librarian fails → `+/`; @connector fails → linkless + flag.
> 5. **Frontmatter + validation** — `standards.md`, `output-standards.md`, Validation Checklist (`.omp/knowledge/workflows.md`).
> 6. **MOC Gate** — `skill://grill-me` + `skill://moc-workbench`; `scripts/validate_moc.py` (`.omp/RULES.md` Step 5; squeeze-point rule).

Never ingest challenge tokens/keys into notes — `.omp/RULES.md` Sensitive Data Protection (FATAL).
