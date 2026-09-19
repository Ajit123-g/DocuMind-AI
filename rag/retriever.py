from langchain_chroma import Chroma
from rag.embeddings import embeddings


def create_retriever(chunks, document_id):
    vectorstore=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=f"chroma_db/{document_id}",
        collection_name=document_id
    )

    retriever=vectorstore.as_retriever(
        search_kwargs={"k":4}
    )

    return retriever

# docs=retriever.invoke("what is this document about?")

# for doc in docs:
#     print(doc.page_content)