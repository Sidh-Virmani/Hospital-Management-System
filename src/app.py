import os
from flask import Flask, render_template, session

from .dashboard_config import get_dashboard_sections
from .session_helpers import ensure_session
from .routes.routes_auth import auth_bp
from .routes.routes_read import read_bp
from .routes.routes_actions import actions_bp
from .routes.routes_chat import chat_bp

app = Flask(__name__)
@app.context_processor
def inject_sidebar():
    role = session.get("role", "GUEST")
    return dict(sections=get_dashboard_sections(role))
app.secret_key = "hospital_project_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SQL_DIR = os.path.join(PROJECT_ROOT, "sql_files")

app.config["BASE_DIR"] = BASE_DIR
app.config["PROJECT_ROOT"] = PROJECT_ROOT
app.config["SQL_DIR"] = SQL_DIR

app.register_blueprint(auth_bp)
app.register_blueprint(read_bp)
app.register_blueprint(actions_bp)
app.register_blueprint(chat_bp)

@app.route("/")
def home():
     ensure_session()
     return render_template("home.html")