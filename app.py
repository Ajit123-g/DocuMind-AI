import os
import tempfile
import uuid
import streamlit as st

from loader import load_source
from processing.splitter import split_documents

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from llm.model import model
from rag.qa import QAResponse
from rag.retriever import create_retriever


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processed" not in st.session_state:
    st.session_state.processed = False

if "source_name" not in st.session_state:
    st.session_state.source_name = ""

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "document_id" not in st.session_state:
    st.session_state.document_id = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📚 DocuMind AI")

    st.markdown("---")

    st.subheader("📂 Add Source")

    source_type = st.selectbox(
        "Select source type",
        [
            "PDF",
            "DOCX",
            "CSV",
            "TXT",
            "Web URL",
            "GitHub URL"
        ]
    )

    uploaded_file = None
    source = None

    # -----------------------------------------------------
    # FILE UPLOAD
    # -----------------------------------------------------

    if source_type in ["PDF", "DOCX", "CSV", "TXT"]:

        extensions = {
            "PDF": ["pdf"],
            "DOCX": ["docx"],
            "CSV": ["csv"],
            "TXT": ["txt"]
        }

        uploaded_file = st.file_uploader(
            f"Upload {source_type}",
            type=extensions[source_type]
        )

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    else:

        source = st.text_input(
            f"Enter {source_type}"
        )

    st.markdown("---")

    process = st.button(
        "⚙️ Process Source",
        use_container_width=True
    )

    clear_chat = st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    )


# =========================================================
# CLEAR CHAT
# =========================================================

if clear_chat:

    st.session_state.chat_history = []

    st.rerun()


# =========================================================
# PROCESS SOURCE
# =========================================================

