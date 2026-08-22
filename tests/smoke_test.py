from io import BytesIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app, db, socketio
from app.config import Config
from app.models import Message, Notification, Room, RoomMember, SharedFile, StudySession, Task, User


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def assert_status(response, expected, label):
    if response.status_code != expected:
        raise AssertionError(
            f"{label}: expected {expected}, got {response.status_code}, "
            f"location={response.headers.get('Location')}"
        )
    print(f"PASS {label}: {response.status_code}")


def main():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        client = app.test_client()

        assert_status(client.get("/"), 200, "home")
        assert_status(
            client.post(
                "/auth/register",
                data={
                    "username": "alice",
                    "email": "alice@example.com",
                    "password": "secret123",
                },
                follow_redirects=True,
            ),
            200,
            "register",
        )
        user = User.query.filter_by(email="alice@example.com").one()
        assert_status(client.get("/dashboard"), 200, "authenticated dashboard")

        assert_status(
            client.post(
                "/rooms/create",
                data={
                    "name": "Math Sprint",
                    "subject": "Math",
                    "description": "Calculus practice",
                    "capacity": "8",
                },
                follow_redirects=True,
            ),
            200,
            "create room",
        )
        room = Room.query.filter_by(name="Math Sprint").one()
        assert RoomMember.query.filter_by(user_id=user.id, room_id=room.id).count() == 1
        print("PASS room membership created")

        assert_status(
            client.post(
                "/rooms/create",
                data={
                    "name": "Private Exam Room",
                    "subject": "Physics",
                    "capacity": "4",
                    "is_private": "on",
                },
                follow_redirects=True,
            ),
            200,
            "create private room",
        )
        private_room = Room.query.filter_by(name="Private Exam Room").one()
        assert_status(client.get("/auth/logout", follow_redirects=True), 200, "logout first user")
        assert_status(
            client.post(
                "/auth/register",
                data={"username": "bob", "email": "bob@example.com", "password": "secret123"},
                follow_redirects=True,
            ),
            200,
            "register second user",
        )
        private_list = client.get("/rooms/")
        assert_status(private_list, 200, "second user room list")
        assert b"Private Exam Room" not in private_list.data
        assert_status(client.get(f"/rooms/{private_room.id}/join"), 404, "private direct join denied")
        assert_status(
            client.post("/rooms/join", data={"invite_code": private_room.invite_code}, follow_redirects=True),
            200,
            "private invite join",
        )
        print("PASS private room privacy")
        assert_status(client.get("/auth/logout", follow_redirects=True), 200, "logout second user")
        assert_status(
            client.post(
                "/auth/login",
                data={"email": "alice@example.com", "password": "secret123"},
                follow_redirects=True,
            ),
            200,
            "login first user again",
        )

        assert_status(
            client.post(
                f"/tasks/room/{room.id}/add",
                data={"title": "Finish integrals"},
                follow_redirects=True,
            ),
            200,
            "add task",
        )
        task = Task.query.filter_by(room_id=room.id, user_id=user.id).one()
        assert_status(client.post(f"/tasks/{task.id}/toggle", follow_redirects=True), 200, "toggle task")
        assert db.session.get(Task, task.id).is_completed is True
        print("PASS task toggled")

        assert_status(
            client.post(
                f"/files/room/{room.id}/upload",
                data={"file": (BytesIO(b"hello notes"), "notes.txt")},
                content_type="multipart/form-data",
                follow_redirects=True,
            ),
            200,
            "upload file",
        )
        shared_file = SharedFile.query.filter_by(room_id=room.id).one()
        response = client.get(f"/files/download/{shared_file.id}")
        assert_status(response, 200, "download file")
        assert response.data == b"hello notes"
        print("PASS file content")

        sio = socketio.test_client(app, flask_test_client=client)
        assert sio.is_connected()
        sio.emit("join_room_channel", {"room_id": room.id})
        sio.get_received()
        sio.emit("send_message", {"room_id": room.id, "content": "Ready to study"})
        received = sio.get_received()
        assert any(item["name"] == "receive_message" for item in received), received
        assert Message.query.filter_by(room_id=room.id, content="Ready to study").count() == 1
        print("PASS socket chat")

        sio.emit(
            "timer_update",
            {"room_id": room.id, "state": "start", "remaining": 1500, "defaultSeconds": 1500},
        )
        print("PASS socket timer emit")

        assert_status(
            client.post(
                f"/rooms/{room.id}/session",
                data={"duration_minutes": "25"},
                follow_redirects=True,
            ),
            200,
            "record study session",
        )
        assert StudySession.query.filter_by(user_id=user.id, room_id=room.id).count() == 1
        assert Notification.query.filter_by(user_id=user.id).count() == 1
        print("PASS session and notification stored")

        assert_status(client.get("/profile"), 200, "profile")
        assert_status(
            client.post(
                "/profile",
                data={"username": "alice2", "email": "alice2@example.com"},
                follow_redirects=True,
            ),
            200,
            "profile update",
        )
        assert db.session.get(User, user.id).username == "alice2"
        print("PASS profile updated")

        assert_status(client.get("/admin/"), 403, "student admin denied")
        user.role = "admin"
        db.session.commit()
        assert_status(client.get("/admin/"), 200, "admin dashboard")

    print("ALL_SMOKE_TESTS_PASSED")


if __name__ == "__main__":
    main()
