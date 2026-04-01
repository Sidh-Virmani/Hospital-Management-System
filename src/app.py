from flask import Flask, render_template, session, redirect, url_for, request
from functools import wraps
from db import get_db_connection
import os

app = Flask(__name__)
app.secret_key = "hospital_project_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SQL_DIR = os.path.join(PROJECT_ROOT, "sql_files")


# =========================================================
# DATABASE HELPERS
# =========================================================
def run_select_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def run_action_query(query, params=None, return_last_id=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid if return_last_id else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def fetch_one(query, params=None):
    rows = run_select_query(query, params)
    return rows[0] if rows else None


# =========================================================
# SESSION / USER HELPERS
# =========================================================
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


# =========================================================
# DASHBOARD CONTENT
# =========================================================
def get_dashboard_sections(role):
    sections = [
        {
            "title": "Browse",
            "actions": [
                {
                    "label": "Available Doctors",
                    "desc": "See all doctors currently marked available.",
                    "endpoint": "available_doctors"
                },
                {
                    "label": "All Doctors",
                    "desc": "View doctor list with specialization and department.",
                    "endpoint": "show_doctors"
                }
            ]
        }
    ]

    if role == "GUEST":
        sections.append(
            {
                "title": "Guest Actions",
                "actions": [
                    {
                        "label": "Login",
                        "desc": "Login with real credentials.",
                        "endpoint": "login"
                    },
                    {
                        "label": "Patient Sign Up",
                        "desc": "Create a patient account.",
                        "endpoint": "signup"
                    }
                ]
            }
        )

    if role == "PATIENT":
        sections.append(
            {
                "title": "Patient Actions",
                "actions": [
                    {
                        "label": "My Appointments",
                        "desc": "View your appointments only.",
                        "endpoint": "show_all_appointments"
                    },
                    {
                        "label": "Book Appointment",
                        "desc": "Schedule an appointment with a doctor.",
                        "endpoint": "book_appointment"
                    },
                    {
                        "label": "My Medical History",
                        "desc": "See your medical records.",
                        "endpoint": "medical_history"
                    },
                    {
                        "label": "My Diagnoses",
                        "desc": "See diagnosis details from your visits.",
                        "endpoint": "patient_diagnoses"
                    },
                    {
                        "label": "My Prescriptions",
                        "desc": "See your prescribed medicines.",
                        "endpoint": "show_all_prescriptions"
                    },
                    {
                        "label": "All Medicines",
                        "desc": "Browse medicine inventory.",
                        "endpoint": "show_all_medicines"
                    }
                ]
            }
        )

    if role == "MEDICAL_STAFF":
        sections.append(
            {
                "title": "Medical Staff Actions",
                "actions": [
                    {
                        "label": "View Patients",
                        "desc": "Browse all registered patients.",
                        "endpoint": "view_patients"
                    },
                    {
                        "label": "All Appointments",
                        "desc": "See all appointments.",
                        "endpoint": "show_all_appointments"
                    },
                    {
                        "label": "Upcoming Appointments",
                        "desc": "See upcoming appointments only.",
                        "endpoint": "show_upcoming_appointments"
                    },
                    {
                        "label": "Add Medical Record",
                        "desc": "Create a new medical record.",
                        "endpoint": "add_medical_record"
                    },
                    {
                        "label": "Add Diagnosis",
                        "desc": "Add diagnosis to an existing record.",
                        "endpoint": "add_diagnosis"
                    },
                    {
                        "label": "Update Appointment Status",
                        "desc": "Mark appointments confirmed/completed/cancelled.",
                        "endpoint": "update_appointment_status"
                    },
                    {
                        "label": "Update Doctor Availability",
                        "desc": "Change doctor status.",
                        "endpoint": "update_doctor_availability"
                    },
                    {
                        "label": "Ward Details",
                        "desc": "View nurse and ward mapping.",
                        "endpoint": "show_ward_details"
                    }
                ]
            }
        )

    if role == "NON_MEDICAL_STAFF":
        sections.append(
            {
                "title": "Non-Medical Staff Actions",
                "actions": [
                    {
                        "label": "Upcoming Appointments",
                        "desc": "See appointment schedule.",
                        "endpoint": "show_upcoming_appointments"
                    },
                    {
                        "label": "Low Medicine Stock",
                        "desc": "Check medicines running low.",
                        "endpoint": "low_medicine_stock"
                    },
                    {
                        "label": "Add Medicine",
                        "desc": "Insert a new medicine item.",
                        "endpoint": "add_medicine"
                    },
                    {
                        "label": "Update Medicine Stock",
                        "desc": "Change stock quantity.",
                        "endpoint": "update_medicine_stock"
                    }
                ]
            }
        )

    if role == "ADMIN":
        sections.extend(
            [
                {
                    "title": "Management",
                    "actions": [
                        {
                            "label": "Register Patient",
                            "desc": "Create a user and patient profile.",
                            "endpoint": "register_patient"
                        },
                        {
                            "label": "Register Medical Staff",
                            "desc": "Create a user and medical staff profile.",
                            "endpoint": "register_medical_staff"
                        },
                        {
                            "label": "Add Doctor Profile",
                            "desc": "Convert an existing DOCTOR staff member into doctor record.",
                            "endpoint": "add_doctor"
                        },
                        {
                            "label": "Add Medicine",
                            "desc": "Create a new medicine entry.",
                            "endpoint": "add_medicine"
                        },
                        {
                            "label": "Update Medicine Stock",
                            "desc": "Change stock quantity.",
                            "endpoint": "update_medicine_stock"
                        }
                    ]
                },
                {
                    "title": "Operations",
                    "actions": [
                        {
                            "label": "Book Appointment",
                            "desc": "Create appointments for any patient.",
                            "endpoint": "book_appointment"
                        },
                        {
                            "label": "Update Appointment Status",
                            "desc": "Update appointment lifecycle.",
                            "endpoint": "update_appointment_status"
                        },
                        {
                            "label": "Add Medical Record",
                            "desc": "Create patient visit record.",
                            "endpoint": "add_medical_record"
                        },
                        {
                            "label": "Add Diagnosis",
                            "desc": "Attach diagnosis to record.",
                            "endpoint": "add_diagnosis"
                        },
                        {
                            "label": "Update Doctor Availability",
                            "desc": "Set doctor to available/busy/etc.",
                            "endpoint": "update_doctor_availability"
                        }
                    ]
                },
                {
                    "title": "Reports & Listings",
                    "actions": [
                        {"label": "All Doctors", "desc": "Doctor listing.", "endpoint": "show_doctors"},
                        {"label": "All Patients", "desc": "Patient listing.", "endpoint": "view_patients"},
                        {"label": "All Staff", "desc": "Medical staff listing.", "endpoint": "show_all_staff"},
                        {"label": "Department Heads", "desc": "Department head mapping.", "endpoint": "department_heads"},
                        {"label": "All Medicines", "desc": "Medicine list.", "endpoint": "show_all_medicines"},
                        {"label": "All Appointments", "desc": "Appointment list.", "endpoint": "show_all_appointments"},
                        {"label": "All Prescriptions", "desc": "Prescription list.", "endpoint": "show_all_prescriptions"},
                        {"label": "All Medical Records", "desc": "Medical record list.", "endpoint": "show_all_medical_records"},
                        {"label": "Patient Appointment Summary", "desc": "Patient-level appointment summary.", "endpoint": "patient_appointment_summary"},
                        {"label": "Ward Details", "desc": "Nurse-ward details.", "endpoint": "show_ward_details"},
                        {"label": "Upcoming Appointments", "desc": "Upcoming appointments only.", "endpoint": "show_upcoming_appointments"},
                        {"label": "Low Medicine Stock", "desc": "Medicines below threshold.", "endpoint": "low_medicine_stock"},
                        {"label": "Show All Users", "desc": "Temporary debugging view.", "endpoint": "show_all_users"}
                    ]
                }
            ]
        )

    return sections


# =========================================================
# AUTH / HOME
# =========================================================
@app.route("/")
def home():
    ensure_session()
    sections = get_dashboard_sections(session["role"])
    return render_template("home.html", sections=sections)


@app.route("/login", methods=["GET", "POST"])
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
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/demo_login/<role>")
def demo_login(role):
    allowed = ["ADMIN", "PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF", "GUEST"]
    if role not in allowed:
        return redirect(url_for("login"))

    session.clear()
    session["role"] = role
    session["username"] = f"Demo {role.title()}"
    session["user_id"] = None
    session["patient_id"] = None
    session["staff_id"] = None
    session["demo_mode"] = True

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    set_guest_session()
    return redirect(url_for("login"))


# =========================================================
# PUBLIC SIGNUP - PATIENT ONLY
# =========================================================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
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

            user = fetch_one("SELECT user_id, username, password, role FROM users WHERE user_id = %s", (user_id,))
            set_logged_in_user(user)

            return render_message(
                "Signup Successful",
                "Your patient account has been created successfully.",
                "success"
            )
        except Exception as e:
            return render_template("signup.html", error=f"Signup failed: {e}")

    return render_template("signup.html")


# =========================================================
# REFRESH TABLES
# =========================================================
@app.route("/refresh_tables")
@role_required("ADMIN")
def refresh_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        schema_path = os.path.join(SQL_DIR, "01_schema.sql")
        sample_path = os.path.join(SQL_DIR, "03_sample_data.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with open(sample_path, "r", encoding="utf-8") as f:
            sample_sql = f.read()

        for query in [q.strip() for q in schema_sql.split(";") if q.strip()]:
            cursor.execute(query)

        for query in [q.strip() for q in sample_sql.split(";") if q.strip()]:
            cursor.execute(query)

        conn.commit()

        return render_message(
            "Database Refreshed",
            "Schema and sample data were loaded successfully.",
            "success"
        )

    except Exception as e:
        conn.rollback()
        return render_message(
            "Refresh Failed",
            f"Database refresh failed: {e}",
            "error"
        )
    finally:
        cursor.close()
        conn.close()


# =========================================================
# EXISTING READ QUERIES
# =========================================================
@app.route("/show_doctors")
def show_doctors():
    query = """
    SELECT 
        d.doctor_id,
        u.username AS doctor_name,
        d.specialization,
        d.availability_status,
        dep.department_name
    FROM doctors d
    JOIN medical_staff ms ON d.staff_id = ms.staff_id
    JOIN users u ON ms.user_id = u.user_id
    LEFT JOIN departments dep ON ms.department_id = dep.department_id
    ORDER BY d.doctor_id;
    """
    data = run_select_query(query)
    return render_template("table.html", title="All Doctors", data=data)


@app.route("/view_patients")
@role_required("MEDICAL_STAFF")
def view_patients():
    query = """
    SELECT 
        patient_id,
        name,
        age,
        gender,
        phone,
        address,
        blood_group
    FROM patients
    ORDER BY patient_id;
    """
    data = run_select_query(query)
    return render_template("table.html", title="All Patients", data=data)


@app.route("/medical_history")
@role_required("PATIENT", "MEDICAL_STAFF")
def medical_history():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view personal history.",
                "error"
            )

        query = """
        SELECT 
            mr.record_id,
            p.name,
            mr.visit_date,
            mr.notes,
            mr.doctor_id
        FROM medical_records mr
        JOIN patients p ON mr.patient_id = p.patient_id
        WHERE mr.patient_id = %s
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query, (patient_id,))
        title = "My Medical History"
    else:
        query = """
        SELECT 
            p.patient_id,
            p.name,
            mr.record_id,
            mr.visit_date,
            mr.notes,
            mr.doctor_id
        FROM medical_records mr
        JOIN patients p ON mr.patient_id = p.patient_id
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query)
        title = "Patient Medical History"

    return render_template("table.html", title=title, data=data)


