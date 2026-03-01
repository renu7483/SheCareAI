import streamlit as st
import openai
import json

# Read OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="SheCare AI", layout="centered")
st.title("SheCare AI – PCOS & Period Health Assistant")
st.write("This AI assistant helps track periods, analyze PCOS risk, and give personalized advice.")

# --- Session state for login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Dummy users (can use data.json later) ---
users = {"test@hackathon.com": "1234"}

# --- Login / SignUp Page ---
if not st.session_state.logged_in:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email in users and users[email] == password:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid email or password.")
else:
    # --- Main Page ---
    st.subheader("Personalized PCOS Care")

    age = st.number_input("Enter your age", min_value=10, max_value=60, value=20)
    cycle_length = st.number_input("Average cycle length (days)", min_value=15, max_value=45, value=28)
    symptoms = st.text_area("Enter your symptoms (e.g., acne, hair loss, weight gain)")

    if st.button("Get Personalized Advice"):
        prompt = f"Patient age: {age}, cycle length: {cycle_length}, symptoms: {symptoms}. Give personalized PCOS health advice in short and simple language."
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=200
            )
            advice = response.choices[0].text.strip()
            st.write("### Personalized Advice:")
            st.write(advice)
        except Exception as e:
            st.error("Error fetching AI advice. Make sure your API key is correct.")

    st.info("You are logged in. Enter your details above and get personalized care.")
