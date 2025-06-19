import streamlit as st
# === Set page config early ===
st.set_page_config(page_title="📘 Lesson Viewer", layout="wide")

import os, json, re
from PIL import Image
from auth import load_authenticator
from auth_utils import get_users

# Load user credentials (same as app.py)
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

# Load authenticator with shared credentials
authenticator = load_authenticator(credentials)

# === Check login status and session keys
required_keys = ["authentication_status", "username", "track_selected", "lesson_topic"]

if not all(k in st.session_state for k in required_keys):
    st.error("🚫 Session is incomplete. Please go back to the dashboard and relaunch the lesson.")
    st.stop()

# === Pull key user info
username = st.session_state["username"]
track_selected = st.session_state["track_selected"]
lesson_topic = st.session_state["lesson_topic"]
name = st.session_state.get("name", username)

# === Header with logo
logo = Image.open("static/wsda-logo.png")
col1, col2 = st.columns([1, 10])
with col1:
    st.image(logo, width=40)
with col2:
    st.markdown("<div style='padding-top: 12px; font-weight: bold;'>Walter Shields Data Academy</div>", unsafe_allow_html=True)


####################AUTHENTICATION ABOVE THIS LINE#######################
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from memory import (
    load_learner_profile,
    save_learner_profile,
    save_memory,
    mark_lesson_complete,
    get_completed_lessons
)

# Check if profile loaded
# === User Login Guard ===
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("⚠️ Please sign in first.")
    st.stop()

# === Sanitize username and define paths ===
def safe_username(raw_username):
    return raw_username.replace("@", "_at_").replace(".", "_dot_")

raw_username = st.session_state["username"]
username = safe_username(raw_username)
memory_folder = f"walter_memory/{username}"
profile_path = f"{memory_folder}/{username}_profile.json"

os.makedirs(memory_folder, exist_ok=True)


# === Setup learner profile and memory path
def safe_username(raw_username):
    return raw_username.replace("@", "_at_").replace(".", "_dot_")

raw_username = st.session_state.get("username")
username = safe_username(raw_username)
memory_folder = f"walter_memory/{username}"
profile_path = f"{memory_folder}/{username}_profile.json"
os.makedirs(memory_folder, exist_ok=True)

profile = load_learner_profile(profile_path)
if not profile:
    st.error("⚠️ No learner profile found. Please return to the main app and complete onboarding.")
    st.stop()

# === Sanitize username for filesystem usage ===
def safe_username(raw_username):
    return raw_username.replace("@", "_at_").replace(".", "_dot_")

# === Set up user memory path and profile ===
raw_username = st.session_state["username"]
username = safe_username(raw_username)
memory_folder = f"walter_memory/{username}"
profile_path = f"{memory_folder}/{username}_profile.json"

os.makedirs(memory_folder, exist_ok=True)



# 🛠 Fallback fix for empty lesson list
if "track_lessons" in profile and st.session_state["track_selected"] in profile["track_lessons"]:

    track_selected = st.session_state.get("track_selected")

    if track_selected not in profile.get("tracks", {}):
        st.error(f"⚠️ The track '{track_selected}' was not found in your profile. Please restart from the dashboard.")
        st.stop()

    lessons = profile["tracks"][track_selected]
    
    if not profile["track_lessons"][st.session_state["track_selected"]]:
        profile["track_lessons"][st.session_state["track_selected"]] = [None] * len(lessons)
        save_learner_profile(profile, profile_path)


# === Ensure track_selected and lesson_topic are present in session ===
if "track_selected" not in st.session_state or not st.session_state["track_selected"]:
    first_track = next(iter(profile.get("tracks", {})), None)
    if first_track:
        st.session_state["track_selected"] = first_track

if "lesson_topic" not in st.session_state or not st.session_state["lesson_topic"]:
    current_track = st.session_state.get("track_selected")
    lessons = profile.get("tracks", {}).get(current_track, [])
    if lessons:
        st.session_state["lesson_topic"] = lessons[0]


# ✅ Ensure track_lessons structure is valid and initialized
track_selected = st.session_state.get("track_selected")

if "track_lessons" not in profile:
    profile["track_lessons"] = {}

if track_selected not in profile["track_lessons"]:
    num_lessons = len(profile.get("tracks", {}).get(track_selected, []))
    profile["track_lessons"][track_selected] = [None] * num_lessons
    save_learner_profile(profile, profile_path)
    st.info(f"🛠 Initialized lesson slots for track: '{track_selected}'")

