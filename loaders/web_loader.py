from langchain_community.document_loaders import WebBaseLoader

#Web 
def load_web(source):
    loader=WebBaseLoader(source)
    documents=loader.load()
    return documents