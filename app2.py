import streamlit as st
st.set_page_config(page_title="📊 Learning Dashboard", layout="wide")

import os
import json
import shutil
import re
import urllib.parse
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import time  # Added for refresh debugging

# STABILIZATION MEASURES
if "_restart" not in st.session_state:
    st.session_state.clear()
    st.session_state._restart = True
    st.rerun()

# Debug refreshes
if "_last_refresh" not in st.session_state:
    st.session_state._last_refresh = time.time()
else:
    print(f"Refresh delta: {time.time()-st.session_state._last_refresh:.2f}s")
    st.session_state._last_refresh = time.time()

from datetime import datetime
from dotenv import load_dotenv

from memory import (
    load_learner_profile as load_profile,
    save_learner_profile as save_profile,
    save_memory,
    get_completed_lessons,
    mark_lesson_complete
)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from auth_utils import add_user, hash_password, get_users, delete_user

# Load environment variables
load_dotenv()

# Constants
REQUESTS_FILE = "pending_requests.json"
APPROVED_USERS_FILE = "access_logs/approved_users.csv"
ADMIN_USERS = ["walter@example.com"]

def initialize_session_state():
    """Initialize all required session state variables"""
    required_keys = {
        "initialized": True,
        "authentication_status": None,
        "username": None,
        "name": None,
        "authenticated_once": False,
        "just_reran": False,
        "logout_triggered": False,
        "memory_folder": None,
        "profile_path": None,
        "track_selected": None,
        "lesson_topic": None
    }
    
    for key, value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_username(raw_username):
    """Sanitize username for filesystem use"""
    return raw_username.replace("@", "_at_").replace(".", "_dot_")

