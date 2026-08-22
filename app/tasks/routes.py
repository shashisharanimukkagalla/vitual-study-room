from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import RoomMember, Task

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/room/<int:room_id>/add", methods=["POST"])
@login_required
def add(room_id):
    if not RoomMember.query.filter_by(room_id=room_id, user_id=current_user.id).first():
        return redirect(url_for("rooms.list_rooms"))
    title = request.form.get("title", "").strip()
    if title:
        db.session.add(Task(user_id=current_user.id, room_id=room_id, title=title))
        db.session.commit()
    return redirect(url_for("rooms.detail", room_id=room_id))


@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for("rooms.detail", room_id=task.room_id))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    room_id = task.room_id
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("rooms.detail", room_id=room_id))
