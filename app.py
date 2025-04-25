import os
import shutil
import streamlit as st
import streamlit.components.v1 as components
import re
import urllib.parse

# === Shared Lesson Launch Function (Global) ===
def launch_lesson(lesson_title, track_title):
    print(f"▶️ LAUNCHING {lesson_title} in {track_title}")  # Optional debug
    st.session_state["lesson_topic"] = lesson_title
    st.session_state["track_selected"] = track_title
    st.switch_page("pages/_lesson_runner.py")



from memory import (
    load_learner_profile as load_profile,
    save_learner_profile as save_profile,
    save_memory,
    get_completed_lessons,
    mark_lesson_complete
)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime
from dotenv import load_dotenv


# List of approved beta users
USER_DB = {
    "walterashields@gmail.com": "test123",
    "jen@mydomain.com": "jenpass",
    "betauser@site.com": "tryme"
}


# ✅ Load environment variables
load_dotenv()

# === STEP 1: Login Logic ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
        <h1 style='margin-top: 0; padding-top: 0; font-size: 2.4rem;'>Welcome to WALTER.AI</h1>
        <p style='margin-top: -0.5rem;'>Please log in to continue</p>
    """, unsafe_allow_html=True)


    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username in USER_DB and password == USER_DB[username]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()  # 👈 Stop execution if not logged in

# Sanitize username to match _lesson_runner.py format
def safe_username(raw_username):
    return raw_username.replace("@", "_at_").replace(".", "_dot_")

username = safe_username(st.session_state["username"])
memory_folder = f"walter_memory/{username}"
profile_path = f"{memory_folder}/{username}_profile.json"

os.makedirs(memory_folder, exist_ok=True)

st.session_state["memory_folder"] = memory_folder
st.session_state["profile_path"] = profile_path

# ✅ Setup Streamlit page config
st.set_page_config(page_title="📊 Learning Dashboard", layout="wide")

st.markdown("""
<style>
div[data-testid="stSidebar"] button {
    width: 95% !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 0.6rem !important;
    margin-bottom: 0.25rem !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
.lesson-group {
    background-color: #f5f7fa;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 1rem;
}
button[kind="secondary"] {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 0.3rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}
section[data-testid="stSidebarNav"] {
    display: none !important;
}
section.main > div:first-child,
.block-container {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)





# 🔧 Enable JS-to-Python postMessage event handling
st.markdown("""
<script>
window.addEventListener("message", (event) => {
    const msg = event.data;
    if (msg && msg.isStreamlitMessage && msg.type === "streamlit:setComponentValue") {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            key: msg.key,
            value: msg.value
        }, "*");
    }
});
</script>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.scroll-list {
    max-height: 120px;
    overflow-y: auto;
    padding-right: 8px;
}
.scroll-list p {
    margin: 0.2rem 0;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
div[data-testid="stButton"] > button {
    font-size: 0.85rem;
    padding: 0.35rem 0.6rem;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)




# CSS for sidebar containers and button styling
st.markdown("""
<style>
.lesson-group {
    background-color: #f5f7fa;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 1rem;
}
button[kind="secondary"] {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 0.3rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.small-button-container button {
    font-size: 0.82rem !important;
    padding: 0.3rem 0.6rem;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# Make dropdown scrollable
st.markdown("""
<style>
.scrollable-dropdown {
    max-height: 180px;
    overflow-y: auto;
    padding-right: 5px;
}
.small-button-container button {
    font-size: 0.85rem !important;
    padding: 0.25rem 0.5rem !important;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)



# Ensure a user is logged in
# if "username" not in st.session_state:
#     st.session_state.clear()
#    st.rerun()



# === Load or create the learner profile
if os.path.exists(profile_path):
    profile = load_profile(profile_path)
else:
    profile = None  # Triggers onboarding if profile doesn't exist



# ✅ Fallback: Auto-assign track and lesson if missing from session state
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


# Save both paths to session state for reuse
st.session_state["memory_folder"] = memory_folder
st.session_state["profile_path"] = profile_path


# Load LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)



# === 1. New User Flow ===
if not profile:
    st.title("👋🏾 Welcome to WALTER.AI")
    st.markdown("Let’s build your personalized learning path in data. Answer a few questions to begin.")

    # === Tabs for Onboarding ===
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
            "", "I'm starting from scratch", "I know the basics", "I’m confident with intermediate topics"
        ])
        track = st.selectbox("📚 Which path are you most interested in?", [
            "", "Data Analyst", "Data Engineer", "Data Scientist"
        ])

    with tab3:
        weekly_time = st.selectbox("⏱ How much time can you spend per week?", [
            "", "Less than 3 hours", "3–5 hours", "5–10 hours", "10+ hours"
        ])
        goal_3mo = st.text_input("🔮 Where do you want to be in 3 months?")

    # === Validation Logic for Submission ===
    required_fields_filled = all([
        name.strip(), current_role, motivation, preferred_style,
        comfort_level, track, weekly_time, goal_3mo.strip()
    ])

    # === Disable after first click ===
    if "submitted_curriculum" not in st.session_state:
        st.session_state["submitted_curriculum"] = False

    st.markdown("### 📋 When you're ready, build your custom learning path:")

    submit_button = st.button("🚀 Generate My Curriculum")

    if submit_button:
        if not required_fields_filled:
            st.error("⚠️ Please fill out all fields from each tab (👤 About You 🧠 Learning Preferences and 🎯 Time & Goals) to generate your personal learning path.")
            st.stop()
        else:
            st.session_state["submitted_curriculum"] = True


    if submit_button:
        with st.spinner("🛠 Generating your custom learning path..."):
            prompt_template = PromptTemplate(
                input_variables=[
                    "track", "motivation", "tools_used", "goal_3mo",
                    "preferred_style", "weekly_time", "comfort_level", "current_role"
                ],
                template="""
            You are an expert curriculum designer creating a highly personalized, job-ready learning path for a new data learner.

            Your inspiration comes from:
            - Google Data Analytics Certificate (for Analysts)
            - IBM Data Science Certificate (for Scientists)
            - Udacity Data Engineering Nanodegree (for Engineers)

            🎯 Learner Profile:
            - Desired Track: {track}
            - Motivation: {motivation}
            - Current Role: {current_role}
            - Comfort Level: {comfort_level}
            - Tools Experience: {tools_used}
            - Weekly Time Available: {weekly_time}
            - Preferred Learning Style: {preferred_style}
            - 3-Month Goal: {goal_3mo}

            🧩 Your Task:
            Create a curriculum made up of multiple **Tracks** (e.g. "SQL Foundations", "Data Cleaning with Pandas", etc.). Each Track must include:
            - A Track Title
            - A list of 8–12 progressively scaffolded lesson titles

            🛠️ Format (Output exactly like this):
            Track: SQL Foundations  
            - Lesson 1: Introduction to Relational Databases  
            - Lesson 2: Basic SQL SELECT Statements  
            ...  
            - Lesson 10: Aggregations and GROUP BY Clauses

            Track: Data Visualization with Python  
            - Lesson 1: Intro to Matplotlib and Line Charts  
            ...  
            - Lesson 8: Building Interactive Dashboards

            📏 Rules:
            - Use only plain text (no bullet points or markdown)
            - Do NOT include explanations or summaries
            - Make sure the lessons match the learner’s motivation, skill level, and weekly time
            - All Tracks must be useful and achievable within a 3-month timeframe
            - Do not exceed 10 total Tracks

            Now build a complete, personalized learning path based on the above profile.
            """
            )

            curriculum = (prompt_template | llm).invoke({
                "track": track,
                "motivation": motivation,
                "tools_used": tools_used,
                "goal_3mo": goal_3mo,
                "preferred_style": preferred_style,
                "weekly_time": weekly_time,
                "comfort_level": comfort_level,
                "current_role": current_role
            })

            # === Extract Tracks and Lessons ===
            tracks = {}
            current_track = None

            for line in curriculum.content.splitlines():
                line = line.strip()
                if line.startswith("Track:"):
                    current_track = line.replace("Track:", "").strip()
                    tracks[current_track] = []
                elif line.startswith("- Lesson") and current_track:
                    lesson_title = re.sub(r"^- Lesson \d+:\s*", "", line).strip()
                    if lesson_title:
                        tracks[current_track].append(lesson_title)

            # Safety check
            if not tracks or not any(tracks.values()):
                st.error("❌ Curriculum did not generate valid tracks or lessons. Please try again.")
                st.stop()

            # Flatten into list of all topics (for legacy display or navigation)
            all_lessons = []
            for tname, modules in tracks.items():
                all_lessons.extend(modules)

            first_lesson = all_lessons[0] if all_lessons else None

            # === Defer Lesson Content Generation Until Track Is Accessed ===
            track_lessons = {
                track: [None] * len(lessons)
                for track, lessons in tracks.items()
            }

            # ✅ Ensure track_lessons keys match tracks
            for track in tracks:
                if track not in track_lessons:
                    track_lessons[track] = [None] * len(tracks[track])

            # === Save Profile and Route ===
            if first_lesson:
                profile = {
                    "name": name,
                    "track": track,
                    "interest": motivation,
                    "tools": tools_used,
                    "future": goal_3mo,
                    "style": preferred_style,
                    "time": weekly_time,
                    "comfort": comfort_level,
                    "role": current_role,
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                    "curriculum": curriculum,
                    "tracks": tracks,
                    "topics": all_lessons,
                    "lesson_blocks": [],
                    "track_lessons": track_lessons,
                    "current_topic": first_lesson
                }

                save_profile(profile, profile_path)
                st.write("🛠 Initialized lesson slots for track:", list(track_lessons.keys()))
                st.write("🛠 Slot count:", {k: len(v) for k, v in track_lessons.items()})

                save_memory(curriculum, {"topic": "curriculum", "type": "generated"}, memory_folder)
                st.session_state["lesson_topic"] = first_lesson
                st.session_state["track_selected"] = list(tracks.keys())[0]
                st.rerun()  # This simply reloads the page and lands them on the dashboard
                # === Ensure current lesson and track are valid
                if "lesson_topic" not in st.session_state or st.session_state["lesson_topic"] not in profile.get("topics", []):
                    first_track = next(iter(profile["tracks"]), None)
                    if first_track:
                        st.session_state["track_selected"] = first_track
                        st.session_state["lesson_topic"] = profile["tracks"][first_track][0]

            else:
                st.error("❌ Could not extract a lesson topic. Please try regenerating your profile.")
                st.stop()

# === 2. Validate profile + curriculum ===
if not profile or "curriculum" not in profile:
    st.warning("⚠️ No profile or curriculum found. Please restart onboarding.")
    st.stop()




# === Handle lesson jump via query params (e.g., from Completed Lessons list)
query_params = st.query_params
if "lesson" in query_params and "track" in query_params:
    lesson = query_params["lesson"]
    track = query_params["track"]
    if track in profile["tracks"] and lesson in profile["tracks"][track]:
        st.session_state["lesson_topic"] = lesson
        st.session_state["track_selected"] = track
        st.switch_page("pages/_lesson_runner.py")




# ✅ Handle lesson launch from fake markdown link
if "fake_click" in st.session_state:
    clicked_lesson = st.session_state.pop("fake_click", None)
    if clicked_lesson:
        for track_name, lessons in profile["tracks"].items():
            if clicked_lesson in lessons:
                launch_lesson(clicked_lesson, track_name)
                break




# === Log Out Button ===
if st.sidebar.button("🚪 Log Out"):
    st.session_state.pop("username", None)
    st.session_state.clear()
    st.rerun()

# === 3. Sidebar ===


if st.session_state["username"] == "walterashields@gmail.com":
    if st.sidebar.button("🧹 Reset All User Data (Safe Dev Use)"):
        try:
            user_root = "walter_memory"
            if os.path.exists(user_root):
                for user_dir in os.listdir(user_root):
                    full_path = os.path.join(user_root, user_dir)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)

            st.success("✅ All user profiles and memory cleared. Vector store left untouched.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Reset failed: {e}")
            st.stop()


completed = get_completed_lessons(memory_folder)
current_lesson = st.session_state.get("lesson_topic", profile.get("current_topic"))
st.session_state["lesson_topic"] = current_lesson

# === Track-aware UI ===
if "tracks" not in profile or not profile["tracks"]:
    st.warning("⚠️ Your profile is missing learning tracks. Please restart your onboarding to regenerate a complete curriculum.")
    st.stop()

tracks = profile["tracks"]

total_lessons = sum(len(lessons) for lessons in tracks.values())

def lesson_status_class(lesson):
    if lesson == current_lesson:
        return "current"
    elif lesson in completed:
        return "completed"
    else:
        return ""

def lesson_status_icon(lesson):
    if lesson == current_lesson:
        return "📍"
    elif lesson in completed:
        return "✅"
    else:
        return "⏳"

# === Sidebar: Tracks & Lessons ===
for track_title, lessons in tracks.items():
    st.sidebar.markdown(f'<div class="lesson-group"><strong>📘 {track_title}</strong>', unsafe_allow_html=True)
    for idx, lesson in enumerate(lessons):
        icon = lesson_status_icon(lesson)
        display = f"{icon} Lesson {idx + 1}: {lesson}"
        if st.sidebar.button(display, key=f"{track_title}_{lesson}"):
            launch_lesson(lesson, track_title)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)



# === Restart button ===
if st.sidebar.button("🔄 Restart Profile"):
    try:
        if os.path.exists(profile_path):
            os.remove(profile_path)
        if os.path.exists(memory_folder):
            for f in os.listdir(memory_folder):
                file_path = os.path.join(memory_folder, f)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as inner_e:
                    print(f"Error deleting {file_path}: {inner_e}")
        st.success("✅ Profile and memory cleared. Please refresh.")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error while clearing profile: {e}")
        st.stop()

# === Dashboard Tiles ===
with st.container():
    st.markdown("""
    <style>
    h1.dash-title {
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0.5rem !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 id='dashboard-title' class='dash-title'>📊 Your Learning Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("""
    <script>
        const target = document.getElementById("dashboard-title");
        if (target) {
            setTimeout(() => {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 100);
        }
    </script>
    """, unsafe_allow_html=True)
    
remaining_lessons = []
for track_lessons in tracks.values():
    remaining_lessons.extend([t for t in track_lessons if t not in completed])
next_lesson = remaining_lessons[0] if remaining_lessons else None

start_date = datetime.strptime(profile.get("start_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
days_since_start = (datetime.now() - start_date).days
avg_days_per_lesson = round(days_since_start / len(completed), 2) if completed else 0

# === Style Enhancements for Curriculum Section ===
st.markdown("""
<style>
/* Expander header tweaks */
details > summary {
    font-weight: 600;
    font-size: 1.05rem;
    background-color: #f0f4f8;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    cursor: pointer;
}

/* Lesson button styling inside expanders */
div[data-testid="stButton"] > button {
    width: 100%;
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    margin-bottom: 0.3rem;
    font-size: 0.93rem;
    transition: background-color 0.2s ease;
}

div[data-testid="stButton"] > button:hover {
    background-color: #e8f0fe;
    border-color: #c6dbfc;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.bubble-tile {
    background: #fff;
    border-radius: 20px;
    padding: 1.3rem 1.2rem;
    box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.05);
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.bubble-tile h4 {
    font-size: 1.1rem;
    color: #222;
    margin-bottom: 1rem;
}
.bubble-tile p {
    margin: 0.25rem 0;
    font-size: 0.95rem;
}
.bubble-tile ul {
    padding-left: 1.2rem;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="bubble-tile">
        <h4>👤 Learner Info</h4>
        <p><strong>Name:</strong> {profile['name']}</p>
        <p><strong>Program:</strong> {profile['track']}</p>
        <p><strong>Time/Week:</strong> {profile['time']}</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="bubble-tile">
        <h4>📈 Lesson Progress</h4>
        <p><strong>Total Lessons:</strong> {total_lessons}</p>
        <p><strong>Completed:</strong> {len(completed)}</p>
        <p><strong>Progress:</strong> {int((len(completed)/total_lessons)*100) if total_lessons else 0}%</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="bubble-tile">
        <h4>📆 Your Activity</h4>
        <p><strong>Days In:</strong> {days_since_start}</p>
        <p><strong>Avg/Lesson:</strong> {avg_days_per_lesson} days</p>
        <p><strong>Started:</strong> {start_date.strftime('%b %d, %Y')}</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="bubble-tile">
        <h4>⏭️ Up Next</h4>
        <p><strong>{next_lesson if next_lesson else "🎉 All complete!"}</strong></p>
    </div>""", unsafe_allow_html=True)


# === Continue Button ===
if next_lesson:
    st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
if st.button("▶️ Start / Continue Lesson", key="start_continue_button"):
    st.session_state["lesson_topic"] = next_lesson
    # This gets the correct track that lesson belongs to
    for track_name, lessons in tracks.items():
        if next_lesson in lessons:
            st.session_state["track_selected"] = track_name
            break
    st.switch_page("pages/_lesson_runner.py")


    st.markdown("</div>", unsafe_allow_html=True)


# === Track Completion Summary ===
track_completion = {
    track: all(lesson in completed for lesson in lessons)
    for track, lessons in tracks.items()
}
tracks_completed = sum(track_completion.values())
total_tracks = len(tracks)

col_track, col_completed_tracks, col_completed_lessons = st.columns(3)
# 🧭 Progress bubble
with col_track:
    st.markdown(f"""
    <div class="bubble-tile" style="display: flex; flex-direction: column; justify-content: flex-start;">
        <h4>📂 Track Progress</h4>
        <p><strong>Tracks:</strong> {total_tracks}</p>
        <p><strong>Completed:</strong> {tracks_completed}</p>
        <p><strong>Progress:</strong> {int((tracks_completed/total_tracks)*100) if total_tracks else 0}%</p>
    </div>
    """, unsafe_allow_html=True)



completed_tracks = {
    t: l for t, l in tracks.items()
    if all(lesson in completed for lesson in l)
}


with col_completed_tracks:
    completed_tracks_html = """
    <div class="bubble-tile" style="display: flex; flex-direction: column; justify-content: flex-start;">
        <h4>✅ Completed Tracks</h4>
        <div style='max-height: 120px; overflow-y: auto; padding-right: 5px;'>"""

    completed_tracks = {
        t: l for t, l in tracks.items()
        if all(lesson in completed for lesson in l)
    }

    if completed_tracks:
        for track_title in completed_tracks:
            completed_tracks_html += f"""
            <p style='margin: 0.2rem 0; font-size: 0.9rem; color:#2b6cb0;'>
                {track_title}
            </p>"""
    else:
        completed_tracks_html += "<p style='font-size: 0.9rem;'>No completed tracks yet.</p>"

    completed_tracks_html += "</div></div>"
    st.markdown(completed_tracks_html, unsafe_allow_html=True)


with col_completed_lessons:
    completed_lessons_html = """
    <div class="bubble-tile" style="display: flex; flex-direction: column; justify-content: flex-start;">
        <h4>✅ Completed Lessons</h4>
        <div style='max-height: 120px; overflow-y: auto; padding-right: 5px;'>"""

    if completed:
        for track_title, lessons in tracks.items():
            for lesson in lessons:
                if lesson in completed:
                    completed_lessons_html += f"""
                    <p style='margin: 0.2rem 0; font-size: 0.9rem; color:#2b6cb0;'>
                        {lesson}
                    </p>"""
    else:
        completed_lessons_html += "<p style='font-size: 0.9rem;'>No completed lessons yet.</p>"

    completed_lessons_html += "</div></div>"
    st.markdown(completed_lessons_html, unsafe_allow_html=True)



# === Expanded Curriculum Display ===
st.markdown("### 📚 Your Full Curriculum by Track")

for track_title, lessons in tracks.items():
    completed_count = len([l for l in lessons if l in completed])
    total_count = len(lessons)
    
    with st.expander(f"📘 {track_title} ({completed_count}/{total_count} completed)", expanded=False):
        for i, lesson in enumerate(lessons, 1):
            status_icon = "✅" if lesson in completed else "⏳"
            button_label = f"{status_icon} Lesson {i}: {lesson}"
            if st.button(button_label, key=f"{track_title}_{lesson}_expander"):
                launch_lesson(lesson, track_title)
