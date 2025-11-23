import os, json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from dotenv import load_dotenv 

load_dotenv()

os.getenv("OPENAI_API_KEY")

BASE = os.path.dirname(os.path.dirname(__file__))
SCALES_DIR = os.path.join(BASE, "scales")
DOCS_DIR   = os.path.join(BASE, "docs")
DB_DIR     = os.path.join(BASE, "vectorstore")

def _json_docs():
    for name in os.listdir(SCALES_DIR):
        if name.endswith(".json"):
            path = os.path.join(SCALES_DIR, name)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Flatten JSON into readable chunks
            yield {
                "page_content": json.dumps(data, ensure_ascii=False, indent=2),
                "metadata": {"source": f"json:{name}", "scale_name": data.get("scale_name")}
            }

def _pdf_docs():
    if not os.path.isdir(DOCS_DIR):
        return
    for name in os.listdir(DOCS_DIR):
        if name.lower().endswith(".pdf"):
            path = os.path.join(DOCS_DIR, name)
            reader = PdfReader(path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                yield {
                    "page_content": text.strip(),
                    "metadata": {"source": f"pdf:{name}", "page": i}
                }

def build_vectorstore():
    texts, metas = [], []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    # Ingest JSON (authoritative rules) + PDFs (explanations/instructions)
    raw_docs = list(_json_docs()) + list(_pdf_docs())
    for d in raw_docs:
        for chunk in splitter.split_text(d["page_content"]):
            texts.append(chunk)
            metas.append(d["metadata"])

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vs = Chroma.from_texts(texts=texts, metadatas=metas, embedding=embeddings, persist_directory=DB_DIR)
    vs.persist()
    print(f"[RAG] Vector DB built with {len(texts)} chunks at {DB_DIR}")

if __name__ == "__main__":
    os.makedirs(DB_DIR, exist_ok=True)
    build_vectorstore()
