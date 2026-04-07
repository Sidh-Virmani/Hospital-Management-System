import os
from flask import Blueprint, render_template, request, session, current_app

from ..db import get_db_connection
from ..db_helpers import run_select_query
from ..session_helpers import role_required, render_message

read_bp = Blueprint("read_bp", __name__)


@read_bp.route("/refresh_tables")
@role_required("ADMIN")
def refresh_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql_dir = current_app.config["SQL_DIR"]
        schema_path = os.path.join(sql_dir, "01_schema.sql")
        sample_path = os.path.join(sql_dir, "03_sample_data.sql")

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


@read_bp.route("/show_doctors")
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


@read_bp.route("/view_patients")
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


@read_bp.route("/medical_history")
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


@read_bp.route("/patient_diagnoses")
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


@read_bp.route("/department_heads")
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


@read_bp.route("/show_all_staff")
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


@read_bp.route("/show_all_medicines")
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


@read_bp.route("/show_all_appointments")
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


@read_bp.route("/show_all_prescriptions")
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


@read_bp.route("/show_all_medical_records")
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


@read_bp.route("/show_all_users")
@role_required("ADMIN")
def show_all_users():
    data = run_select_query("SELECT * FROM users ORDER BY user_id;")
    return render_template("table.html", title="All Users", data=data)


@read_bp.route("/show_ward_details")
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


@read_bp.route("/show_upcoming_appointments")
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


@read_bp.route("/low_medicine_stock")
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


@read_bp.route("/available_doctors")
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


@read_bp.route("/patient_appointment_summary")
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


# ---------------------------------------------------------
# NEW BACKEND ROUTES FOR FUTURE BETTER UI
# These do not break old code. They are extra filtered pages.
# ---------------------------------------------------------

@read_bp.route("/doctor_directory")
def doctor_directory():
    specialization = request.args.get("specialization", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()
    search_text = request.args.get("search", "").strip()

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
    WHERE 1=1
    """
    params = []

    if specialization:
        query += " AND d.specialization = %s"
        params.append(specialization)

    if department:
        query += " AND dep.department_name = %s"
        params.append(department)

    if status:
        query += " AND d.availability_status = %s"
        params.append(status)

    if search_text:
        query += " AND (u.username LIKE %s OR d.specialization LIKE %s OR dep.department_name LIKE %s)"
        like_value = f"%{search_text}%"
        params.extend([like_value, like_value, like_value])

    query += " ORDER BY dep.department_name, u.username;"

    data = run_select_query(query, tuple(params) if params else None)
    return render_template("table.html", title="Doctor Directory", data=data)


@read_bp.route("/patient_directory")
@role_required("MEDICAL_STAFF")
def patient_directory():
    gender = request.args.get("gender", "").strip()
    blood_group = request.args.get("blood_group", "").strip()
    search_text = request.args.get("search", "").strip()

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
    WHERE 1=1
    """
    params = []

    if gender:
        query += " AND gender = %s"
        params.append(gender)

    if blood_group:
        query += " AND blood_group = %s"
        params.append(blood_group)

    if search_text:
        query += " AND (name LIKE %s OR phone LIKE %s OR address LIKE %s)"
        like_value = f"%{search_text}%"
        params.extend([like_value, like_value, like_value])

    query += " ORDER BY name;"

    data = run_select_query(query, tuple(params) if params else None)
    return render_template("table.html", title="Patient Directory", data=data)


@read_bp.route("/medicine_inventory")
@role_required("PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def medicine_inventory():
    manufacturer = request.args.get("manufacturer", "").strip()
    low_stock_only = request.args.get("low_stock", "").strip()
    search_text = request.args.get("search", "").strip()

    query = """
    SELECT
        medicine_id,
        medicine_name,
        medicine_stock,
        medicine_price,
        medicine_manufacturer
    FROM medicines
    WHERE 1=1
    """
    params = []

    if manufacturer:
        query += " AND medicine_manufacturer = %s"
        params.append(manufacturer)

    if low_stock_only == "1":
        query += " AND medicine_stock < 100"

    if search_text:
        query += " AND (medicine_name LIKE %s OR medicine_manufacturer LIKE %s)"
        like_value = f"%{search_text}%"
        params.extend([like_value, like_value])

    query += " ORDER BY medicine_name;"

    data = run_select_query(query, tuple(params) if params else None)
    return render_template("table.html", title="Medicine Inventory", data=data)


@read_bp.route("/appointment_hub")
@role_required("PATIENT", "MEDICAL_STAFF", "NON_MEDICAL_STAFF")
def appointment_hub():
    role = session.get("role")
    patient_id = session.get("patient_id")

    status = request.args.get("status", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    doctor_name = request.args.get("doctor_name", "").strip()

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
    WHERE 1=1
    """
    params = []

    if role == "PATIENT":
        if not patient_id:
            return render_message(
                "Patient Profile Missing",
                "This demo patient session is not linked to a real patient record. Use a real patient login to view personal appointments.",
                "error"
            )
        query += " AND a.patient_id = %s"
        params.append(patient_id)

    if status:
        query += " AND a.appointment_status = %s"
        params.append(status)

    if date_from:
        query += " AND a.appointment_date >= %s"
        params.append(date_from)

    if date_to:
        query += " AND a.appointment_date <= %s"
        params.append(date_to)

    if doctor_name:
        query += " AND u.username LIKE %s"
        params.append(f"%{doctor_name}%")

    query += " ORDER BY a.appointment_date, a.appointment_time;"

    data = run_select_query(query, tuple(params) if params else None)
    return render_template("table.html", title="Appointment Hub", data=data)