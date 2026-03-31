USE hospital_management;

-- =========================================================
-- QUERY 1
-- UI Button: "Show All Doctors"
-- Role using it: Admin / Patient
-- Purpose: Display all doctors with their specialization,
--          availability, and department name.
-- =========================================================
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


-- =========================================================
-- QUERY 2
-- UI Button: "View All Patients"
-- Role using it: Admin / Staff
-- Purpose: Display basic patient details for hospital records.
-- =========================================================
SELECT 
    patient_id,
    name,
    age,
    gender,
    phone,
    blood_group
FROM patients;


-- =========================================================
-- QUERY 3
-- UI Button: "View Patient Medical History"
-- Role using it: Doctor / Patient / Admin
-- Purpose: Show visit history of patients with doctor ID and notes.
-- Note: Later in backend, you can add:
--       WHERE p.patient_id = ?
--       to fetch one specific patient's history.
-- =========================================================
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


-- =========================================================
-- QUERY 4
-- UI Button: "View Patient Diagnoses"
-- Role using it: Doctor / Patient / Admin
-- Purpose: Show diagnosed diseases of each patient with severity.
-- Note: Later in backend, this can also be filtered for one patient.
-- =========================================================
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


-- =========================================================
-- QUERY 5
-- UI Button: "Show Department Heads"
-- Role using it: Admin
-- Purpose: Display each department and the doctor who heads it.
-- =========================================================
SELECT 
    dep.department_id,
    dep.department_name,
    dep.department_head_id,
    d.specialization
FROM departments dep
LEFT JOIN doctors d
    ON dep.department_head_id = d.doctor_id;


-- =========================================================
-- QUERY 6
-- UI Button: "Show All Staff"
-- Role using it: Admin
-- Purpose: Display all staff members with their role and department.
-- =========================================================
SELECT 
    ms.staff_id,
    u.username,
    ms.staff_type as designation,
    dep.department_name as department
FROM (medical_staff ms
LEFT JOIN departments dep 
    ON ms.department_id = dep.department_id)
LEFT JOIN users u 
    ON ms.user_id = u.user_id;


-- =========================================================
-- QUERY 7
-- UI Button: "Show All Medicines"
-- Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
-- Purpose: Display all medicines with their stock, price, and manufacturer.
-- =========================================================
SELECT 
    medicine_id as id,
    medicine_name as name,
    medicine_stock as stock,
    medicine_price as price,
    medicine_manufacturer as manufacturer
FROM medicines;


-- =========================================================
-- QUERY 8
-- UI Button: "Show All Appointments"
-- Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
-- Purpose: Display all appointments with their patient name, doctor specialization, date, time, and status.
-- Note: Later in backend, this can also be filtered for one patient.
-- =========================================================
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


-- =========================================================
-- QUERY 9
-- UI Button: "Show All Prescriptions"
-- Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
-- Purpose: Display all prescriptions with their patient name, doctor specialization, date, time, and status.
-- =========================================================
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

-- =========================================================
-- QUERY 10
-- UI Button: Show All Medical Records
-- Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
-- Purpose: Display all medical records with their patient name, doctor specialization, date, time, and status.
-- =========================================================
SELECT 
    mr.record_id as id,
    p.name as patient_name,
    doc.doctor_id as doctor_id,
    mr.visit_date as date,
    mr.notes as notes
FROM medical_records mr
LEFT JOIN patients p 
    ON mr.patient_id = p.patient_id
LEFT JOIN doctors doc 
    ON mr.doctor_id = doc.doctor_id;

-- =========================================================
-- QUERY 11
-- UI Button: Show All Diagnoses
-- Role allowed: ADMIN, MEDICAL_STAFF, PATIENT, DOCTOR
-- Purpose: Display all diagnoses with their patient name, doctor specialization, date, time, and status.
-- =========================================================
SELECT 
    d.diagnosis_id as id,
    p.name as patient_name,
    doc.doctor_id as doctor_id,
    mr.visit_date as date,
    d.disease as disease,
    d.severity as severity
FROM diagnoses d
LEFT JOIN medical_records mr
    ON d.record_id = mr.record_id
LEFT JOIN patients p 
    ON mr.patient_id = p.patient_id
LEFT JOIN doctors doc 
    ON mr.doctor_id = doc.doctor_id;

-- =========================================================
-- QUERY 12
-- UI Button: Upcoming Appointments
-- Role allowed: ADMIN, MEDICAL STAFF, NON MEDICAL STAFF
-- Purpose: Display all medical information for a specific patient.
-- =========================================================

select patient_id, doctor_id, appointment_date, appointment_time 
from appointments 
where appointment_date > curdate() or (appointment_date = curdate() and appointment_time >= curtime()) 
and appointment_status != 'CANCELLED'
order by appointment_date, appointment_time;

-- =========================================================
-- QUERY 13
-- UI Button: Low Medicine Stock
-- Role allowed: ADMIN,  NON MEDICAL STAFF
-- Purpose: Display all medicines having low stock.
-- =========================================================

SELECT * FROM medicines
WHERE medicine_stock < 100;

-- =========================================================
-- QUERY 14
-- UI Button: Available Doctors
-- Role allowed: ADMIN, MEDICAL STAFF, NON MEDICAL STAFF, PATIENT
-- Purpose: Display all doctors who are currently available.
-- =========================================================

SELECT 
        d.doctor_id,
        u.username AS doctor_name,
        d.specialization,
        d.availability_status,
        dep.department_name
    FROM doctors d
    JOIN medical_staff ms
        ON d.staff_id = ms.staff_id
    JOIN users u
        ON ms.user_id = u.user_id
    LEFT JOIN departments dep
        ON ms.department_id = dep.department_id
    WHERE d.availability_status = 'AVAILABLE'
    ORDER BY dep.department_name;

-- =========================================================
-- QUERY 15
-- UI Button: Patient Appointment Summary
-- Role allowed: ADMIN, MEDICAL STAFF, NON MEDICAL STAFF
-- Purpose: Displays number of complete appointments for each patient as well as whether they have
--          any upcoming appointments, and if yes, when is the next one.
-- =========================================================


    SELECT 
    p.patient_id,
    p.name,

    COUNT(
    CASE 
        WHEN a.appointment_status = 'COMPLETED' 
        THEN 1 
    END
) AS total_completed_appointments,

    CASE 
        WHEN MIN(
            CASE 
                WHEN (a.appointment_date > CURDATE() 
                      OR (a.appointment_date = CURDATE() AND a.appointment_time >= CURTIME()))
                THEN CONCAT(a.appointment_date, ' ', a.appointment_time)
                ELSE NULL
            END
        ) IS NOT NULL 
        THEN 'YES'
        ELSE 'NO'
    END AS has_upcoming_appointment,

    MIN(
        CASE 
            WHEN (a.appointment_date > CURDATE() 
                  OR (a.appointment_date = CURDATE() AND a.appointment_time >= CURTIME()))
            THEN CONCAT(a.appointment_date, ' ', a.appointment_time)
            ELSE NULL
        END
    ) AS next_appointment

FROM patients p
LEFT JOIN appointments a 
    ON p.patient_id = a.patient_id

GROUP BY p.patient_id, p.name
ORDER BY p.name;