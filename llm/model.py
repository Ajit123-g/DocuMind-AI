import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

model=ChatMistralAI(model="ministral-3b-2512")

# result=model.invoke("Expain about AI.")

# print(result.content)