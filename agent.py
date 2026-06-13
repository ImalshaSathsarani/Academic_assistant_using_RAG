
# import os
# import shutil
# from fastapi import FastAPI, HTTPException, UploadFile, File
# from pydantic import BaseModel
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.documents import Document
# from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from langchain_community.vectorstores import Chroma
# from langchain_core.tools import create_retriever_tool  
# from langchain_classic.agents import AgentExecutor  
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# # Modernized classic tracking imports
# from langchain_classic.agents.format_scratchpad import format_to_openai_function_messages
# from langchain_classic.agents.output_parsers import OpenAIFunctionsAgentOutputParser


# app = FastAPI(title="Dynamic Academic Assistant API")
# # Ensure your API key is properly loaded
# if not os.environ.get("GEMINI_API_KEY"):
#     raise ValueError("GEMINI_API_KEY environment variable is missing!")

# #temporary storage configuration
# UPLOAD_DIR = "./temp_uploads"
# DB_DIR = "./chroma_db"

# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)

# if not os.path.exists(DB_DIR):
#     os.makedirs(DB_DIR)

# #Global tracking variables for the active session
# agent_runner  = None

# # =====================================================================
# # PHASE 1: PREPARE THE KNOWLEDGE BASE (INDEXING)
# # =====================================================================

# # print("🔄 Step 1: Loading 'company_policy.txt'...")
# # with open("company_policy.txt", "r", encoding="utf-8") as f:
# #     text_content = f.read()
# # raw_documents = [Document(page_content=text_content)]

# # print("🔄 Step 2: Splitting text into manageable chunks...")
# # text_splitter = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
# # text_chunks = text_splitter.split_documents(raw_documents)

# # print("🔄 Step 3: Generating Gemini embeddings and storing in Vector DB...")
# # embedding_engine = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
# # vector_db = Chroma.from_documents(text_chunks, embedding_engine)

# # # =====================================================================
# # # PHASE 2: PACKAGING THE DATABASE AS A TOOL
# # # =====================================================================

# # print("🔄 Step 4: Wrapping the database search function into a Tool...")
# # db_retriever = vector_db.as_retriever(search_kwargs={"k": 2})

# # retriever_tool = create_retriever_tool(
# #     db_retriever,
# #     name="query_acmecorp_policy",
# #     description="Mandatory tool to use when answering questions about AcmeCorp working hours, leaves, insurance, and remote work rules."
# # )
# # tools_list = [retriever_tool]

# # # =====================================================================
# # # PHASE 3: BUILDING THE MODERN AGENT
# # # =====================================================================

# # print("🔄 Step 5: Initializing the Gemini Brain and assembling the Agent...")
# # llm_brain = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# # prompt_template = ChatPromptTemplate.from_messages([
# #     ("system", (
# #         "You are a helpful HR Assistant for AcmeCorp. "
# #         "You must prioritize using your tools to answer user questions. "
# #         "If you cannot find the answer within the tool output, respond honestly: "
# #         "'I am sorry, but I do not possess that specific policy detail.'"
# #     )),
# #     ("user", "{input}"),
# #     MessagesPlaceholder(variable_name="agent_scratchpad")
# # ])

# # # Connect tools onto the brain
# # llm_with_tools = llm_brain.bind_tools(tools_list)

# # # Declarative execution graph pipeline
# # ai_agent = (
# #     {
# #         "input": lambda x: x["input"],
# #         "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"])
# #     }
# #     | prompt_template
# #     | llm_with_tools
# #     | OpenAIFunctionsAgentOutputParser()
# # )

# # agent_runner = AgentExecutor(agent=ai_agent, tools=tools_list, verbose=True)

# # # =====================================================================
# # # PHASE 4: RUNNING EXAMPLES
# # # =====================================================================
# # print("\n🚀 System Ready! Testing Gemini Agent queries...\n")

# # print("--- Question ---")
# # response = agent_runner.invoke({"input": "How many casual leaves do I get?"})

# # # --- CLEAN UP ENGINE ---
# # # Extract the raw output object
# # raw_output = response['output']

# # # If the output is a list containing dictionaries, extract just the text content
# # if isinstance(raw_output, list) and len(raw_output) > 0:
# #     clean_text = "".join([chunk['text'] if isinstance(chunk, dict) and 'text' in chunk else str(chunk) for chunk in raw_output])
# # else:
# #     clean_text = str(raw_output)

# # print(f"\n✨ Final Clean Answer:\n{clean_text}\n")

# def rebuild_agent_with_doc(pdf_path: str):
#     """Dynamically parses the uploaded PDF and rebuilds the LangChain Agent"""

# # 1. Clear out any previous database directory to keep queries isolated to the new file
#     global agent_runner  # Ensure we modify the global variable

#     if os.path.exists(DB_DIR):
#         shutil.rmtree(DB_DIR)  # Clear previous database

#     print(f' Processing new document source: {pdf_path}')

#     #2. Extract text from the specific uploaded file
#     loader = PyPDFLoader(pdf_path)
#     raw_docs = loader.load()

#     #3. Chunk text recursively
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
#     text_chunks = text_splitter.split_documents(raw_docs)

#     #4. Generate embeddings and create database index
#     embedding_engine = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
#     vector_db = Chroma.from_documents(
#         documents=text_chunks,
#         embedding=embedding_engine,
#         persist_directory=DB_DIR
#     )

