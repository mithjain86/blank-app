import streamlit as st
import requests
import pandas as pd

API_BASE = "https://tracker.myuta.xyz/api"

st.set_page_config(page_title="AI Lead Dashboard", layout="wide")

# Session state setup
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- LOGIN FORM ---
def login_form():
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # Do login logic here
            if email == "admin@example.com" and password == "secret":
                st.session_state["is_logged_in"] = True
                st.experimental_rerun()  # ✅ Valid here
            else:
                st.error("Invalid login")

# --- FETCH LEADS ---
def fetch_leads(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_BASE}/leads", headers=headers)
    return res.json() if res.status_code == 200 else []

# --- FETCH JOURNEY ---
def fetch_journey(session_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_BASE}/journey/{session_id}", headers=headers)
    return res.json() if res.status_code == 200 else {}

# --- DASHBOARD UI ---
def show_dashboard():
    st.title("📊 AI Lead Tracking Dashboard")

    # Fetch leads
    leads = fetch_leads(st.session_state.auth_token)

    if not leads:
        st.warning("No leads data available.")
        return

    df = pd.DataFrame(leads)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["form_data"] = df["form_data"].apply(lambda x: str(x) if x else "")
    df["chat_summary"] = df["chat_summary"].apply(lambda x: str(x) if x else "")
    df["pages_visited"] = df["pages_visited"].apply(lambda x: ", ".join(x) if x else "")

    st.dataframe(df[[
        "session_id", "created_at", "ip", "device", "utm_source",
        "utm_medium", "utm_campaign", "referrer", "pages_visited",
        "form_data", "chat_summary"
    ]], use_container_width=True)

    session_id = st.selectbox("Select Session for Detailed Journey", df["session_id"].tolist())

    if session_id:
        journey = fetch_journey(session_id, st.session_state.auth_token)
        st.subheader("👣 Lead Journey")
        st.json(journey)

    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.auth_token = None
        st.experimental_rerun()

# === MAIN LOGIC ===
if st.session_state.auth_token:
    show_dashboard()
else:
    login_form()
