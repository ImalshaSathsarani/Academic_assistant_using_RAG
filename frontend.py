import streamlit as st
import requests
st.set_page_config(page_title="Dynamic AI Agent", page_icon="📄", layout="centered")

st.title("📄 Dynamic Academic Assistant")
st.write("Upload any PDF research paper, assignment layout, or policy document and chat with it instantly.")

# =====================================================================
# INITIALIZE CHAT HISTORY USING SESSION STATE
# =====================================================================
# This tells Streamlit: "Keep a memory array of our chat turns so they don't erase on refresh!"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
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
                    backend_upload_url = "https://academic-assistant-using-rag.onrender.com/upload"
                    response = requests.post(backend_upload_url, files=files)
                    if response.status_code == 200:
                        st.success(response.json().get("message"))
                        # Clear old chat histories when a brand new document is successfully processed
                        st.session_state.chat_history = []
                    else:
                        st.error(f"Failed processing: {response.text}")
                except Exception as e:
                    st.error(f"Could not reach backend server: {str(e)}")

        else:
            st.warning("Please upload a file before pressing process.")

# =====================================================================
# DISPLAY COMPLETED CONVERSATION STREAM
# =====================================================================
# This loops through and draws all previous messages on every single script rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# st.subheader("💬 Ask Your Document")
# user_question = st.text_input("Enter your query based on the processed document:", placeholder="What are the main conclusions of this file?")

# if st.button("Submit Query"):
#     if user_question.strip() == "":
#         st.warning("Please enter a question before submitting.")
#     else:
#         with st.spinner("🤖 Agent is thinking..."):
#             try:
#                 backend_ask_url = "https://academic-assistant-using-rag.onrender.com/ask"
#                 payload = {"question": user_question}
#                 response = requests.post(backend_ask_url, json=payload)

#                 if response.status_code == 200:
#                     answer = response.json().get("answer")
#                     st.write("### ✨ Answer:")
#                     st.info(answer)
#                 else:
#                     # Handle case where user asks a question before uploading a file
#                     error_msg = response.json().get("detail", "Error Occurred.")
#                     st.error(error_msg)
#             except Exception as e:
#                 st.error(f"Could not connect to backend server: {str(e)}")
# =====================================================================
# HANDING THE USER CHAT INPUT INPUT
# =====================================================================
# st.chat_input creates an elegant, interactive text input field at the bottom of the page
if user_question := st.chat_input("Ask something about the processed document..."):
    
    # 1. Instantly render the user's message to the screen and save to history
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    
    # 2. Trigger the call to your live Render container
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent is thinking..."):
            try:
                backend_ask_url = "https://academic-assistant-using-rag.onrender.com/ask"
                payload = {"question": user_question}
                response = requests.post(backend_ask_url, json=payload)

                if response.status_code == 200:
                    answer = response.json().get("answer")
                    # Render the complete answer text cleanly
                    st.write(answer)
                    # Append it to the history list so it persists on screen
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    error_msg = response.json().get("detail", "Error Occurred.")
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Could not connect to backend server: {str(e)}")