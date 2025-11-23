from core.loader import load_scale
from core.state import init_state, get_next_question, record_response
from core.scoring import calculate_score, interpret_score

# Load PHQ-9 as example
scale_data = load_scale("PHQ-9")
state = init_state("PHQ-9")

# Simulate answering questions
while True:
    q = get_next_question(scale_data, state)
    if not q:
        break
    print(f"{q['id']}: {q['text']}")
    print("Options:", q["options"])
    ans = int(input("Your answer (0-3): "))
    record_response(state, q["id"], ans)

# Calculate score
score = calculate_score(scale_data, state["responses"])
interpretation = interpret_score(scale_data, score)

print("\n--- Results ---")
print("Responses:", state["responses"])
print("Score:", score)
print("Interpretation:", interpretation)
