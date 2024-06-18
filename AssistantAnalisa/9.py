import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import csv
from datetime import datetime

xstatus = 0
# Load environment variables
load_dotenv()

# Configure the Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the generation configuration
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Initialize the Generative Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to load template files
def load_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to log history to a CSV file
def log_history(input_text, generated_code):
    history_file = 'history.csv'
    file_exists = os.path.isfile(history_file)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(history_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'User Input', 'Generated Code'])
        writer.writerow([current_time, input_text, generated_code])

# Function to read history from the CSV file
def read_history():
    history_file = 'history.csv'
    if os.path.isfile(history_file):
        history_df = pd.read_csv(history_file)
        return history_df
    return pd.DataFrame(columns=['Timestamp', 'User Input', 'Generated Code'])

# Function to delete a history entry
def delete_history_entry(index):
    history_file = 'history.csv'
    history_df = read_history()
    history_df = history_df.drop(index)
    history_df.to_csv(history_file, index=False)

# Main function to run the Streamlit app

def check_login(username, password):
    # Untuk contoh ini, kita gunakan username dan password yang statis
    if username == 'admin' and password == 'password':
        return True
    else:
        return False
 

@st.experimental_dialog("Yakin Data History akan dihapus??")
def HapusData(item):
    col1, spacer, col2 = st.columns([1, 2.8, 1])
    with col1:
        if st.button("Yes"):
           delete_history_entry(item)
           reason = 'Yes'
           st.session_state.vote = reason
           print(st.session_state.vote)
           st.rerun()
           
    with col2:
        if st.button("Cancel"):
            reason = 'Cancel'
            st.session_state.vote = reason
            print(st.session_state.vote)
            st.rerun()


def main():
    st.set_page_config(page_title="Assistant AI Data FDS", page_icon=":robot:")
    st.markdown("""
        <div style="text-align: center;">
            <h1>AI Assistant FDS Generator</h1>
        </div>
    """, unsafe_allow_html=True)

    # text_input = st.text_area("Enter Your Request:", value=st.session_state.text_input)

    # Sidebar to display history
    buttoninq = st.sidebar.button('New Inquery')
    if buttoninq:
        st.session_state.text_input = ''
        st.experimental_rerun()


    history_df = read_history()

    if 'text_input' not in st.session_state:
        st.session_state.text_input = ''

    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = ''

    # if not history_df.empty:
    #     for index, row in history_df.iterrows():
    #         key = row['User Input'][:50]  # Show the first 50 characters as a key
    #         col1, col2 = st.sidebar.columns([0.8, 0.2])
    #         if col1.button(key, key=f"history_{index}"):
    #             with st.spinner('Generating data...'):
    #                 st.code(row['User Input'])
    #                 exec(row['Generated Code'], globals())
    #             # st.experimental_rerun()
    #         if col2.button("...", key=f"delete_{index}"):
    #             delete_history_entry(index)
    #             st.experimental_rerun()

    

    # Input text from user
    text_input = st.text_area("Enter Your Request:", value=st.session_state.text_input)

    # Load templates and data
    str_template = load_template('template/template_str.txt')
    path_csv = "data/tx_training.csv"
    str_anomali = load_template('template/template_anomali2.txt')
    pandas_template = load_template('template/template_duckdb.txt')

    # Create columns for buttons with spacing

    col1, spacer, col2 = st.columns([1, 2.9, 1])

    with col1:
        generate_data_button = st.button("Generate Data")
    with col2:
        save_history_button = st.button("Save Generated")

    if generate_data_button:
        if len(text_input) > 1 :
            st.code(text_input)
            with st.spinner('Generating data...'):
                try:
                    # Format the template with user input
                    formatted_template = pandas_template.format(
                        text_input=text_input,
                        csv_structure=str_template,
                        path_csv=path_csv,
                        str_anomali=str_anomali
                    )
                    
                    # Generate content using the model
                    response = model.generate_content(formatted_template)
                    pandas_code = response.text.strip()
                    exec_python_code = pandas_code.replace("```python", '').replace("'''", '').replace("```", '')
                    
                    # st.code(exec_python_code, language='python')

                    # Execute the generated code
                    exec(exec_python_code, globals())

                    # Save the generated code to session state for later use
                    st.session_state.generated_code = exec_python_code

                except Exception as err:
                    st.error(f'Error: {err}')
                    st.error('Please generate again or be more specific in your request for better understanding. Thank you.')

    if not history_df.empty:
        for index, row in history_df.iterrows():
            key = row['User Input'][:29]  # Show the first 50 characters as a key
            col1, col2 = st.sidebar.columns([0.8, 0.2])
            if col1.button(key, key=f"history_{index}"):
                with st.spinner('Generating data...'):
                    pass
                    st.session_state.text_input = row['User Input'] 
                    st.code(row['User Input'])
                    exec(row['Generated Code'], globals())
                # st.experimental_rerun()

            deletebutton = col2.button("...", key=f"delete_{index}")

            if deletebutton:
                    HapusData(index)
    if save_history_button and 'generated_code' in st.session_state:
        log_history(text_input, st.session_state.generated_code)
        st.success("Generated code saved to history.")
        st.experimental_rerun()  # Rerun the app to refresh the sidebar with updated history


if __name__ == "__main__":
    main()
