---
created: 2026-08-14
up:
  - "[[Things]]"
  - "[[Root-Me Nginx - Root Location Misconfiguration]]"
related:
  - "[[Nginx Alias Misconfiguration (Path Traversal)]]"
in:
  - "[[Things]]"
tags:
  - concept
  - nginx
  - root
  - misconfiguration
  - config-exposure
  - web-security
  - needs-moc
---

# Nginx Root Location Misconfiguration (Config Exposure)

> [!map]+ TL;DR
> When `root` points at a config directory like `/etc/nginx` instead of the intended web root, nginx maps the full request URI onto that sensitive path. A catch-all `location / { try_files $uri $uri/ =404; }` serves every reachable file — including `nginx.conf`, `conf.d/*`, and `sites-enabled/*`, which often contain secrets (tokens, upstream hosts, credentials). Fix: `root` must always point at the intended document root only.

## The bug

nginx's `root` directive prepends the configured path to the full request URI. A request for `GET /nginx.conf` with `root /etc/nginx;` resolves to `/etc/nginx/nginx.conf` — a straight concatenation, no splicing, no suffix trickery. The request URI is appended as-is.

The danger is simple: if `root` points at a directory that contains sensitive config files, and those files exist at predictable paths under the nginx document root, they're served directly to any client. Unlike the alias misconfiguration (where the bug is suffix-splicing that enables path traversal), the root misconfiguration is about the *path itself* being wrong. There's no traversal needed — the attacker just requests well-known filenames.

A catch-all `location / { try_files $uri $uri/ =404; }` makes it worse: it tries every URI as a file, so anything reachable under the root directory is served. nginx won't return 403 for a config file — it returns 200 with the contents, because from nginx's perspective, the file is in the document root and the request is valid.

This is distinct from alias traversal (where `..` segments in the URI splice past the intended boundary). With root, there's no splice — the entire URI maps onto the path. The misconfiguration is a *deploy-time error*: someone pointed the server at the wrong directory.

## Attack flow

```mermaid
sequenceDiagram
    actor Attacker
    participant Nginx
    participant FS

    Note over Nginx: root /etc/nginx;<br/>location / { try_files $uri $uri/ =404; }

    Attacker->>Nginx: GET /nginx.conf
    Nginx->>FS: open("/etc/nginx/nginx.conf")
    FS-->>Nginx: config contents (reveals include directive)
    Nginx-->>Attacker: 200 + live config

    Note over Attacker: config reveals include /etc/nginx/conf.d/default.conf;

    Attacker->>Nginx: GET /conf.d/default.conf
    Nginx->>FS: open("/etc/nginx/conf.d/default.conf")
    FS-->>Nginx: secrets (tokens, upstream hosts, credentials)
    Nginx-->>Attacker: 200 + sensitive config
```

## Spotting it

> [!PUZZLE]- Test pattern
> 1. **Check the `root` directive.** Grep nginx configs for `root` — if it points at `/etc/nginx`, `/etc/nginx/conf.d`, or any non-web-root directory, that's the smell. The correct value is something like `/var/www/html` or `/usr/share/nginx/html`.
> 2. **Probe well-known config paths.** Request `GET /nginx.conf`, `GET /conf.d/default.conf`, `GET /sites-enabled/default`. A 200 with config syntax (`server {`, `listen`, `location`, `upstream`) confirms exposure.
> 3. **Check `try_files` scope.** A catch-all `location /` with `try_files $uri $uri/ =404;` amplifies the impact — every file under root is served. More restrictive locations or explicit `location` blocks for sensitive paths reduce the surface.
> 4. **Verify the fix.** After changing `root` to the intended document root, repeat the probes. nginx should return 404 for config paths — they're no longer under the served tree.

## Where it shows up

Docker images that template nginx.conf without separating config from content, automated hosting panels that generate configs with wrong root paths, dev/staging environments where `root /etc/nginx;` was a quick debug shortcut left in production. Also common in single-container setups where nginx and the application share a filesystem and the config directory is co-located with the web root. The misconfiguration survives because it doesn't break anything — nginx serves files normally, just from the wrong directory.

## Connections

- **Sibling:** [[Nginx Alias Misconfiguration (Path Traversal)]] — both are nginx URL-to-filesystem mapping flaws; alias truncation enables traversal, root misdirection enables direct access to a sensitive directory
- **Root cause family:** CWE-552 (Files or Directories Accessible to External Parties) — the server exposes files that were never intended to be web-accessible; CWE-200 (Exposure of Sensitive Information)
- **Related class:** information disclosure via misconfigured document roots — same family as Apache `DocumentRoot /etc` or IIS physical path exposure
- **Mitigation overlap:** `root` must point at the intended document root only; never at config directories; isolate nginx configs outside the web tree; use `location` blocks to restrict or deny access to sensitive paths; least-privilege filesystem permissions on config files

## Source

- [nginx — `root` directive documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#root) — official root behavior and URI-to-path mapping
- [Root-Me: Nginx — Root Location Misconfiguration](https://www.root-me.org/en/Challenges/Web-Server/Nginx-Root-Location-Misconfiguration) — hands-on challenge demonstrating config exposure via `root /etc/nginx;`

---

*Created from challenge context distillation by Sensemaker*
