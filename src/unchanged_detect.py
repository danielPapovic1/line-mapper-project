import sys
import difflib

from preprocess import preprocess_file
from utils import filter_records, get_norm_list


def detect_unchanged(old_records, new_records):
    """
    Find unchanged lines using normalized text from Step 1.
    Only records with skip=False participate so blank/comment lines do not
    create inflated matches.
    """
    old_work = filter_records(old_records, keep_skip=False)
    new_work = filter_records(new_records, keep_skip=False)

    old_norms = get_norm_list(old_work)
    new_norms = get_norm_list(new_work)

    # difflib respects relative order, giving us exact matches quickly.
    matcher = difflib.SequenceMatcher(None, old_norms, new_norms)

    unchanged_map = {}

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            length = i2 - i1
            for offset in range(length):
                old_line_no = old_work[i1 + offset]["line_no"]
                new_line_no = new_work[j1 + offset]["line_no"]
                unchanged_map[old_line_no] = new_line_no

    matched_old_line_nos = set(unchanged_map.keys())
    matched_new_line_nos = set(unchanged_map.values())

    unmatched_old = []
    for record in old_work:
        if record["line_no"] not in matched_old_line_nos:
            unmatched_old.append(record)

    unmatched_new = []
    for record in new_work:
        if record["line_no"] not in matched_new_line_nos:
            unmatched_new.append(record)

    return unchanged_map, unmatched_old, unmatched_new


def print_sample_mappings(unchanged_map, limit=15):
    """Display a small sample of unchanged mappings for quick inspection."""
    count = 0
    for old_ln in sorted(unchanged_map.keys()):
        print(str(old_ln) + " -> " + str(unchanged_map[old_ln]))
        count += 1
        if count >= limit:
            break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python unchanged_detect.py <old_file> <new_file>")
        raise SystemExit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    old_records = preprocess_file(old_path)
    new_records = preprocess_file(new_path)

    unchanged_map, unmatched_old, unmatched_new = detect_unchanged(old_records, new_records)

    print("Unchanged matches:", len(unchanged_map))
    print("Unmatched old:", len(unmatched_old))
    print("Unmatched new:", len(unmatched_new))

    print("\nSample unchanged mappings (old -> new):")
    print_sample_mappings(unchanged_map, limit=15)
