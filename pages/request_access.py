import streamlit as st
import os
import csv
from datetime import datetime

# ✅ Setup paths
requests_file = "access_requests.csv"
os.makedirs("access_logs", exist_ok=True)
full_path = os.path.join("access_logs", requests_file)

st.set_page_config(page_title="Request Access", page_icon="📩")

st.title("📩 Request Access to Walter.AI")

st.write("Please fill out the form below to request access. Our team will review your request and contact you.")

with st.form("request_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    goals = st.text_area("Briefly describe your goals or interest in joining")
    submitted = st.form_submit_button("Submit Request")

    if submitted:
        if not name or not email or not goals:
            st.error("All fields are required.")
        else:
            timestamp = datetime.now().isoformat()
            # Save to CSV file
            new_entry = [timestamp, name, email, goals]
            file_exists = os.path.exists(full_path)

            with open(full_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "name", "email", "goals"])
                writer.writerow(new_entry)

            st.success("✅ Request submitted! We'll be in touch soon.")
            st.info("You can now close this tab or return to the login screen.")
