import streamlit as st
from pydantic import BaseModel, Field
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage
from llm.model import model
# from rag.retriever import retriever

class QAResponse(BaseModel):
    answer:str=Field(
        description="Answer to the user's question using only on the provided context."
        )
    key_points:List[str]=Field(
            description="Important points from the context that support the answer."
        )
    # sources:List[str]=Field(
    #         description="Page numbers or source names of the documents used."
    #     )
structured_model=model.with_structured_output(QAResponse)

def ask_question(question, history):
    docs=st.session_state.retriever.invoke(question)

    context="\n\n".join(
        f"Page: {doc.metadata.get('page', 'Unknown')}\n"
        f"Content: {doc.page_content}"
        for doc in docs
    )

    sources=[]
    for doc in docs:
        page=doc.metadata.get("page")
        source=doc.metadata.get("source")
        if page is not None:
            sources.append(f"Page {page+1}")
        elif source:
            sources.append(source)

    sources=list(dict.fromkeys(sources))


    messages=[
        SystemMessage(
            content="""
You are a document question-answering assistant.
Answer the user's question using only the provided context.

Rules:
-Do not use outside knowledge.
-Give a clear and direct answer.
-Key_points must contain 1-5 important points supporting the answer.
-source must contain the page number or source names actually used.
-If the answer is not available in the context, say:
"The information is not available in the provided document."
"""
            )
    ]

    messages.extend(history)
    messages.append(
        HumanMessage(
                        content=f"""
            Context:{context}
            Retrieved sources:{sources}
            Question:{question}      
            """
        )
    )

    response=structured_model.invoke(messages)
    response.sources=sources
    return response