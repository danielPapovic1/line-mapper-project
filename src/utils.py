"""Utility helpers shared across preprocessing steps."""
import re
import hashlib
import math
from collections import Counter
import xml.etree.ElementTree as ET
import os

_ws_re = re.compile(r"\s+")


def read_file_lines(path):
    """
    Return all lines from a file without newline characters.
    Empty lines are preserved so downstream line numbers stay stable.
    """
    with open(path, "r", encoding="utf8", errors="ignore") as handle:
        return [line.rstrip("\n") for line in handle]


def collapse_whitespace(value):
    """Collapse any whitespace run into a single space and trim the ends."""
    return _ws_re.sub(" ", value).strip()


def is_blank(value):
    """True if the string contains only whitespace characters."""
    return value.strip() == ""


def filter_records(records, keep_skip=False):
    """
    Either return records as-is or drop entries flagged as skip=True.
    Step 2 uses this so blank/comment-only lines do not dominate the diff.
    """
    if keep_skip:
        return records
    return [record for record in records if not record["skip"]]


def get_norm_list(records):
    """Pull out the normalized strings from each record for quick comparisons."""
    return [record["norm"] for record in records]



_word_re = re.compile(r"\w+")


def tokenize(text):
    """Return lowercase word tokens for use in similarity measurements."""
    return _word_re.findall(text.lower())

def simhash(text):
    """
    Build a 64-bit SimHash fingerprint from the normalized text tokens.
    Each bit stores whether ones or zeros were more common in that position.
    """
    tokens = tokenize(text)
    if not tokens:
        return 0

    bit_scores = [0] * 64
    for token in tokens:
        # Use the first 64 bits of the MD5 digest for a deterministic token hash.
        digest = hashlib.md5(token.encode("utf8")).hexdigest()
        value = int(digest[:16], 16)
        for bit_index in range(64):
            mask = 1 << bit_index
            if value & mask:
                bit_scores[bit_index] += 1
            else:
                bit_scores[bit_index] -= 1

    fingerprint = 0
    for bit_index, score in enumerate(bit_scores):
        if score > 0:
            fingerprint |= 1 << bit_index
    return fingerprint


def hamming_distance(a, b):
    """Count differing bits between two SimHash fingerprints."""
    value = a ^ b
    distance = 0
    while value:
        value &= value - 1
        distance += 1
    return distance


def levenshtein_similarity(a, b):
    """Return a 0-1 score based on normalized Levenshtein edit distance."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    len_a = len(a)
    len_b = len(b)
    previous = list(range(len_b + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            replace = previous[j - 1] + cost
            delete = previous[j] + 1
            insert = current[-1] + 1
            current.append(min(replace, delete, insert))
        previous = current

    distance = previous[-1]
    max_len = max(len_a, len_b)
    return 1.0 - (distance / max_len)


def cosine_similarity(a, b):
    """Return cosine similarity of token frequency vectors for two strings."""
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0

    counts_a = Counter(tokens_a)
    counts_b = Counter(tokens_b)

    common = set(counts_a.keys()) & set(counts_b.keys())
    dot = sum(counts_a[token] * counts_b[token] for token in common)

    magnitude_a = math.sqrt(sum(value * value for value in counts_a.values()))
    magnitude_b = math.sqrt(sum(value * value for value in counts_b.values()))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot / (magnitude_a * magnitude_b)


def combined_similarity(a, b):
    """Weighted mix of edit-distance and cosine similarity for Step 4 scoring."""
    return 0.6 * levenshtein_similarity(a, b) + 0.4 * cosine_similarity(a, b)


def join_norm_lines(parts):
    """Concatenate normalized line fragments into one string for split scoring."""
    return " ".join(parts).strip()



def parse_truth_xml(xml_path):
    """
    Load the truth mapping from the final VERSION block of a provided XML file.
    Returns a dictionary of {old_line: new_line}; -1 values indicate deletions.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    versions = root.findall(".//VERSION")
    if not versions:
        return {}

    version = versions[-1]
    mapping = {}
    for loc in version.findall("LOCATION"):
        old_line = int(loc.attrib["ORIG"])
        new_line = int(loc.attrib["NEW"])
        mapping[old_line] = new_line
    return mapping

def save_prediction_xml(name, mapping, split_map, out_path):
    folder = os.path.dirname(out_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    test = ET.Element("TEST")
    test.set("NAME", str(name))

    version = ET.SubElement(test, "VERSION")
    version.set("NUMBER", "1")
    version.set("CHECKED", "TRUE")

    for old_ln in sorted(mapping.keys()):
        loc = ET.SubElement(version, "LOCATION")
        loc.set("ORIG", str(old_ln))
        loc.set("NEW", str(mapping[old_ln]))

    if split_map and len(split_map) > 0:
        splits = ET.SubElement(test, "SPLITS")
        for old_ln in sorted(split_map.keys()):
            s = ET.SubElement(splits, "SPLIT")
            s.set("ORIG", str(old_ln))
            s.set("NEW", ",".join([str(x) for x in split_map[old_ln]]))

    tree = ET.ElementTree(test)
    tree.write(out_path, encoding="utf8", xml_declaration=True)
