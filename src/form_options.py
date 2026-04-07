from .db_helpers import run_select_query


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


def get_unassigned_doctor_staff_options():
    rows = run_select_query("""
        SELECT ms.staff_id, u.username
        FROM medical_staff ms
        JOIN users u ON ms.user_id = u.user_id
        LEFT JOIN doctors d ON ms.staff_id = d.staff_id
        WHERE ms.staff_type = 'DOCTOR' AND d.doctor_id IS NULL
        ORDER BY u.username;
    """)
    return [
        {"value": row["staff_id"], "label": f'{row["staff_id"]} - {row["username"]}'}
        for row in rows
    ]