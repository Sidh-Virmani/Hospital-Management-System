USE hospital_management;

-- USERS
INSERT INTO users (username, password, role) VALUES
('admin1', 'pass', 'ADMIN'),
('doc1', 'pass', 'MEDICAL_STAFF'),
('doc2', 'pass', 'MEDICAL_STAFF'),
('doc3', 'pass', 'MEDICAL_STAFF'),
('nurse1', 'pass', 'MEDICAL_STAFF'),
('nurse2', 'pass', 'MEDICAL_STAFF'),
('nurse3', 'pass', 'MEDICAL_STAFF'),
('patient1', 'pass', 'PATIENT');

-- ADMINS
INSERT INTO admins (user_id, admin_level) VALUES
(1, 'SUPER');

-- MEDICAL STAFF
INSERT INTO medical_staff (user_id, staff_type) VALUES
(2, 'DOCTOR'),
(3, 'DOCTOR'),
(4, 'DOCTOR'),
(5, 'NURSE'),
(6, 'NURSE'),
(7, 'NURSE');

-- DOCTOR
INSERT INTO doctors (staff_id, specialization) VALUES
(1, 'Cardiology'),
(2, 'Neurology'),
(3, 'Orthopedics');

--WARDS
INSERT INTO wards (ward_name, ward_type) VALUES
('ICU Ward A', 'ICU'),
('General Ward A', 'GENERAL'),
('Emergency Ward A', 'EMERGENCY'),
('Maternity Ward A', 'MATERNITY'),
('Surgical Ward A', 'SURGICAL'),
('ICU Ward B', 'ICU'),
('General Ward B', 'GENERAL'),
('Emergency Ward B', 'EMERGENCY'),
('Maternity Ward B', 'MATERNITY'),
('Surgical Ward B', 'SURGICAL');

-- NURSES
INSERT INTO nurses (staff_id) VALUES
(4), (5), (6);

-- NURSE_WARDS
INSERT INTO nurse_wards (nurse_id, ward_id) VALUES
(1,1), (1,2),
(2,3),
(3,4);

-- DEPARTMENT
INSERT INTO departments (department_name, department_head_id) VALUES
('Cardiology', 1);

-- UPDATE staff department
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 1;
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 2;

-- PATIENT
INSERT INTO patients (user_id, name, age, gender) VALUES
(8, 'John Doe', 25, 'Male');

-- MEDICAL RECORD
INSERT INTO medical_records (patient_id, doctor_id, visit_date, notes) VALUES
(1, 1, '2025-03-27', 'Regular checkup');

-- DIAGNOSIS
INSERT INTO diagnoses (record_id, disease, severity) VALUES
(1, 'Flu', 'Mild');