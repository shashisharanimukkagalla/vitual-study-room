from datetime import timedelta

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Message, Notification, Room, RoomMember, SharedFile, StudySession, Task, utcnow

rooms_bp = Blueprint("rooms", __name__)


def user_can_access(room):
    if not room.is_private:
        return True
    return RoomMember.query.filter_by(room_id=room.id, user_id=current_user.id).first() is not None


def user_can_manage(room):
    return current_user.is_admin or room.created_by_id == current_user.id


@rooms_bp.route("/")
@login_required
def list_rooms():
    joined_room_ids = [membership.room_id for membership in RoomMember.query.filter_by(user_id=current_user.id).all()]
    rooms = (
        Room.query.filter((Room.is_private.is_(False)) | (Room.id.in_(joined_room_ids)))
        .order_by(Room.created_at.desc())
        .all()
    )
    return render_template("rooms/list.html", rooms=rooms)


@rooms_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_room():
    if request.method == "POST":
        room = Room(
            name=request.form.get("name", "").strip(),
            subject=request.form.get("subject", "").strip(),
            description=request.form.get("description", "").strip(),
            capacity=int(request.form.get("capacity") or 12),
            is_private=bool(request.form.get("is_private")),
            created_by_id=current_user.id,
        )
        if not room.name or not room.subject:
            flash("Room name and subject are required.", "error")
        else:
            db.session.add(room)
            db.session.flush()
            db.session.add(RoomMember(user_id=current_user.id, room_id=room.id))
            db.session.commit()
            return redirect(url_for("rooms.detail", room_id=room.id))
    return render_template("rooms/create.html")


@rooms_bp.route("/join", methods=["POST"])
@login_required
def join_by_code():
    invite_code = request.form.get("invite_code", "").strip()
    room = Room.query.filter_by(invite_code=invite_code).first()
    if not room:
        flash("No room found for that invite code.", "error")
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("rooms.join", room_id=room.id, code=room.invite_code))


@rooms_bp.route("/<int:room_id>/join")
@login_required
def join(room_id):
    room = Room.query.get_or_404(room_id)
    existing = RoomMember.query.filter_by(room_id=room.id, user_id=current_user.id).first()
    if existing:
        return redirect(url_for("rooms.detail", room_id=room.id))
    if room.is_private and request.args.get("code") != room.invite_code:
        abort(404)
    if room.member_count >= room.capacity:
        flash("This room is already full.", "error")
        return redirect(url_for("rooms.list_rooms"))
    db.session.add(RoomMember(user_id=current_user.id, room_id=room.id))
    db.session.commit()
    return redirect(url_for("rooms.detail", room_id=room.id))


@rooms_bp.route("/<int:room_id>/leave", methods=["POST"])
@login_required
def leave(room_id):
    membership = RoomMember.query.filter_by(room_id=room_id, user_id=current_user.id).first_or_404()
    db.session.delete(membership)
    db.session.commit()
    return redirect(url_for("main.dashboard"))


@rooms_bp.route("/<int:room_id>")
@login_required
def detail(room_id):
    room = Room.query.get_or_404(room_id)
    if not user_can_access(room):
        abort(403)
    membership = RoomMember.query.filter_by(room_id=room.id, user_id=current_user.id).first()
    if not membership:
        return redirect(url_for("rooms.join", room_id=room.id))
    messages = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.asc()).limit(80).all()
    tasks = Task.query.filter_by(room_id=room.id, user_id=current_user.id).order_by(Task.created_at.desc()).all()
    files = SharedFile.query.filter_by(room_id=room.id).order_by(SharedFile.uploaded_at.desc()).all()
    return render_template("rooms/detail.html", room=room, messages=messages, tasks=tasks, files=files)


@rooms_bp.route("/<int:room_id>/delete", methods=["POST"])
@login_required
def delete(room_id):
    room = Room.query.get_or_404(room_id)
    if not user_can_manage(room):
        abort(403)
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted.", "success")
    return redirect(url_for("main.dashboard"))


@rooms_bp.route("/<int:room_id>/session", methods=["POST"])
@login_required
def record_session(room_id):
    room = Room.query.get_or_404(room_id)
    if not RoomMember.query.filter_by(room_id=room.id, user_id=current_user.id).first():
        abort(403)
    duration_minutes = int(request.form.get("duration_minutes") or 0)
    duration_minutes = max(1, min(duration_minutes, 240))
    ended_at = utcnow()
    db.session.add(
        StudySession(
            user_id=current_user.id,
            room_id=room.id,
            duration_minutes=duration_minutes,
            started_at=ended_at - timedelta(minutes=duration_minutes),
            ended_at=ended_at,
        )
    )
    db.session.add(
        Notification(
            user_id=current_user.id,
            message=f"Great work. You completed {duration_minutes} focused minutes in {room.name}.",
        )
    )
    db.session.commit()
    return jsonify({"ok": True, "duration_minutes": duration_minutes})
