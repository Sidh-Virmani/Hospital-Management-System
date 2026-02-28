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