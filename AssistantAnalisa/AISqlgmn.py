import streamlit as st
import google.generativeai as genai

from dotenv import load_dotenv
import os 

load_dotenv()

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))


# GOOGLE_API_KEY = "AIzaSyDUbXkX2ViQyv8M4YF-dOneur8tJbsV_vw"
# genai.configure(api_key = GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def main():
    st.set_page_config(page_title="SQL Generator", page_icon=":robot:")
     # Konten HTML untuk judul
    st.markdown("""
        <div style="text-align: center;">
            <h1>Sql Query Generator</h1>
            <h3>I Can Generate SQL Query</h3>
            <h4>With Explanation as well</h4>
        </div>
    """, unsafe_allow_html=True)  # Jadikan HTML tidak aman
# Tambahkan pemanggilan fungsi main
    text_input = st.text_area ("Enter Your Query Here : ")
    submit=st.button("Generate SQL QUery" )
    if submit:
        # response = model.generate_content(text_input)
        # # print(response.text)
        # st.write(response.text)
        with st.spinner('Generating SQL Query...'):
            template = """
                    Create SQL Query snippet using the bellow text :
                    '''
                        {text_input}
                    '''
                    i just want a SQL Query 
            """
            formatted_template = template.format(text_input = text_input)   
            st.write(formatted_template)    
            response=model.generate_content(formatted_template)
            sql_query= response.text
            st.write(sql_query)
            expeted_output = """
                    Create SQL Query snippet using the bellow text :
                    '''
                    {sql_query}
                    '''
                    provide sample tabular sql
            """
            expeted_output_formatted = expeted_output.format(sql_query = sql_query)
            eoutput = model.generate_content(expeted_output_formatted)
            eoutput = eoutput.text
            st.write(eoutput)
main()

