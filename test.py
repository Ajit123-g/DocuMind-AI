from loader import load_source
from loaders.pdf_loader import load_pdf
from processing.splitter import split_documents
from rag.embeddings import embeddings

#Load PDF
source="data/Resume1.pdf"
documents=load_source(source)

print("Pages loaded:", len(documents))

#Split into chunks
chunks=split_documents(documents)
print("Total chunks:", len(chunks))

#Create embeddings
vectors=embeddings.embed_documents(
    [chunk.page_content for chunk in chunks]
)

#Check embeddings
print("Vectors:", len(vectors))
print("Vectors dimensions:", len(vectors[0]))
print("First 5 values:", vectors[0][:5])

#Check first chunk
if chunks:
    print("\nFirst chunks:")
    print(chunks[0].page_content)

    print("\nMetadata:")
    print(chunks[0].metadata)

else:
    print("No chunks were created.")