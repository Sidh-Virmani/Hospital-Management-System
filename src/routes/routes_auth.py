from flask import Blueprint, render_template, session, redirect, url_for, request

from ..db_helpers import fetch_one, run_action_query
from ..session_helpers import ensure_session, set_logged_in_user, set_guest_session, render_message

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    ensure_session()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template("login.html", error="Please enter both username and password.")

        user = fetch_one(
            "SELECT user_id, username, password, role FROM users WHERE username = %s",
            (username,)
        )

        if not user or user["password"] != password:
            return render_template("login.html", error="Invalid username or password.")

        set_logged_in_user(user)

        if user["role"] == "MEDICAL_STAFF":
            doctor = fetch_one(
                """
                SELECT d.doctor_id
                FROM doctors d
                JOIN medical_staff ms ON d.staff_id = ms.staff_id
                WHERE ms.user_id = %s
                """,
                (user["user_id"],)
            )
            if doctor:
                session["doctor_id"] = doctor["doctor_id"]
        return redirect(url_for("home"))

    return render_template("login.html")


@auth_bp.route("/demo_login/<role>")
def demo_login(role):
    allowed = ["ADMIN", "PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF", "GUEST"]
    if role not in allowed:
        return redirect(url_for("auth_bp.login"))

    session.clear()
    session["role"] = role
    session["username"] = f"Demo {role.title()}"
    session["user_id"] = None
    session["patient_id"] = None
    session["staff_id"] = None
    session["demo_mode"] = True

    return redirect(url_for("home"))


@auth_bp.route("/logout")
def logout():
    set_guest_session()
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        if age: 
                age = int(age)
                if age < 0 or age > 130:
                    return render_message(
                        "Invalid Age",
                        "Age must be between 0 and 130",
                        "error"
                    )
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        blood_group = request.form.get("blood_group", "").strip()

        if not username or not password or not name:
            return render_template("signup.html", error="Username, password, and patient name are required.")

        existing = fetch_one("SELECT user_id FROM users WHERE username = %s", (username,))
        if existing:
            return render_template("signup.html", error="Username already exists.")

        try:
            user_id = run_action_query(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, "PATIENT"),
                return_last_id=True
            )

            run_action_query(
                """
                INSERT INTO patients (user_id, name, age, gender, phone, address, blood_group)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    name,
                    int(age) if age else None,
                    gender if gender else None,
                    phone if phone else None,
                    address if address else None,
                    blood_group if blood_group else None
                )
            )

            user = fetch_one(
                "SELECT user_id, username, password, role FROM users WHERE user_id = %s",
                (user_id,)
            )
            set_logged_in_user(user)

            return render_message(
                "Signup Successful",
                "Your patient account has been created successfully.",
                "success"
            )
        except Exception as e:
            return render_template("signup.html", error=f"Signup failed: {e}")

    return render_template("signup.html")