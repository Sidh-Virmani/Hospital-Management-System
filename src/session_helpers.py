from functools import wraps
from flask import session, render_template

from .db_helpers import fetch_one


def set_guest_session():
    session.clear()
    session["role"] = "GUEST"
    session["username"] = "Guest"
    session["user_id"] = None
    session["patient_id"] = None
    session["staff_id"] = None
    session["demo_mode"] = False


def set_logged_in_user(user):
    session.clear()
    session["role"] = user["role"]
    session["username"] = user["username"]
    session["user_id"] = user["user_id"]
    session["demo_mode"] = False

    patient = fetch_one(
        "SELECT patient_id FROM patients WHERE user_id = %s",
        (user["user_id"],)
    )
    staff = fetch_one(
        "SELECT staff_id FROM medical_staff WHERE user_id = %s",
        (user["user_id"],)
    )

    session["patient_id"] = patient["patient_id"] if patient else None
    session["staff_id"] = staff["staff_id"] if staff else None


def ensure_session():
    if "role" not in session:
        set_guest_session()


def render_message(title, message, kind="info"):
    return render_template("message.html", title=title, message=message, kind=kind)


def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ensure_session()
            current_role = session.get("role", "GUEST")

            # Admin can access everything
            if current_role == "ADMIN":
                return func(*args, **kwargs)

            if current_role not in allowed_roles:
                return render_message(
                    "Access Denied",
                    f"This page is only available to: {', '.join(allowed_roles)}",
                    "error"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator