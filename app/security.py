from secrets import token_urlsafe

from flask import abort, request, session


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def register_security(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_post_requests():
        if app.config.get("WTF_CSRF_ENABLED") is False:
            return
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        expected = session.get("_csrf_token")
        received = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        if not expected or not received or expected != received:
            abort(400)
