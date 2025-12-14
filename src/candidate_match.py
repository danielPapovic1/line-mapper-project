import sys

from preprocess import preprocess_file
from unchanged_detect import detect_unchanged
from utils import simhash, hamming_distance, combined_similarity


def make_record_dict(records):
    """Return a quick lookup from line number to the record dict."""
    d = {}
    for record in records:
        d[record["line_no"]] = record
    return d


def get_candidate_sets(unmatched_old, unmatched_new, k=15):
    """
    Build top-k candidate lists for each unmatched old line using SimHash
    fingerprints and Hamming distance comparisons.
    """
    old_fps = []
    for record in unmatched_old:
        old_fps.append((record["line_no"], simhash(record["norm"])))

    new_fps = []
    for record in unmatched_new:
        new_fps.append((record["line_no"], simhash(record["norm"])))

    candidates = {}

    for old_ln, old_fp in old_fps:
        distances = []
        for new_ln, new_fp in new_fps:
            dist = hamming_distance(old_fp, new_fp)
            distances.append((dist, new_ln))

        distances.sort(key=lambda pair: pair[0])
        top = []
        for _, new_ln in distances[:k]:
            top.append(new_ln)

        candidates[old_ln] = top

    return candidates


def resolve_best_matches(unmatched_old, unmatched_new, candidates, threshold=0.5):
    """
    Score each candidate pair using combined similarity and greedily assign
    best matches so each new line is used at most once. Anything below the
    threshold is marked deleted (-1).
    """
    old_dict = make_record_dict(unmatched_old)
    new_dict = make_record_dict(unmatched_new)

    scored_pairs = []

    for old_ln, new_list in candidates.items():
        old_text = old_dict.get(old_ln, {}).get("norm", "")
        for new_ln in new_list:
            if new_ln not in new_dict:
                continue
            new_text = new_dict[new_ln]["norm"]
            score = combined_similarity(old_text, new_text)
            if score >= threshold:
                scored_pairs.append((score, old_ln, new_ln))

    scored_pairs.sort(key=lambda triple: triple[0], reverse=True)

    match_map = {}
    match_scores = {}
    used_new = set()

    for score, old_ln, new_ln in scored_pairs:
        if old_ln in match_map:
            continue
        if new_ln in used_new:
            continue
        match_map[old_ln] = new_ln
        match_scores[old_ln] = score
        used_new.add(new_ln)

    for record in unmatched_old:
        old_ln = record["line_no"]
        if old_ln not in match_map:
            match_map[old_ln] = -1
            match_scores[old_ln] = 0.0

    return match_map, match_scores


def print_some_candidates(candidates, limit=5):
    """Print a subset of candidate line lists for manual inspection."""
    count = 0
    for old_ln in sorted(candidates.keys()):
        print(str(old_ln) + " -> " + str(candidates[old_ln][:10]))
        count += 1
        if count >= limit:
            break


def print_some_matches(match_map, match_scores, limit=15):
    """Print a subset of resolved matches with their scores."""
    shown = 0
    for old_ln in sorted(match_map.keys()):
        new_ln = match_map[old_ln]
        score = match_scores.get(old_ln, 0.0)
        print(str(old_ln) + " -> " + str(new_ln) + "  score=" + str(round(score, 3)))
        shown += 1
        if shown >= limit:
            break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python candidate_match.py <old_file> <new_file>")
        raise SystemExit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    old_records = preprocess_file(old_path)
    new_records = preprocess_file(new_path)

    unchanged_map, unmatched_old, unmatched_new = detect_unchanged(old_records, new_records)

    print("Unchanged matches:", len(unchanged_map))
    print("Unmatched old:", len(unmatched_old))
    print("Unmatched new:", len(unmatched_new))

    candidates = get_candidate_sets(unmatched_old, unmatched_new, k=15)

    print("\nSample candidate lists (old -> [new,...]):")
    print_some_candidates(candidates, limit=5)

    match_map, match_scores = resolve_best_matches(unmatched_old, unmatched_new, candidates, threshold=0.5)

    deleted_count = 0
    matched_count = 0
    for old_ln in match_map:
        if match_map[old_ln] == -1:
            deleted_count += 1
        else:
            matched_count += 1

    print("\nMatched:", matched_count)
    print("Deleted:", deleted_count)

    print("\nSample final matches (old -> new):")
    print_some_matches(match_map, match_scores, limit=15)
