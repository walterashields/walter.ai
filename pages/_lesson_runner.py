import streamlit as st

if "lesson_topic" not in st.session_state:
    st.warning("⚠️ No topic selected. Please launch a lesson from the main app.")
    st.stop()

from memory import (
    load_learner_profile,
    save_learner_profile,
    save_memory,
    mark_lesson_complete,
    get_completed_lessons
)
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import re

# Reduce top padding of main content
st.markdown("""
<style>
section.main > div { padding-top: 1rem !important; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# === Add CSS Styling to Match Dashboard Sidebar ===
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

# === Load learner profile and curriculum ===
profile = load_learner_profile()
if not profile or "curriculum" not in profile:
    st.warning("⚠️ No learner profile found. Please return to the main app to start.")
    st.stop()

curriculum = profile["curriculum"]
raw_topics = re.findall(r"^\s*(?:\d+\.|\•|\-)?\s*(Topic Title:\s*.+?)(?:\s+Project\:|$)", curriculum, re.MULTILINE)
topics = [t.replace("Topic Title:", "").strip() for t in raw_topics]

if not topics:
    st.warning("⚠️ Curriculum was generated, but no topics were found. Please restart and try again.")
    st.stop()

# === Load and normalize completed lessons ===
completed = [t.strip() for t in get_completed_lessons()]

# Recover or set lesson topic
if "lesson_topic" not in st.session_state or not st.session_state["lesson_topic"]:
    fallback = profile.get("current_topic")
    if fallback and fallback in topics:
        st.session_state["lesson_topic"] = fallback
    elif topics:
        st.session_state["lesson_topic"] = topics[0]
    else:
        st.warning("⚠️ No valid topic found. Please regenerate your curriculum.")
        st.stop()

current_topic = st.session_state["lesson_topic"]

# Fix edge case: current topic shown as complete without code
if (
    "code_input" not in st.session_state or
    not st.session_state["code_input"].strip()
) and current_topic in completed:
    completed.remove(current_topic)

# Final topic validation
if current_topic not in topics:
    st.warning("⚠️ Invalid topic loaded. Please return to the main app.")
    st.stop()

# Persist lesson topic
profile["current_topic"] = current_topic
save_learner_profile(profile)

# === Initialize model ===
llm = OllamaLLM(model="mistral")

# === Sidebar Styling ===
st.sidebar.title("📊 Your Progress")
st.sidebar.markdown(f"**👤 Name:** {profile.get('name', 'Anonymous')}")
st.sidebar.markdown(f"**Track:** {profile['track']}")
st.sidebar.markdown(f"**Completed:** {len(completed)} / {len(topics)}")

# Current Lesson Section
st.sidebar.markdown('<div class="lesson-group"><strong>📍 Current Lesson</strong>', unsafe_allow_html=True)
idx = topics.index(current_topic) + 1
if st.sidebar.button(f"{idx}. {current_topic}", key=f"current_{idx}"):
    st.session_state["lesson_topic"] = current_topic
    st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Upcoming Lessons
upcoming = [t for t in topics if t not in completed and t != current_topic]
if upcoming:
    st.sidebar.markdown('<div class="lesson-group"><strong>⏭️ Upcoming Lessons</strong>', unsafe_allow_html=True)
    for t in upcoming:
        idx = topics.index(t) + 1
        if st.sidebar.button(f"{idx}. {t}", key=f"upcoming_{idx}"):
            st.session_state["lesson_topic"] = t
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Completed Lessons
if completed:
    st.sidebar.markdown('<div class="lesson-group"><strong>✅ Completed Lessons</strong>', unsafe_allow_html=True)
    for t in completed:
        idx = topics.index(t) + 1
        if st.sidebar.button(f"{idx}. {t}", key=f"completed_{idx}"):
            st.session_state["lesson_topic"] = t
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# === 1. Show lesson ===
st.title("📘 Lesson In Progress")
st.subheader(f"🎯 Topic: {current_topic}")

with st.spinner("🧠 Generating your personalized lesson..."):
    lesson_prompt = PromptTemplate(
        input_variables=["topic"],
        template="""
You are a highly engaging and hands-on data instructor. Help the learner deeply understand the following topic: "{topic}"

Write the lesson in a way that is:
- Beginner-friendly and human (like a mentor)
- Structured and practical
- Focused on clarity and outcomes

Use this format exactly:

=== 🧠 Concept ===
...

=== 🛠️ Step-by-Step Walkthrough ===
...

=== 🚀 Your Mini Project Challenge ===
...

=== ✅ What Success Looks Like ===
...
"""
    )
    lesson_chain = lesson_prompt | llm
    lesson = lesson_chain.invoke({"topic": current_topic})

def validate_lesson(lesson_text):
    required_keywords = ["Concept", "Walkthrough", "Challenge", "Success"]
    return all(keyword in lesson_text for keyword in required_keywords)

if validate_lesson(lesson):
    save_memory(lesson, {"topic": current_topic, "type": "lesson"})
    st.markdown(lesson)
else:
    st.error("⚠️ Sorry, the lesson generation failed. Please go back and try again.")
    st.stop()

st.divider()

# === 2. Code submission ===
if "code_input" not in st.session_state or not st.session_state.get("lesson_generated", False):
    st.session_state["code_input"] = ""
    st.session_state["lesson_generated"] = True

st.markdown("## 🧑‍💻 Your Turn to Try")
st.text_area("Paste your solution to the mini project challenge below:", key="code_input", height=300)

st.caption("Submit code at least once to maek this lesson Complete")
if st.button("📤 Submit Code for Review") and st.session_state["code_input"].strip():
    with st.spinner("🧠 Reviewing your code with WALTER.AI..."):
        feedback_prompt = PromptTemplate(
            input_variables=["topic", "submitted_code"],
            template="""
You're a friendly and skilled code coach. A learner just completed a project on: "{topic}"

Here’s their code:
{submitted_code}

Please review it by responding with:
- Encouraging tone
- What they did well
- Any fixes or improvements
- Suggestions to go further

Use this structure:

=== ✅ What You Did Well ===
...

=== ⚠️ Fixes & Suggestions ===
...

=== 💡 Pro Tips to Go Further ===
...
"""
        )
        review_chain = feedback_prompt | llm
        feedback = review_chain.invoke({
            "topic": current_topic,
            "submitted_code": st.session_state["code_input"]
        })

        save_memory(feedback, {"topic": current_topic, "type": "code_review"})
        st.success("✅ Code reviewed! See your feedback below.")

        sections = {
            "✅ What You Did Well": st.success,
            "⚠️ Fixes & Suggestions": st.warning,
            "💡 Pro Tips to Go Further": st.info
        }

        for title, display_func in sections.items():
            start = feedback.find(title)
            if start != -1:
                end = min([
                    feedback.find(t, start + 1)
                    for t in sections
                    if t != title and feedback.find(t, start + 1) != -1
                ] + [len(feedback)])
                section_text = feedback[start:end].strip()
                display_func(section_text)

        mark_lesson_complete(current_topic)
        completed = get_completed_lessons()

    st.divider()
    st.markdown("## ✅ Lesson Complete")
    st.success(f"You've completed: {current_topic}")

# === 3. Progress Navigation ===
remaining = [t for t in topics if t not in completed and t != current_topic]

if remaining:
    next_lesson = remaining[0]
    st.info(f"➡️ Up Next: {next_lesson}")

    if st.button("🚀 Go to Next Lesson"):
        st.session_state.pop("code_input", None)
        st.session_state.pop("feedback", None)
        st.session_state["lesson_generated"] = False
        st.session_state["lesson_topic"] = next_lesson
        st.rerun()
else:
    st.balloons()
    st.success("🎉 You’ve completed all lessons in your curriculum!")