# ✅ Auto-recover track_selected if it's missing but lesson_topic exists
if not st.session_state.get("track_selected") and st.session_state.get("lesson_topic") and profile:
    lesson = st.session_state["lesson_topic"]
    for track_name, lessons in profile.get("tracks", {}).items():
        if lesson in lessons:
            st.session_state["track_selected"] = track_name
            break

track_selected = st.session_state.get("track_selected")

if not profile:
    st.error("⚠️ Could not load learner profile. Please return to the main app and start your learning path again.")
    st.stop()

# === Recover missing track from topic ===
if "track_selected" not in st.session_state or not st.session_state["track_selected"]:
    topic = st.session_state.get("lesson_topic")
    if profile and topic and "tracks" in profile:
        for tname, lessons in profile["tracks"].items():
            if topic in lessons:
                st.session_state["track_selected"] = tname
                break

# === Final variable assignments ===
track_selected = st.session_state.get("track_selected")
topic = st.session_state.get("lesson_topic")

# === Validate track presence in profile ===
if not track_selected or track_selected not in profile.get("tracks", {}):
    st.warning("⚠️ No track selected. Please return to the main app and launch a track.")
    st.stop()

# === UI Setup ===


# 🔙 Back to Dashboard button (only on lesson page)
if st.sidebar.button("🔙 Back to Dashboard"):
    st.switch_page("app.py")


# === Sidebar: Full Track & Lesson Navigation ===
st.sidebar.title("📚 Your Lessons")

completed = get_completed_lessons(memory_folder)
current_lesson = st.session_state.get("lesson_topic")

def lesson_status_icon(lesson):
    if lesson == current_lesson:
        return "📍"
    elif lesson in completed:
        return "✅"
    else:
        return "⏳"

# Render all tracks and their lessons
for track_title, lessons in profile["tracks"].items():
    st.sidebar.markdown(f'<div class="lesson-group"><strong>{track_title}</strong>', unsafe_allow_html=True)
    for idx, lesson in enumerate(lessons):
        label = f"{lesson_status_icon(lesson)} Lesson {idx + 1}: {lesson}"
        if st.sidebar.button(label, key=f"{track_title}_{lesson}_sidebar"):
            # Reset input-related session keys when navigating via sidebar
            for key in ["code_input", "feedback", "mcq_answer", "generic_challenge_input", "code_answer"]:
                st.session_state.pop(key, None)

            st.session_state["lesson_generated"] = False
            st.session_state["lesson_topic"] = lesson
            st.session_state["track_selected"] = track_title
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


