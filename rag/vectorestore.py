from langchain_chroma import Chroma
from rag.embeddings import embeddings
from processing.splitter import split_documents
from loader import load_source

def create_vectorstore(source):
    documents=load_source(source)
    chunks=split_documents(documents)
    vectorstore=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db",
        # collection_name="my_documents"
    )

    print("Documents stored in ChromaDB!")
    return vectorstore