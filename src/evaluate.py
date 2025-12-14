import argparse

from provided_loader import load_provided_pairs
from my_dataset_loader import load_my_dataset_pairs
from preprocess import preprocess_file
from unchanged_detect import detect_unchanged
from candidate_match import get_candidate_sets, resolve_best_matches
from split_detect import detect_splits
from metrics import score_mapping, accuracy_percent


def run_pipeline(old_path, new_path):
    """Run Steps 1-5 and return the merged line mapping."""
    old_records = preprocess_file(old_path)
    new_records = preprocess_file(new_path)

    unchanged_map, unmatched_old, unmatched_new = detect_unchanged(old_records, new_records)

    candidates = get_candidate_sets(unmatched_old, unmatched_new, k=15)
    match_map, match_scores = resolve_best_matches(unmatched_old, unmatched_new, candidates, threshold=0.5)

    final_map, split_map = detect_splits(unmatched_old, unmatched_new, match_map, threshold_gain=0.02, max_extra=4)

    merged_map = {}
    for old_line, new_line in unchanged_map.items():
        merged_map[old_line] = new_line
    for old_line, new_line in final_map.items():
        merged_map[old_line] = new_line

    return merged_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["provided", "my_dataset"], required=True)
    args = parser.parse_args()

    if args.dataset == "provided":
        pairs = load_provided_pairs()
    else:
        pairs = load_my_dataset_pairs()

    print("Pairs:", len(pairs))

    overall_correct = 0
    overall_total = 0

    for pair in pairs:
        name = pair["name"]
        old_path = pair["old_path"]
        new_path = pair["new_path"]
        truth = pair["truth"]

        predicted = run_pipeline(old_path, new_path)

        correct, total = score_mapping(predicted, truth)
        overall_correct += correct
        overall_total += total

        pct = accuracy_percent(correct, total)
        print(name + ": " + str(correct) + "/" + str(total) + " (" + format(pct, ".2f") + "%)")

    overall_pct = accuracy_percent(overall_correct, overall_total)
    print("OVERALL: " + str(overall_correct) + "/" + str(overall_total) + " (" + format(overall_pct, ".2f") + "%)")


if __name__ == "__main__":
    main()
