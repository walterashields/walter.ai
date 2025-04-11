import streamlit as st
import os
import json
from memory import get_completed_lessons, save_memory
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

MEMORY_FOLDER = "memory"
llm = OllamaLLM(model="mistral")

st.title("🔁 Retry a Past Lesson")

completed = get_completed_lessons()
if not completed:
    st.warning("You haven't completed any lessons yet. Go complete a lesson first.")
    st.stop()

selected_topic = st.selectbox("Select a completed lesson to review and retry:", completed)

# Search for the lesson content
lesson_content = None
for filename in os.listdir(MEMORY_FOLDER):
    if filename.startswith("lesson_"):
        with open(os.path.join(MEMORY_FOLDER, filename)) as f:
            data = json.load(f)
            if data["metadata"].get("topic") == selected_topic:
                lesson_content = data["content"]
                break

if not lesson_content:
    st.error("Lesson content not found.")
    st.stop()

st.markdown(f"### 📘 Reviewing: {selected_topic}")
st.markdown(lesson_content)

st.markdown("## 🧑‍💻 Retry the Challenge")
retry_code = st.text_area("Paste your updated code below. Type carefully and improve your work!", height=300)

if st.button("📤 Submit Retry for Feedback"):
    with st.spinner("Reviewing your improved code..."):
        retry_prompt = PromptTemplate(
            input_variables=["topic", "submitted_code"],
            template="""
You're a friendly and skilled data coach. A learner is retrying their project on "{topic}".

Their new code is:
{submitted_code}

Please review with:
- Warm encouragement
- What improved
- Any remaining fixes
- How to take it further

Structure:

=== ✅ What You Did Better ===
...

=== ⚠️ Things to Fix or Improve ===
...

=== 💡 Pro Tips for Your Retry ===
...
"""
        )
        review_chain = retry_prompt | llm
        feedback = review_chain.invoke({
            "topic": selected_topic,
            "submitted_code": retry_code
        })

        save_memory(feedback, {"topic": selected_topic, "type": "code_retry"})
        st.success("✅ Your retry has been reviewed! Here's your feedback:")
        st.markdown(feedback)
