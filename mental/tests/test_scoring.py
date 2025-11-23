from core.loader import load_scale
from core.scoring import calculate_score, interpret_score

def test_phq9():
    scale_data = load_scale("PHQ-9")
    responses = {"Q1": 2, "Q2": 3, "Q3": 1, "Q4": 0, "Q5": 1, "Q6": 2, "Q7": 0, "Q8": 1, "Q9": 0}
    score = calculate_score(scale_data, responses)
    interpretation = interpret_score(scale_data, score)
    assert isinstance(score, int)
    print("PHQ-9 test passed:", score, interpretation)
