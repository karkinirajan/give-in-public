# GiveInPublic

A Flask web app where people record their charitable donations and share a public dashboard of what they have given: totals, a breakdown by organisation, a cumulative-over-time chart, and a leaderboard.

## Features

- Sign up and log in (email and password); passwords are hashed, and hashes written by older versions of the app still work and are upgraded on the next login.
- Private dashboard (`/dashboard/configure`) to add and delete donations (organisation, amount, description, date).
- Public dashboard per user (`/dashboard/public/<id>`) with totals, per-organisation split, cumulative chart data, and a ranking of donors.
- CSRF protection on all forms; deleting a donation is a POST restricted to its owner.
- Landing, subscribe, manage-plan and feedback pages (static templates).

Not implemented: the `/mission` page has no template yet (it returns 404), and there is no payment processing.

## Stack

Python 3.13, Flask 3, Flask-SQLAlchemy 3, Flask-Login, Flask-WTF, gunicorn; SQLite locally and PostgreSQL via `DATABASE_URL`. Styling uses Tailwind CSS (prebuilt CSS is checked in under `Website/static/`). Versions: [VERSIONS.md](./VERSIONS.md).

## Quickstart

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/kneeraazon404/GiveInPublic.git
cd GiveInPublic
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
uv sync
uv run flask --app app run --debug
```

Open http://127.0.0.1:5000. Without `DATABASE_URL` a local SQLite database is created automatically.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | required | session and CSRF signing; startup fails without it |
| `DATABASE_URL` | local SQLite | `postgresql://...` or Heroku-style `postgres://...` |
| `SESSION_COOKIE_SECURE` | `false` | set `true` behind HTTPS |

See [.env.example](./.env.example). Production: `Procfile` runs `gunicorn app:app`. There is no migration tool yet; missing tables are created at startup, so schema changes to an existing database need a manual migration.

## Testing

```bash
uv run pytest -q
TEST_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/gip_test uv run pytest -q
uv run ruff check . && uv run ruff format --check .
```

27 tests cover password hashing (including legacy hashes), sign-up/log-in, CSRF, donations, ownership checks and the public dashboard. CI runs them on SQLite and on a PostgreSQL service.

## Project structure

```
app.py              entry point (gunicorn app:app)
Website/            application package: factory, models, auth and views blueprints, security helpers
Website/templates/  Jinja templates
Website/static/     JS, prebuilt Tailwind CSS and its build config
tests/              pytest suite
```
