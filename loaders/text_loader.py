from langchain_community.document_loaders import TextLoader

#Text
def load_text(file_path):
    loader=TextLoader(file_path)
    return loader.load()