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

CREATE TABLE nurses(
    nurse_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT NOT NULL UNIQUE,
    ward_assigned VARCHAR(100),

    constraint fk_nurse_staff
        FOREIGN KEY (staff_id)
        REFERENCES medical_staff(staff_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE diagnoses (
    diagnosis_id INT PRIMARY KEY,
    record_id INT,
    disease VARCHAR(100),
    severity VARCHAR(50),

    FOREIGN KEY (record_id) REFERENCES medical_records(record_id)
);

CREATE TABLE medical_records (
    record_id INT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    visit_date DATE,
    notes TEXT,

    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE patients (
    patient_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(15),
    address VARCHAR(255),
    blood_group VARCHAR(5),

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