if process:

    source_name = None

    # -----------------------------------------------------
    # FILE
    # -----------------------------------------------------

    if uploaded_file is not None:

        suffix = os.path.splitext(
            uploaded_file.name
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(
                uploaded_file.getbuffer()
            )

            source = temp_file.name

        source_name = uploaded_file.name

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    elif source and source.strip():

        source = source.strip()
        source_name = source.strip()

    else:

        st.warning(
            "Please upload a file or enter a URL."
        )

        st.stop()

    # -----------------------------------------------------
    # LOAD + PROCESS
    # -----------------------------------------------------

    try:

        # -------------------------------------------------
        # VALIDATE URL
        # -------------------------------------------------

        if source_type in ["Web URL", "GitHub URL"]:

            if not source.strip():

                st.error("Please enter a URL.")
                st.stop()

            if not source.startswith(
                ("http://", "https://")
            ):

                st.error(
                    "Please enter a valid URL starting "
                    "with http:// or https://"
                )

                st.stop()

        # -------------------------------------------------
        # LOAD SOURCE
        # -------------------------------------------------

        with st.spinner("📖 Loading source..."):

            documents = load_source(source)

        if not documents:

            st.error(
                "No content found in the source."
            )

            st.stop()

        # -------------------------------------------------
        # SPLIT DOCUMENT
        # -------------------------------------------------

        with st.spinner(
            "✂️ Splitting into chunks..."
        ):

            chunks = split_documents(documents)

        if not chunks:

            st.error(
                "No chunks were created."
            )

            st.stop()

        # -------------------------------------------------
        # CREATE UNIQUE DOCUMENT ID
        # -------------------------------------------------

        document_id = (
            f"document_{uuid.uuid4().hex}"
        )

        # -------------------------------------------------
        # CREATE NEW VECTOR STORE + RETRIEVER
        # -------------------------------------------------

        with st.spinner(
            "🔎 Creating embeddings and vector store..."
        ):

            new_retriever = create_retriever(
                chunks,
                document_id
            )

        # -------------------------------------------------
        # SAVE CURRENT RETRIEVER
        # -------------------------------------------------

        st.session_state.retriever = new_retriever

        st.session_state.document_id = document_id

        st.session_state.processed = True

        st.session_state.source_name = source_name

        # IMPORTANT:
        # New document = New chat

        st.session_state.chat_history = []

        st.success(
            "✅ Source processed successfully!"
        )

        st.info(
            f"Documents: {len(documents)}  |  "
            f"Chunks: {len(chunks)}"
        )

    except Exception as e:

        st.error(
            f"❌ Error while processing source:\n\n{e}"
        )


# =========================================================
# MAIN UI
# =========================================================

st.title("📚 DocuMind AI")

st.markdown(
    "### Ask questions from your documents using RAG"
)


# =========================================================
# SOURCE STATUS
# =========================================================

if st.session_state.processed:

    st.success(
        f"📄 Source: "
        f"{st.session_state.source_name}"
    )

else:

    st.info(
        "👈 Upload a document or enter a URL "
        "from the sidebar and click "
        "**Process Source**."
    )


# =========================================================
# CHAT HISTORY DISPLAY
# =========================================================

for message in st.session_state.chat_history:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            response = message["response"]

            st.markdown("### 💡 Answer")

            st.write(
                response.answer
            )

            if response.key_points:

                st.markdown(
                    "### 📌 Key Points"
                )

                for point in response.key_points:

                    st.markdown(
                        f"- {point}"
                    )


# =========================================================
# QUESTION INPUT
# =========================================================

question = st.chat_input(
    "Ask something about your document..."
)


# =========================================================
# ANSWER QUESTION
# =========================================================

if question:

    # -----------------------------------------------------
    # CHECK SOURCE
    # -----------------------------------------------------

    if (
        not st.session_state.processed
        or st.session_state.retriever is None
    ):

        st.warning(
            "⚠️ Please process a document first."
        )

        st.stop()

    # -----------------------------------------------------
    # SHOW USER QUESTION
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.write(question)

    try:

        # -------------------------------------------------
        # GET CURRENT DOCUMENT RETRIEVER
        # -------------------------------------------------

        current_retriever = (
            st.session_state.retriever
        )

        # -------------------------------------------------
        # RETRIEVE RELEVANT DOCUMENTS
        # -------------------------------------------------

        with st.spinner(
            "🔎 Searching your document..."
        ):

            docs = current_retriever.invoke(
                question
            )

        # -------------------------------------------------
        # CREATE CONTEXT
        # -------------------------------------------------

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        # -------------------------------------------------
        # PREVIOUS CHAT
        # -------------------------------------------------

        history = ""

        for message in st.session_state.chat_history:

            if message["role"] == "user":

                history += (
                    f"User: "
                    f"{message['content']}\n"
                )

            else:

                history += (
                    f"Assistant: "
                    f"{message['response'].answer}\n"
                )

        # -------------------------------------------------
        # MESSAGES
        # -------------------------------------------------

        messages = [

            SystemMessage(
                content="""
You are DocuMind AI, a document
question-answering assistant.

Answer the user's question using ONLY
the provided document context.

Do not use outside knowledge.

If the answer cannot be found in the
provided context, say that the information
could not be found in the provided document.

Do not make up information.

Return the answer using the required
structured output format.
"""
            ),

            SystemMessage(
                content=f"""
DOCUMENT CONTEXT:

{context}
"""
            ),

            SystemMessage(
                content=f"""
PREVIOUS CHAT HISTORY:

{history}
"""
            ),

            HumanMessage(
                content=question
            )
        ]

        # -------------------------------------------------
        # STRUCTURED OUTPUT
        # -------------------------------------------------

        with st.spinner(
            "🤖 Generating answer..."
        ):

            structured_model = (
                model.with_structured_output(
                    QAResponse
                )
            )

            response = structured_model.invoke(
                messages
            )

        # -------------------------------------------------
        # SHOW RESPONSE
        # -------------------------------------------------

        with st.chat_message("assistant"):

            st.markdown(
                "### 💡 Answer"
            )

            st.markdown(
                response.answer
            )

            if response.key_points:

                st.markdown(
                    "### 📌 Key Points"
                )

                for point in response.key_points:

                    st.markdown(
                        f"- {point}"
                    )

        # -------------------------------------------------
        # SAVE HISTORY
        # -------------------------------------------------

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "response": response
            }
        )

    except Exception as e:

        st.error(
            f"❌ Error while answering:\n\n{e}"
        )