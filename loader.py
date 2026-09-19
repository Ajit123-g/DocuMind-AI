from loaders.pdf_loader import load_pdf
from loaders.docx_loader import load_docx
from loaders.text_loader import load_text
from loaders.csv_loader import load_csv
from loaders.web_loader import load_web
from loaders.github_loader import load_github

def load_source(source):
    if source.startswith("http://") or source.startswith("https://"):
        if "github.com" in source.lower():
            return load_github(source)
        return load_web(source)
    source_lower=source.lower()
    if source_lower.endswith(".pdf"):
        return load_pdf(source)
    elif source_lower.endswith(".docx"):
        return load_docx(source)
    elif source_lower.endswith(".txt"):
        return load_text(source)
    elif source_lower.endswith(".csv"):
        return load_csv(source)
    else:
        raise ValueError(
            "Unsupported source. Use PDF, DOCX, TXT, CSV, Web URL, or GitHub URL."
        )