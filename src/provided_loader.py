import os

from utils import parse_truth_xml


def split_base_and_version(filename):
    """Return base name and version number (if present) from a dataset filename."""
    name = filename
    if "." in name:
        name = name.rsplit(".", 1)[0]
    if "_" not in name:
        return name, None
    base, ver = name.rsplit("_", 1)
    if ver.isdigit():
        return base, int(ver)
    return name, None


def group_versions(folder_path):
    """Group all versioned files in a folder by their base name."""
    groups = {}
    for f in os.listdir(folder_path):
        full = os.path.join(folder_path, f)
        if not os.path.isfile(full):
            continue
        base, ver = split_base_and_version(f)
        if ver is None:
            continue
        if base not in groups:
            groups[base] = []
        groups[base].append((ver, full, f))
    return groups


def load_provided_pairs():
    """
    Build the list of provided test pairs with paths and truth maps.
    Picks the lowest version as old, highest as new, and parses the last
    VERSION block from the matching truth XML.
    """
    here = os.path.dirname(__file__)
    base = os.path.join(here, "..", "datasets", "provided")
    old_dir = os.path.join(base, "old")
    new_dir = os.path.join(base, "new")
    truth_dir = os.path.join(base, "truth")

    old_groups = group_versions(old_dir)
    new_groups = group_versions(new_dir)

    truth_files = {}
    for f in os.listdir(truth_dir):
        full = os.path.join(truth_dir, f)
        if os.path.isfile(full) and f.lower().endswith(".xml"):
            key = f.rsplit(".", 1)[0]
            truth_files[key] = full

    pairs = []

    for base_name in sorted(old_groups.keys()):
        if base_name not in new_groups:
            continue

        old_versions = old_groups[base_name]
        new_versions = new_groups[base_name]

        old_versions.sort(key=lambda x: x[0])
        new_versions.sort(key=lambda x: x[0])

        old_ver, old_path, old_file = old_versions[0]
        new_ver, new_path, new_file = new_versions[-1]

        truth_path = None
        if base_name in truth_files:
            truth_path = truth_files[base_name]
        else:
            # Some truth files include prefixes like TEST5; fall back to suffix match.
            found = None
            for key in truth_files:
                if key.upper().endswith(base_name.upper()):
                    found = truth_files[key]
                    break
            truth_path = found

        if truth_path is None:
            continue

        truth = parse_truth_xml(truth_path)

        pairs.append({
            "name": base_name,
            "old_path": old_path,
            "new_path": new_path,
            "truth": truth
        })

    return pairs


if __name__ == "__main__":
    pairs = load_provided_pairs()
    print("Pairs found:", len(pairs))
    for p in pairs:
        old_file = os.path.basename(p["old_path"])
        new_file = os.path.basename(p["new_path"])
        print(p["name"], old_file, "->", new_file, "truth_lines=", len(p["truth"]))
