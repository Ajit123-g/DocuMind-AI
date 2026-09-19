from langchain_community.document_loaders import CSVLoader

#CSV
def load_csv(file_path):
    loader=CSVLoader(file_path)
    return loader.load()