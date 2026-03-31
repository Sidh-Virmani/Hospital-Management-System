from flask import Flask, render_template, session, redirect, url_for, request
from db import get_db_connection

# Create Flask app
app = Flask(__name__)

# Secret key is needed for using session
app.secret_key = "hospital_project_secret_key"


# ---------------------------------------------------------
# HOME PAGE
# This is the starting page of our website.
# It shows current role and all available buttons.
# ---------------------------------------------------------
@app.route("/")
def home():
    # If no role is selected yet, we keep it as GUEST
    if "role" not in session:
        session["role"] = "GUEST"

    return render_template("home.html", role=session["role"])


# ---------------------------------------------------------
# ROLE SWITCH ROUTE
# For now, since we are keeping project minimal,
# we do not make full login system.
# Instead, clicking a link will set the role in session.
# Later this can be replaced with real login.
# ---------------------------------------------------------
@app.route("/set_role/<role>")
def set_role(role):
    allowed_roles = ["ADMIN", "PATIENT", "MEDICAL_STAFF", "GUEST"]

    if role in allowed_roles:
        session["role"] = role

    return redirect(url_for("home"))


# ---------------------------------------------------------
# LOGOUT / RESET ROLE
# This resets current role back to GUEST.
# ---------------------------------------------------------
@app.route("/logout")
def logout():
    session["role"] = "GUEST"
    return redirect(url_for("home"))


# ---------------------------------------------------------
# HELPER FUNCTION
# This function runs a SELECT query and returns all rows.
# We use dictionary=True so each row behaves like:
# {"column_name": value}
# which makes HTML display easier.
# ---------------------------------------------------------
def run_select_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# ---------------------------------------------------------
# HELPER FUNCTION
# This function runs an INSERT, UPDATE, or DELETE query and commits the transaction.
# ---------------------------------------------------------
def run_insert_query(query, params=None):
    """
    Args:
        query (str): The SQL query string.
        params (tuple, optional): A tuple of parameters to safely inject into the query. 
    Returns:
        int: The ID of the last inserted row (if applicable).
    """
    conn = get_db_connection()
    # We do not need dictionary=True here because we aren't fetching rows
    cursor = conn.cursor()

    try:
        # Using params prevents SQL injection vulnerabilities
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Crucial step: Commit the transaction to save changes to the database
        conn.commit()
        
        # Capture the ID of the newly inserted row
        last_inserted_id = cursor.lastrowid
        
    except Exception as e:
        # If something goes wrong, rollback the transaction
        conn.rollback()
        print(f"Error executing query: {e}")
        raise e
        
    finally:
        # Ensure cleanup always happens, even if an error occurred
        cursor.close()
        conn.close()

    return last_inserted_id



# =========================================================
# SIGN UP
# =========================================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if not username or not password or not role:
            return render_template('signup.html', error="Please fill all the fields")
        
        users = run_select_query("SELECT username FROM users WHERE username = %s", (username,))
        
        if users:
            return render_template('signup.html', error="Username already exists")

        try:
            query = """
            INSERT INTO users (username, password, role) VALUES (%s, %s, %s);
            """
            run_insert_query(query, (username, password, role))
        except Exception as e:
            return render_template('signup.html', error="some error occured")
        finally:
            return render_template('home.html')
    # Render form on GET request
    return render_template('signup.html')

# =========================================================
# QUERY 1
# UI Button: Show All Doctors
# Role allowed: ADMIN, PATIENT
# =========================================================
@app.route("/show_doctors")
def show_doctors():

    query = """
    SELECT 
        d.doctor_id,
        d.specialization,
        d.availability_status,
        dep.department_name
    FROM doctors d
    JOIN medical_staff ms
        ON d.staff_id = ms.staff_id
    LEFT JOIN departments dep
        ON ms.department_id = dep.department_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Doctors",
        data=data
    )


# =========================================================
# QUERY 2
# UI Button: View All Patients
# Role allowed: ADMIN, MEDICAL_STAFF
# =========================================================
@app.route("/view_patients")
def view_patients():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF"]:
        return "Access Denied: Only ADMIN or MEDICAL_STAFF can view patients."

    query = """
    SELECT 
        patient_id,
        name,
        age,
        gender,
        phone,
        blood_group
    FROM patients;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Patients",
        data=data
    )


# =========================================================
# QUERY 3
# UI Button: View Patient Medical History
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT
# =========================================================
@app.route("/medical_history")
def medical_history():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, or PATIENT can view medical history."

    query = """
    SELECT 
        p.patient_id,
        p.name,
        mr.record_id,
        mr.visit_date,
        mr.notes,
        mr.doctor_id
    FROM medical_records mr
    JOIN patients p
        ON mr.patient_id = p.patient_id
    ORDER BY mr.visit_date DESC;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="Patient Medical History",
        data=data
    )


# =========================================================
# QUERY 4
# UI Button: View Patient Diagnoses
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT
# =========================================================
@app.route("/patient_diagnoses")
def patient_diagnoses():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, or PATIENT can view diagnoses."

    query = """
    SELECT 
        p.patient_id,
        p.name,
        d.disease,
        d.severity,
        mr.visit_date
    FROM diagnoses d
    JOIN medical_records mr
        ON d.record_id = mr.record_id
    JOIN patients p
        ON mr.patient_id = p.patient_id
    ORDER BY mr.visit_date DESC;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="Patient Diagnoses",
        data=data
    )


