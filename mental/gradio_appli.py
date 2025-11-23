import gradio as gr
from core.loader import load_scale
from core.state import init_state, get_next_question, record_response
from core.scoring import calculate_score, interpret_score
from chat.scale_selector import choose_scale
from chat.loop import explain_scale, clarify_option, final_feedback
import os 
from dotenv import load_dotenv 

load_dotenv()

os.getenv("OPENAI_API_KEY")

# Global conversation state per session
session_states = {}

def start_session(user_intro_text):
    scale_name = choose_scale(user_intro_text)
    scale = load_scale(scale_name)
    state = init_state(scale_name)
    session_states["state"] = state
    session_states["scale"] = scale
    session_states["intro"] = explain_scale(scale_name)
    return session_states["intro"]

def chatbot_response(user_input):
    state = session_states.get("state")
    scale = session_states.get("scale")

    # If no active session yet
    if not state or not scale:
        return "Please start by describing how you feel."

    # If user types "help X"
    if user_input.lower().startswith("help"):
        parts = user_input.split()
        if len(parts) > 1:
            option = parts[-1]
            return clarify_option("?", option, state["current_scale"])
        return "Type `help <option_number>` to clarify what an option means."

    # Get current question
    q = get_next_question(scale, state)
    if not q:
        # Already completed
        score = calculate_score(scale, state["responses"])
        interpretation = interpret_score(scale, score)
        feedback = final_feedback(state["current_scale"], score, interpretation)
        return f"✅ Screening complete!\n\nScore: {score}\nInterpretation: {interpretation}\n\n{feedback}"

    # Expect numeric input
    try:
        val = int(user_input)
        record_response(state, q["id"], val)
    except ValueError:
        return f"Please answer with a number corresponding to the options."

    # Next question
    next_q = get_next_question(scale, state)
    if not next_q:
        score = calculate_score(scale, state["responses"])
        interpretation = interpret_score(scale, score)
        feedback = final_feedback(state["current_scale"], score, interpretation)
        return f"✅ Screening complete!\n\nScore: {score}\nInterpretation: {interpretation}\n\n{feedback}"

    options_str = ", ".join([f"{k}={v}" for k,v in next_q["options"].items()])
    return f"{next_q['id']}. {next_q['text']}\nOptions: {options_str}"

with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Mental Health Chatbot ")
    gr.Markdown("Describe how you feel to begin. The assistant will pick a scale and ask questions step by step.")

    with gr.Row():
        user_intro = gr.Textbox(label="How do you feel?", placeholder="I'm feeling sad and tired...")
        start_btn = gr.Button("Start Screening")
    chatbox = gr.Chatbot()
    user_input = gr.Textbox(label="Your Answer", placeholder="Type a number, or 'help 2' for clarification...")
    send_btn = gr.Button("Send")

    def start_action(intro_text):
        intro = start_session(intro_text)
        first_q = get_next_question(session_states["scale"], session_states["state"])
        if first_q:
            options_str = ", ".join([f"{k}={v}" for k,v in first_q["options"].items()])
            return [(None, intro), (None, f"{first_q['id']}. {first_q['text']}\nOptions: {options_str}")]
        return [(None, intro)]

    start_btn.click(fn=start_action, inputs=user_intro, outputs=chatbox)

    def send_action(message, history):
        bot_reply = chatbot_response(message)
        history.append((message, bot_reply))
        return history, ""

    send_btn.click(fn=send_action, inputs=[user_input, chatbox], outputs=[chatbox, user_input])
    user_input.submit(fn=send_action, inputs=[user_input, chatbox], outputs=[chatbox, user_input])

demo.launch(share=True)
