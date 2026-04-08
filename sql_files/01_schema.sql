DROP DATABASE IF EXISTS hospital_management;

CREATE DATABASE IF NOT EXISTS hospital_management;
USE hospital_management;

-- Creating the Users table: user_id is the primary key and auto-increments with each new user.
-- The username is unique and cannot be null
-- The password is stored as a string and cannot be null
-- And the role is defined as an ENUM with specific allowed values.
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'PATIENT', 'MEDICAL_STAFF', 'NON_MEDICAL_STAFF') NOT NULL
);

CREATE TABLE admins(
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    admin_level VARCHAR(50),

    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Will be automated in the future using python, action cannot be auotmated by MySQL
CREATE TABLE activity_logs(
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE medical_staff(
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    staff_type ENUM('DOCTOR', 'NURSE') NOT NULL,
    department_id INT,

    constraint fk_medical_staff_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE non_medical_staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    staff_type VARCHAR(255),
    shift VARCHAR(255),

    constraint fk_non_medical_staff_user
        FOREIGN KEY (user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE doctors(
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT NOT NULL UNIQUE,
    specialization VARCHAR(100),
    availability_status ENUM('BUSY', 'AVAILABLE', 'ON LEAVE', 'OFF DUTY') DEFAULT 'AVAILABLE' NOT NULL,

    constraint fk_doctor_staff
        FOREIGN KEY (staff_id)
        REFERENCES medical_staff(staff_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE wards (
    ward_id INT PRIMARY KEY AUTO_INCREMENT,
    ward_name VARCHAR(100) NOT NULL UNIQUE,
    ward_type ENUM('ICU', 'GENERAL', 'EMERGENCY', 'MATERNITY', 'SURGICAL')
);



CREATE TABLE nurses(
    nurse_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT NOT NULL UNIQUE,

    constraint fk_nurse_staff
        FOREIGN KEY (staff_id)
        REFERENCES medical_staff(staff_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE nurse_wards (
    nurse_id INT,
    ward_id INT,

    PRIMARY KEY (nurse_id, ward_id),

    CONSTRAINT fk_nurse_wards_nurse
        FOREIGN KEY (nurse_id)
        REFERENCES nurses(nurse_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_nurse_wards_ward
        FOREIGN KEY (ward_id)
        REFERENCES wards(ward_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(255) NOT NULL,
    department_head_id INT
);

CREATE TABLE interns (
    intern_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT NOT NULL,
    mentor_doctor_id INT,

    constraint fk_intern_staff
        FOREIGN KEY (staff_id) REFERENCES medical_staff(staff_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    constraint fk_intern_doctor
        FOREIGN KEY (mentor_doctor_id) REFERENCES doctors(doctor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    name VARCHAR(100),
    age INT CHECK (age >= 0 AND age <= 130),
    gender VARCHAR(10),
    phone VARCHAR(15),
    address VARCHAR(255),
    blood_group VARCHAR(5),

    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE medical_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    visit_date DATE,
    notes TEXT,

    CONSTRAINT fk_record_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_record_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE diagnoses (
    diagnosis_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    disease VARCHAR(100),
    severity VARCHAR(50),

    CONSTRAINT fk_diagnosis_record
        FOREIGN KEY (record_id)
        REFERENCES medical_records(record_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- Added delayed Fk because it was creating circular dependancies
-- Order of commands matter btw

ALTER TABLE departments
ADD CONSTRAINT fk_department_staff
FOREIGN KEY (department_head_id)
REFERENCES doctors(doctor_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE medical_staff
ADD CONSTRAINT fk_medical_staff_department
FOREIGN KEY (department_id)
REFERENCES departments(department_id)
ON DELETE SET NULL
ON UPDATE CASCADE;


-- medicines table

CREATE TABLE medicines (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_name VARCHAR(100) NOT NULL,
    medicine_stock INT NOT NULL,
    medicine_price INT NOT NULL,
    medicine_manufacturer VARCHAR(100) NOT NULL
);

-- prescriptions table

CREATE TABLE prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    medicine_id INT NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,

    CONSTRAINT fk_prescription_record
        FOREIGN KEY (record_id)
        REFERENCES medical_records(record_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_prescription_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES medicines(medicine_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_status ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED') DEFAULT 'PENDING' NOT NULL,

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_appointment_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
); 
CREATE TABLE bills (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    bill_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_bill_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE bill_items (
    bill_item_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT NOT NULL,
    description VARCHAR(255),
    cost DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_bill_items_bill
        FOREIGN KEY (bill_id)
        REFERENCES bills(bill_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
); 
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT NOT NULL,
    payment_mode ENUM('CASH', 'CARD', 'UPI', 'INSURANCE') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,

    CONSTRAINT fk_payment_bill
        FOREIGN KEY (bill_id)
        REFERENCES bills(bill_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);