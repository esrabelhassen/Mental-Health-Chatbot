from core.loader import load_scale
from core.state import init_state, get_next_question, record_response
from core.scoring import calculate_score, interpret_score
from chat.scale_selector import choose_scale
from rag.retriever import get_retriever, pretty_context
from langchain_openai import ChatOpenAI
from chat.policy import SYSTEM_PROMPT
from dotenv import load_dotenv 
import os

load_dotenv()

os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-3.5-turbo")

def explain_scale(scale_name: str) -> str:
    retriever = get_retriever(k=4)
    docs = retriever.get_relevant_documents(f"Explain what {scale_name} measures and how it's scored.")
    ctx = pretty_context(docs)
    prompt = f"""{SYSTEM_PROMPT}

Use the context to explain {scale_name} in 2-3 sentences, then ask consent to begin.

Context:
{ctx}
"""
    return llm.invoke(prompt).content

def clarify_option(question_text: str, option_key: str, scale_name: str) -> str:
    retriever = get_retriever(k=3)
    docs = retriever.get_relevant_documents(f"{scale_name} answer options meaning")
    ctx = pretty_context(docs)
    prompt = f"""{SYSTEM_PROMPT}

A user asked what option '{option_key}' means for this question:
"{question_text}"

Use the context to briefly clarify.
Context:
{ctx}"""
    return llm.invoke(prompt).content

def final_feedback(scale_name: str, score, interpretation) -> str:
    retriever = get_retriever(k=4)
    docs = retriever.get_relevant_documents(f"{scale_name} interpretation guidance and general support suggestions")
    ctx = pretty_context(docs)
    prompt = f"""{SYSTEM_PROMPT}

Scale: {scale_name}
Score: {score}
Interpretation: {interpretation}

Using the context, give supportive, plain-language feedback (3-6 lines). Remind it's a screening.
Context:
{ctx}"""
    return llm.invoke(prompt).content

def run_screening(user_intro_text: str, simulated_answers: dict[str,int] | None = None):
    # 1) pick scale
    scale_name = choose_scale(user_intro_text)
    scale = load_scale(scale_name)
    # 2) explain and consent
    intro = explain_scale(scale_name)
    print(intro)

    state = init_state(scale_name)

    idx = 0
    while True:
        q = get_next_question(scale, state)
        if not q:
            break
        print(f"\n{q['id']}. {q['text']}")
        print("Options:", ", ".join([f"{k}={v}" for k,v in q["options"].items()]))

        if simulated_answers:
            val = simulated_answers[q["id"]]
            print(f"[auto] answer -> {val}")
        else:
            raw = input("Your answer: ").strip()
            if raw.lower().startswith("help"):
                print(clarify_option(q["text"], raw.split()[-1], scale_name))
                raw = input("Your answer: ").strip()
            val = int(raw)

        record_response(state, q["id"], val)
        idx += 1
        print(f"(saved) Progress: {idx}/{len(scale['questions'])}")

    score = calculate_score(scale, state["responses"])
    interpretation = interpret_score(scale, score)
    print("\n--- RESULTS ---")
    print("Score:", score)
    print("Interpretation:", interpretation)
    print("\n" + final_feedback(scale_name, score, interpretation))