@app.route("/patient_diagnoses")
@role_required("PATIENT", "MEDICAL_STAFF")
def patient_diagnoses():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view personal diagnoses.",
                "error"
            )

        query = """
        SELECT 
            d.diagnosis_id,
            p.name,
            d.disease,
            d.severity,
            mr.visit_date
        FROM diagnoses d
        JOIN medical_records mr ON d.record_id = mr.record_id
        JOIN patients p ON mr.patient_id = p.patient_id
        WHERE p.patient_id = %s
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query, (patient_id,))
        title = "My Diagnoses"
    else:
        query = """
        SELECT 
            p.patient_id,
            p.name,
            d.disease,
            d.severity,
            mr.visit_date
        FROM diagnoses d
        JOIN medical_records mr ON d.record_id = mr.record_id
        JOIN patients p ON mr.patient_id = p.patient_id
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query)
        title = "Patient Diagnoses"

    return render_template("table.html", title=title, data=data)


@app.route("/department_heads")
@role_required("ADMIN")
def department_heads():
    query = """
    SELECT 
        dep.department_id,
        dep.department_name,
        dep.department_head_id,
        u.username AS head_name,
        d.specialization
    FROM departments dep
    LEFT JOIN doctors d ON dep.department_head_id = d.doctor_id
    LEFT JOIN medical_staff ms ON d.staff_id = ms.staff_id
    LEFT JOIN users u ON ms.user_id = u.user_id
    ORDER BY dep.department_id;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Department Heads", data=data)


@app.route("/show_all_staff")
@role_required("ADMIN")
def show_all_staff():
    query = """
    SELECT 
        ms.staff_id,
        u.username,
        ms.staff_type,
        dep.department_name
    FROM medical_staff ms
    LEFT JOIN users u ON ms.user_id = u.user_id
    LEFT JOIN departments dep ON ms.department_id = dep.department_id
    ORDER BY ms.staff_id;
    """
    data = run_select_query(query)
    return render_template("table.html", title="All Medical Staff", data=data)


@app.route("/show_all_medicines")
@role_required("PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def show_all_medicines():
    query = """
    SELECT 
        medicine_id,
        medicine_name,
        medicine_stock,
        medicine_price,
        medicine_manufacturer
    FROM medicines
    ORDER BY medicine_id;
    """
    data = run_select_query(query)
    return render_template("table.html", title="All Medicines", data=data)


@app.route("/show_all_appointments")
@role_required("PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def show_all_appointments():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view personal appointments.",
                "error"
            )

        query = """
        SELECT 
            a.appointment_id,
            p.name AS patient_name,
            u.username AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.appointment_status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN medical_staff ms ON d.staff_id = ms.staff_id
        JOIN users u ON ms.user_id = u.user_id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date, a.appointment_time;
        """
        data = run_select_query(query, (patient_id,))
        title = "My Appointments"
    else:
        query = """
        SELECT 
            a.appointment_id,
            p.name AS patient_name,
            u.username AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.appointment_status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN medical_staff ms ON d.staff_id = ms.staff_id
        JOIN users u ON ms.user_id = u.user_id
        ORDER BY a.appointment_date, a.appointment_time;
        """
        data = run_select_query(query)
        title = "All Appointments"

    return render_template("table.html", title=title, data=data)


@app.route("/show_all_prescriptions")
@role_required("PATIENT", "MEDICAL_STAFF")
def show_all_prescriptions():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view prescriptions.",
                "error"
            )

        query = """
        SELECT 
            p.prescription_id,
            pat.name AS patient_name,
            m.medicine_name,
            p.frequency,
            p.duration,
            mr.visit_date
        FROM prescriptions p
        JOIN medical_records mr ON p.record_id = mr.record_id
        JOIN patients pat ON mr.patient_id = pat.patient_id
        JOIN medicines m ON p.medicine_id = m.medicine_id
        WHERE pat.patient_id = %s
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query, (patient_id,))
        title = "My Prescriptions"
    else:
        query = """
        SELECT 
            p.prescription_id,
            pat.name AS patient_name,
            m.medicine_name,
            p.frequency,
            p.duration,
            mr.visit_date
        FROM prescriptions p
        JOIN medical_records mr ON p.record_id = mr.record_id
        JOIN patients pat ON mr.patient_id = pat.patient_id
        JOIN medicines m ON p.medicine_id = m.medicine_id
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query)
        title = "All Prescriptions"

    return render_template("table.html", title=title, data=data)


@app.route("/show_all_medical_records")
@role_required("PATIENT", "MEDICAL_STAFF")
def show_all_medical_records():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view medical records.",
                "error"
            )

        query = """
        SELECT 
            mr.record_id,
            p.name AS patient_name,
            mr.doctor_id,
            mr.visit_date,
            mr.notes
        FROM medical_records mr
        JOIN patients p ON mr.patient_id = p.patient_id
        WHERE mr.patient_id = %s
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query, (patient_id,))
        title = "My Medical Records"
    else:
        query = """
        SELECT 
            mr.record_id,
            p.name AS patient_name,
            mr.doctor_id,
            mr.visit_date,
            mr.notes
        FROM medical_records mr
        JOIN patients p ON mr.patient_id = p.patient_id
        ORDER BY mr.visit_date DESC;
        """
        data = run_select_query(query)
        title = "All Medical Records"

    return render_template("table.html", title=title, data=data)


