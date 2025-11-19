import os

import streamlit as st 

from backend.auth import OAuthHandler  
from backend.db import Database 
from backend.llm import LLMClient  
from backend.processing import process_documents  
from backend.rag_engine import RAGEngine  
from style.global_style import css as global_css
from style.question_style import css as question_css

st.set_page_config(
    page_title="Moorcheh Intelligent RAG",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(global_css, unsafe_allow_html=True)


oauth_handler = OAuthHandler()


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None


query_params = st.query_params
if "code" in query_params and "state" in query_params:
    code = query_params["code"]
    state = query_params["state"]
    space_host = os.getenv("SPACE_HOST", "")
    if space_host:
        if not space_host.startswith("http"):
            redirect_uri = f"https://{space_host}"
        else:
            redirect_uri = space_host
    else:
        redirect_uri = "http://localhost:8501"

    user_info = oauth_handler.handle_callback(code, state, redirect_uri)
    if user_info:
        st.success(f"✅ Successfully logged in as {user_info.get('username', 'User')}!")
        st.rerun()

if not oauth_handler.is_configured():
    st.warning("⚠️ OAuth is not configured. Running in development mode.")
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.session_state.authenticated = True
        st.session_state.user_info = {
            "user_id": "dev_user",
            "username": "Developer",
        }
elif not st.session_state.authenticated:
    st.markdown(
        '<div class="main-header">🔐 Login Required</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Please log in with your Hugging Face account to access the RAG Assistant</div>',
        unsafe_allow_html=True,
    )

    space_host = os.getenv("SPACE_HOST", "")
    if space_host:
        if not space_host.startswith("http"):
            redirect_uri = f"https://{space_host}"
        else:
            redirect_uri = space_host
    else:
        redirect_uri = "http://localhost:8501"

    auth_url, state = oauth_handler.generate_authorization_url(redirect_uri)

    st.markdown(
        f'<a href="{auth_url}" target="_self" style="display: inline-block; padding: 0.5rem 1rem; background: linear-gradient(to right, #005A9E, #0078D4, #00BCF2); color: white; text-decoration: none; border-radius: 5px; font-weight: 600;">🔑 Login with Hugging Face</a>',
        unsafe_allow_html=True,
    )
    st.stop()

user_info = st.session_state.user_info
user_id = user_info.get("user_id") if user_info else None
username = user_info.get("username", "User") if user_info else "User"

namespace = os.getenv("NAMESPACE")

if "db" not in st.session_state:
    st.session_state.db = Database()

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine(namespace=namespace, user_id=user_id, db=st.session_state.db)
elif st.session_state.rag_engine.user_id != user_id:
    st.session_state.rag_engine = RAGEngine(namespace=namespace, user_id=user_id, db=st.session_state.db)
else:
    st.session_state.rag_engine.db = st.session_state.db

if "llm_client" not in st.session_state:
    st.session_state.llm_client = LLMClient()


with st.sidebar:
    st.markdown("### 👤 User")
    st.markdown(f"**Logged in as:** {username}")
    if st.button("🚪 Logout"):
        oauth_handler.logout()
        if "rag_engine" in st.session_state:
            del st.session_state.rag_engine
        if "db" in st.session_state:
            st.session_state.db.close()
            del st.session_state.db
        st.rerun()

    st.divider()

    st.markdown("### 📁 Document Management")

    st.markdown(
        '<div style="font-weight:700; font-size:0.95rem;">Upload Documents</div>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        label="Upload Documents",
        label_visibility="hidden",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="Upload PDF, TXT, or MD files",
    )

    # Index button
    if st.button("📚 Index Documents", type="primary"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                try:
                    documents = process_documents(uploaded_files, user_id=user_id)
                    if documents:
                        st.session_state.rag_engine.add_documents(documents)
                        st.success(
                            f"✅ Indexed {len(documents)} documents from {len(uploaded_files)} file(s)!"
                        )
                        st.rerun()
                    else:
                        st.warning("No valid documents extracted from documents.")
                except Exception as e:
                    st.error(f"Error processing documents: {str(e)} expect")
        else:
            st.warning("Please upload files first.")

    st.divider()

    chunk_count = st.session_state.rag_engine.get_chunk_count()

    if user_id:
        user_files = st.session_state.db.get_user_files(user_id)
        if user_files:
            st.markdown("**Indexed Files:**")
            for file_info in user_files:
                filename = file_info["filename"]
                count = file_info["count"]
                st.markdown(f"• {filename} ({count} documents)")

    st.divider()

    if st.button("🔄 Reset Namespace"):
        st.session_state.rag_engine.reset_namespace()
        st.rerun()

    st.divider()

    st.markdown("### 🔑 HuggingFace Token")
    has_token = st.session_state.llm_client.has_token()
    if has_token:
        st.success("✅ Token configured")
    else:
        st.warning("⚠️ No token (using extractive fallback)")
        st.caption("Set HF_TOKEN environment variable for LLM generation")


st.markdown(
    '<div class="main-header">🐜 Moorcheh Intelligent RAG</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Ask questions about your uploaded documents using RAG-powered search</div>',
    unsafe_allow_html=True,
)


st.markdown(question_css, unsafe_allow_html=True)

st.markdown(
    '<div style="font-weight:700;">Ask a question about your documents:</div>',
    unsafe_allow_html=True,
)
question = st.text_input(
    label="Question Input",
    label_visibility="hidden",
    placeholder="e.g., What are the main findings in the research papers?",
    key="question_input",
)

col1, col2 = st.columns([5, 1.12], gap="small")
with col1:
    st.markdown(
        '<div style="font-weight:700;">Number of documents to retrieve:</div>',
        unsafe_allow_html=True,
    )
    top_k = st.slider(
        label="Number of documents to retrieve",
        label_visibility="hidden",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )
with col2:
    st.write("")
    search_clicked = st.button("Search & Generate Answer", type="primary")

if search_clicked:
    if not question:
        st.warning("Please enter a question.")
    elif chunk_count == 0:
        st.warning("Please index some documents first.")
    else:
        with st.spinner("Searching and generating answer..."):
            rag_response = st.session_state.rag_engine.search(question, top_k=top_k)
            results = rag_response["results"]
            time_taken = rag_response["time_taken"]

            if results:
                st.markdown(f"### Retrieved Documents (Time taken: {time_taken} ms)")

                table_data = []
                for i, result in enumerate(results, 1):
                    table_data.append(
                        {
                            "Rank": i,
                            "Source": result["metadata"]["source"],
                            "Score": f"{result['score']:.3f}",
                            "Preview": result["text"][:150] + "..."
                            if len(result["text"]) > 150
                            else result["text"],
                        }
                    )

                st.dataframe(table_data, width="stretch", hide_index=True)

                answer = st.session_state.llm_client.generate_answer(question, results)

                st.markdown("### 💡 Generated Answer")
                st.markdown(
                    f"""
                    <div class="answer-card">
                        <div class="answer-title">Answer</div>
                        <div>{answer.replace(chr(10), "<br>")}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("### 📚 Citations")
                for i, result in enumerate(results, 1):
                    source = result["metadata"]["source"]
                    chunk_id = result["metadata"].get("chunk_id", f"chunk_{i}")
                    preview = (
                        result["text"][:200] + "..."
                        if len(result["text"]) > 200
                        else result["text"]
                    )

                    st.markdown(
                        f"""
                        <div class="citation-item">
                            <strong>[{i}] {source}</strong> (Score: {result["score"]:.3f})<br>
                            <small>{preview}</small>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning("No results found. Try rephrasing your question.")

st.divider()
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built by <a href='https://github.com/mahimairaja' target='_blank'>mahimairaja</a>"
    "</div>",
    unsafe_allow_html=True,
)
