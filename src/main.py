import argparse
import os

from provided_loader import load_provided_pairs
from my_dataset_loader import load_my_dataset_pairs
from preprocess import preprocess_file
from unchanged_detect import detect_unchanged
from candidate_match import get_candidate_sets, resolve_best_matches
from split_detect import detect_splits
from utils import save_prediction_xml


def run_pipeline(old_path, new_path):
    old_records = preprocess_file(old_path)
    new_records = preprocess_file(new_path)

    unchanged_map, unmatched_old, unmatched_new = detect_unchanged(old_records, new_records)

    candidates = get_candidate_sets(unmatched_old, unmatched_new, k=15)
    match_map, match_scores = resolve_best_matches(unmatched_old, unmatched_new, candidates, threshold=0.5)

    final_map, split_map = detect_splits(unmatched_old, unmatched_new, match_map, threshold_gain=0.02, max_extra=4)

    merged_map = {}
    for k in unchanged_map:
        merged_map[k] = unchanged_map[k]
    for k in final_map:
        merged_map[k] = final_map[k]

    return merged_map, split_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["provided", "my_dataset"], required=True)
    args = parser.parse_args()

    here = os.path.dirname(__file__)

    if args.dataset == "provided":
        print("Loading dataset: provided")
        pairs = load_provided_pairs()
        out_dir = os.path.join(here, "..", "results", "provided_predictions")
    else:
        print("Loading dataset: my_dataset")
        pairs = load_my_dataset_pairs()
        out_dir = os.path.join(here, "..", "results", "my_dataset_predictions")

    print("Pairs found:", len(pairs))

    for pair in pairs:
        name = pair["name"]
        old_path = pair["old_path"]
        new_path = pair["new_path"]

        print("Processing", name)

        mapping, split_map = run_pipeline(old_path, new_path)

        out_path = os.path.join(out_dir, name + ".xml")
        save_prediction_xml(name, mapping, split_map, out_path)

        print("Saved:", out_path)


if __name__ == "__main__":
    main()
