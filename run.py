import os
from getpass import getpass

from app import create_app, db, socketio
from app.models import User

app = create_app()


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized.")


@app.cli.command("create-admin")
def create_admin():
    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass("Password: ")
    if not username or not email or not password:
        raise SystemExit("Username, email, and password are required.")
    if User.query.filter((User.username == username) | (User.email == email)).first():
        raise SystemExit("Username or email already exists.")
    user = User(username=username, email=email, role="admin")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin created: {email}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    socketio.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=debug,
        allow_unsafe_werkzeug=debug,
    )
