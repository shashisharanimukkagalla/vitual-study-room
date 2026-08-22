from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Notification, Room, RoomMember, StudySession, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    memberships = RoomMember.query.filter_by(user_id=current_user.id).all()
    my_rooms = [membership.room for membership in memberships]
    public_rooms = Room.query.filter_by(is_private=False).order_by(Room.created_at.desc()).limit(8).all()
    sessions = StudySession.query.filter_by(user_id=current_user.id).all()
    total_minutes = sum(session.duration_minutes for session in sessions)
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )
    today = date.today()
    return render_template(
        "dashboard.html",
        my_rooms=my_rooms,
        public_rooms=public_rooms,
        total_minutes=total_minutes,
        notifications=notifications,
        today=today,
    )


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        if not username or not email:
            flash("Username and email are required.", "error")
        elif User.query.filter(User.id != current_user.id, User.username == username).first():
            flash("Username is already taken.", "error")
        elif User.query.filter(User.id != current_user.id, User.email == email).first():
            flash("Email is already taken.", "error")
        elif new_password and not current_user.check_password(current_password):
            flash("Current password is required to change password.", "error")
        else:
            current_user.username = username
            current_user.email = email
            if new_password:
                current_user.set_password(new_password)
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("main.profile"))
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.started_at.desc()).all()
    total_minutes = sum(session.duration_minutes for session in sessions)
    return render_template("profile.html", sessions=sessions, total_minutes=total_minutes)


@main_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return redirect(url_for("main.dashboard"))
