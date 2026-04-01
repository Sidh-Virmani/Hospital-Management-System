# Hospital Management System

A full-stack database-driven Hospital Management System with a clean UI, role-based access control, and real CRUD workflows built using Flask and MySQL.

---

## Objective

To design and implement a real-world hospital database system that supports:
- structured relational modeling  
- role-based operations  
- real-time data interaction through a web interface  

The focus is on DBMS concepts and practical usability.

---

## System Design

The system is built on a normalized relational schema with strong foreign key constraints.

### Core Architecture:
- Users → authentication and role management  
- Patients → personal and medical data  
- Medical Staff → doctors, nurses, departments  
- Appointments → scheduling system  
- Medical Records → visits, diagnoses, prescriptions  
- Medicines → inventory management  
- Billing → bills and payments  

### DBMS Concepts Used:
- Primary and Foreign Keys  
- Cascading constraints  
- Weak entities  
- Many-to-many relationships  
- Role-based data access  

---

## Features

### Authentication and Roles
- Login system (username + password)
- Demo login for evaluation
- Role-based access:
  - ADMIN
  - PATIENT
  - MEDICAL_STAFF
  - NON_MEDICAL_STAFF
  - GUEST

---

### Data Viewing
- View doctors, patients, staff  
- View appointments  
- View medical history and diagnoses  
- View prescriptions and records  
- View departments and wards  
- View upcoming appointments  
- Patient appointment summary  
- Low medicine stock  

---

### Data Operations

#### User and Staff
- Register patient  
- Register medical staff  
- Add doctor profile  

#### Appointments
- Book appointment  
- Update appointment status  

#### Medical
- Add medical record  
- Add diagnosis  

#### Inventory
- Add medicine  
- Update medicine stock  
- Update doctor availability  

---

## Role-Based Behavior

| Role | Capabilities |
|------|-------------|
| ADMIN | Full access |
| PATIENT | Own data access |
| MEDICAL_STAFF | Medical operations |
| NON_MEDICAL_STAFF | Inventory and scheduling |
| GUEST | Limited access |

---

## UI

- Dashboard-based layout  
- Role-specific sections  
- Reusable forms  
- Table-based data display  
- Clean minimal design  

---

## Tech Stack

- Backend: Flask (Python)  
- Database: MySQL  
- Frontend: HTML + CSS  
- Version Control: Git  

---

## Current Status

- Fully working backend and UI  
- Role-based system implemented  
- CRUD operations implemented  
- Complex queries integrated  

---

## Notes

- Passwords stored in plain text (demo purpose)  
- Demo login enabled  
- Production should use hashing and proper authentication  

---

## Team Members

- Sidh Virmani — 2024A7PS0520G  
- Rhea Jain — 2024A7PS0575G  
- Ishani Tagare — 2024A7RM0216G  
- Aditya Anand Kumar Singh — 2024A7PS0502G  
- Shivani Deo — 2024A7PS0051G  
- Mridul Sardana — 2024A7PS0547G  

---

## Final Note

This project demonstrates strong relational database design, backend integration, and practical DBMS implementation.