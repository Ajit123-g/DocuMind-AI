import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

model_name=os.getenv("HF_EMBEDDING_MODEL")

embeddings=HuggingFaceEmbeddings(
    model_name=model_name
)

text="LangChain is used to build LLM applications."

vector=embeddings.embed_query(text)

print("Embedding dimensions:", len(vector))
print("First 5 values:", vector[:5])