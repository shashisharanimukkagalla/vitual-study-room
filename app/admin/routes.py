from functools import wraps
from pathlib import Path

from flask import Blueprint, abort, current_app, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Message, Notification, Room, RoomMember, SharedFile, StudySession, Task, User

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/")
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    rooms = Room.query.order_by(Room.created_at.desc()).all()
    files = SharedFile.query.order_by(SharedFile.uploaded_at.desc()).limit(20).all()
    return render_template("admin/dashboard.html", users=users, rooms=rooms, files=files)


@admin_bp.route("/rooms/<int:room_id>/delete", methods=["POST"])
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/role/<role>", methods=["POST"])
@admin_required
def set_user_role(user_id, role):
    if role not in {"student", "admin"}:
        abort(404)
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id and role != "admin":
        abort(400)
    user.role = role
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        abort(400)
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    for shared_file in SharedFile.query.filter_by(user_id=user.id).all():
        file_path = upload_dir / shared_file.stored_filename
        if file_path.exists():
            file_path.unlink()
        db.session.delete(shared_file)
    for room in Room.query.filter_by(created_by_id=user.id).all():
        db.session.delete(room)
    RoomMember.query.filter_by(user_id=user.id).delete()
    Message.query.filter_by(user_id=user.id).delete()
    Task.query.filter_by(user_id=user.id).delete()
    StudySession.query.filter_by(user_id=user.id).delete()
    Notification.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))
