import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os



load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
  "temperature": 2,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,)
# model = genai.GenerativeModel('gemini-pro')
# model = genai.GenerativeModel(model_name="gemini-1.5-Pro",
                            #   generation_config=generation_config,)

def load_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    
    st.set_page_config(page_title="Assistant AI Data FDS  ", page_icon=":robot:")
    

    # Konten HTML untuk judul
    st.markdown("""
        <div style="text-align: center;">
            <h1>AI Assistant FDS Generator</h1>
        </div>
    """, unsafe_allow_html=True)  # Jadikan HTML tidak aman
    
    # Input teks dari pengguna
    text_input = st.text_area("Enter Your Request: ")
    
    # Input struktur kolom CSV
    
    # promt
    str_template = load_template('template/template_str.txt')
    path_csv = "data/tx_training.csv"
    str_anomali = load_template('template/template_anomali2.txt')

    submit = st.button("Generate Data")
    if submit:
        st.code(text_input) 
        with st.spinner('Generating data...'):
            # Memuat template dari file
            pandas_template = load_template('template/template_duckdb.txt')
            formatted_template = pandas_template.format(text_input=text_input, csv_structure=str_template,path_csv = path_csv,str_anomali = str_anomali)
            # formatted_template = pandas_template.format(text_input=text_input)
            
            # st.write("Generated Template:")
            # st.write(formatted_template)
            
            response = model.generate_content(formatted_template)
            pandas_code = response.text.strip()
            execpythoncode = pandas_code.replace("```python",'') .replace("'''",'') .replace("```",'')
            # st.write("Generated Python Code:")
            st.code( execpythoncode, language='python')
            # st.code( '', language='python')
            
            # Menjalankan kode yang dihasilkan (evaluasi di lingkungan yang aman diperlukan)
            try:
                # st.code( execpythoncode, language='python')
                exec(execpythoncode, globals())
                pass
            except Exception as err:
                # st.code( execpythoncode, language='python')
                st.error(f'Please generate again or be more specific in your request for better understanding. Thank you: {err}')        
            
if __name__ == "__main__":
    
    main()
