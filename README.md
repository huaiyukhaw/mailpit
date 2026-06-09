# Mailpit — Local SMTP for Mendix Email Connector

A throwaway, local email server for **developing and testing the Mendix Email
Connector** without sending real mail. [Mailpit](https://mailpit.axllent.org/)
catches everything your app sends and shows it in a web inbox — no messages
ever leave your machine.

What you get:

- **SMTP** server on `localhost:1025` — point Mendix's *outgoing* email at it.
- **Web inbox** on <http://localhost:8025> — read every captured message, view
  HTML/plain/source, headers, and attachments.
- **POP3** server on `localhost:1110` — optionally let Mendix *retrieve* mail
  to exercise the receive flow.
- **REST API** on the same port as the UI — for automated assertions in tests.

> Local dev only. Mailpit accepts any SMTP credentials and runs without TLS, so
> never expose it publicly or use it for real mail.

---

## Prerequisites

- Docker + Docker Compose v2 (`docker compose version`)
- Mendix Studio Pro with the **Email Connector** module imported from the
  Marketplace

## Quick start

```bash
# 1. (optional) customise ports
cp .env.example .env

# 2. start Mailpit
docker compose up -d          # or: make up

# 3. open the inbox
#    http://localhost:8025

# 4. confirm SMTP works before touching Mendix
python3 scripts/send-test-email.py   # or: make test
#    Windows: use `python` or `py` instead of `python3`
```

A test message should appear in the inbox within a second. Stop with
`docker compose down` (mail is kept) or `make clean` (mail is wiped).

> **Windows note:** `python3` is a Microsoft Store alias, not a real command —
> use `python scripts\send-test-email.py` (or `py scripts\...`). `make test`
> auto-detects whichever launcher you have.

---

## Configuring the Mendix Email Connector

The Email Connector stores accounts at runtime (usually via its
`EmailConnector_Overview` administration page, or seeded with `AfterStartup`
microflow logic). Use these values.

### Outgoing mail (SMTP — sending)

| Setting              | Value                          | Notes                                            |
| -------------------- | ------------------------------ | ------------------------------------------------ |
| SMTP host / server   | `localhost`                    | See [networking](#where-is-mendix-running) below |
| SMTP port            | `1025`                         | `MP_SMTP_PORT`                                    |
| Encryption / TLS     | **None**                       | Mailpit dev server is plaintext                  |
| Username             | anything (e.g. `test`)         | Mailpit accepts any credentials                  |
| Password             | anything (e.g. `test`)         | "                                                |
| From address         | any, e.g. `noreply@example.test` |                                                |

If the connector version requires you to pick a security mode and "None" is not
allowed, choose **STARTTLS** — Mailpit advertises it and will still accept the
message. Leave certificate validation off.

### Incoming mail (POP3 — retrieving), optional

Only needed if you're testing the *receive* side of the connector.

| Setting            | Value          | Notes                                  |
| ------------------ | -------------- | -------------------------------------- |
| Protocol           | **POP3**       | Mailpit supports POP3 (not IMAP)       |
| Host / server      | `localhost`    |                                        |
| Port               | `1110`         | `MP_POP3_PORT`                         |
| Encryption / TLS   | **None**       |                                        |
| Username           | `test`         | Must match `MP_POP3_AUTH` (`user`)     |
| Password           | `test`         | Must match `MP_POP3_AUTH` (`pass`)     |

POP3 serves the messages already captured by Mailpit. Change the credentials
via `MP_POP3_AUTH=user:pass` in your `.env`.

> **Common gotcha:** the POP3 **username must be the literal `MP_POP3_AUTH`
> user (`test`), _not_ the mailbox email address.** Unlike a real mail server,
> Mailpit's POP3 only accepts that one exact user/password pair — entering the
> account's email address (or any other value) returns
> `AuthenticationFailedException: invalid password`.

### Where is Mendix running?

The SMTP/POP3 **host** depends on where Studio Pro runs the app relative to
Docker:

| Mendix runs on…                              | Use host                  |
| -------------------------------------------- | ------------------------- |
| Same machine as Docker (typical, Win/Mac)    | `localhost`               |
| A container, with Mailpit in another         | `host.docker.internal` or the compose service name `mailpit` if on the same network |
| Mendix Cloud / remote                         | **Won't work** — Mailpit is local only |

---

## Verifying it works

- **Web UI** — <http://localhost:8025> lists every captured message.
- **Test script** — `make test` sends a known message; confirm it shows up.
- **REST API** — handy for automated tests:

  ```bash
  # list captured messages
  curl -s http://localhost:8025/api/v1/messages | python3 -m json.tool
  # (Windows: python -m json.tool)

  # delete all captured messages (reset between test runs)
  curl -s -X DELETE http://localhost:8025/api/v1/messages
  ```

See the [Mailpit API docs](https://mailpit.axllent.org/docs/api-v1/) for the
full surface (search, mark read, release, etc.).

---

## Common tasks

| Task                         | Command                          |
| ---------------------------- | -------------------------------- |
| Start                        | `make up`                        |
| Stop (keep mail)             | `make down`                      |
| Restart                      | `make restart`                   |
| Tail logs                    | `make logs`                      |
| Wipe all stored mail         | `make clean`                     |
| Send a test email            | `make test`                      |

Run `make` with no target to see the full list.

---

## Configuration reference

All settings live in `docker-compose.yml`, overridable via `.env`
(see `.env.example`):

| Variable          | Default     | Purpose                                       |
| ----------------- | ----------- | --------------------------------------------- |
| `MP_UI_PORT`      | `8025`      | Host port for the web UI + REST API           |
| `MP_SMTP_PORT`    | `1025`      | Host port for SMTP                            |
| `MP_POP3_PORT`    | `1110`      | Host port for POP3                            |
| `MP_MAX_MESSAGES` | `5000`      | Messages kept before oldest are rotated out   |
| `MP_POP3_AUTH`    | `test:test` | POP3 `user:pass` Mendix uses to retrieve mail |
| `TZ`              | `UTC`       | Timezone for timestamps in the UI             |

Messages persist in the `mailpit-data` Docker volume across restarts. Delete
them with `make clean` (`docker compose down -v`).

## Troubleshooting

- **Connection refused from Mendix** — check the host (see the table above);
  `localhost` only works when Studio Pro runs on the same machine as Docker.
- **Port already in use** — set a different `MP_*_PORT` in `.env` and update the
  matching value in the Mendix account.
- **Auth errors on send** — Mailpit accepts any credentials; make sure
  encryption is **None** (or STARTTLS) and certificate validation is off.
- **Nothing in the inbox** — confirm the container is healthy with `make ps`
  and tail `make logs`; then re-run `make test`.
- **`pull rate limit` / image won't download** — Docker Hub throttles anonymous
  pulls. Either `docker login`, or switch the image in `docker-compose.yml` to
  the GitHub Container Registry mirror: `ghcr.io/axllent/mailpit:latest`.
