import os
from flask import Blueprint, request, jsonify, session
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

chat_bp = Blueprint("chat_bp", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_hospital_related(message):
    """
    Simple first-level filter.
    If question does not look hospital/site related,
    we refuse before sending it to OpenAI.
    """
    if not message:
        return False

    message = message.lower()

    allowed_keywords = [
        "hospital", "doctor", "doctors", "patient", "patients",
        "appointment", "appointments", "book", "booking",
        "medicine", "medicines", "prescription", "prescriptions",
        "diagnosis", "diagnoses", "medical record", "medical records",
        "department", "departments", "staff", "nurse", "nurses",
        "ward", "wards", "billing", "bill", "payment",
        "login", "log in", "signup", "sign up", "register",
        "dashboard", "portal", "website", "site",
        "admin", "doctor availability", "inventory"
    ]

    return any(keyword in message for keyword in allowed_keywords)


@chat_bp.route("/api/chat", methods=["POST"])
def chatbot_reply():
    data = request.get_json()

    if not data:
        return jsonify({"reply": "Invalid request."}), 400

    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message first."}), 400

    # HARD FILTER FIRST
    if not is_hospital_related(user_message):
        return jsonify({
            "reply": (
                "I am the Penguin Hospital assistant. "
                "I can only help with hospital-related questions such as doctors, "
                "appointments, departments, medicines, billing, staff, patients, "
                "and how to use this website."
            )
        })

    # Session info for slightly more context
    user_role = session.get("role", "GUEST")
    username = session.get("username", "Guest")

    system_instructions = f"""
You are the Penguin Hospital website assistant.

Rules:
1. Only answer questions related to Penguin Hospital or this website.
2. Allowed topics: doctors, departments, appointments, medicines, billing, staff,
   patients, records, login/signup, dashboard help, and hospital portal navigation.
3. If the user asks an unrelated question, politely refuse and say you only handle hospital topics.
4. Keep answers concise, clear, and practical.
5. Do not pretend to know real database values unless they are explicitly provided.
6. If a question requires actual live hospital data, guide the user to the correct portal page instead of inventing details.

Current user role: {user_role}
Current username: {username}
"""

    try:
        response = client.responses.create(
            model="gpt-5.4",
            instructions=system_instructions,
            input=user_message
        )

        bot_reply = response.output_text.strip()

        if not bot_reply:
            bot_reply = "Sorry, I could not generate a response right now."

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Chatbot error:", e)
        return jsonify({
            "reply": "Sorry, the chatbot is currently unavailable right now."
        }), 500