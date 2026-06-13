import streamlit as st
import requests
st.set_page_config(page_title="Dynamic AI Agent", page_icon="📄", layout="centered")

st.title("📄 Dynamic Academic Assistant")
st.write("Upload any PDF research paper, assignment layout, or policy document and chat with it instantly.")

#Create a sidebar
with st.sidebar:
    st.header("📁 Document Ingestion")
    uploaded_file = st.file_uploader("Choose a PDF File", type=["pdf"])

    if st.button("Process Document", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Processing file..."):
                try:
                    # Prepare the file payload for standard multipart form upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(),"application/pdf")}
                    backend_upload_url = "http://127.0.0.1:8000/upload"
                    response = requests.post(backend_upload_url, files=files)
                    if response.status_code == 200:
                        st.success(response.json().get("message"))
                    else:
                        st.error(f"Failed processing: {response.text}")
                except Exception as e:
                    st.error(f"Could not reach backend server: {str(e)}")

        else:
            st.warning("Please upload a file before pressing process.")

st.subheader("💬 Ask Your Document")
user_question = st.text_input("Enter your query based on the processed document:", placeholder="What are the main conclusions of this file?")

if st.button("Submit Query"):
    if user_question.strip() == "":
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("🤖 Agent is thinking..."):
            try:
                backend_ask_url = "http://127.0.0.1:8000/ask"
                payload = {"question": user_question}
                response = requests.post(backend_ask_url, json=payload)

                if response.status_code == 200:
                    answer = response.json().get("answer")
                    st.write("### ✨ Answer:")
                    st.info(answer)
                else:
                    # Handle case where user asks a question before uploading a file
                    error_msg = response.json().get("detail", "Error Occurred.")
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Could not connect to backend server: {str(e)}")