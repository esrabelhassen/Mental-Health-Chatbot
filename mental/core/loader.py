import json
import os

SCALES_PATH = os.path.join(os.path.dirname(__file__), "..", "scales")

def load_scale(scale_name):
    filepath = os.path.join(SCALES_PATH, f"{scale_name}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