# =========================================================
# QUERY 5
# UI Button: Show Department Heads
# Role allowed: ADMIN
# =========================================================
@app.route("/department_heads")
def department_heads():
    if session.get("role") != "ADMIN":
        return "Access Denied: Only ADMIN can view department heads."

    query = """
    SELECT 
        dep.department_id,
        dep.department_name,
        dep.department_head_id,
        d.specialization
    FROM departments dep
    LEFT JOIN doctors d
        ON dep.department_head_id = d.doctor_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="Department Heads",
        data=data
    )

# =========================================================
# QUERY 6
# UI Button: Show All Staff
# Role allowed: ADMIN
# =========================================================
@app.route("/show_all_staff")
def show_all_staff():
    if session.get("role") != "ADMIN":
        return "Access Denied: Only ADMIN can view all staff."

    query = """
    SELECT 
        ms.staff_id,
        u.username,
        ms.staff_type as designation,
        dep.department_name as department
    FROM medical_staff ms
    LEFT JOIN departments dep
        ON ms.department_id = dep.department_id
    LEFT JOIN users u
        ON ms.user_id = u.user_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Staff",
        data=data
    )

#=========================================================
# QUERY 7
# UI Button: Show All Medicines
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
# =========================================================
@app.route("/show_all_medicines")
def show_all_medicines():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, PATIENT, or DOCTOR can view all medicines."

    query = """
    SELECT 
        medicine_id as id,
        medicine_name as name,
        medicine_stock as stock,
        medicine_price as price,
        medicine_manufacturer as manufacturer
    FROM medicines;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Medicines",
        data=data
    )

# =========================================================
# QUERY 8
# UI Button: Show All Appointments
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
# =========================================================
@app.route("/show_all_appointments")
def show_all_appointments():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, PATIENT, or DOCTOR can view all appointments."

    query = """
    SELECT 
        a.appointment_id as id,
        p.name as patient_name,
        d.specialization as doctor_specialization,
        d.doctor_id as doctor_id,
        a.appointment_date as date,
        a.appointment_time as time,
        a.appointment_status as status
    FROM appointments a
    LEFT JOIN patients p
        ON a.patient_id = p.patient_id
    LEFT JOIN doctors d
        ON a.doctor_id = d.doctor_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Appointments",
        data=data
    )

# =========================================================
# QUERY 9
# UI Button: Show All Prescriptions
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
# =========================================================
@app.route("/show_all_prescriptions")
def show_all_prescriptions():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, PATIENT, or DOCTOR can view all prescriptions."

    query = """
    SELECT 
        p.prescription_id as id,
        pat.name as patient_name,
        doc.doctor_id as doctor_id,
        mr.visit_date as date,
        m.medicine_name as medicine_name,
        p.frequency as frequency,
        p.duration as duration
    FROM prescriptions p
    LEFT JOIN medical_records mr
        ON p.record_id = mr.record_id
    LEFT JOIN patients pat
        ON mr.patient_id = pat.patient_id
    LEFT JOIN doctors doc
        ON mr.doctor_id = doc.doctor_id
    LEFT JOIN medicines m
        ON p.medicine_id = m.medicine_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Prescriptions",
        data=data
    )  

# =========================================================
# QUERY 10
# UI Button: Show All Medical Records
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
# =========================================================
@app.route("/show_all_medical_records")
def show_all_medical_records():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, PATIENT, or DOCTOR can view all medical records."

    query = """
    SELECT 
        mr.record_id as id,
        p.name as patient_name,
        d.doctor_id as doctor_id,
        mr.visit_date as date,
        mr.notes as notes
    FROM medical_records mr
    LEFT JOIN patients p
        ON mr.patient_id = p.patient_id
    LEFT JOIN doctors d
        ON mr.doctor_id = d.doctor_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Medical Records",
        data=data
    )  

# =========================================================
# QUERY 11 (only for debugging purposes)
# UI Button: Show All users
# Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
# =========================================================
@app.route("/show_all_users")
def show_all_users():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "PATIENT", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF, PATIENT, or DOCTOR can view all diagnoses."

    query = """
    SELECT 
        *
    FROM users;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="All Users",
        data=data
    )

# =========================================================
# QUERY 12
# UI Button: Show Ward and Nurse details
# Role allowed: ADMIN, MEDICAL_STAFF, DOCTOR
# =========================================================
@app.route("/show_ward_details")
def show_ward_details():
    if session.get("role") not in ["ADMIN", "MEDICAL_STAFF", "DOCTOR"]:
        return "Access Denied: Only ADMIN, MEDICAL_STAFF or DOCTOR can view ward details."

    query = """
    SELECT 
        users.username, wards.ward_name
    FROM nurse_wards LEFT JOIN wards on nurse_wards.ward_id=wards.ward_id LEFT JOIN (nurses LEFT JOIN users on nurses.staff_id=users.user_id) 
    on nurse_wards.nurse_id=nurses.nurse_id;
    """

    data = run_select_query(query)

    return render_template(
        "table.html",
        title="Ward Details",
        data=data
    ) 

# ---------------------------------------------------------
# Run the Flask app
# debug=True means code changes auto-refresh while developing
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)