#     #5. Connect Vector DB as an agent tool
#     db_retriever = vector_db.as_retriever(search_kwargs={"k": 3})
#     retriever_tool = create_retriever_tool(
#         db_retriever,
#         name="document_knowledge_search",
#         description="Mandatory tool to search through the contents of the uploaded user document to find factual truths."
#     )

#     tools_list = [retriever_tool]

#     #6. Initialize gemini and establish pipeline
#     llm_brain = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

#     prompt_template = ChatPromptTemplate.from_messages([
#         ("system",(
#             "You are a helpful assistant analyzing an uploaded document."
#             "You must prioritize using your tools to scan the text files to answer user questions. "
#             "If the answer is completely missing, respond honestly: 'I cannot find that information in the uploaded document.'"
#         )),
#         ("user", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad")
#     ])

#     llm_with_tools = llm_brain.bind_tools(tools_list)

#     ai_agent = (
#         {
#             "input": lambda x: x["input"],
#             "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"])
#         }
#         | prompt_template | llm_with_tools | OpenAIFunctionsAgentOutputParser()
#     )

#     agent_runner = AgentExecutor(agent=ai_agent, tools=tools_list, verbose=True)
#     print("Agent successfully reconstructed and primed for questions!")

#     @app.post("/upload")
#     async def upload_document(file: UploadFile = File(...)):
#         """Receives file bytes from frontend, saves it locally, and triggers indexing"""
#         try:
#             file_path = os.path.join(UPLOAD_DIR, file.filename)
#             #Write incoming uploaded file stream to storage disk
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)

#             # Re-index database with this file
#             rebuild_agent_with_doc(file_path)

#             return {"status": "success", "message": f"Document '{file.filename}' processed successfully!"}
#         except Exception as e:
#           raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")  
        
#     class QueryRequest(BaseModel):
#         question: str

#     @app.post("/ask")
#     def ask_agent(payload: QueryRequest):
#         global agent_runner
#         if not agent_runner:
#             raise HTTPException(status_code=400, detail="No document has been uploaded yet. Please upload a document first.")
#         try:
#             response = agent_runner.invoke({"input": payload.question})
#             raw_output = response['output']

#             if isinstance(raw_output, list) and len(raw_output) > 0:
#                 clean_text = "".join([chunk['text'] if isinstance(chunk, dict) and 'text' in chunk else str(chunk) for chunk in raw_output])
#             else:
#                 clean_text = str(raw_output)

#             return {"answer": clean_text}
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")




import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.tools import create_retriever_tool  
from langchain_classic.agents import AgentExecutor  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents.format_scratchpad import format_to_openai_function_messages
from langchain_classic.agents.output_parsers import OpenAIFunctionsAgentOutputParser

app = FastAPI(title="Dynamic Academic Assistant API")

# Ensure your API key is properly loaded
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("❌ GEMINI_API_KEY environment variable is missing!")

# Temporary storage configuration
UPLOAD_DIR = "./temp_uploads"
DB_DIR = "./chroma_db"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Global tracking variables for the active session
agent_runner = None


def rebuild_agent_with_doc(pdf_path: str):
    """Dynamically parses the uploaded PDF and rebuilds the LangChain Agent"""
    global agent_runner  # Ensure we modify the global variable

    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)  # Clear previous database

    print(f"🔄 Processing new document source: {pdf_path}")

    # 2. Extract text from the specific uploaded file
    loader = PyPDFLoader(pdf_path)
    raw_docs = loader.load()

    # 3. Chunk text recursively
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    text_chunks = text_splitter.split_documents(raw_docs)

    # 4. Generate embeddings and create database index
    embedding_engine = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_db = Chroma.from_documents(
        documents=text_chunks, embedding=embedding_engine, persist_directory=DB_DIR
    )

    # 5. Connect Vector DB as an agent tool
    db_retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    retriever_tool = create_retriever_tool(
        db_retriever,
        name="document_knowledge_search",
        description="Mandatory tool to search through the contents of the uploaded user document to find factual truths.",
    )

    tools_list = [retriever_tool]

    # 6. Initialize gemini and establish pipeline
    llm_brain = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a helpful assistant analyzing an uploaded document."
                    "You must prioritize using your tools to scan the text files to answer user questions. "
                    "If the answer is completely missing, respond honestly: 'I cannot find that information in the uploaded document.'"
                ),
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm_with_tools = llm_brain.bind_tools(tools_list)

    ai_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt_template
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_runner = AgentExecutor(agent=ai_agent, tools=tools_list, verbose=True)
    print("🚀 Agent successfully reconstructed and primed for questions!")


# =====================================================================
# FASTAPI ENDPOINTS (FIXED: Moved outside function scope structure)
# =====================================================================


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Receives file bytes from frontend, saves it locally, and triggers indexing"""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        # Write incoming uploaded file stream to storage disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Re-index database with this file
        rebuild_agent_with_doc(file_path)

        return {
            "status": "success",
            "message": f"Document '{file.filename}' processed successfully!",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Upload processing failed: {str(e)}"
        )


class QueryRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_agent(payload: QueryRequest):
    global agent_runner
    if not agent_runner:
        raise HTTPException(
            status_code=400,
            detail="No document has been uploaded yet. Please upload a document first.",
        )
    try:
        response = agent_runner.invoke({"input": payload.question})
        raw_output = response["output"]

        if isinstance(raw_output, list) and len(raw_output) > 0:
            clean_text = "".join(
                [
                    chunk["text"] if isinstance(chunk, dict) and "text" in chunk else str(chunk)
                    for chunk in raw_output
                ]
            )
        else:
            clean_text = str(raw_output)

        return {"answer": clean_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")