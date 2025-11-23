def init_state(scale_name):
    return {
        "current_scale": scale_name,
        "question_index": 0,
        "responses": {}
    }

def get_next_question(scale_data, state):
    if state["question_index"] < len(scale_data["questions"]):
        return scale_data["questions"][state["question_index"]]
    return None  # No more questions

def record_response(state, question_id, answer_value):
    state["responses"][question_id] = answer_value
    state["question_index"] += 1
