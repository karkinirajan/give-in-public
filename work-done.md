# Work done: give-in-public

Branch: `chore/modernize` (local, not pushed). Date: 2026-10-29. The repo had no uncommitted work.

## What was there
A Flask app (package `Website`) on Flask 2.0 / Flask-SQLAlchemy 2.5 with a 2021 `requirements.txt` saved as UTF-16 (unreadable by pip). `Website/__init__.py` hardcoded the Flask `SECRET_KEY` and a complete Heroku PostgreSQL connection URL including credentials. A SQLite file (`Website/database.db`) was tracked. No tests, no CI, and a README describing a Django project (`manage.py migrate`) that this is not.

## Changes by file
| File | Before | Change |
|---|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | absent | New uv project, Python 3.13, Flask 3.1 |
| `requirements.txt` | UTF-16, ~60 pins incl. Jupyter and pyppeteer | ASCII export from the lockfile |
| `Website/__init__.py` | hardcoded secret key and database URL; `create_all(app=app)` (removed API); stray `print("Test")` | Secret and database from `SECRET_KEY` / `DATABASE_URL` (fails fast without a key; Heroku `postgres://` accepted; SQLite fallback); CSRF protection; secure session-cookie options; Flask-SQLAlchemy 3 `create_all` |
| `Website/security.py` | absent | New: `hash_password` (pbkdf2, fits the existing `String(150)` column) and `verify_password`, which still accepts the old Werkzeug-2 `sha256$salt$hmac` hashes and reports them for upgrade; unsupported hash methods return False instead of raising |
| `Website/auth.py` | `generate_password_hash(method='sha256')` (removed in Werkzeug 3, which would have locked out every existing user); `len(first_name)` on a missing field; flash category typo `succcess`; unused imports | New hashing; legacy hashes upgraded at login; missing fields handled; typo fixed; empty password rejected |
| `Website/views.py` | `flash(..., error)` passed the `logging.error` function as category; `amount` undefined for invalid input (UnboundLocalError); delete by GET link; `/mission` rendered a missing template (500); leaderboard query invalid on PostgreSQL | Invalid amount/date flash an error and save nothing; delete is POST-only with an owner check (403 otherwise); `/mission` returns 404; leaderboard groups by name and orders by the label (see below) |
| `Website/models.py` | `datetime.utcnow` defaults | Timezone-aware `datetime.now(UTC)` |
| `Website/templates/login.html`, `signup.html`, `Configure.html` | no CSRF tokens; delete was a link | CSRF hidden fields; delete is a small POST form |
| `tests/` | absent | 27 tests: hashing incl. legacy, sign-up/log-in, CSRF, donations, ownership, public dashboard |
| `.github/workflows/ci.yml`, `.env.example` | absent | New; CI runs the suite on SQLite and a PostgreSQL service |
| `.gitignore` | had `node_modules/`, `.env` | Also the SQLite file, `instance/`, `.venv`, caches |
| `Website/database.db` | tracked | Untracked (file stays on disk) |
| `README.md` | described a Django app | Rewritten from the code |
| `VERSIONS.md`, `work-done.md` | absent | New |

## Bugs found by running on real PostgreSQL
Production uses PostgreSQL, but SQLite is lenient, so these only appeared when the suite ran against a PostgreSQL 17 container:
1. The public dashboard's leaderboard selected `User.first_name` without grouping by it (PostgreSQL error).
2. It ordered by an unquoted `Total` while the label was created as the quoted `"Total"` (PostgreSQL error).
Both would have returned HTTP 500 for `/dashboard/public/<id>` on the live database. Fixed; 27 tests pass on both databases.

## Verification (actual runs)
- `uv run pytest -q`: 27 passed on SQLite; 27 passed against PostgreSQL 17 (throwaway container, removed afterwards).
- `uv run ruff check .` and `ruff format --check .`: clean.
- Not run: `gunicorn app:app` against a production database, the browser UI, a Tailwind rebuild.

## Needs your attention
- **Rotate the Flask `SECRET_KEY` and the Heroku PostgreSQL credentials** that were hardcoded; they remain in git history, and that database URL (host, user, password) should be treated as exposed. I did not copy any of the values anywhere.
- Existing users keep working (legacy hashes verify and upgrade at next login). If the live `user.password` column is wider or narrower than 150, check it.
- No schema migrations: tables are created at startup only. Adding Flask-Migrate would be the next step.
- Tailwind 2 build tooling is old; `/mission`, `vision.html` and `dashboard.html` do not exist.
- `/logout` is still a GET link.
- Nothing pushed. To publish: `git push -u origin chore/modernize`
