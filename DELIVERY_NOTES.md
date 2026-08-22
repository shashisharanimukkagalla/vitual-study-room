# Delivery Notes

## Included
- Flask source code.
- Jinja templates, CSS, and JavaScript.
- Product planning documents in `docs/`.
- Fresh-machine setup scripts.
- Smoke test.
- Installation guide.

## Excluded
- Local virtual environment `.venv/`.
- Runtime database files in `instance/*.db`.
- Uploaded user files in `instance/uploads/`.
- Python cache files.
- Local `.env`.

## Main Entry Points
- `setup_and_run.bat`: automatic setup and start.
- `setup_and_run.ps1`: PowerShell implementation of the setup flow.
- `run.py`: Flask development/local runner.
- `wsgi.py`: WSGI entry point for production servers.
- `tests/smoke_test.py`: end-to-end smoke test.
