# Versions

Resolved in `uv.lock` on 2026-10-29. "Previous" is the old `requirements.txt` (2021 pins, saved as UTF-16 so `pip` could not even read it).

| Component | Version | Previous | Note |
|---|---|---|---|
| Python | 3.13 | 3.8+ (unstated) | `requires-python >=3.13` |
| Flask | 3.1.3 | 2.0.1 | |
| Flask-SQLAlchemy | 3.1.1 | 2.5.1 | `create_all(app=...)` and `Model.query.get` patterns replaced |
| Flask-Login | 0.6.3 | 0.5.0 | |
| Flask-WTF | 1.3.0 | 0.15.1 (listed, unused) | now used for CSRF protection |
| python-dateutil | 3.0.0 | 2.8.1 | |
| gunicorn | 26.2.0 | 20.1.0 | |
| psycopg | 3.3.6 (binary) | psycopg2 2.9.1 | URL scheme `postgresql+psycopg://` |
| PostgreSQL (CI) | 17-alpine | n/a | not verified as the newest major |
| Tailwind CSS (build tooling in `Website/static/package.json`) | ^2.0.1 | ^2.0.1 | unchanged; Tailwind 2 is old, and upgrading means rebuilding the stylesheet |

Removed as unused: about 40 pinned packages (Jupyter/nbformat, pyppeteer, pyquery, Flask-Bcrypt, and others) that the app never imports.

Dev: pytest, ruff.
