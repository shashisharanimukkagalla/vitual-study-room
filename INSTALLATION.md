# Virtual Study Hall Installation Guide

## System Requirements
- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Internet connection during first setup for Python package installation.
- Modern browser such as Chrome, Edge, or Firefox.

## Quick Start
1. Extract the project zip.
2. Open the extracted folder.
3. Double-click `setup_and_run.bat`, or run it from Command Prompt:

```bat
setup_and_run.bat
```

4. Open the website:

```text
http://127.0.0.1:5000
```

The script automatically creates the virtual environment, installs dependencies, creates `.env`, initializes the database, and starts the server.

## Create First Admin
Run:

```bat
setup_and_run.bat -CreateAdmin
```

Enter the admin username, email, and password when asked.

## Start Without Setup
After the first successful setup, run:

```bat
setup_and_run.bat
```

The script reuses the existing `.venv`, `.env`, and database.

## Prepare Only, Do Not Start Server
Run:

```bat
setup_and_run.bat -NoStart
```

## Production-Style Local Server
Run:

```bat
setup_and_run.bat -Production -HostName 0.0.0.0 -Port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Manual Setup
Use this only if the automatic script is not allowed on the client machine.

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
set FLASK_APP=run.py
flask init-db
python run.py
```

## Run Smoke Test
After setup:

```bat
.venv\Scripts\python.exe tests\smoke_test.py
```

Expected final line:

```text
ALL_SMOKE_TESTS_PASSED
```

## Important Configuration
The first setup creates `.env` automatically. For deployment, update:

```text
SECRET_KEY=use-a-long-random-secret
DATABASE_URL=sqlite:///absolute/path/to/instance/study_hall.db
SESSION_COOKIE_SECURE=true
SOCKETIO_CORS_ALLOWED_ORIGINS=https://your-domain.example
```

For a public commercial deployment, use HTTPS, PostgreSQL, private object storage for uploads, and Redis-backed Socket.IO.

## Troubleshooting
- If `python` is not recognized, install Python 3.11+ and enable “Add Python to PATH”.
- If PowerShell script execution is blocked, run `setup_and_run.bat`; it already uses a temporary execution-policy bypass for this script.
- If port `5000` is busy, run:

```bat
setup_and_run.bat -Port 5001
```

- If dependencies fail to install, check internet access and rerun the setup command.
