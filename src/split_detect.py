import sys

from preprocess import preprocess_file
from unchanged_detect import detect_unchanged
from candidate_match import get_candidate_sets, resolve_best_matches
from utils import combined_similarity, join_norm_lines


def detect_splits(unmatched_old, unmatched_new, match_map, threshold_gain=0.02, max_extra=4):
    """Find old lines that match better when adjoining new lines are combined."""
    old_dict = {}
    for record in unmatched_old:
        old_dict[record["line_no"]] = record

    new_dict = {}
    for record in unmatched_new:
        new_dict[record["line_no"]] = record

    new_line_nos = sorted(record["line_no"] for record in unmatched_new)

    used_new = set()
    for old_ln, mapped_ln in match_map.items():
        if mapped_ln != -1:
            used_new.add(mapped_ln)

    final_map = {}
    for old_ln, mapped_ln in match_map.items():
        final_map[old_ln] = mapped_ln

    split_map = {}

    old_keys = list(match_map.keys())
    old_keys.sort()

    for old_ln in old_keys:
        start_new_ln = match_map[old_ln]
        if start_new_ln == -1:
            continue
        if old_ln not in old_dict:
            continue
        if start_new_ln not in new_dict:
            continue

        if start_new_ln not in new_line_nos:
            continue

        old_text = old_dict[old_ln]["norm"]
        parts = [new_dict[start_new_ln]["norm"]]
        original_score = combined_similarity(old_text, join_norm_lines(parts))

        best_score = original_score
        best_list = [start_new_ln]

        try:
            start_index = new_line_nos.index(start_new_ln)
        except ValueError:
            continue

        current_list = [start_new_ln]
        extra_added = 0
        next_index = start_index + 1

        while extra_added < max_extra and next_index < len(new_line_nos):
            next_ln = new_line_nos[next_index]
            next_index += 1

            if next_ln in used_new:
                continue
            if next_ln not in new_dict:
                continue

            parts.append(new_dict[next_ln]["norm"])
            candidate_text = join_norm_lines(parts)
            score = combined_similarity(old_text, candidate_text)

            if score > best_score:
                best_score = score
                current_list.append(next_ln)
                best_list = list(current_list)
                extra_added += 1
            else:
                parts.pop()
                break

        if len(best_list) > 1 and best_score >= original_score + threshold_gain:
            split_map[old_ln] = best_list
            for ln in best_list[1:]:
                used_new.add(ln)

    return final_map, split_map


def print_some_splits(split_map, limit=10):
    keys = list(split_map.keys())
    keys.sort()
    shown = 0
    for old_ln in keys:
        print(str(old_ln) + " -> " + str(split_map[old_ln]))
        shown += 1
        if shown >= limit:
            break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python split_detect.py <old_file> <new_file>")
        raise SystemExit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    old_records = preprocess_file(old_path)
    new_records = preprocess_file(new_path)

    unchanged_map, unmatched_old, unmatched_new = detect_unchanged(old_records, new_records)

    candidates = get_candidate_sets(unmatched_old, unmatched_new, k=15)
    match_map, match_scores = resolve_best_matches(unmatched_old, unmatched_new, candidates, threshold=0.5)

    final_map, split_map = detect_splits(unmatched_old, unmatched_new, match_map, threshold_gain=0.02, max_extra=4)

    print("Splits found:", len(split_map))
    if len(split_map) > 0:
        print("\nSample splits (old -> [new,...]):")
        print_some_splits(split_map, limit=10)
