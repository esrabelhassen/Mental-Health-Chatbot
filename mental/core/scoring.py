def calculate_score(scale_data, responses):
    method = scale_data["scoring"]["method"]

    if method == "sum":
        total = 0
        reverse_items = scale_data["scoring"].get("reverse_scored", [])
        for q_id, val in responses.items():
            if q_id in reverse_items:
                max_val = max(int(k) for k in scale_data["questions"][0]["options"].keys())
                total += max_val - val  # invert score
            else:
                total += val
        return total

    elif method == "subscales":
        results = {}
        for subscale, config in scale_data["scoring"]["subscales"].items():
            q_ids = config["questions"]
            score = 0
            for q in q_ids:
                if q in responses:
                    val = responses[q]
                    # Handle reverse scoring if needed
                    reverse_items = config.get("reverse_scored", [])
                    if q in reverse_items:
                        max_val = max(int(k) for k in scale_data["questions"][0]["options"].keys())
                        score += max_val - val
                    else:
                        score += val
            results[subscale] = score
        return results

    else:
        raise ValueError(f"Unknown scoring method: {method}")


def interpret_score(scale_data, score):
    method = scale_data["scoring"]["method"]

    if method == "sum":
        for rule in scale_data["scoring"]["interpretation"]:
            min_v = rule.get("min", float("-inf"))
            max_v = rule.get("max", float("inf"))
            if min_v <= score <= max_v:
                return rule["level"]

    elif method == "subscales":
        interpretations = {}
        for subscale, config in scale_data["scoring"]["subscales"].items():
            sub_score = score[subscale]
            for rule in config["interpretation"]:
                min_v = rule.get("min", float("-inf"))
                max_v = rule.get("max", float("inf"))
                if min_v <= sub_score <= max_v:
                    interpretations[subscale] = rule["level"]
                    break
        return interpretations
