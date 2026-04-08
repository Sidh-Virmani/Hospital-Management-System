from flask import Blueprint, render_template, request, session

from ..db_helpers import fetch_one, run_action_query
from ..form_options import (
    get_patient_options,
    get_department_options,
    get_available_doctor_options,
    get_all_doctor_options,
    get_record_options,
    get_medicine_options,
    get_appointment_options,
    get_unassigned_doctor_staff_options,
)
from ..session_helpers import role_required, render_message

actions_bp = Blueprint("actions_bp", __name__)


@actions_bp.route("/register_patient", methods=["GET", "POST"])
@role_required("ADMIN")
def register_patient():
    if request.method == "POST":
        try:
            username = request.form["username"].strip()
            password = request.form["password"].strip()
            name = request.form["name"].strip()
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


@actions_bp.route("/register_medical_staff", methods=["GET", "POST"])
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


@actions_bp.route("/add_doctor", methods=["GET", "POST"])
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

    fields = [
        {
            "name": "staff_id",
            "label": "Medical Staff (DOCTOR type)",
            "type": "select",
            "required": True,
            "options": get_unassigned_doctor_staff_options()
        },
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


@actions_bp.route("/book_appointment", methods=["GET", "POST"])
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


@actions_bp.route("/update_appointment_status", methods=["GET", "POST"])
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


@actions_bp.route("/add_medical_record", methods=["GET", "POST"])
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


@actions_bp.route("/add_diagnosis", methods=["GET", "POST"])
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


@actions_bp.route("/add_medicine", methods=["GET", "POST"])
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


@actions_bp.route("/update_medicine_stock", methods=["GET", "POST"])
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


@actions_bp.route("/update_doctor_availability", methods=["GET", "POST"])
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