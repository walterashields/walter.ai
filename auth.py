# auth.py
import streamlit_authenticator as stauth

def load_authenticator(credentials):
    return stauth.Authenticate(
        credentials=credentials,
        cookie_name="walter_ai_cookie",   # Must match app.py and lesson_runner.py
        key="walter_ai_signature",
        cookie_expiry_days=30
    )
