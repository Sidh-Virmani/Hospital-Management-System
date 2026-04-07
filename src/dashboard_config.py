def get_dashboard_sections(role):
    sections = [
        {
            "title": "Browse",
            "actions": [
                {
                    "label": "Available Doctors",
                    "desc": "See all doctors currently marked available.",
                    "endpoint": "read_bp.available_doctors"
                },
                {
                    "label": "All Doctors",
                    "desc": "View doctor list with specialization and department.",
                    "endpoint": "read_bp.show_doctors"
                },
                {
                    "label": "Doctor Directory",
                    "desc": "Advanced doctor listing with filters for future UI.",
                    "endpoint": "read_bp.doctor_directory"
                }
            ]
        }
    ]

    if role == "GUEST":
        sections.append(
            {
                "title": "Guest Actions",
                "actions": [
                    {
                        "label": "Login",
                        "desc": "Login with real credentials.",
                        "endpoint": "auth_bp.login"
                    },
                    {
                        "label": "Patient Sign Up",
                        "desc": "Create a patient account.",
                        "endpoint": "auth_bp.signup"
                    }
                ]
            }
        )

    if role == "PATIENT":
        sections.append(
            {
                "title": "Patient Actions",
                "actions": [
                    {
                        "label": "My Appointments",
                        "desc": "View your appointments only.",
                        "endpoint": "read_bp.show_all_appointments"
                    },
                    {
                        "label": "Book Appointment",
                        "desc": "Schedule an appointment with a doctor.",
                        "endpoint": "actions_bp.book_appointment"
                    },
                    {
                        "label": "My Medical History",
                        "desc": "See your medical records.",
                        "endpoint": "read_bp.medical_history"
                    },
                    {
                        "label": "My Diagnoses",
                        "desc": "See diagnosis details from your visits.",
                        "endpoint": "read_bp.patient_diagnoses"
                    },
                    {
                        "label": "My Prescriptions",
                        "desc": "See your prescribed medicines.",
                        "endpoint": "read_bp.show_all_prescriptions"
                    },
                    {
                        "label": "All Medicines",
                        "desc": "Browse medicine inventory.",
                        "endpoint": "read_bp.show_all_medicines"
                    }
                ]
            }
        )

    if role == "MEDICAL_STAFF":
        sections.append(
            {
                "title": "Medical Staff Actions",
                "actions": [
                    {
                        "label": "View Patients",
                        "desc": "Browse all registered patients.",
                        "endpoint": "read_bp.view_patients"
                    },
                    {
                        "label": "Patient Directory",
                        "desc": "Advanced patient listing with future filters.",
                        "endpoint": "read_bp.patient_directory"
                    },
                    {
                        "label": "All Appointments",
                        "desc": "See all appointments.",
                        "endpoint": "read_bp.show_all_appointments"
                    },
                    {
                        "label": "Appointment Hub",
                        "desc": "Filtered appointment view for better UI later.",
                        "endpoint": "read_bp.appointment_hub"
                    },
                    {
                        "label": "Upcoming Appointments",
                        "desc": "See upcoming appointments only.",
                        "endpoint": "read_bp.show_upcoming_appointments"
                    },
                    {
                        "label": "Add Medical Record",
                        "desc": "Create a new medical record.",
                        "endpoint": "actions_bp.add_medical_record"
                    },
                    {
                        "label": "Add Diagnosis",
                        "desc": "Add diagnosis to an existing record.",
                        "endpoint": "actions_bp.add_diagnosis"
                    },
                    {
                        "label": "Update Appointment Status",
                        "desc": "Mark appointments confirmed/completed/cancelled.",
                        "endpoint": "actions_bp.update_appointment_status"
                    },
                    {
                        "label": "Update Doctor Availability",
                        "desc": "Change doctor status.",
                        "endpoint": "actions_bp.update_doctor_availability"
                    },
                    {
                        "label": "Ward Details",
                        "desc": "View nurse and ward mapping.",
                        "endpoint": "read_bp.show_ward_details"
                    }
                ]
            }
        )

    if role == "NON_MEDICAL_STAFF":
        sections.append(
            {
                "title": "Non-Medical Staff Actions",
                "actions": [
                    {
                        "label": "Upcoming Appointments",
                        "desc": "See appointment schedule.",
                        "endpoint": "read_bp.show_upcoming_appointments"
                    },
                    {
                        "label": "Appointment Hub",
                        "desc": "Filtered appointment view for better UI later.",
                        "endpoint": "read_bp.appointment_hub"
                    },
                    {
                        "label": "Low Medicine Stock",
                        "desc": "Check medicines running low.",
                        "endpoint": "read_bp.low_medicine_stock"
                    },
                    {
                        "label": "Medicine Inventory",
                        "desc": "Advanced medicine listing with filters.",
                        "endpoint": "read_bp.medicine_inventory"
                    },
                    {
                        "label": "Add Medicine",
                        "desc": "Insert a new medicine item.",
                        "endpoint": "actions_bp.add_medicine"
                    },
                    {
                        "label": "Update Medicine Stock",
                        "desc": "Change stock quantity.",
                        "endpoint": "actions_bp.update_medicine_stock"
                    }
                ]
            }
        )

    if role == "ADMIN":
        sections.extend(
            [
                {
                    "title": "Management",
                    "actions": [
                        {
                            "label": "Register Patient",
                            "desc": "Create a user and patient profile.",
                            "endpoint": "actions_bp.register_patient"
                        },
                        {
                            "label": "Register Medical Staff",
                            "desc": "Create a user and medical staff profile.",
                            "endpoint": "actions_bp.register_medical_staff"
                        },
                        {
                            "label": "Add Doctor Profile",
                            "desc": "Convert an existing DOCTOR staff member into doctor record.",
                            "endpoint": "actions_bp.add_doctor"
                        },
                        {
                            "label": "Add Medicine",
                            "desc": "Create a new medicine entry.",
                            "endpoint": "actions_bp.add_medicine"
                        },
                        {
                            "label": "Update Medicine Stock",
                            "desc": "Change stock quantity.",
                            "endpoint": "actions_bp.update_medicine_stock"
                        }
                    ]
                },
                {
                    "title": "Operations",
                    "actions": [
                        {
                            "label": "Book Appointment",
                            "desc": "Create appointments for any patient.",
                            "endpoint": "actions_bp.book_appointment"
                        },
                        {
                            "label": "Update Appointment Status",
                            "desc": "Update appointment lifecycle.",
                            "endpoint": "actions_bp.update_appointment_status"
                        },
                        {
                            "label": "Add Medical Record",
                            "desc": "Create patient visit record.",
                            "endpoint": "actions_bp.add_medical_record"
                        },
                        {
                            "label": "Add Diagnosis",
                            "desc": "Attach diagnosis to record.",
                            "endpoint": "actions_bp.add_diagnosis"
                        },
                        {
                            "label": "Update Doctor Availability",
                            "desc": "Set doctor to available/busy/etc.",
                            "endpoint": "actions_bp.update_doctor_availability"
                        }
                    ]
                },
                {
                    "title": "Reports & Listings",
                    "actions": [
                        {"label": "All Doctors", "desc": "Doctor listing.", "endpoint": "read_bp.show_doctors"},
                        {"label": "Doctor Directory", "desc": "Advanced doctor filters.", "endpoint": "read_bp.doctor_directory"},
                        {"label": "All Patients", "desc": "Patient listing.", "endpoint": "read_bp.view_patients"},
                        {"label": "Patient Directory", "desc": "Advanced patient filters.", "endpoint": "read_bp.patient_directory"},
                        {"label": "All Staff", "desc": "Medical staff listing.", "endpoint": "read_bp.show_all_staff"},
                        {"label": "Department Heads", "desc": "Department head mapping.", "endpoint": "read_bp.department_heads"},
                        {"label": "All Medicines", "desc": "Medicine list.", "endpoint": "read_bp.show_all_medicines"},
                        {"label": "Medicine Inventory", "desc": "Advanced medicine filters.", "endpoint": "read_bp.medicine_inventory"},
                        {"label": "All Appointments", "desc": "Appointment list.", "endpoint": "read_bp.show_all_appointments"},
                        {"label": "Appointment Hub", "desc": "Advanced appointment filters.", "endpoint": "read_bp.appointment_hub"},
                        {"label": "All Prescriptions", "desc": "Prescription list.", "endpoint": "read_bp.show_all_prescriptions"},
                        {"label": "All Medical Records", "desc": "Medical record list.", "endpoint": "read_bp.show_all_medical_records"},
                        {"label": "Patient Appointment Summary", "desc": "Patient-level appointment summary.", "endpoint": "read_bp.patient_appointment_summary"},
                        {"label": "Ward Details", "desc": "Nurse-ward details.", "endpoint": "read_bp.show_ward_details"},
                        {"label": "Upcoming Appointments", "desc": "Upcoming appointments only.", "endpoint": "read_bp.show_upcoming_appointments"},
                        {"label": "Low Medicine Stock", "desc": "Medicines below threshold.", "endpoint": "read_bp.low_medicine_stock"},
                        {"label": "Show All Users", "desc": "Temporary debugging view.", "endpoint": "read_bp.show_all_users"}
                    ]
                }
            ]
        )

    return sections