@app.route("/show_all_users")
@role_required("ADMIN")
def show_all_users():
    data = run_select_query("SELECT * FROM users ORDER BY user_id;")
    return render_template("table.html", title="All Users", data=data)


@app.route("/show_ward_details")
@role_required("MEDICAL_STAFF")
def show_ward_details():
    query = """
    SELECT 
        n.nurse_id,
        u.username AS nurse_name,
        w.ward_name,
        w.ward_type
    FROM nurse_wards nw
    JOIN nurses n ON nw.nurse_id = n.nurse_id
    JOIN medical_staff ms ON n.staff_id = ms.staff_id
    JOIN users u ON ms.user_id = u.user_id
    JOIN wards w ON nw.ward_id = w.ward_id
    ORDER BY w.ward_name, u.username;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Ward Details", data=data)


@app.route("/show_upcoming_appointments")
@role_required("MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def show_upcoming_appointments():
    query = """
    SELECT 
        appointment_id,
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        appointment_status
    FROM appointments
    WHERE (
        appointment_date > CURDATE()
        OR (appointment_date = CURDATE() AND appointment_time >= CURTIME())
    )
    AND appointment_status != 'CANCELLED'
    ORDER BY appointment_date, appointment_time;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Upcoming Appointments", data=data)


@app.route("/low_medicine_stock")
@role_required("NON_MEDICAL_STAFF")
def low_medicine_stock():
    query = """
    SELECT *
    FROM medicines
    WHERE medicine_stock < 100
    ORDER BY medicine_stock ASC;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Low Medicine Stock", data=data)


@app.route("/available_doctors")
def available_doctors():
    query = """
    SELECT 
        d.doctor_id,
        u.username AS doctor_name,
        d.specialization,
        d.availability_status,
        dep.department_name
    FROM doctors d
    JOIN medical_staff ms ON d.staff_id = ms.staff_id
    JOIN users u ON ms.user_id = u.user_id
    LEFT JOIN departments dep ON ms.department_id = dep.department_id
    WHERE d.availability_status = 'AVAILABLE'
    ORDER BY dep.department_name, u.username;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Available Doctors", data=data)


