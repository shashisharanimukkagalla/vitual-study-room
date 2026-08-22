# Architecture

## Stack
- Backend: Flask
- Realtime: Flask-SocketIO
- Database: SQLite for development, PostgreSQL-ready SQLAlchemy models
- ORM: Flask-SQLAlchemy
- Auth: Flask-Login
- Forms: Flask-WTF
- Frontend: Jinja templates, CSS, JavaScript
- Video: Jitsi Meet embed
- File storage: private local `instance/uploads` folder for MVP

## Application Structure
```text
study_hall/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── auth/
│   ├── main/
│   ├── rooms/
│   ├── tasks/
│   ├── files/
│   ├── admin/
│   ├── templates/
│   └── static/
├── docs/
├── instance/
├── migrations/
├── requirements.txt
├── run.py
└── README.md
```

## Module Responsibilities

### auth
Handles registration, login, logout, and current-user session state.

### main
Handles home page and student dashboard.

### rooms
Handles room creation, joining, leaving, room pages, chat socket events, and timer socket events.

### tasks
Handles room-linked personal tasks.

### files
Handles upload, validation, listing, and download of room resources.

### admin
Handles admin dashboard and moderation actions.

## Realtime Design
Socket.IO room names use `room_<room_id>`.

Events:
- `join_room_channel`
- `send_message`
- `timer_start`
- `timer_pause`
- `timer_reset`

Messages are persisted before broadcasting. Timer state is broadcast in memory for MVP and can later be persisted in Redis.

## Video Design
Each study room gets a deterministic Jitsi room name:

```text
studyhall-<invite_code>
```

The room page embeds Jitsi through the public Jitsi API. Later, the deployment can switch to a self-hosted Jitsi server without changing the database model.

## Deployment Notes
- Development uses SQLite and private local uploads.
- Production should use PostgreSQL, Redis for Socket.IO message queue, HTTPS, and private cloud/object storage for uploads.
- Uploaded files should never be placed under Flask's public static directory.
- Socket.IO CORS defaults to same-origin and should only be opened to trusted domains.
