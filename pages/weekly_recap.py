import streamlit as st
import os
import json
from memory import get_completed_lessons, load_learner_profile

# === Load user profile and memory ===
profile = load_learner_profile()
if not profile:
    st.warning("⚠️ No learner profile found. Please return to the main app.")
    st.stop()

st.title("📅 Weekly Recap")
st.markdown("Here’s a quick recap of your learning progress so far.")

# === Profile Summary ===
st.markdown("### 👤 Profile")
st.markdown(f"- **Name:** {profile.get('name', 'Anonymous')}")
st.markdown(f"- **Track:** {profile['track']}")
st.markdown(f"- **Weekly Commitment:** {profile['time']} hrs")

# === Completed Lessons Summary ===
completed = get_completed_lessons()
if not completed:
    st.info("You haven’t completed any lessons yet. Come back after your first few!")
    st.stop()

st.markdown("### ✅ Completed Lessons")
for lesson in completed:
    st.markdown(f"- {lesson}")

# === Motivation Booster ===
st.markdown("### 🚀 Motivation Boost")
st.success("You're making great progress! Stay consistent and you'll reach your goals. 💪")

# === Export Option ===
if st.button("📤 Export Recap to Text File"):
    export_data = {
        "profile": profile,
        "completed_lessons": completed,
    }
    os.makedirs("portfolio", exist_ok=True)
    file_path = f"portfolio/weekly_recap_{profile.get('name', 'user')}.txt"
    with open(file_path, "w") as f:
        f.write("WEEKLY PROGRESS RECAP\n")
        f.write("======================\n\n")
        f.write(f"Name: {profile.get('name', 'Anonymous')}\n")
        f.write(f"Track: {profile['track']}\n")
        f.write(f"Weekly Hours: {profile['time']}\n\n")
        f.write("Completed Lessons:\n")
        for lesson in completed:
            f.write(f"- {lesson}\n")
    st.success(f"📁 Recap saved to {file_path}")

# === Back to Lesson Link ===
if st.button("🔙 Back to Lesson"):
    st.switch_page("pages/_lesson_runner.py")