st.markdown("""
<style>
section.main > div { padding-top: 1rem !important; }
.block-container { padding-top: 1rem !important; }
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

# === Shared Lesson Launch Function ===
def launch_lesson(lesson_title, track_title):
    st.session_state["lesson_topic"] = lesson_title
    st.session_state["track_selected"] = track_title
    st.switch_page("pages/_lesson_runner.py")

# ✅ Reset session if previous track_selected no longer exists
if "track_selected" in st.session_state:
    if st.session_state["track_selected"] not in profile["tracks"]:
        st.session_state["track_selected"] = list(profile["tracks"].keys())[0]

# ✅ Same for lesson_topic
if "lesson_topic" in st.session_state:
    all_lessons = [lesson for lessons in profile["tracks"].values() for lesson in lessons]
    if st.session_state["lesson_topic"] not in all_lessons:
        st.session_state["lesson_topic"] = all_lessons[0]

if not profile or "tracks" not in profile or "track_lessons" not in profile:
    st.warning("⚠️ Incomplete profile. Please regenerate your curriculum from the main app.")
    st.stop()

# === Extract Topics and Lessons for Current Track ===
topics = profile["tracks"].get(track_selected, [])
lesson_blocks = profile.get("track_lessons", {}).get(track_selected, [])

if not lesson_blocks or not isinstance(lesson_blocks, list):
    st.error("⚠️ This track has no lessons yet. Please return to the main app and regenerate the curriculum.")
    st.stop()

try:
    lesson_index = topics.index(st.session_state["lesson_topic"])
except ValueError:
    st.error("⚠️ Current lesson not found in track. Please return to the dashboard.")
    st.stop()

# === Generate the lesson only if missing or empty string
lesson_raw = lesson_blocks[lesson_index] if lesson_index < len(lesson_blocks) else None

if lesson_raw is None or lesson_raw.strip() == "":

    with st.spinner(f"🛠 Generating content for lesson: '{st.session_state['lesson_topic']}'"):

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

        from langchain.chat_models import ChatOpenAI
        from langchain.prompts import PromptTemplate


        # import os

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
            input_variables=[
                "track", "lesson", "lesson_index", "total_lessons",
                "previous_lesson", "next_lesson", "retrieved_context"
            ],
            template="""
        You are a senior curriculum developer writing a world-class technical lesson in markdown format. 
        This is **Lesson {lesson_index} of {total_lessons}** in the **{track}** learning track. The topic is: **{lesson}**.

        The previous lesson was: "{previous_lesson}"  
        The next lesson will be: "{next_lesson}"

        📘 Use only the following trusted reference materials:
        {retrieved_context}

        ---

        🛠️ FORMAT AND INSTRUCTIONS:

        Your output must follow the format **exactly as shown below**, using only markdown (no HTML).

        ✅ Writing Guidelines (Must Follow):
        - Each concept explanation must be 2–4 paragraphs written in beginner friendly full sentences (avoid bullet lists).
        - Align each sub-concept to at least one learning objective from above.
        - After any SQL or code example, include a properly formatted markdown **output table** showing example results.
        - Follow the output with a clear, full-sentence explanation of what each line of code does. Highlight important terms using **bold**.
        
        Match the tone, structure, and clarity of the Microsoft "Data Science for Beginners" GitHub curriculum:  
        https://github.com/microsoft/Data-Science-For-Beginners

        ---

        # 📖 **{lesson}**
        
        ---

        ## 🌟 Learning Objectives  
        List 3–4 measurable outcomes using Bloom’s action verbs like: define, apply, analyze, compare, create, specifically relevent to the lesson topic {lesson}. Use bullet points.  
        ⚠️ Make sure that each Learning Objective is explicitly addressed within the lesson content.

        ---

        ## 💡 Introduction  
        Explain why this topic matters. Use a real-world analogy or relatable beginner-friendly scenario.  
        Keep this section to 2–3 short paragraphs in a clear, accessible tone.

        ---

        ## 📊 Core Concepts  

        Break this section into the same number and topic subsections as there are Leaning Objectives listed above. They should progress sequentially in a smooth logical order. Each one should include:

        ### 📚 Sub-Concept Title  
        - 3–5 clear paragraphs that sufficiently explain the concept in plain, student-friendly language  
        - A multi-line code block (e.g., ```sql or ```python) using proper formatting and indentation  
        - A markdown output table (if applicable) shown below the code  
        - A **clear explanation written in 3-4 full sentences** (not bullet points). Emphasize important keywords in bold or italics.  
        - A 💡 **Pro Tip** section for common beginner mistakes or misunderstandings — also written in full sentences

        💻 Example:
        ```sql
        SELECT 
            Product_Name, 
            SUM(Amount) AS Total_Sales
        FROM 
            Movies_Transactions
        GROUP BY 
            Product_Name;
        ```
        -A supporting table that illustrates the output of code example
        📊 Sample Output:
        Product_Name	Total_Sales
        Monty Python	$45.00
        Gone With the Wind	$30.00

        🧠 Explanation:
        This SQL query retrieves each product name from the database and calculates the total sales amount using the SUM() function.
        The results are grouped by product name, so each row shows the total for one movie title.

        💡 Pro Tip:
        Always use GROUP BY when applying aggregate functions like SUM() or AVG() to prevent unexpected results.

        🔍 Scenario or Walkthrough
        Show a realistic scenario where the learner applies 2–3 concepts from above. Walk through a mini real-world problem with input and output.

        Multi-line code block

        Output table (if applicable)

        Clear explanation in sentence form

        ✅ Self-Check Quiz
        Write 3–5 short questions to help the learner reflect. Use a mix of multiple choice and true/false.
        ⚠️ Do not include the answers.

        
        ## 🧑‍💼 Your Turn to Try
        Your Turn to Try
        Give one challenge that is a slight variation of something shown earlier in the lesson. Keep it simple and beginner-appropriate.

        💻 Example: Modify the previous query to calculate the average sales amount per product.
        
        🚫 DO NOT INCLUDE:

        HTML tags like <dl>, <dt>, <dd>

        Any “Teaching Notes” section

        Generic checklists like “✅ Did I use correct syntax?”

        Repeated “Challenge” or “Enter your solution” labels

        Motivational filler like “Nice job!”

        External references like “See notebook.ipynb”

        Now generate the full markdown lesson using only the context and structure above. """ )



        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        try:

            # Optional: Trim context if it’s too long
            if len(retrieved_context) > 12000:
                retrieved_context = retrieved_context[:12000]
                print("✂️ Trimmed context to avoid token overflow.")

            response = (lesson_template | llm).invoke({
                "track": track_selected,
                "lesson": st.session_state["lesson_topic"],
                "lesson_index": lesson_index,
                "total_lessons": len(topics),
                "previous_lesson": topics[lesson_index - 1] if lesson_index > 0 else "",
                "next_lesson": topics[lesson_index + 1] if lesson_index < len(topics) - 1 else "",
                "retrieved_context": retrieved_context
            })

            content = response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            content = f"[ERROR generating content for {st.session_state['lesson_topic']}]\n\nDetails: {e}"
            print("❌ Generation Error:", e)


        profile["track_lessons"][track_selected][lesson_index] = content
        save_learner_profile(profile, profile_path)
        lesson_blocks = profile["track_lessons"][track_selected]


        if not topics or not lesson_blocks:
            st.warning("⚠️ No topics or lessons found for the selected track.")
            st.stop()

        completed = get_completed_lessons(memory_folder)

        # === Determine current topic ===
        if "lesson_topic" not in st.session_state or not st.session_state["lesson_topic"]:
            fallback = profile.get("current_topic")
            st.session_state["lesson_topic"] = fallback if fallback in topics else topics[0]

        current_topic = st.session_state["lesson_topic"]

        if current_topic not in topics:
            st.warning("⚠️ Invalid topic loaded. Please return to the main app.")
            st.stop()

        profile["current_topic"] = current_topic
        save_learner_profile(profile, profile_path)

        if st.sidebar.button("🏠 Back to Dashboard"):
            st.switch_page("app.py")

        # === Sidebar Progress ===
        st.sidebar.title("📊 Your Progress")
        # === Log Out Button ===
        if st.sidebar.button("🚪 Log Out"):
            st.session_state.pop("username", None)
            st.session_state.clear()
            st.rerun()


        st.sidebar.markdown(f"**👤 Name:** {profile.get('name', 'Anonymous')}")
        st.sidebar.markdown(f"**Track:** {track_selected}")

        # Reload lessons only for the current track
        topics = profile["tracks"][track_selected]
        lesson_blocks = profile["track_lessons"][track_selected]

        completed = get_completed_lessons(memory_folder)
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



        # === Detect lesson change and force rerun
        if "last_loaded_topic" in st.session_state:
            if st.session_state["lesson_topic"] != st.session_state["last_loaded_topic"]:
                st.session_state["lesson_generated"] = False
                st.session_state["code_input"] = ""
                st.session_state["feedback"] = ""
                st.session_state["mcq_answer"] = ""
                st.session_state["generic_challenge_input"] = ""
                st.session_state["code_answer"] = ""
                st.rerun()


        # 🧠 Track current topic
        st.session_state["last_loaded_topic"] = st.session_state["lesson_topic"]




        # === Load Lesson ===
        lesson_index = topics.index(current_topic)

        # 🔄 Reload lesson content for selected topic
        lesson_blocks = profile["track_lessons"].get(track_selected, [])
        lesson_content = lesson_blocks[lesson_index] if lesson_index < len(lesson_blocks) else ""





        if not lesson_content:
            st.error("⚠️ Could not load the selected lesson.")
            st.stop()


        # === Final Lesson Display Block (Always Render) ===
        lesson_index = topics.index(current_topic)
        lesson_blocks = profile.get("track_lessons", {}).get(track_selected, [])
        lesson_content = lesson_blocks[lesson_index] if lesson_index < len(lesson_blocks) else ""


# === FINAL Lesson Content Display Block (Always Render on Rerun) ===
current_topic = st.session_state.get("lesson_topic")
lesson_index = topics.index(current_topic)
lesson_blocks = profile.get("track_lessons", {}).get(track_selected, [])
lesson_content = lesson_blocks[lesson_index] if lesson_index < len(lesson_blocks) else ""


if isinstance(lesson_content, str) and len(lesson_content.strip()) > 0:
    st.markdown(lesson_content, unsafe_allow_html=True)
    st.markdown("""
        <script>
            setTimeout(function() {
                window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
            }, 100);
        </script>
    """, unsafe_allow_html=True)

        # === Code Submission ===
    if "code_input" not in st.session_state or not st.session_state.get("lesson_generated", False):
        st.session_state["code_input"] = ""
        st.session_state["lesson_generated"] = True

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
    st.text_input("Enter your answer for the above challenge:", key="mcq_answer")
    mcq_answer = st.session_state.get("mcq_answer", "")


if challenge_code:
    st.markdown("### Code Challenge")
    st.info(challenge_code)
    st.text_area("Enter your solution code below:", height=300, key="code_answer")
    code_answer = st.session_state.get("code_answer", "")


# If neither marker exists, use fallback challenge block
if not challenge_mcq and not challenge_code:
    default_prompt = (
        "Take your best shot—there’s no such thing as a wrong answer here. "
        "Submit at least once to mark this lesson complete!"
    )
    st.text_area(default_prompt, key="generic_challenge_input", height=250)
    generic_answer = st.session_state.get("generic_challenge_input", "")



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


response_provided = any([
    user_response.get("mcq", None),
    user_response.get("code", None),
    user_response.get("generic", None)
]) and any([
    bool(user_response.get("mcq", "").strip()),
    bool(user_response.get("code", "").strip()),
    bool(user_response.get("generic", "").strip())
])

submit_clicked = st.button("📤 Submit Answer for Review")

if submit_clicked:
    if not response_provided:
        st.error("⚠️ You must attempt the challenge to receive a code review and mark the lesson as complete.")
        st.stop()
    else:
        with st.spinner("🧠 Reviewing your submission..."):
            llm = ChatOpenAI(model="gpt-4", temperature=0.3)

            # Identify which challenge type was submitted
            if challenge_code:
                submitted_type = "Code"
                learner_response = user_response["code"]
                challenge_text = challenge_code
            elif challenge_mcq:
                submitted_type = "MCQ"
                learner_response = user_response["mcq"]
                challenge_text = challenge_mcq
            else:
                submitted_type = "Reflection"
                learner_response = user_response["generic"]
                challenge_text = "Open-ended reflection challenge from the lesson."

            feedback_prompt = PromptTemplate(
                input_variables=["topic", "submitted_type", "challenge_text", "learner_response"],
                template="""
You are a helpful, beginner-friendly coach reviewing a learner's submission in a data training lesson.

🎯 Topic: {topic}  
📌 Challenge Type: {submitted_type}  
🧠 Challenge Instructions:  
{challenge_text}

📩 Learner's Submission:  
{learner_response}

Please provide constructive, supportive feedback tailored to this exact challenge. Your feedback must:
- Focus ONLY on the actual challenge (don’t reference other formats like JOINs if they weren’t part of it)
- Mention what they did well
- Suggest improvements
- Share 1–2 beginner-friendly pro tips

Be clear and concise. Encourage continued learning.
"""
            )

            review_chain = feedback_prompt | llm
            response = review_chain.invoke({
                "topic": current_topic,
                "submitted_type": submitted_type,
                "challenge_text": challenge_text,
                "learner_response": learner_response
            })

            feedback = response.content if hasattr(response, "content") else str(response)
            if not feedback:
                feedback = "⚠️ No feedback could be generated. Please try again or check your input."

            save_memory(feedback, {"topic": current_topic, "type": "review"}, memory_folder)
            st.success("✅ Submission reviewed! See feedback below:")
            st.markdown(feedback)

            # ✅ Mark lesson complete
            mark_lesson_complete(current_topic, memory_folder)
            completed = get_completed_lessons(memory_folder)

        st.divider()
        st.markdown("## ✅ Lesson Complete")
        st.success(f"You've completed: {current_topic}")
        completed = get_completed_lessons(memory_folder)


# === Progress Navigation ===
remaining = [t for t in topics if t not in completed and t != current_topic]
if remaining:
    next_lesson = remaining[0]
    st.info(f"➡️ Up Next: {next_lesson}")
    if st.button("🚀 Go to Next Lesson"):
        # 🔄 Reset all challenge-related session keys
        for key in ["code_input", "feedback", "mcq_answer", "generic_challenge_input", "code_answer"]:
            st.session_state.pop(key, None)

        st.session_state["lesson_generated"] = False
        st.session_state["lesson_topic"] = next_lesson
        st.rerun()
else:
    st.balloons()
    st.success("🎉 You’ve completed all lessons in this track!")
