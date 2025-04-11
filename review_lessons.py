import os
import json
import streamlit as st
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from memory import get_completed_lessons, load_learner_profile, save_memory

# === 1. Load Profile and Completed Lessons ===
profile = load_learner_profile()
completed = get_completed_lessons()

st.title("🔁 Retry a Past Lesson")

if not completed:
    st.warning("⚠️ No completed lessons found. Complete a lesson first.")
    st.stop()

# === 2. Let Learner Pick a Lesson to Retry ===
selected_topic = st.selectbox("📚 Select a completed lesson to retry:", completed)

# === 3. Load Original Lesson Content ===
lesson_content = None
for filename in os.listdir("memory"):
    if filename.startswith("lesson_"):
        with open(os.path.join("memory", filename)) as f:
            data = json.load(f)
            if data["metadata"].get("topic") == selected_topic:
                lesson_content = data["content"]
                break

if lesson_content:
    with st.expander("📖 Original Lesson Content", expanded=False):
        st.markdown(lesson_content)
else:
    st.error("❌ Could not find lesson content in memory.")
    st.stop()

# === 4. Retry Code Submission ===
st.markdown("## 🧑‍💻 Try the Mini Project Again")
retry_code = st.text_area("Paste your updated code below:", height=300)

if st.button("📤 Submit Retry for Review"):
    with st.spinner("🧠 Reviewing your updated code..."):
        llm = OllamaLLM(model="mistral")
        feedback_prompt = PromptTemplate(
            input_variables=["topic", "submitted_code"],
            template="""
You're a friendly and highly skilled data and code coach. A learner is retrying a challenge for: "{topic}"

Here’s their updated code:
{submitted_code}

Please review it and respond with:

=== ✅ What You Did Better ===
...

=== ⚠️ Things to Fix or Improve ===
...

=== 💡 Pro Tips for Your Retry ===
...
"""
        )
        chain = feedback_prompt | llm
        feedback = chain.invoke({
            "topic": selected_topic,
            "submitted_code": retry_code
        })

        # Save feedback
        save_memory(feedback, {"topic": selected_topic, "type": "code_retry"})

        st.success("✅ Retry feedback generated!")
        st.markdown(feedback)
