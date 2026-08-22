from pathlib import Path
from secrets import token_hex

from flask import Blueprint, current_app, flash, redirect, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Notification, Room, RoomMember, SharedFile

files_bp = Blueprint("files", __name__)


def allowed_file(filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in current_app.config["ALLOWED_UPLOAD_EXTENSIONS"]


def allowed_mime(uploaded):
    if uploaded.mimetype == "application/octet-stream":
        return True
    return uploaded.mimetype in current_app.config["ALLOWED_UPLOAD_MIMES"]


@files_bp.route("/room/<int:room_id>/upload", methods=["POST"])
@login_required
def upload(room_id):
    if not RoomMember.query.filter_by(room_id=room_id, user_id=current_user.id).first():
        flash("Join the room before sharing files.", "error")
        return redirect(url_for("rooms.list_rooms"))
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        flash("Choose a file first.", "error")
        return redirect(url_for("rooms.detail", room_id=room_id))
    if not allowed_file(uploaded.filename):
        flash("This file type is not allowed.", "error")
        return redirect(url_for("rooms.detail", room_id=room_id))
    if not allowed_mime(uploaded):
        flash("This file content type is not allowed.", "error")
        return redirect(url_for("rooms.detail", room_id=room_id))
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    original = secure_filename(uploaded.filename)
    stored = f"{token_hex(8)}_{original}"
    uploaded.save(upload_dir / stored)
    shared_file = SharedFile(
        room_id=room_id,
        user_id=current_user.id,
        original_filename=original,
        stored_filename=stored,
    )
    db.session.add(shared_file)
    room = db.session.get(Room, room_id)
    for member in RoomMember.query.filter(RoomMember.room_id == room_id, RoomMember.user_id != current_user.id).all():
        db.session.add(
            Notification(
                user_id=member.user_id,
                message=f"{current_user.username} shared {original} in {room.name}.",
            )
        )
    db.session.commit()
    flash("File uploaded.", "success")
    return redirect(url_for("rooms.detail", room_id=room_id))


@files_bp.route("/download/<int:file_id>")
@login_required
def download(file_id):
    shared_file = SharedFile.query.get_or_404(file_id)
    if not RoomMember.query.filter_by(room_id=shared_file.room_id, user_id=current_user.id).first():
        flash("Join the room before downloading its files.", "error")
        return redirect(url_for("rooms.list_rooms"))
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        shared_file.stored_filename,
        as_attachment=True,
        download_name=shared_file.original_filename,
    )


@files_bp.route("/<int:file_id>/delete", methods=["POST"])
@login_required
def delete(file_id):
    shared_file = SharedFile.query.get_or_404(file_id)
    room = shared_file.room
    if shared_file.user_id != current_user.id and room.created_by_id != current_user.id and not current_user.is_admin:
        flash("You cannot delete this file.", "error")
        return redirect(url_for("rooms.detail", room_id=room.id))
    file_path = Path(current_app.config["UPLOAD_FOLDER"]) / shared_file.stored_filename
    if file_path.exists():
        file_path.unlink()
    db.session.delete(shared_file)
    db.session.commit()
    flash("File deleted.", "success")
    return redirect(url_for("rooms.detail", room_id=room.id))
