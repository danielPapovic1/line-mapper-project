"""Step 1"""

import sys
from utils import read_file_lines, collapse_whitespace, is_blank


def normalize_line(line, *, lowercase=True, collapse_ws=True):
    """
    Produce a normalized variant of the raw line so later steps can compare
    strings without getting distracted by casing or spacing.
    """
    normalized = line.rstrip("\n").strip()

    if collapse_ws:
        normalized = collapse_whitespace(normalized)

    if lowercase:
        normalized = normalized.lower()

    return normalized


def preprocess_file(path, lowercase=True, collapse_ws=True):
    """
    Read a file and return a record per line:
    { line_no, raw, norm, skip }.
    """
    raw_lines = read_file_lines(path)
    records = []

    for line_no, raw in enumerate(raw_lines, start=1):
        norm = normalize_line(raw, lowercase=lowercase, collapse_ws=collapse_ws)
        skip = is_blank(raw)  # Blank lines are flagged but still recorded.

        records.append({
            "line_no": line_no,
            "raw": raw,
            "norm": norm,
            "skip": skip
        })

    return records


def preprocess_pair(old_path, new_path, lowercase=True, collapse_ws=True):
    """Convenience helper that preprocesses both old and new files."""
    old_records = preprocess_file(old_path, lowercase=lowercase, collapse_ws=collapse_ws)
    new_records = preprocess_file(new_path, lowercase=lowercase, collapse_ws=collapse_ws)
    return old_records, new_records


def print_preview(label, path, records, show=15):
    """Print a quick sample of normalized records for debugging and tests."""
    print(label + ": " + path)
    for record in records[:show]:
        print(
            str(record["line_no"]).rjust(5),
            "skip=" + str(record["skip"]),
            "norm=" + record["norm"]
        )

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage:")
        print("  python src/preprocess.py <file>")
        print("  python src/preprocess.py <old_file> <new_file>")
        raise SystemExit(1)

    if len(sys.argv) == 2:
        recs = preprocess_file(sys.argv[1])
        print_preview("FILE", sys.argv[1], recs)
    else:
        old_recs, new_recs = preprocess_pair(sys.argv[1], sys.argv[2])
        print_preview("OLD", sys.argv[1], old_recs)
        print_preview("NEW", sys.argv[2], new_recs)
"""Used for testing to run step directly. Pattern will follow with the next steps."""