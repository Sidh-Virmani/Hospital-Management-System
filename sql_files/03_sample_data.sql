USE hospital_management;

-- USERS
INSERT INTO users (username, password, role) VALUES
('admin1', 'pass', 'ADMIN'),
('doc1', 'pass', 'MEDICAL_STAFF'),
('doc2', 'pass', 'MEDICAL_STAFF'),
('doc3', 'pass', 'MEDICAL_STAFF'),
('doc4', 'pass', 'MEDICAL_STAFF'),
('nurse1', 'pass', 'MEDICAL_STAFF'),
('nurse2', 'pass', 'MEDICAL_STAFF'),
('nurse3', 'pass', 'MEDICAL_STAFF'),
('patient1', 'pass', 'PATIENT'),
('patient2', 'pass', 'PATIENT'),
('patient3', 'pass', 'PATIENT'),
('patient4', 'pass', 'PATIENT'),
('admin2', 'pass', 'ADMIN'),
('admin3', 'pass', 'ADMIN'),
('admin4', 'pass', 'ADMIN'),
('admin5', 'pass', 'ADMIN'),
('admin6', 'pass', 'ADMIN');

-- ADMINS
INSERT INTO admins (user_id, admin_level) VALUES
(1, 'SUPER'),
(13, 'NORMAL'),
(14, 'NORMAL'),
(15, 'NORMAL'),
(16, 'NORMAL'),
(17, 'NORMAL');

-- MEDICAL STAFF
INSERT INTO medical_staff (user_id, staff_type) VALUES
(2, 'DOCTOR'),
(3, 'DOCTOR'),
(4, 'DOCTOR'),
(5, 'DOCTOR'),
(6, 'NURSE'),
(7, 'NURSE'),
(8, 'NURSE'),
(9, 'NURSE'),
(10, 'NURSE'),
(11, 'NURSE'),
(12, 'NURSE'),
(1, 'NURSE');

-- DOCTOR
INSERT INTO doctors (staff_id, specialization) VALUES
(1, 'Cardiology'),
(2, 'Neurology'),
(3, 'Orthopedics'),
(4, 'Pediatrics');

-- WARDS
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
(5), (6), (7), (8), (9), (10), (11), (12);

-- NURSE_WARDS
INSERT INTO nurse_wards (nurse_id, ward_id) VALUES
(1,1), (1,2), (1, 3), (2, 4), (2, 5), (2, 6), (3, 7), (3, 8), (3, 9),
(2,3),
(3,4),
(4, 1),
(4, 2),
(5, 3),
(6, 4),
(7, 5);

-- DEPARTMENT
INSERT INTO departments (department_name, department_head_id) VALUES
('Cardiology', 1),
('General Medicine', 2),
('Orthopedics', 3),
('Surgery', 4);

-- UPDATE staff department
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 1;
UPDATE medical_staff SET department_id = 2 WHERE staff_id = 2;
UPDATE medical_staff SET department_id = 3 WHERE staff_id = 3;
UPDATE medical_staff SET department_id = 4 WHERE staff_id = 4;
UPDATE medical_staff SET department_id = 1 WHERE staff_id = 4;
UPDATE medical_staff SET department_id = 2 WHERE staff_id = 5;
UPDATE medical_staff SET department_id = 3 WHERE staff_id = 6;

-- PATIENT
INSERT INTO patients (user_id, name, age, gender) VALUES
(9, 'John Doe', 25, 'Male'),
(10, 'Clary Fray', 20, 'Female'),
(12, 'Jake Herondale', 22, 'Male'),
(11, 'Abc', 5, 'Female');

-- MEDICAL RECORD
INSERT INTO medical_records (patient_id, doctor_id, visit_date, notes) VALUES
(1, 1, '2025-03-27', 'Regular checkup'),
(2, 2, '2025-03-31', 'Sprained ankle'),
(3, 2, '2025-03-31', 'Migraine evaluation'),
(4, 4, '2026-02-25', 'Stomach ache');

-- DIAGNOSIS
INSERT INTO diagnoses (record_id, disease, severity) VALUES
(1, 'Flu', 'Mild'),
(2, 'Ankle Sprain', 'Severe'),
(3, 'Migraine', 'Severe'),
(4, 'Food poisoning', 'Mild');

-- medicines
INSERT INTO medicines (medicine_name, medicine_stock, medicine_price, medicine_manufacturer) VALUES
('Paracetamol 500mg', 1500, 25, 'PharmaCorp Inc.'),
('Amoxicillin 250mg', 800, 150, 'HealthMeds LLC'),
('Ibuprofen 400mg', 1200, 55, 'Wellness Pharma'),
('Cetirizine 10mg', 600, 42, 'AllergyCare Ltd.'),
('Omeprazole 20mg', 45, 125, 'GastroMed Co.'),
('Metformin 500mg', 2000, 89, 'DiabeticCare Inc.'),
('Aspirin 81mg', 900, 30, 'CardioHealth Pharma'),
('Atorvastatin 40mg', 550, 220, 'CholesterolMeds Corp.'),
('Azithromycin 250mg', 300, 185, 'HealthMeds LLC'),
('Vitamin C 1000mg', 2500, 60, 'NutriLife Supplements');

-- prescriptions
INSERT INTO prescriptions (record_id, medicine_id, frequency, duration) VALUES
(1, 1, '3 times a day', '5 days'),
(2, 2, '2 times a day', '7 days'),
(3, 3, '3 times a day', '5 days'),
(4, 4, '1 time a day', '3 days'),
(2, 5, '2 times a day', '10 days'),
(3, 6, '1 time a day', '15 days'),
(1, 7, '1 time a day', '7 days'),
(4, 8, '2 times a day', '5 days');

-- APPOINTMENTS
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, appointment_status) VALUES
(1, 1, '2026-04-01', '09:00:00', 'CONFIRMED'),
(2, 2, '2026-04-01', '10:30:00', 'CONFIRMED'),
(3, 1, '2026-04-02', '14:00:00', 'PENDING'),
(1, 3, '2026-04-03', '11:15:00', 'COMPLETED'),
(2, 2, '2026-04-04', '09:45:00', 'CANCELLED'),
(3, 3, '2026-04-05', '16:00:00', 'CONFIRMED'),
(1, 1, '2026-04-06', '13:30:00', 'PENDING'),
(4, 4, '2026-02-25', '14:00:00', 'COMPLETED');

