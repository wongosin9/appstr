import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import hashlib
from pathlib import Path



# Load environment variables
load_dotenv()

# GOOGLE_API_KEY='AIzaSyB7SPxVu7N1rteqZCDnu1nY1DqSDWR6pa0'

load_dotenv()

genai.configure(api_key=os.getenv("AIzaSyB7SPxVu7N1rteqZCDnu1nY1DqSDWR6pa0"))

model = genai.GenerativeModel('gemini-pro')

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load users
def load_users(file_path="users.csv"):
    if Path(file_path).exists():
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["username", "password"])

# Function to save users
def save_users(users, file_path="users.csv"):
    users.to_csv(file_path, index=False)

# Function to check if user exists
def user_exists(username, users):
    return username in users["username"].values

# Function to add a new user
def add_user(username, password, users):
    new_user = pd.DataFrame({"username": [username], "password": [hash_password(password)]})
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return users

# Function to validate user credentials
def validate_user(username, password, users):
    hashed_password = hash_password(password)
    user = users[users["username"] == username]
    if not user.empty and user.iloc[0]["password"] == hashed_password:
        return True
    return False

# Signup page
def signup_page():
    st.title("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    password_confirm = st.text_input("Confirm Password", type="password")
    users = load_users()

    if st.button("Signup"):
        if user_exists(username, users):
            st.error("Username already exists. Please choose a different username.")
        elif password != password_confirm:
            st.error("Passwords do not match.")
        else:
            users = add_user(username, password, users)
            st.success("Signup successful. You can now log in.")

# Login page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()

    if st.button("Login"):
        if validate_user(username, password, users):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful.")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# Logout
def logout():
    st.session_state.logged_in = False
    st.experimental_rerun()

# Function to load template
def load_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to save chat history to CSV
def save_chat_history_to_csv(chat_history, file_path="chat_history.csv"):
    df = pd.DataFrame(chat_history)
    df.to_csv(file_path, index=False)

# Main application
def main_app():
    st.set_page_config(page_title="Assistant Analisa", page_icon=":robot:")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar configuration
    st.sidebar.title("Chat History")
    for chat in st.session_state.chat_history:
        st.sidebar.markdown(f"**You:** {chat['user_input']}")
        st.sidebar.markdown(f"**Assistant:** {chat['response']}")

    if st.sidebar.button("New Chat"):
        st.session_state.chat_history = []
        st.sidebar.success("Started a new chat session.")

    st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        logout()

    # Konten HTML untuk judul
    st.markdown("""
        <div style="text-align: center;">
            <h1>Assistant Analisa Generator</h1>
        </div>
    """, unsafe_allow_html=True)

    # Input teks dari pengguna
    text_input = st.text_area("Enter Your Request:")

    # Input struktur kolom CSV
    str_template = load_template('template/template_str.txt')
    path_csv = "data/tx_training.csv"

    submit = st.button("Generate Code")

    if submit:
        with st.spinner('Generating data...'):
            # Memuat template dari file
            pandas_template = load_template('template/template_code.txt')
            formatted_template = pandas_template.format(text_input=text_input, csv_structure=str_template, path_csv=path_csv)

            try:
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(formatted_template)
                pandas_code = response.text.strip()
                execpythoncode = pandas_code.replace("```python",'').replace("'''",'').replace("```",'')

                assistant_response = ""
                try:
                    exec(execpythoncode, globals())
                    if 'df' in globals():
                        assistant_response = "Code executed successfully. DataFrame is available."
                    else:
                        assistant_response = "Code executed, but no DataFrame was created."
                except Exception as err:
                    assistant_response = f"Error: {err}"

                st.session_state.chat_history.append({"user_input": text_input, "response": assistant_response})
                save_chat_history_to_csv(st.session_state.chat_history)

                st.write("Generated Python Code:")
                st.code(execpythoncode, language='python')
                st.write(assistant_response)

                if 'df' in globals():
                    st.write("Resulting DataFrame:")
                    st.dataframe(df)

                    st.write("Graph:")
                    fig, ax = plt.subplots()
                    df.plot(ax=ax)
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generating content: {e}")

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        st.sidebar.title("User Authentication")
        auth_option = st.sidebar.radio("Choose an option", ["Login", "Signup"])
        if auth_option == "Login":
            login_page()
        else:
            signup_page()

if __name__ == "__main__":
    main()
