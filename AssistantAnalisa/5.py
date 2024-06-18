import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import hashlib
from pathlib import Path
from datetime import datetime


# Load environment variables
load_dotenv()

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
def save_chat_history_to_csv(chat_history, username, file_path="chat_history.csv"):
    df = pd.DataFrame(chat_history)
    df['username'] = username
    df['date'] = datetime.now().strftime("%Y-%m-%d")
    if Path(file_path).exists():
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

# Load chat history from CSV
def load_chat_history_from_csv(file_path="chat_history.csv"):
    if Path(file_path).exists():
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["user_input", "response", "username", "date"])

# Main application
def main_app():
    st.set_page_config(page_title="Assistant Data FDS", page_icon=":robot:")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar configuration
    st.sidebar.title("Chat History")

    # Date filter
    date_filter = st.sidebar.date_input("Filter by date")
    date_filter = date_filter.strftime("%Y-%m-%d")

    chat_history_df = load_chat_history_from_csv()

    # Debugging statements
    # st.sidebar.write(f"Loaded chat history dataframe:\n{chat_history_df}")

    # Check if the necessary columns exist
    if 'username' in chat_history_df.columns and 'date' in chat_history_df.columns:
        user_chat_history_df = chat_history_df[(chat_history_df["username"] == st.session_state.username) & (chat_history_df["date"] == date_filter)]
        st.sidebar.write(f"Filtered chat history dataframe:\n{user_chat_history_df}")

        if not user_chat_history_df.empty:
            # Display only the 'user_input' column
            st.sidebar.table(user_chat_history_df[["user_input"]])
        else:
            st.sidebar.warning("No chat history available for the selected date.")
    else:
        st.sidebar.warning("No chat history available.")

    if st.sidebar.button("New Chat"):
        st.session_state.chat_history = []
        st.sidebar.success("Started a new chat session.")

    if st.sidebar.button("Logout"):
        logout()

    # Konten HTML untuk judul
    st.markdown("""
        <div style="text-align: center;">
            <h1>Assistant Data FDS Generator</h1>
        </div>
    """, unsafe_allow_html=True)

    # Input teks dari pengguna
    # text_input = st.text_area("Enter Your Request:")
    # if prompt := st.chat_input("What is up?"):
    # text_input = st.chat_input("Enter Your Request")   

    # Input struktur kolom CSV
    # str_template = load_template('template/template_str.txt')
    # path_csv = "data/"
    str_template_ml = load_template('template/template_ml.txt')
    # submit = st.button("Generate Code")
    str_template = load_template('template/template_str.txt')
    path_csv = "data/tx_training.csv"
    if text_input := st.chat_input("What is up?"):
        with st.chat_message("user"):
             st.markdown(text_input)
        with st.spinner('Generating data...'):
            # Memuat template dari file
            # pandas_template = load_template('template/template_duckdb.txt')
            # formatted_template = pandas_template.format(text_input=text_input, csv_structure=str_template, path_csv=path_csv,str_template_ml = str_template_ml )
            pandas_template = load_template('template/template_duckdb.txt')
            formatted_template = pandas_template.format(text_input=text_input, csv_structure=str_template,path_csv = path_csv)

            try:
                
                generation_config = {
                "temperature": 2,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                }

                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config=generation_config,)

                # genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                # model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(formatted_template)
                execpythoncode = response.text.strip()
                execpythoncode = execpythoncode.replace("```python",'').replace("'''",'').replace("```",'')
                # print(execpythoncode)
                assistant_response = ""
                try:
                    exec(execpythoncode, globals())
                    if 'df' in globals():
                        assistant_response = "Code executed successfully. DataFrame is available."
                    else:
                        assistant_response = "Code executed, but no DataFrame was created."
                except Exception as err:
                    assistant_response = f"Error: {err}"

                # st.session_state.chat_history.append({"user_input": text_input, "response": assistant_response})
                # save_chat_history_to_csv(st.session_state.chat_history, st.session_state.username)

                # st.write("Generated Python Code:")
                # st.code(execpythoncode, language='python')
                # st.write(assistant_response)

                # if 'df' in globals():
                #     st.write("Resulting DataFrame:")
                #     st.dataframe(df)

                #     st.write("Graph:")
                #     fig, ax = plt.subplots()
                #     df.plot(ax=ax)
                #     st.pyplot(fig)
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
