import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# GOOGLE_API_KEY='AIzaSyB7SPxVu7N1rteqZCDnu1nY1DqSDWR6pa0'

load_dotenv()

genai.configure(api_key=os.getenv("AIzaSyB7SPxVu7N1rteqZCDnu1nY1DqSDWR6pa0"))

model = genai.GenerativeModel('gemini-pro')

def load_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    st.set_page_config(page_title="Asistant Analisa", page_icon=":robot:")
    
    # Konten HTML untuk judul
    st.markdown("""
        <div style="text-align: center;">
            <h1>Asistant Analisa Generator</h1>
        </div>
    """, unsafe_allow_html=True)  # Jadikan HTML tidak aman
    
    # Input teks dari pengguna
    text_input = st.text_area("Enter Your Request:")
    
    # Input struktur kolom CSV
    str_template = load_template('template/template_str.txt')
    # csv_structure = st.text_area("Enter CSV Column Structure :")
    print(str_template)
    path_csv = "data/tx_training.csv"

    submit = st.button("Generate Code")
    
    if submit:
        with st.spinner('Generating data...'):
            # Memuat template dari file
            pandas_template = load_template('template/template_code.txt')
            formatted_template = pandas_template.format(text_input=text_input, csv_structure=str_template,path_csv = path_csv)
            # formatted_template = pandas_template.format(text_input=text_input)
            
            # st.write("Generated Template:")
            # st.write(formatted_template)
            
            response = model.generate_content(formatted_template)
            pandas_code = response.text.strip()
            execpythoncode = pandas_code.replace("```python",'') .replace("'''",'') .replace("```",'')
            # st.write("Generated Python Code:")
            # st.code( execpythoncode, language='python')
            # st.code( '', language='python')
            
            # Menjalankan kode yang dihasilkan (evaluasi di lingkungan yang aman diperlukan)
            try:
                exec(execpythoncode, globals())
            except Exception as err:
                st.error(err)        
            # Menampilkan tabel hasil dan grafik jika tersedia
            # st.write("Resulting DataFrame:")
            # if 'df' in globals():
            #     st.dataframe(df)
                
            #     st.write("Graph:")
            #     fig, ax = plt.subplots()
            #     df.plot(ax=ax)
            #     st.pyplot(fig)

if __name__ == "__main__":
    main()
