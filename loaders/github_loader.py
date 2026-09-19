import tempfile
from langchain_community.document_loaders import GitLoader

def load_github(repo_url):
    repo_path=tempfile.mkdtemp()
    loader=GitLoader(
        repo_path=repo_path,
        clone_url=repo_url,
        branch=None
    )

    return loader.load()