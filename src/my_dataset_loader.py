import os

from utils import parse_truth_xml


def _base_name(filename):
    """Return the dataset base name (Example01) without version suffix or extension."""
    name = filename
    if "." in name:
        name = name.rsplit(".", 1)[0]
    if "_" in name:
        base, suffix = name.rsplit("_", 1)
        if suffix.isdigit():
            return base
    return name


def load_my_dataset_pairs():
    """
    Load my_dataset pairs by matching identical filenames in old/new folders
    and grabbing the corresponding truth XML with the same base name.
    """
    here = os.path.dirname(__file__)
    base = os.path.join(here, "..", "datasets", "my_dataset")
    old_dir = os.path.join(base, "old")
    new_dir = os.path.join(base, "new")
    truth_dir = os.path.join(base, "truth")

    new_files = {}
    # Map base names to new file paths so Example01_1 finds Example01_2.
    for f in os.listdir(new_dir):
        full = os.path.join(new_dir, f)
        if os.path.isfile(full):
            base = _base_name(f)
            new_files[base] = full

    truth_files = {}
    for f in os.listdir(truth_dir):
        full = os.path.join(truth_dir, f)
        if os.path.isfile(full) and f.lower().endswith(".xml"):
            key = f.rsplit(".", 1)[0]
            truth_files[key] = full

    pairs = []

    for old_f in sorted(os.listdir(old_dir)):
        old_path = os.path.join(old_dir, old_f)
        if not os.path.isfile(old_path):
            continue

        base = _base_name(old_f)
        if base not in new_files:
            continue
        if base not in truth_files:
            continue

        new_path = new_files[base]
        truth_path = truth_files[base]
        truth = parse_truth_xml(truth_path)

        pairs.append({
            "name": base,
            "old_path": old_path,
            "new_path": new_path,
            "truth": truth
        })

    return pairs


if __name__ == "__main__":
    pairs = load_my_dataset_pairs()
    print("Pairs found:", len(pairs))
    for p in pairs:
        old_file = os.path.basename(p["old_path"])
        new_file = os.path.basename(p["new_path"])
        print(p["name"], old_file, "->", new_file, "truth_lines=", len(p["truth"]))
