import streamlit as st
import re

st.set_page_config(page_title="🔐 Sign In to WALTER.AI", layout="centered")

st.title("👋🏾 Welcome to WALTER.AI")
st.markdown("Let's get started. Please enter your name or email to access your personalized learning experience.")

# --- Begin login form ---
with st.form("login_form"):
    username = st.text_input("🔑 Enter your name or email:")
    submitted = st.form_submit_button("➡️ Continue")

# --- Validation logic ---
if submitted:
    if not username.strip():
        st.error("Please enter a valid name or email.")
    elif not re.match(r"^[a-zA-Z0-9._@+-]+$", username.strip()):
        st.error("Username may only contain letters, numbers, and . _ @ + -")
    else:
        st.session_state["username"] = username.strip().lower().replace(" ", "_")
        st.switch_page("app.py")  # ✅ Try this first
        # Or try: st.switch_page("📊 Learning Dashboard")
