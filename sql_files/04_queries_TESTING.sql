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