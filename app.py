import streamlit as st
import sqlite3
import google.generativeai as genai

# Configure the Google Gemini API using secrets
genai.configure(api_key=st.secrets["api_keys"]["google_generative_ai"])

# Prompt for converting questions to SQL
prompt = [
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name STUDENTS and has the following columns - NAME, CLASS, 
    Marks, Company \n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM STUDENTS ;
    \nExample 2 - Tell me all the students studying in MCA class?, 
    the SQL command will be something like this SELECT * FROM STUDENT 
    where CLASS="MCA"; 
    also the sql code should not have ``` in beginning or end and sql word in output
    """
]

# Function to get response from Google Gemini API
def get_response(que, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0], que])
    return response.text

# Function to execute SQL query and fetch results
def read_query(sql, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

# App configuration
st.set_page_config(
    page_title="Google Gemini SQL Query Retriever",
    page_icon="🌟"
)

st.title("Welcome to QueryCraft!! 🤖")
st.markdown("""
This app retrieves SQL data for the given text using Google Gemini.
""")

# File uploader for database
uploaded_file = st.file_uploader("Upload your SQLite database", type=["db"])
if uploaded_file is not None:
    db_path = uploaded_file.name
    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded file: {db_path}")
else:
    db_path = "data.db"  # Fallback to a static database if no file is uploaded

# Input query from user
que = st.text_input("Enter Your Query:", key="sql_query")
submit = st.button("Get Answer", key="submit_button", help="Click to retrieve the SQL data")

# Execute on button click or input provided
if submit or que:
    if que:
        try:
            response = get_response(que, prompt).strip()
            st.subheader("Generated SQL Query:")
            st.code(response, language='sql')

            # Read and display query results
            query_results = read_query(response, db_path)
            if query_results:
                st.subheader("The Response is:")
                st.table(query_results)
            else:
                st.subheader("No data found.")
        except Exception as e:
            st.subheader("An error occurred:")
            st.error(str(e))
    else:
        st.subheader("Please enter a valid query.")


