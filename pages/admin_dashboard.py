import streamlit as st
import os
from auth_utils import add_user, delete_user, update_password, hash_password, log_temp_password, update_approved_user_password
from utils import load_pending_requests, save_pending_requests, log_approved_user
from auth_utils import get_users

# Load user database
users = get_users()

# Sanitize username
raw_username = st.session_state.get("username")
def safe_username(raw_username):
    return raw_username.replace("@", "_at_").replace(".", "_dot_") if raw_username else None

username = safe_username(raw_username)
ADMIN_USERS = ["walter_at_example_dot_com"]

if not username or username not in ADMIN_USERS:
    st.error("⛔ You do not have access to this page.")
    st.stop()

st.set_page_config(page_title="Admin Tools", layout="wide")
st.title("🔐 Admin Dashboard")

# --- Add New User ---
st.markdown("### ➕ Add a New User")
with st.form("add_user_form"):
    new_email = st.text_input("Email")
    new_name = st.text_input("Name")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Add User")

    if submitted:
        if not new_email or not new_name or not new_password:
            st.error("All fields are required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                hashed = hash_password(new_password)
                add_user(new_email, new_name, hashed)
                log_approved_user(new_name, new_email, "Manually added", new_password)  # ✅ Added line
                st.success(f"✅ User {new_email} added successfully.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- Handle Pending Requests ---
st.markdown("---")
st.markdown("### 📨 Pending Access Requests")
pending_requests = load_pending_requests()
if pending_requests:
    for i, req in enumerate(pending_requests):
        with st.expander(f"{req['name']} — {req['email']}"):
            st.markdown(f"**Goals:** {req['goals']}")
            approve = st.button("✅ Grant Access", key=f"approve_{i}")
            if approve:
                grant_email = req["email"]
                grant_name = req["name"]
                grant_goals = req["goals"]
                generated_pw = os.urandom(4).hex()
                hashed_pw = hash_password(generated_pw)

                try:
                    add_user(grant_email, grant_name, hashed_pw)
                    pending_requests = [r for r in pending_requests if r["email"] != grant_email]
                    save_pending_requests(pending_requests)
                    log_approved_user(grant_name, grant_email, grant_goals, generated_pw)
                    st.success(f"✅ {grant_email} added. Temp password saved to logs.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
else:
    st.info("No pending requests.")

# --- Delete User ---
st.markdown("---")
st.markdown("### 🗑️ Delete User")
all_emails = list(users.keys())
selected_email = st.selectbox("Select user to delete", all_emails)
if st.button("Delete User"):
    if selected_email in ADMIN_USERS:
        st.warning("You cannot delete an admin user.")
    else:
        delete_user(selected_email)
        st.success(f"✅ User {selected_email} deleted.")
        st.rerun()

# --- Reset Password ---
st.markdown("---")
st.markdown("### 🔁 Reset User Password")
reset_email = st.selectbox("Select user", list(users.keys()), key="reset_user_select")
with st.form("reset_password_form"):
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Reset Password")
    if submitted:
        if not new_pw or not confirm_pw:
            st.error("Both fields required.")
        elif new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            hashed = hash_password(new_pw)
            update_password(reset_email, hashed)
            log_temp_password(reset_email, new_pw)
            update_approved_user_password(reset_email, new_pw)
            st.success(f"✅ Password for {reset_email} updated.")

# --- Approved Users Log ---
st.markdown("---")
st.markdown("### 📋 Approved Users Log")

# ✅ This displays the contents of access_logs/approved_users.csv
# which logs: name, email, goals, generated password, and approval timestamp
log_file = "access_logs/approved_users.csv"
if os.path.exists(log_file):
    with open(log_file) as f:
        lines = f.readlines()

    if lines:
        # Begin styled table
        st.markdown("<table><tr><th>Name</th><th>Email</th><th>Goals</th><th>Password</th><th>Approved</th></tr>", unsafe_allow_html=True)

        for line in lines:
            try:
                name, email, goals, password, timestamp = line.strip().split(",", 4)
                st.markdown(
                    f"<tr><td>{name}</td><td>{email}</td><td>{goals}</td><td><code>{password}</code></td><td>{timestamp}</td></tr>",
                    unsafe_allow_html=True
                )
            except ValueError:
                continue  # Skip malformed lines gracefully

        st.markdown("</table>", unsafe_allow_html=True)
    else:
        st.info("✅ No approved users yet.")
else:
    st.info("🗂️ Approved users log not found.")


