# 🏥 Hospital Management System

A database-driven Hospital Management System designed to manage hospital operations with role-based access for **Admin, Medical Staff, Non-Medical Staff, and Patients**.

---

## 📌 Objective

To design and implement a structured database system that efficiently handles hospital workflows including patient management, appointments, medical records, and billing.

---

## 🧠 System Design

The system follows a relational architecture with a centralized **users table** and role-based extensions:

* Users → Authentication & roles
* Medical Staff → Doctors / Nurses specialization
* Patients → Personal & medical data
* Appointments → Scheduling system
* Medical Records → Diagnosis & prescriptions
* Billing → Bills, payments, and items

---

## ⚙️ Features

* 🔐 Role-based login system
* 👨‍⚕️ Doctor & nurse management
* 🧑 Patient records management
* 📅 Appointment scheduling
* 🧾 Billing & payment tracking
* 💊 Prescription and diagnosis handling
* 🏥 Department and ward organization

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** MySQL
* **Frontend:** (to be implemented)
* **Version Control:** Git & GitHub

---

## 🗂️ Project Structure

```bash
hospital-management-system/
├── backend/
├── database/
│   └── 01_schema.sql
├── frontend/              # (planned)
├── README.md
└── .gitignore
```

---

## 🚀 How to Run

### 🔧 Setup

```bash
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 🗄️ Database Setup

```bash
mysql -u root -p < 01_schema.sql
```

### ▶️ Run Backend

```bash
python app.py
```

---

## 📈 Current Status

* Database schema designed and implemented
* Core relationships and constraints enforced
* Backend development in progress

---

## 👥 Team Members

* Sidh Virmani — 2024A7PS0520G
* Rhea Jain — 2024A7PS0575G
* Ishani Tagare — 2024A7RM0216G
* Aditya Anand Kumar Singh — 2024A7PS0502G
* Shivani Deo — 2024A7PS0051G
* Mridul Sardana — 2024A7PS0547G

---

## 📄 Note

This project is developed as part of DBMS coursework and focuses on building a scalable and well-structured relational database system.

---
