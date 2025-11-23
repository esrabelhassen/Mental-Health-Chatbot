import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv 

load_dotenv()

os.getenv("OPENAI_API_KEY")

BASE = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE, "vectorstore")

def get_retriever(k: int = 4):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vs = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return vs.as_retriever(search_kwargs={"k": k})

def pretty_context(docs: list[Document]) -> str:
    lines = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        lines.append(f"[{src}] {d.page_content}")
    return "\n\n".join(lines)
