import os
import shutil
import streamlit as st
from memory import (
    load_learner_profile as load_profile,
    save_learner_profile as save_profile,
    save_memory,
    get_completed_lessons,
    mark_lesson_complete
)
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from datetime import datetime
import re

# Setup
st.set_page_config(page_title="📊 Learning Dashboard", layout="wide")

# Reduce top padding of main content
st.markdown("""
<style>
section.main > div { padding-top: 1rem !important; }
.block-container { padding-top: 1rem !important; }
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

profile_path = "learner_profile.json"
memory_folder = "walter_memory"
llm = OllamaLLM(model="mistral")

# Load or initialize learner profile
profile = load_profile()

# === 1. New User Flow ===
if not profile:
    st.title("👋 Welcome to WALTER.AI")
    st.markdown("Let’s build your personalized learning path in data. Answer a few questions to begin.")

    tab1, tab2, tab3 = st.tabs(["👤 About You", "📚 Preferences", "🚀 Goals"])

    with tab1:
        name = st.text_input("🧑 What should we call you?")
        interest = st.text_input("💡 What's motivating you to learn data?")
        tools = st.text_input("🧰 Have you used any tools like SQL, Python, or Excel?")

    with tab2:
        style = st.text_input("🎧 How do you learn best? (Step-by-step, try-first, videos, etc.)")
        time = st.text_input("⏱ How many hours per week can you dedicate?")
        track = st.selectbox("📚 Which learning track do you want to follow?", ["Analyst", "Engineer", "Scientist"])

    with tab3:
        future = st.text_input("🔮 Where do you see yourself in 3 months with these new skills?")
        submitted = st.button("Generate My Curriculum")

    if submitted:
        st.write("🧠 Creating your custom curriculum...")

        prompt_template = PromptTemplate(
            input_variables=["track", "interest", "tools", "future", "style", "time"],
            template="""
You are a world-class data career coach designing a personalized 8-week learning path.

Here is the learner's background:
- Track: {track}
- Interest: {interest}
- Tools: {tools}
- Future Goals: {future}
- Learning Style: {style}
- Weekly Time: {time} hours

Design an 8-week curriculum. For each week, return:
1. One clear and concise **topic title only** (no prefixes like "Week", "Topic", or "Hands-On Activity")
2. One **hands-on project or activity** related to the topic

🧱 Format example:
Topic Title: Data Cleaning and Preprocessing  
Project: Clean a messy dataset in Excel or Python (remove nulls, fix types)

Do this for all 8 weeks.
"""
        )

        chain = prompt_template | llm
        curriculum = chain.invoke({
            "track": track,
            "interest": interest,
            "tools": tools,
            "future": future,
            "style": style,
            "time": time
        })

        topic_lines = re.findall(r'Topic Title:\s*(.+)', curriculum)
        if not topic_lines:
            topic_lines = [
                line.strip()
                for line in curriculum.splitlines()
                if len(line.strip()) > 6 and not line.lower().startswith(("project:", "-", "week", "hands-on"))
            ]

        first_lesson = topic_lines[0] if topic_lines else None

        if first_lesson:
            profile = {
                "name": name,
                "track": track,
                "interest": interest,
                "tools": tools,
                "future": future,
                "style": style,
                "time": time,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "curriculum": curriculum
            }
            profile["current_topic"] = first_lesson
            save_profile(profile)
            save_memory(curriculum, {"topic": "curriculum", "type": "generated"})
            st.session_state["lesson_topic"] = first_lesson
            st.switch_page("pages/_lesson_runner.py")
        else:
            st.error("❌ Could not extract a lesson topic. Please try regenerating your profile.")
            st.stop()

# === 2. Validate profile + curriculum ===
if not profile or "curriculum" not in profile:
    st.warning("⚠️ No profile or curriculum found. Please restart onboarding.")
    st.stop()

# === 3. Sidebar ===
st.sidebar.title("👤 Profile")
st.sidebar.markdown(f"**User:** {profile.get('name', 'Anonymous')}")
st.sidebar.markdown(f"**Track:** {profile['track']}")
st.sidebar.markdown(f"**Time per week:** {profile['time']} hrs")

curriculum = profile["curriculum"]
raw_lessons = re.findall(r"^\s*(?:\d+\.|\•|\-)?\s*(Topic Title:\s*.+?)(?:\s+Project\:|$)", curriculum, re.MULTILINE)
lessons = [t.replace("Topic Title:", "").strip() for t in raw_lessons]
topics = lessons

completed = get_completed_lessons()
current_lesson = st.session_state.get("lesson_topic")
upcoming = [t for t in topics if t not in completed and t != current_lesson]

# CSS Styling
st.markdown("""
<style>
.lesson-group {
    background-color: #f5f7fa;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 1rem;
}
.lesson-button {
    display: block;
    width: 100%;
    text-align: left;
    padding: 0.4rem 0.6rem;
    margin-bottom: 0.2rem;
    font-size: 0.9rem;
    border: none;
    background-color: #fff;
    border-radius: 6px;
    cursor: pointer;
}
.lesson-button:hover {
    background-color: #e0f0ff;
}
.lesson-button.current {
    background-color: #e0f0ff;
    font-weight: bold;
    border-left: 4px solid #2563eb;
}
.lesson-button.completed {
    color: #4caf50;
}
</style>
""", unsafe_allow_html=True)

# === Sidebar: Lesson Overview ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 📘 Your Lessons")

# Get topic list and current lesson
topics = lessons  # already extracted earlier
completed = get_completed_lessons()
current_lesson = st.session_state.get("lesson_topic")

# Safeguard against edge case
if not current_lesson and "current_topic" in profile:
    current_lesson = profile["current_topic"]
    st.session_state["lesson_topic"] = current_lesson

# Now calculate upcoming (excluding current and completed)
upcoming = [t for t in topics if t not in completed and t != current_lesson]

# Sidebar styling
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

# 📍 Current Lesson
if current_lesson in topics:
    st.sidebar.markdown('<div class="lesson-group"><strong>📍 Current Lesson</strong>', unsafe_allow_html=True)
    idx = topics.index(current_lesson) + 1
    if st.sidebar.button(f"{idx}. {current_lesson}", key=f"current_{idx}"):
        st.session_state["lesson_topic"] = current_lesson
        st.switch_page("pages/_lesson_runner.py")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ⏭️ Upcoming Lessons
if upcoming:
    st.sidebar.markdown('<div class="lesson-group"><strong>⏭️ Upcoming Lessons</strong>', unsafe_allow_html=True)
    for topic in upcoming:
        idx = topics.index(topic) + 1
        if st.sidebar.button(f"{idx}. {topic}", key=f"upcoming_{idx}"):
            st.session_state["lesson_topic"] = topic
            st.switch_page("pages/_lesson_runner.py")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ✅ Completed Lessons
if completed:
    st.sidebar.markdown('<div class="lesson-group"><strong>✅ Completed Lessons</strong>', unsafe_allow_html=True)
    for topic in completed:
        idx = topics.index(topic) + 1
        if st.sidebar.button(f"{idx}. {topic}", key=f"completed_{idx}"):
            st.session_state["lesson_topic"] = topic
            st.switch_page("pages/_lesson_runner.py")
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
st.title("📊 Your Learning Dashboard")
remaining_lessons = [t for t in lessons if t not in completed]
next_lesson = remaining_lessons[0] if remaining_lessons else None
start_date = datetime.strptime(profile.get("start_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
days_since_start = (datetime.now() - start_date).days
avg_days_per_lesson = round(days_since_start / len(completed), 2) if completed else 0

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
        <p><strong>Track:</strong> {profile['track']}</p>
        <p><strong>Time/Week:</strong> {profile['time']} hrs</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="bubble-tile">
        <h4>📈 Progress</h4>
        <p><strong>Lessons:</strong> {len(lessons)}</p>
        <p><strong>Completed:</strong> {len(completed)}</p>
        <p><strong>Progress:</strong> {int((len(completed)/len(lessons))*100) if lessons else 0}%</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="bubble-tile">
        <h4>📆 Activity</h4>
        <p><strong>Days In:</strong> {days_since_start}</p>
        <p><strong>Avg/Lesson:</strong> {avg_days_per_lesson} days</p>
        <p><strong>Started:</strong> {start_date.strftime('%b %d, %Y')}</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="bubble-tile">
        <h4>⏭️ Up Next</h4>
        <p><strong>{next_lesson if next_lesson else "🎉 All complete!"}</strong></p>
    </div>""", unsafe_allow_html=True)

