from flask_login import current_user
from flask_socketio import emit, join_room

from ..extensions import db
from ..models import Message, Room, RoomMember


def is_room_member(room_id):
    return RoomMember.query.filter_by(room_id=room_id, user_id=current_user.id).first() is not None


def register_events(socketio):
    @socketio.on("join_room_channel")
    def on_join(data):
        room_id = int(data["room_id"])
        room = Room.query.get(room_id)
        if not room or not current_user.is_authenticated or not is_room_member(room_id):
            return
        channel = f"room_{room_id}"
        join_room(channel)
        emit("system_message", {"content": f"{current_user.username} joined the room."}, to=channel)

    @socketio.on("send_message")
    def on_message(data):
        if not current_user.is_authenticated:
            return
        room_id = int(data["room_id"])
        content = data.get("content", "").strip()
        if not content or not is_room_member(room_id):
            return
        message = Message(room_id=room_id, user_id=current_user.id, content=content)
        db.session.add(message)
        db.session.commit()
        emit(
            "receive_message",
            {
                "user": current_user.username,
                "content": content,
                "time": message.created_at.strftime("%H:%M"),
            },
            to=f"room_{room_id}",
        )

    @socketio.on("timer_update")
    def on_timer_update(data):
        if not current_user.is_authenticated:
            return
        room_id = int(data["room_id"])
        if not is_room_member(room_id):
            return
        emit("timer_update", data, to=f"room_{room_id}", include_self=False)
