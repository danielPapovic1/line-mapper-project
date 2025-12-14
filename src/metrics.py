def score_mapping(predicted, truth):
    """Return (correct, total) counts by comparing predicted mappings to truth."""
    correct = 0
    total = 0

    for old_line, true_new in truth.items():
        total += 1
        pred_new = predicted.get(old_line)
        if pred_new == true_new:
            correct += 1

    return correct, total


def accuracy_percent(correct, total):
    if total == 0:
        return 0.0
    return (correct / total) * 100.0