@app.route("/patient_appointment_summary")
@role_required("MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def patient_appointment_summary():
    query = """
    SELECT 
        p.patient_id,
        p.name,
        COUNT(CASE WHEN a.appointment_status = 'COMPLETED' THEN 1 END) AS total_completed_appointments,
        CASE
            WHEN MIN(
                CASE
                    WHEN (
                        a.appointment_date > CURDATE()
                        OR (a.appointment_date = CURDATE() AND a.appointment_time >= CURTIME())
                    )
                    THEN CONCAT(a.appointment_date, ' ', a.appointment_time)
                    ELSE NULL
                END
            ) IS NOT NULL THEN 'YES'
            ELSE 'NO'
        END AS has_upcoming_appointment,
        MIN(
            CASE
                WHEN (
                    a.appointment_date > CURDATE()
                    OR (a.appointment_date = CURDATE() AND a.appointment_time >= CURTIME())
                )
                THEN CONCAT(a.appointment_date, ' ', a.appointment_time)
                ELSE NULL
            END
        ) AS next_appointment
    FROM patients p
    LEFT JOIN appointments a ON p.patient_id = a.patient_id
    GROUP BY p.patient_id, p.name
    ORDER BY p.name;
    """
    data = run_select_query(query)
    return render_template("table.html", title="Patient Appointment Summary", data=data)


# =========================================================
# OPTION BUILDERS FOR FORMS
# =========================================================
def get_patient_options():
    rows = run_select_query("SELECT patient_id, name FROM patients ORDER BY name;")
    return [{"value": row["patient_id"], "label": f'{row["patient_id"]} - {row["name"]}'} for row in rows]


def get_department_options():
    rows = run_select_query("SELECT department_id, department_name FROM departments ORDER BY department_name;")
    options = [{"value": "", "label": "No Department"}]
    options.extend(
        [{"value": row["department_id"], "label": f'{row["department_id"]} - {row["department_name"]}'} for row in rows]
    )
    return options


def get_available_doctor_options():
    rows = run_select_query("""
        SELECT d.doctor_id, u.username AS doctor_name, d.specialization
        FROM doctors d
        JOIN medical_staff ms ON d.staff_id = ms.staff_id
        JOIN users u ON ms.user_id = u.user_id
        WHERE d.availability_status = 'AVAILABLE'
        ORDER BY u.username;
    """)
    return [
        {"value": row["doctor_id"], "label": f'{row["doctor_id"]} - {row["doctor_name"]} ({row["specialization"]})'}
        for row in rows
    ]


def get_all_doctor_options():
    rows = run_select_query("""
        SELECT d.doctor_id, u.username AS doctor_name, d.specialization, d.availability_status
        FROM doctors d
        JOIN medical_staff ms ON d.staff_id = ms.staff_id
        JOIN users u ON ms.user_id = u.user_id
        ORDER BY u.username;
    """)
    return [
        {
            "value": row["doctor_id"],
            "label": f'{row["doctor_id"]} - {row["doctor_name"]} ({row["specialization"]}) [{row["availability_status"]}]'
        }
        for row in rows
    ]


def get_record_options():
    rows = run_select_query("""
        SELECT mr.record_id, p.name, mr.visit_date
        FROM medical_records mr
        JOIN patients p ON mr.patient_id = p.patient_id
        ORDER BY mr.record_id DESC;
    """)
    return [
        {"value": row["record_id"], "label": f'{row["record_id"]} - {row["name"]} ({row["visit_date"]})'}
        for row in rows
    ]


def get_medicine_options():
    rows = run_select_query("""
        SELECT medicine_id, medicine_name, medicine_stock
        FROM medicines
        ORDER BY medicine_name;
    """)
    return [
        {"value": row["medicine_id"], "label": f'{row["medicine_id"]} - {row["medicine_name"]} [Stock: {row["medicine_stock"]}]'}
        for row in rows
    ]


def get_appointment_options():
    rows = run_select_query("""
        SELECT a.appointment_id, p.name, a.appointment_date, a.appointment_time, a.appointment_status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC;
    """)
    return [
        {
            "value": row["appointment_id"],
            "label": f'{row["appointment_id"]} - {row["name"]} - {row["appointment_date"]} {row["appointment_time"]} [{row["appointment_status"]}]'
        }
        for row in rows
    ]


# =========================================================
# CREATE / UPDATE ROUTES
# =========================================================
@app.route("/register_patient", methods=["GET", "POST"])
@role_required("ADMIN")
def register_patient():
    if request.method == "POST":
        try:
            username = request.form["username"].strip()
            password = request.form["password"].strip()
            name = request.form["name"].strip()
            age = request.form.get("age", "").strip()
            gender = request.form.get("gender", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            blood_group = request.form.get("blood_group", "").strip()

            if fetch_one("SELECT user_id FROM users WHERE username = %s", (username,)):
                return render_message("Patient Registration Failed", "Username already exists.", "error")

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

            return render_message("Patient Registered", "Patient account created successfully.", "success")
        except Exception as e:
            return render_message("Patient Registration Failed", str(e), "error")

    fields = [
        {"name": "username", "label": "Username", "type": "text", "required": True},
        {"name": "password", "label": "Password", "type": "password", "required": True},
        {"name": "name", "label": "Patient Name", "type": "text", "required": True},
        {"name": "age", "label": "Age", "type": "number"},
        {"name": "gender", "label": "Gender", "type": "text"},
        {"name": "phone", "label": "Phone", "type": "text"},
        {"name": "address", "label": "Address", "type": "textarea"},
        {"name": "blood_group", "label": "Blood Group", "type": "text"}
    ]
    return render_template("form.html", title="Register Patient", fields=fields, submit_label="Create Patient")


@app.route("/register_medical_staff", methods=["GET", "POST"])
@role_required("ADMIN")
def register_medical_staff():
    if request.method == "POST":
        try:
            username = request.form["username"].strip()
            password = request.form["password"].strip()
            staff_type = request.form["staff_type"].strip()
            department_id = request.form.get("department_id", "").strip()

            if fetch_one("SELECT user_id FROM users WHERE username = %s", (username,)):
                return render_message("Registration Failed", "Username already exists.", "error")

            user_id = run_action_query(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, "MEDICAL_STAFF"),
                return_last_id=True
            )

            run_action_query(
                """
                INSERT INTO medical_staff (user_id, staff_type, department_id)
                VALUES (%s, %s, %s)
                """,
                (
                    user_id,
                    staff_type,
                    int(department_id) if department_id else None
                )
            )

            return render_message("Medical Staff Registered", "Medical staff account created successfully.", "success")
        except Exception as e:
            return render_message("Registration Failed", str(e), "error")

    fields = [
        {"name": "username", "label": "Username", "type": "text", "required": True},
        {"name": "password", "label": "Password", "type": "password", "required": True},
        {
            "name": "staff_type",
            "label": "Staff Type",
            "type": "select",
            "required": True,
            "options": [
                {"value": "DOCTOR", "label": "DOCTOR"},
                {"value": "NURSE", "label": "NURSE"}
            ]
        },
        {
            "name": "department_id",
            "label": "Department",
            "type": "select",
            "options": get_department_options()
        }
    ]
    return render_template("form.html", title="Register Medical Staff", fields=fields, submit_label="Create Medical Staff")


@app.route("/add_doctor", methods=["GET", "POST"])
@role_required("ADMIN")
def add_doctor():
    if request.method == "POST":
        try:
            staff_id = request.form["staff_id"]
            specialization = request.form["specialization"].strip()
            availability_status = request.form["availability_status"].strip()

            run_action_query(
                """
                INSERT INTO doctors (staff_id, specialization, availability_status)
                VALUES (%s, %s, %s)
                """,
                (staff_id, specialization, availability_status)
            )

            return render_message("Doctor Added", "Doctor profile created successfully.", "success")
        except Exception as e:
            return render_message("Doctor Creation Failed", str(e), "error")

    staff_rows = run_select_query("""
        SELECT ms.staff_id, u.username
        FROM medical_staff ms
        JOIN users u ON ms.user_id = u.user_id
        LEFT JOIN doctors d ON ms.staff_id = d.staff_id
        WHERE ms.staff_type = 'DOCTOR' AND d.doctor_id IS NULL
        ORDER BY u.username;
    """)

    staff_options = [
        {"value": row["staff_id"], "label": f'{row["staff_id"]} - {row["username"]}'}
        for row in staff_rows
    ]

    fields = [
        {"name": "staff_id", "label": "Medical Staff (DOCTOR type)", "type": "select", "required": True, "options": staff_options},
        {"name": "specialization", "label": "Specialization", "type": "text", "required": True},
        {
            "name": "availability_status",
            "label": "Availability Status",
            "type": "select",
            "required": True,
            "options": [
                {"value": "AVAILABLE", "label": "AVAILABLE"},
                {"value": "BUSY", "label": "BUSY"},
                {"value": "ON LEAVE", "label": "ON LEAVE"},
                {"value": "OFF DUTY", "label": "OFF DUTY"}
            ]
        }
    ]
    return render_template("form.html", title="Add Doctor Profile", fields=fields, submit_label="Create Doctor")


@app.route("/book_appointment", methods=["GET", "POST"])
@role_required("PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def book_appointment():
    role = session.get("role")
    patient_id = session.get("patient_id")

    if request.method == "POST":
        try:
            if role == "PATIENT":
                if not patient_id:
                    return render_message(
                        "Booking Failed",
                        "Demo patient role is not linked to a real patient record. Use a real patient login.",
                        "error"
                    )
                selected_patient_id = patient_id
            else:
                selected_patient_id = request.form["patient_id"]

            doctor_id = request.form["doctor_id"]
            appointment_date = request.form["appointment_date"]
            appointment_time = request.form["appointment_time"]
            appointment_status = request.form["appointment_status"]

            run_action_query(
                """
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, appointment_status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (selected_patient_id, doctor_id, appointment_date, appointment_time, appointment_status)
            )

            return render_message("Appointment Booked", "Appointment created successfully.", "success")
        except Exception as e:
            return render_message("Booking Failed", str(e), "error")

    fields = []

    if role == "PATIENT":
        fields.append(
            {
                "name": "patient_note",
                "label": "Patient",
                "type": "readonly_text",
                "value": f"Logged-in patient ID: {patient_id}" if patient_id else "No linked patient profile"
            }
        )
    else:
        fields.append(
            {
                "name": "patient_id",
                "label": "Patient",
                "type": "select",
                "required": True,
                "options": get_patient_options()
            }
        )

    fields.extend([
        {
            "name": "doctor_id",
            "label": "Doctor",
            "type": "select",
            "required": True,
            "options": get_available_doctor_options()
        },
        {"name": "appointment_date", "label": "Appointment Date", "type": "date", "required": True},
        {"name": "appointment_time", "label": "Appointment Time", "type": "time", "required": True},
        {
            "name": "appointment_status",
            "label": "Initial Status",
            "type": "select",
            "required": True,
            "options": [
                {"value": "PENDING", "label": "PENDING"},
                {"value": "CONFIRMED", "label": "CONFIRMED"}
            ]
        }
    ])

    return render_template("form.html", title="Book Appointment", fields=fields, submit_label="Book Appointment")


@app.route("/update_appointment_status", methods=["GET", "POST"])
@role_required("MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def update_appointment_status():
    if request.method == "POST":
        try:
            appointment_id = request.form["appointment_id"]
            appointment_status = request.form["appointment_status"]

            run_action_query(
                """
                UPDATE appointments
                SET appointment_status = %s
                WHERE appointment_id = %s
                """,
                (appointment_status, appointment_id)
            )

            return render_message("Appointment Updated", "Appointment status updated successfully.", "success")
        except Exception as e:
            return render_message("Update Failed", str(e), "error")

    fields = [
        {
            "name": "appointment_id",
            "label": "Appointment",
            "type": "select",
            "required": True,
            "options": get_appointment_options()
        },
        {
            "name": "appointment_status",
            "label": "New Status",
            "type": "select",
            "required": True,
            "options": [
                {"value": "PENDING", "label": "PENDING"},
                {"value": "CONFIRMED", "label": "CONFIRMED"},
                {"value": "CANCELLED", "label": "CANCELLED"},
                {"value": "COMPLETED", "label": "COMPLETED"}
            ]
        }
    ]
    return render_template("form.html", title="Update Appointment Status", fields=fields, submit_label="Update Status")


@app.route("/add_medical_record", methods=["GET", "POST"])
@role_required("MEDICAL_STAFF")
def add_medical_record():
    if request.method == "POST":
        try:
            patient_id = request.form["patient_id"]
            doctor_id = request.form["doctor_id"]
            visit_date = request.form["visit_date"]
            notes = request.form.get("notes", "").strip()

            run_action_query(
                """
                INSERT INTO medical_records (patient_id, doctor_id, visit_date, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (patient_id, doctor_id, visit_date, notes)
            )

            return render_message("Medical Record Added", "Medical record created successfully.", "success")
        except Exception as e:
            return render_message("Creation Failed", str(e), "error")

    fields = [
        {"name": "patient_id", "label": "Patient", "type": "select", "required": True, "options": get_patient_options()},
        {"name": "doctor_id", "label": "Doctor", "type": "select", "required": True, "options": get_all_doctor_options()},
        {"name": "visit_date", "label": "Visit Date", "type": "date", "required": True},
        {"name": "notes", "label": "Notes", "type": "textarea"}
    ]
    return render_template("form.html", title="Add Medical Record", fields=fields, submit_label="Create Record")


@app.route("/add_diagnosis", methods=["GET", "POST"])
@role_required("MEDICAL_STAFF")
def add_diagnosis():
    if request.method == "POST":
        try:
            record_id = request.form["record_id"]
            disease = request.form["disease"].strip()
            severity = request.form["severity"].strip()

            run_action_query(
                """
                INSERT INTO diagnoses (record_id, disease, severity)
                VALUES (%s, %s, %s)
                """,
                (record_id, disease, severity)
            )

            return render_message("Diagnosis Added", "Diagnosis created successfully.", "success")
        except Exception as e:
            return render_message("Creation Failed", str(e), "error")

    fields = [
        {"name": "record_id", "label": "Medical Record", "type": "select", "required": True, "options": get_record_options()},
        {"name": "disease", "label": "Disease", "type": "text", "required": True},
        {"name": "severity", "label": "Severity", "type": "text", "required": True}
    ]
    return render_template("form.html", title="Add Diagnosis", fields=fields, submit_label="Create Diagnosis")


@app.route("/add_medicine", methods=["GET", "POST"])
@role_required("NON_MEDICAL_STAFF")
def add_medicine():
    if request.method == "POST":
        try:
            medicine_name = request.form["medicine_name"].strip()
            medicine_stock = request.form["medicine_stock"]
            medicine_price = request.form["medicine_price"]
            medicine_manufacturer = request.form["medicine_manufacturer"].strip()

            run_action_query(
                """
                INSERT INTO medicines (medicine_name, medicine_stock, medicine_price, medicine_manufacturer)
                VALUES (%s, %s, %s, %s)
                """,
                (medicine_name, medicine_stock, medicine_price, medicine_manufacturer)
            )

            return render_message("Medicine Added", "Medicine created successfully.", "success")
        except Exception as e:
            return render_message("Creation Failed", str(e), "error")

    fields = [
        {"name": "medicine_name", "label": "Medicine Name", "type": "text", "required": True},
        {"name": "medicine_stock", "label": "Initial Stock", "type": "number", "required": True},
        {"name": "medicine_price", "label": "Price", "type": "number", "required": True},
        {"name": "medicine_manufacturer", "label": "Manufacturer", "type": "text", "required": True}
    ]
    return render_template("form.html", title="Add Medicine", fields=fields, submit_label="Create Medicine")


@app.route("/update_medicine_stock", methods=["GET", "POST"])
@role_required("NON_MEDICAL_STAFF")
def update_medicine_stock():
    if request.method == "POST":
        try:
            medicine_id = request.form["medicine_id"]
            medicine_stock = request.form["medicine_stock"]

            run_action_query(
                """
                UPDATE medicines
                SET medicine_stock = %s
                WHERE medicine_id = %s
                """,
                (medicine_stock, medicine_id)
            )

            return render_message("Medicine Stock Updated", "Medicine stock updated successfully.", "success")
        except Exception as e:
            return render_message("Update Failed", str(e), "error")

    fields = [
        {"name": "medicine_id", "label": "Medicine", "type": "select", "required": True, "options": get_medicine_options()},
        {"name": "medicine_stock", "label": "New Stock Quantity", "type": "number", "required": True}
    ]
    return render_template("form.html", title="Update Medicine Stock", fields=fields, submit_label="Update Stock")


@app.route("/update_doctor_availability", methods=["GET", "POST"])
@role_required("MEDICAL_STAFF")
def update_doctor_availability():
    if request.method == "POST":
        try:
            doctor_id = request.form["doctor_id"]
            availability_status = request.form["availability_status"]

            run_action_query(
                """
                UPDATE doctors
                SET availability_status = %s
                WHERE doctor_id = %s
                """,
                (availability_status, doctor_id)
            )

            return render_message("Doctor Availability Updated", "Doctor availability updated successfully.", "success")
        except Exception as e:
            return render_message("Update Failed", str(e), "error")

    fields = [
        {"name": "doctor_id", "label": "Doctor", "type": "select", "required": True, "options": get_all_doctor_options()},
        {
            "name": "availability_status",
            "label": "New Availability Status",
            "type": "select",
            "required": True,
            "options": [
                {"value": "AVAILABLE", "label": "AVAILABLE"},
                {"value": "BUSY", "label": "BUSY"},
                {"value": "ON LEAVE", "label": "ON LEAVE"},
                {"value": "OFF DUTY", "label": "OFF DUTY"}
            ]
        }
    ]
    return render_template("form.html", title="Update Doctor Availability", fields=fields, submit_label="Update Availability")


if __name__ == "__main__":
    app.run(debug=True)