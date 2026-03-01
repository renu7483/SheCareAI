import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import os

# Load API key from .env (for local) or use Streamlit Secrets (for cloud)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

# --- Connect to SQLite database ---
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create users table if not exists
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- App Title ---
st.set_page_config(page_title="SheCare AI", layout="centered")
st.title("🩸 SheCare AI – Period Tracker + ChatGPT AI")

# --- SignUp Page ---
def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Create Account"):
        if email and password:
            try:
                c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()
                st.success("Account created! Please log in.")
            except sqlite3.IntegrityError:
                st.error("Email already exists.")
        else:
            st.warning("Please enter email and password.")

# --- Login Page ---
def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if email and password:
            c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success(f"Logged in as {email}")
            else:
                st.error("Invalid email or password.")
        else:
            st.warning("Please enter email and password.")

# --- Main App Page ---
def main_page():
    st.subheader(f"Welcome, {st.session_state.email}!")

    # --- Period Tracker ---
    last_period = st.date_input("Last period date", datetime.today())
    cycle_length = st.number_input("Cycle length (days)", min_value=20, max_value=45, value=28)

    if st.button("Predict Next Period"):
        next_period = last_period + timedelta(days=cycle_length)
        st.write(f"📅 Your next period is predicted on: **{next_period.strftime('%A, %d %B %Y')}**")

    # --- ChatGPT AI ---
    st.subheader("ChatGPT AI for Menstrual Health")
    user_input = st.text_input("Ask a question")
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(f"User: {user_input}")
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"You are a helpful assistant for menstrual health. Answer concisely and politely.\n\nUser: {user_input}\nAI:",
                    max_tokens=150,
                    temperature=0.7
                )
                answer = response.choices[0].text.strip()
            except Exception as e:
                answer = "Error: Could not get response. Check your API key."
            st.session_state.chat_history.append(f"AI: {answer}")

    # Show chat history
    for chat in st.session_state.chat_history:
        st.write(chat)

# --- Page flow ---
if not st.session_state.logged_in:
    choice = st.radio("Select Action", ["Login", "Sign Up"])
    if choice == "Login":
        login()
    else:
        signup()
else:
    main_page()

    