# === Curriculum Section ===
st.markdown("### 🧭 Your Curriculum", unsafe_allow_html=True)

# --- CSS Styling ---
st.markdown("""
<style>
.learning-box {
    background: #fff;
    border-radius: 20px;
    padding: 1.3rem 1.2rem;
    box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.05);
}
.learning-box h4 {
    font-size: 1.1rem;
    color: #222;
    margin-bottom: 1rem;
}
.learning-box ul {
    padding-left: 1.2rem;
    font-size: 0.95rem;
    margin-top: 0;
}
.learning-box p {
    font-size: 0.95rem;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# --- Layout with Proportional Columns ---
col1, col2 = st.columns([2.5, 1])

# 📚 Left: Learning Path
with col1:
    st.markdown(f"""
    <div class="learning-box" style="height: 300px;">
        <h4>📚 Your Learning Path</h4>
        <ul>
            {''.join([f"<li>{w}</li>" for w in lessons])}
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 🚀 Right: Next Lesson + Button
with col2:
    st.markdown(f"""
    <div class="learning-box" style="min-height: 90px;">
        <h4>🚀 Continue Learning</h4>
        <p><strong>{next_lesson if next_lesson else "🎉 All complete!"}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        div[data-testid="stButton"][aria-label="start_continue_button"] > button {
            background-color: #0FBC02 !important;
            color: white !important;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            font-size: 0.95rem;
        }
        </style>
    """, unsafe_allow_html=True)


    
    if next_lesson:
        st.markdown("<div style='margin-top: 0.75rem;'>", unsafe_allow_html=True)
        if st.button("▶️ Start / Continue Lesson", key="start_continue_button"):
            st.session_state["lesson_topic"] = next_lesson
            st.switch_page("pages/_lesson_runner.py")
        st.markdown("</div>", unsafe_allow_html=True)



