from langchain_openai import ChatOpenAI
from rag.retriever import get_retriever, pretty_context

SCALES = ["PHQ-9", "GAD-7", "Maslach", "BDI", "PSS"]

def choose_scale(user_text: str) -> str:
    text = user_text.lower()
    if any(w in text for w in ["anxious","anxiety","panic","worry","worried"]): return "GAD-7"
    if any(w in text for w in ["depress","sad","hopeless","anhedonia","fatigue"]): return "PHQ-9"
    if any(w in text for w in ["burnout","épuisement","épuisé","dépersonnalisation"]): return "Maslach"
    if any(w in text for w in ["stress","overwhelmed","stressed"]): return "PSS"

    retriever = get_retriever(k=3)
    ctx_docs = retriever.get_relevant_documents("Which screening scale fits: " + user_text)
    ctx = pretty_context(ctx_docs)
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = f"""Context (scales info):
{ctx}

User statement:
{user_text}

Pick one most relevant scale name from: {", ".join(SCALES)}.
Answer with only the exact scale name."""
    out = llm.invoke(prompt).content.strip()
    return out if out in SCALES else "PHQ-9" 