def load_pending_requests():
    """Load pending access requests"""
    if not os.path.exists(REQUESTS_FILE):
        return []
    try:
        with open(REQUESTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_pending_requests(requests):
    """Save pending access requests"""
    with open(REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)

def log_approved_user(name, email, goals, password):
    """Log approved users to file"""
    os.makedirs("access_logs", exist_ok=True)
    with open(APPROVED_USERS_FILE, "a") as f:
        f.write(f"{name},{email},{goals},{password},{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

def log_temp_password(email, password):
    """Log temporary passwords"""
    os.makedirs("access_logs", exist_ok=True)
    filepath = "access_logs/temp_passwords.csv"
    lines = []
    
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            lines = [line for line in f.readlines() if not line.startswith(email + ",")]
    
    lines.append(f"{email},{password}\n")
    with open(filepath, "w") as f:
        f.writelines(lines)

def update_approved_user_password(email, new_password):
    """Update approved user password"""
    filepath = "access_logs/approved_users.csv"
    if not os.path.exists(filepath):
        return

    updated_lines = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split(",", 4)
            if len(parts) == 5 and parts[1] == email:
                parts[3] = new_password
                parts[4] = datetime.now().strftime('%Y-%m-%d %H:%M')
            updated_lines.append(",".join(parts))

    with open(filepath, "w") as f:
        f.write("\n".join(updated_lines) + "\n")

def launch_lesson(lesson_title, track_title):
    """Launch a lesson page"""
    st.session_state["lesson_topic"] = lesson_title
    st.session_state["track_selected"] = track_title
    st.switch_page("pages/_lesson_runner.py")

# Initialize session state
initialize_session_state()

# Check if we just reran - prevent infinite loops
if st.session_state.get("just_reran", False):
    st.session_state["just_reran"] = False
    st.stop()

# === Setup Authentication ===
users = get_users()
credentials = {
    "usernames": {
        email: {
            "name": user["name"],
            "password": user["password"]
        }
        for email, user in users.items()
    }
}

if not credentials["usernames"]:
    st.error("⚠️ No users found in the database. Please add at least one user.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="walter_ai_cookie",
    key="walter_ai_signature",
    cookie_expiry_days=30
)

# === Authentication Flow ===
def show_login_screen():
    """Display login form and handle authentication"""
    st.markdown("""
        <div style='text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;'>
            <h2>🔐 Welcome to WALTER.AI</h2>
            <p style='font-size: 1rem; color: #555;'>Log in below to access your personalized learning platform.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
    
    name, auth_status, username = authenticator.login("Login", "main")  # Simple fix
    
    if auth_status:
        st.session_state.update({
            "authentication_status": True,
            "username": username,
            "name": name,
            "authenticated_once": True,
            "just_reran": True
        })
        st.rerun()
    elif auth_status is False:
        st.error("Invalid username or password")
    elif auth_status is None:
        st.info("Please enter your credentials")

# Main auth guard
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None

if not st.session_state.authentication_status:
    show_login_screen()
    
    # Access request form
    pending_requests = load_pending_requests()
    with st.expander("👉🏾 Don't have access? Request it here.", expanded=False):
        with st.form("access_request_form", clear_on_submit=True):
            req_name = st.text_input("Full Name", key="request_name")
            req_email = st.text_input("Email Address", key="request_email")
            req_goals = st.text_area("Why do you want access?", key="request_goals")
            submitted = st.form_submit_button(
                "Submit Request", 
                key="access_request_submit"
            )

        if submitted:
            if not req_name or not req_email or not req_goals:
                st.error("All fields are required.")
            elif any(r["email"] == req_email for r in pending_requests):
                st.warning("You've already submitted a request.")
            else:
                pending_requests.append({
                    "name": req_name,
                    "email": req_email,
                    "goals": req_goals
                })
                save_pending_requests(pending_requests)
                st.success("✅ Request submitted. We'll review it shortly.")
    st.stop()

# === Handle Logout ===
if st.session_state.get("authentication_status"):
    if authenticator.logout(
        "🚪 Log Out", 
        "sidebar", 
        key=f"logout_{st.session_state.get('username','default')}"
    ):
        # Clear session state
        for key in list(st.session_state.keys()):
            if key not in ["initialized", "just_reran"]:
                del st.session_state[key]
        
        st.session_state.update({
            "authentication_status": None,
            "logout_triggered": True,
            "just_reran": True
        })
        st.rerun()

# === Main App Content ===
username = st.session_state["username"]
name = st.session_state["name"]

# Sanitize username and set up memory paths
sanitized_username = safe_username(username)
memory_folder = f"walter_memory/{sanitized_username}"
profile_path = f"{memory_folder}/{sanitized_username}_profile.json"
os.makedirs(memory_folder, exist_ok=True)

st.session_state["memory_folder"] = memory_folder
st.session_state["profile_path"] = profile_path

# Load or create profile
if os.path.exists(profile_path):
    profile = load_profile(profile_path)
else:
    profile = None

# === Fallback: Auto-assign track and lesson ===
if "track_selected" not in st.session_state or not st.session_state["track_selected"]:
    if profile and "tracks" in profile:
        first_track = next(iter(profile["tracks"]), None)
        if first_track:
            st.session_state["track_selected"] = first_track

if "lesson_topic" not in st.session_state or not st.session_state["lesson_topic"]:
    selected_track = st.session_state.get("track_selected")
    if selected_track and selected_track in profile["tracks"]:
        lessons_in_track = profile["tracks"][selected_track]
        if lessons_in_track:
            st.session_state["lesson_topic"] = lessons_in_track[0]

# Load LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# === 1. New User Flow ===
if not profile:
    st.title("👋🏾 Welcome to WALTER.AI")
    st.markdown("Let's build your personalized learning path in data. Answer a few questions to begin.")

    # Tabs for onboarding
    tab1, tab2, tab3 = st.tabs(["👤 About You", "🧠 Learning Preferences", "🎯 Time & Goals"])
    
    with tab1:
        name = st.text_input("🧑 What should we call you?")
        current_role = st.selectbox("💼 What's your current role or background?", [
            "", "Student", "Career Switcher", "Junior Analyst", "Non-technical Professional", "Other"
        ])
        motivation = st.selectbox("💡 What's your main motivation for learning data?", [
            "", "Get a new job", "Enhance current role", "Start freelancing", "Explore career options"
        ])
        tools_used = st.multiselect("🧰 Which tools have you used before?", [
            "Excel", "SQL", "Python", "Power BI", "Tableau", "Jupyter", "Google Sheets"
        ])

    with tab2:
        preferred_style = st.selectbox("🧠 How do you prefer to learn?", [
            "", "Step-by-step guidance", "Try first, then get help", "Visual and interactive", "Text-based and structured"
        ])
        comfort_level = st.selectbox("📊 What best describes your current comfort level?", [
            "", "I'm starting from scratch", "I know the basics", "I'm confident with intermediate topics"
        ])
        track = st.selectbox("📚 Which path are you most interested in?", [
            "", "Data Analyst", "Data Engineer", "Data Scientist"
        ])

    with tab3:
        weekly_time = st.selectbox("⏱ How much time can you spend per week?", [
            "", "Less than 3 hours", "3-5 hours", "5-10 hours", "10+ hours"
        ])
        goal_3mo = st.text_input("🔮 Where do you want to be in 3 months?")

    # Validation
    required_fields_filled = all([
        name.strip(), current_role, motivation, preferred_style,
        comfort_level, track, weekly_time, goal_3mo.strip()
    ])

    if "submitted_curriculum" not in st.session_state:
        st.session_state["submitted_curriculum"] = False

    st.markdown("### 📋 When you're ready, build your custom learning path:")
    submit_button = st.button("🚀 Generate My Curriculum", key="generate_curriculum_btn")

    if submit_button:
        if not required_fields_filled:
            st.error("⚠️ Please fill out all fields to generate your learning path.")
            st.stop()
        else:
            with st.spinner("🛠 Generating your custom learning path..."):
                # Curriculum generation logic remains the same
                # ... [rest of your existing curriculum generation code]
                pass

# === 2. Validate profile + curriculum ===
if (st.session_state.get("authentication_status") 
    and st.session_state.get("username") 
    and str(st.session_state.username) not in ADMIN_USERS):
    if not profile or "curriculum" not in profile:
        st.warning("⚠️ No profile or curriculum found. Please restart onboarding.")
        st.stop()

# === Handle lesson navigation ===
query_params = st.query_params
if "lesson" in query_params and "track" in query_params:
    lesson = query_params["lesson"]
    track = query_params["track"]
    if track in profile["tracks"] and lesson in profile["tracks"][track]:
        st.session_state["lesson_topic"] = lesson
        st.session_state["track_selected"] = track
        st.switch_page("pages/_lesson_runner.py")

# === Sidebar Navigation ===
completed = get_completed_lessons(memory_folder)
current_lesson = st.session_state.get("lesson_topic", profile.get("current_topic"))
st.session_state["lesson_topic"] = current_lesson

if "tracks" not in profile or not profile["tracks"]:
    st.warning("⚠️ Your profile is missing learning tracks. Please restart onboarding.")
    st.stop()

tracks = profile["tracks"]

def lesson_status_icon(lesson):
    if lesson == current_lesson:
        return "📍"
    elif lesson in completed:
        return "✅"
    else:
        return "⏳"

# Sidebar lesson navigation with unique keys
for track_title, lessons in tracks.items():
    st.sidebar.markdown(f'<div class="lesson-group"><strong>📘 {track_title}</strong>', unsafe_allow_html=True)
    for idx, lesson in enumerate(lessons):
        btn_key = f"nav_{track_title[:5]}_{idx}_{hash(lesson)}"
        if st.sidebar.button(
            f"{lesson_status_icon(lesson)} Lesson {idx + 1}: {lesson}",
            key=btn_key
        ):
            st.session_state["lesson_topic"] = lesson
            st.session_state["track_selected"] = track_title
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Admin controls
if st.session_state.get("username") in ADMIN_USERS:
    if st.sidebar.button("🧹 Reset All User Data", key="admin_reset_data"):
        try:
            shutil.rmtree("walter_memory", ignore_errors=True)
            st.success("✅ All user data cleared")
            st.stop()
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Dashboard UI remains the same
# ... [rest of your existing dashboard UI code]

# === Final Lesson Navigation ===
remaining_lessons = [l for track in tracks.values() for l in track if l not in completed]
next_lesson = remaining_lessons[0] if remaining_lessons else None

if next_lesson and st.button(
    "▶️ Start / Continue Lesson", 
    key="continue_lesson_btn"
):
    st.session_state["lesson_topic"] = next_lesson
    for track_name, lessons in tracks.items():
        if next_lesson in lessons:
            st.session_state["track_selected"] = track_name
            break
    st.switch_page("pages/_lesson_runner.py")

# Track completion summary
# ... [rest of your existing track completion UI]