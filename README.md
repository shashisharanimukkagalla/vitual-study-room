# Virtual Study Hall

A Flask website for collaborative online study rooms with authentication, realtime chat, focus timers, file sharing, tasks, admin controls, and Jitsi video rooms.

## Product Features
- Student registration, login, logout, and profile/password settings.
- Public and private study rooms with invite codes.
- Realtime room chat and synchronized focus timer.
- Completed focus sessions saved to each user's study history.
- Room file sharing with authenticated, membership-checked downloads.
- Notifications for study completion and shared resources.
- Jitsi video study room embedded per room.
- Admin dashboard for room, user, and role management.

## Setup
### One-command Windows setup
For a completely fresh client system with Python installed:

```bat
setup_and_run.bat
```

To create the first admin while setting up:

```bat
setup_and_run.bat -CreateAdmin
```

Then open `http://127.0.0.1:5000`.

To prepare dependencies and database without starting the server:

```bat
setup_and_run.bat -NoStart
```

### Manual setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## First Admin
```bash
$env:FLASK_APP="run.py"
flask create-admin
```

## Production Start
Use a real `SECRET_KEY`, set `FLASK_DEBUG=false`, use PostgreSQL for shared deployments, and serve behind HTTPS.

```bash
waitress-serve --listen=0.0.0.0:8000 wsgi:app
```

On Windows, the setup script can start the Waitress server too:

```bat
setup_and_run.bat -Production -HostName 0.0.0.0 -Port 8000
```

## Smoke Test
```bash
python tests/smoke_test.py
```
