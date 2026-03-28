USE hospital_management;

-- USERS
INSERT INTO users (username, password, role) VALUES
('admin1', 'pass', 'ADMIN'),
('doc1', 'pass', 'MEDICAL_STAFF'),
('nurse1', 'pass', 'MEDICAL_STAFF'),
('patient1', 'pass', 'PATIENT');

-- ADMINS
INSERT INTO admins (user_id, admin_level) VALUES
(1, 'SUPER');

-- MEDICAL STAFF
INSERT INTO medical_staff (user_id, staff_type) VALUES
(2, 'DOCTOR'),
(3, 'NURSE');

-- DOCTOR
INSERT INTO doctors (staff_id, specialization, availability_status) VALUES
(1, 'Cardiology', 'AVAILABLE'),
(2, 'Neurology', 'BUSY'),
(3, 'Orthopedics', 'AVAILABLE'),
(4, 'Pediatrics', 'ON LEAVE'),
(5, 'Dermatology', 'AVAILABLE'),
(6, 'Cardiology', 'BUSY'),
(7, 'General Medicine', 'AVAILABLE'),
(8, 'Radiology', 'OFF DUTY'),
(9, 'Psychiatry', 'AVAILABLE'),
(10, 'Cardiology', 'ON LEAVE'),
(11, 'ENT', 'AVAILABLE'),
(12, 'Ophthalmology', 'BUSY');

-- NURSE
INSERT INTO nurses (staff_id, ward_assigned) VALUES
(2, 'Ward A');

-- DEPARTMENT
INSERT INTO departments (department_name, department_head_id) VALUES
('Cardiology', 1);

-- UPDATE staff department
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 1;
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 2;

-- PATIENT
INSERT INTO patients (user_id, name, age, gender) VALUES
(4, 'John Doe', 25, 'Male');

-- MEDICAL RECORD
INSERT INTO medical_records (patient_id, doctor_id, visit_date, notes) VALUES
(1, 1, '2025-03-27', 'Regular checkup');

-- DIAGNOSIS
INSERT INTO diagnoses (record_id, disease, severity) VALUES
(1, 'Flu', 'Mild');