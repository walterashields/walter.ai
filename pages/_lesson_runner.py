import streamlit as st
<<<<<<< HEAD
import re
=======

if "lesson_topic" not in st.session_state:
    st.warning("⚠️ No topic selected. Please launch a lesson from the main app.")
    st.stop()

>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
from memory import (
    load_learner_profile,
    save_learner_profile,
    save_memory,
    mark_lesson_complete,
    get_completed_lessons
)
<<<<<<< HEAD
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# === UI Setup ===
=======
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import re

# Reduce top padding of main content
>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
st.markdown("""
<style>
section.main > div { padding-top: 1rem !important; }
.block-container { padding-top: 1rem !important; }
<<<<<<< HEAD
=======
</style>
""", unsafe_allow_html=True)

# === Add CSS Styling to Match Dashboard Sidebar ===
st.markdown("""
<style>
>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
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

<<<<<<< HEAD
# === Load learner profile ===
profile = load_learner_profile()
if not profile or "tracks" not in profile or "track_lessons" not in profile:
    st.warning("⚠️ Incomplete profile. Please regenerate your curriculum from the main app.")
    st.stop()

# === Select current track ===
track_selected = st.session_state.get("track_selected")
if not track_selected or track_selected not in profile["tracks"]:
    st.warning("⚠️ No track selected. Please return to the main app and launch a track.")
    st.stop()

# Include all lessons from all tracks for sidebar navigation
topics = [lesson for lessons in profile["tracks"].values() for lesson in lessons]
lesson_blocks = profile["track_lessons"][track_selected]

# === Generate the Current Lesson Only if Missing ===
lesson_index = profile["tracks"][track_selected].index(st.session_state["lesson_topic"])

# === Load vector store and retrieve context for lesson ===
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

import os

# Build rich query
track = profile.get("track", "")
comfort = profile.get("comfort_level", "beginner")
role = profile.get("current_role", "")
topic = st.session_state.get("lesson_topic", "")

query_string = f"{track} | {comfort} | {role} | {topic}"

# Load prioritized file list
prioritized_path = "vector_store_openai/prioritized_files.txt"
prioritized_files = set()
if os.path.exists(prioritized_path):
    with open(prioritized_path, "r") as f:
        prioritized_files = set(line.strip() for line in f if line.strip())

# Vector store retrieval
retriever = Chroma(
    persist_directory="vector_store_openai",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002")
).as_retriever(search_kwargs={"k": 15})

all_docs = retriever.get_relevant_documents(query_string)

# Re-rank: prioritize documents from curated GitHub files
ranked_docs = sorted(
    all_docs,
    key=lambda doc: 0 if doc.metadata.get("source") in prioritized_files else 1
)

retrieved_docs = ranked_docs[:6]
retrieved_context = "\n\n".join([doc.page_content for doc in retrieved_docs])


from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

if lesson_blocks[lesson_index] is None:
    with st.spinner(f"🛠 Generating content for lesson: '{st.session_state['lesson_topic']}'"):

        import os

        # Rebuild query with learner context
        track = profile.get("track", "")
        comfort = profile.get("comfort_level", "beginner")
        role = profile.get("current_role", "")
        topic = st.session_state.get("lesson_topic", "")
        query_string = f"{track} | {comfort} | {role} | {topic}"

        # Load prioritized sources
        prioritized_path = "vector_store_openai/prioritized_files.txt"
        prioritized_files = set()
        if os.path.exists(prioritized_path):
            with open(prioritized_path, "r") as f:
                prioritized_files = set(line.strip() for line in f if line.strip())

        # Retrieve from vector store
        retriever = Chroma(
            persist_directory="vector_store_openai",
            embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002")
        ).as_retriever(search_kwargs={"k": 15})

        all_docs = retriever.get_relevant_documents(query_string)

        # Prioritize
        ranked_docs = sorted(
            all_docs,
            key=lambda doc: 0 if doc.metadata.get("source") in prioritized_files else 1
        )

        retrieved_docs = ranked_docs[:6]
        retrieved_context = "\n\n".join([doc.page_content for doc in retrieved_docs])


        lesson_template = PromptTemplate(
            input_variables=["track", "lesson", "retrieved_context"],
            template="""
        You're an expert instructional designer creating a markdown-formatted data science lesson for a self-paced course. This lesson is part of the **{track}** track and focuses on the topic: **{lesson}**.

        🧭 Your task is to write the lesson in the same format and quality as the [Data Science for Beginners GitHub curriculum](https://github.com/microsoft/Data-Science-For-Beginners). Use ONLY the trusted context provided. Do NOT invent content not grounded in that context.

        ---

        📘 **REFERENCE CONTEXT**  
        {retrieved_context}

        ---

        📘 **Lesson Structure and Guidelines**

        ### ✅ Format your output like this:

        ---

        # 📘 Lesson Title  
        Write a short, clear, and inviting title that aligns with the topic (but don't repeat it word-for-word).

        ---

        ## 🎯 Learning Objectives  
        Start with a short list (3–5) of specific, outcome-driven objectives.  
        Use Bloom’s action verbs like: *define, explain, compare, analyze, build*.

        ---

        ## 💡 Introduction  
        Provide a short and clear explanation of why this topic matters, connecting it to the learner’s real-world context or future applications.  
        Use plain language and examples that make abstract ideas relatable.

        ---

        ## 📊 Core Concepts  
        Break the lesson into **clearly labeled sections** for each concept or technique.  
        Each section should include:

        - 📚 Concept explanation (2–4 paragraphs)
        - 💻 Code examples (with output if relevant)
        - 📊 Visual aids or tables where applicable
        - 📌 Use analogies or real-world case studies if available

        Use **markdown formatting** consistently. For example:
        - `### Understanding Structured vs Unstructured Data`
        - `**Syntax Example**:` followed by a code block
        - Use `<dl><dt><dd>` for definition lists where helpful

        ---

        ## 🔍 Scenario or Walkthrough  
        Include a practical scenario that brings all core ideas together.  
        This can be a guided example or short project-style walkthrough.

        ---

        ## 🧪 Challenge  
        List 1–2 hands-on tasks learners should complete based on the lesson.  
        These should be grounded in the material just covered.

        - Task 1: _(Short instruction or question)_
        - Task 2: _(Optional second challenge)_

        ---

        ## ✅ Self-Check  
        Provide a checklist or quiz with 3–5 items. Use multiple choice or yes/no checks to help learners assess their own understanding.

        ---

        ## 🧠 Teaching Notes  
        This section is for instructors.

        - Point out common misconceptions
        - Suggest analogies or teaching strategies
        - Recommend optional follow-up topics
        - Do not repeat content or summarize here

        ---

        ### ❌ Do NOT include:
        - Motivational filler text like “Congratulations!”
        - External references like “see notebook.ipynb”
        - Generic sections like "Conclusion" or "Summary"
        - The word “Objective:” as a prefix to section titles

        ---

        🔚 When you're ready, generate the complete markdown-formatted lesson content using this structure, voice, and reference context only.
        """
        )


        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        try:
            # DEBUG: Print context length to prevent overflow
            print("🔍 Retrieved context length:", len(retrieved_context))

            # Optional: Trim context if it’s too long
            if len(retrieved_context) > 12000:
                retrieved_context = retrieved_context[:12000]
                print("✂️ Trimmed context to avoid token overflow.")

            response = (lesson_template | llm).invoke({
                "track": track_selected,
                "lesson": st.session_state["lesson_topic"],
                "retrieved_context": retrieved_context
            })

            content = response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            content = f"[ERROR generating content for {st.session_state['lesson_topic']}]\n\nDetails: {e}"
            print("❌ Generation Error:", e)


        profile["track_lessons"][track_selected][lesson_index] = content
        save_learner_profile(profile)
        lesson_blocks = profile["track_lessons"][track_selected]


if not topics or not lesson_blocks:
    st.warning("⚠️ No topics or lessons found for the selected track.")
    st.stop()

completed = get_completed_lessons()

# === Determine current topic ===
if "lesson_topic" not in st.session_state or not st.session_state["lesson_topic"]:
    fallback = profile.get("current_topic")
    st.session_state["lesson_topic"] = fallback if fallback in topics else topics[0]

current_topic = st.session_state["lesson_topic"]

=======
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
>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
if current_topic not in topics:
    st.warning("⚠️ Invalid topic loaded. Please return to the main app.")
    st.stop()

<<<<<<< HEAD
profile["current_topic"] = current_topic
save_learner_profile(profile)

# === Sidebar Progress ===
st.sidebar.title("📊 Your Progress")
st.sidebar.markdown(f"**👤 Name:** {profile.get('name', 'Anonymous')}")
st.sidebar.markdown(f"**Track:** {track_selected}")

# Reload lessons only for the current track
topics = profile["tracks"][track_selected]
lesson_blocks = profile["track_lessons"][track_selected]

completed = get_completed_lessons()
completed_in_track = [t for t in topics if t in completed]
upcoming_in_track = [t for t in topics if t not in completed and t != current_topic]

st.sidebar.markdown(f"**Completed:** {len(completed_in_track)} / {len(topics)}")

# === Sidebar Navigation ===
def show_topic_section(label, items, class_name):
    if items:
        st.sidebar.markdown(f'<div class="lesson-group"><strong>{label}</strong>', unsafe_allow_html=True)
        for t in items:
            try:
                idx = topics.index(t) + 1
            except ValueError:
                idx = "?"
            if st.sidebar.button(f"{idx}. {t}", key=f"{label}_{idx}"):
                st.session_state["lesson_topic"] = t
                st.session_state["track_selected"] = track_selected  # stay within the same track
                st.rerun()
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

show_topic_section("📍 Current Lesson", [current_topic], "current")
show_topic_section("⏭️ Upcoming Lessons", upcoming_in_track, "upcoming")
show_topic_section("✅ Completed Lessons", completed_in_track, "completed")



# === Load Lesson ===
lesson_index = topics.index(current_topic)
lesson_content = lesson_blocks[lesson_index] if lesson_index < len(lesson_blocks) else ""

if not lesson_content:
    st.error("⚠️ Could not load the selected lesson.")
    st.stop()

st.title("📘 Lesson In Progress")
st.subheader(f"🎯 Topic: {current_topic}")
st.markdown(lesson_content)

# === Code Submission ===
=======
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
>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
if "code_input" not in st.session_state or not st.session_state.get("lesson_generated", False):
    st.session_state["code_input"] = ""
    st.session_state["lesson_generated"] = True

st.markdown("## 🧑‍💻 Your Turn to Try")
<<<<<<< HEAD

# --- Dynamic Challenge Parsing ---
# We assume that the generated lesson_content includes an optional challenge section
# with markers like "MCQ:" and "CODE CHALLENGE:" to separate challenge types.
# For example, a lesson might include:
#    ... lesson content ...
#    --- Your Turn to Try ---
#    MCQ: What does DML stand for? Options: A) Data Manipulation Language, B) Data Mining Logic, C) Data Modeling Language
#    CODE CHALLENGE: Write an SQL query to retrieve all rows where "City" = 'New York'.
challenge_mcq = None
challenge_code = None

if "MCQ:" in lesson_content:
    # Split on the "MCQ:" marker and take the text after it.
    parts = lesson_content.split("MCQ:")
    # If there is also a CODE CHALLENGE marker in the same section, split it out.
    if "CODE CHALLENGE:" in parts[1]:
        mcq_text = parts[1].split("CODE CHALLENGE:")[0]
    else:
        mcq_text = parts[1]
    challenge_mcq = mcq_text.strip()

if "CODE CHALLENGE:" in lesson_content:
    parts = lesson_content.split("CODE CHALLENGE:")
    challenge_code = parts[1].strip()

# --- Display Challenge Inputs (if present) ---
if challenge_mcq:
    st.markdown("### Multiple-Choice / Short Answer Challenge")
    st.info(challenge_mcq)
    mcq_answer = st.text_input("Enter your answer for the above challenge:")

if challenge_code:
    st.markdown("### Code Challenge")
    st.info(challenge_code)
    code_answer = st.text_area("Enter your solution code below:", height=300)

# If neither marker exists, default to a generic text input challenge.
if not challenge_mcq and not challenge_code:
    st.markdown("### Challenge")
    generic_answer = st.text_area("Enter your solution or answer below:", height=300)

# --- Submission Handling ---
# We'll use one submission button that gathers the responses.
# You might structure the collected answer as a dictionary.
user_response = {}
if challenge_mcq:
    user_response["mcq"] = mcq_answer
if challenge_code:
    user_response["code"] = code_answer
if not challenge_mcq and not challenge_code:
    user_response["generic"] = generic_answer

# Disable the submit button if no response is provided.
response_provided = any([user_response.get("mcq", "").strip(), user_response.get("code", "").strip(), user_response.get("generic", "").strip()])

if st.button("📤 Submit Answer for Review", disabled=not response_provided):
    with st.spinner("🧠 Reviewing your submission..."):
        # For review, create a unified prompt that references both parts if applicable.
        review_prompt = """
You're a friendly and skilled coach. A learner just submitted an answer for the challenge.
If a code solution was provided, review the code. If a text answer (MCQ or short answer) was provided, review that.
Provide:
- What they did well.
- Any corrections or improvements.
- Pro tips to enhance their solution.

Include distinct sections if both types were provided.
"""
        # Use ChatOpenAI for the review, assuming it's imported and configured.
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        # Create a combined response string for review.
        combined_response = ""
        if "mcq" in user_response:
            combined_response += "MCQ Answer:\n" + user_response["mcq"] + "\n\n"
        if "code" in user_response:
            combined_response += "Code Answer:\n" + user_response["code"] + "\n\n"
        if "generic" in user_response:
            combined_response += "Answer:\n" + user_response["generic"] + "\n\n"
        
        # Generate feedback based on the combined response.
        feedback_prompt = PromptTemplate(
            input_variables=["topic", "submitted_response"],
            template="""
You're a friendly and skilled code coach. A learner just completed a challenge for: "{topic}"

Here is their submission:
{submitted_response}

Please review it with:
- What they did well.
- Any corrections or improvements.
- Pro tips to go further.
"""
        )
        review_chain = feedback_prompt | llm
        response = review_chain.invoke({
            "topic": current_topic,
            "submitted_response": combined_response
        })
        feedback = response.content if hasattr(response, "content") else str(response)


        save_memory(feedback, {"topic": current_topic, "type": "review"})
        st.success("✅ Submission reviewed! See feedback below:")
        st.markdown(feedback)

        # Mark lesson complete after review
=======
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

>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
        mark_lesson_complete(current_topic)
        completed = get_completed_lessons()

    st.divider()
    st.markdown("## ✅ Lesson Complete")
    st.success(f"You've completed: {current_topic}")

<<<<<<< HEAD

# === Progress Navigation ===
remaining = [t for t in topics if t not in completed and t != current_topic]
if remaining:
    next_lesson = remaining[0]
    st.info(f"➡️ Up Next: {next_lesson}")
=======
# === 3. Progress Navigation ===
remaining = [t for t in topics if t not in completed and t != current_topic]

if remaining:
    next_lesson = remaining[0]
    st.info(f"➡️ Up Next: {next_lesson}")

>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
    if st.button("🚀 Go to Next Lesson"):
        st.session_state.pop("code_input", None)
        st.session_state.pop("feedback", None)
        st.session_state["lesson_generated"] = False
        st.session_state["lesson_topic"] = next_lesson
        st.rerun()
else:
    st.balloons()
<<<<<<< HEAD
    st.success("🎉 You’ve completed all lessons in this track!")
=======
    st.success("🎉 You’ve completed all lessons in your curriculum!")
>>>>>>> 65ca58895611140109c4e872b15c5eca3f755117
