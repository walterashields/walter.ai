import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Simulated config from YAML
config = {
    'credentials': {
        'usernames': {
            'walter@example.com': {
                'name': 'Walter',
                'password': '$2b$12$8lcoByk/nz6cVm/FLLQrgeX92EwBQglBBwLGL6IecHieApfUjWxpe'  # "admin123"
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'walter_ai_signature',
        'name': 'walter_ai_cookie'
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login", "main")

st.write("🧪 DEBUG — Login result:")
st.write("auth_status:", authentication_status)
st.write("username:", username)
st.write("name:", name)

if authentication_status:
    st.success(f"Welcome {name}!")
elif authentication_status is False:
    st.error("Incorrect username or password")
elif authentication_status is None:
    st.info("Please enter your login credentials.")
