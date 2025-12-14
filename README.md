# Line Mapping Project

This repository implements a five-step pipeline for mapping lines between versions of source files. It supports two datasets:

- **Provided dataset** – instructor-supplied test cases.
- **My dataset** – custom dataset located in `datasets/my_dataset/`.

The project cleans lines (Step 1), detects unchanged lines (Step 2), generates candidates (Step 3), resolves matches (Step 4), and detects line splits (Step 5). It includes loaders, metrics, evaluation, and XML output utilities.

## Project Structure

- `src/preprocess.py` – Step 1: normalization and record creation.
- `src/unchanged_detect.py` – Step 2: exact match detection via difflib.
- `src/candidate_match.py` – Steps 3 & 4: SimHash candidate generation and similarity scoring.
- `src/split_detect.py` – Step 5: optional multi-line detection for splits.
- `src/provided_loader.py` – dataset loader for `datasets/provided`.
- `src/my_dataset_loader.py` – dataset loader for `datasets/my_dataset`.
- `src/metrics.py` – scoring helpers for evaluation.
- `src/evaluate.py` – runs the full pipeline and reports accuracy.
- `src/main.py` – orchestrates Steps 1–5 and writes XML predictions.
- `src/utils.py` – shared helper functions (I/O, normalization, similarity, XML).

All scripts assume you run from inside `src/`.

## Requirements

- Python 3.10+
- No third-party dependencies (standard library only).

## Running the Pipeline

`main.py` produces XML predictions for every pair in a dataset. Outputs land in `../results/<dataset>_predictions/`.

```bash
cd src

# Provided dataset
python main.py --dataset provided

# Custom dataset
python main.py --dataset my_dataset
```

Each run prints progress and writes `<pair-name>.xml` files containing `<LOCATION ORIG="x" NEW="y"/>` elements plus optional split info.

## Evaluating Accuracy

`evaluate.py` recomputes predictions and compares them to truth XML using `metrics.py`.

```bash
cd src

# Evaluate on provided cases
python evaluate.py --dataset provided

# Evaluate on my dataset
python evaluate.py --dataset my_dataset
```

Output includes per-file accuracy (`correct/total (percent)`) and an overall summary.

## How the Pipeline Works

1. **Preprocessing** – `preprocess_file()` reads each file, strips whitespace, normalizes case, and records original line numbers.
2. **Unchanged Detection** – `detect_unchanged()` runs a difflib sequence match on normalized lines (excluding skip lines) to capture exact matches and produce `unmatched_old`/`unmatched_new`.
3. **Candidate Generation** – `get_candidate_sets()` fingerprints each unmatched line with SimHash and keeps the top `k` closest new lines per old line.
4. **Best Match Resolution** – `resolve_best_matches()` compares candidates with blended Levenshtein/cosine similarity, greedy assigns one-to-one matches, and marks the rest as deletions (`-1`).
5. **Split Detection** – `detect_splits()` extends matched new lines with adjacent unmatched lines when the combined similarity improves, recording multi-line splits.

Finally, `main.py` merges unchanged and matched mappings, formats them into XML, and saves them per dataset.

## Dataset Loaders

- **Provided dataset** – Files live under `datasets/provided/{old,new,truth}/`. Loader groups versions by base name, picks the lowest version as old and highest as new, and parses the last `<VERSION>` in the truth XML.
- **My dataset** – Files follow `ExampleXX_1.java`/`ExampleXX_2.java`. Loader matches by base name (e.g., `Example01`) and reads `truth/Example01.xml`.

Both loaders return a list of dictionaries with `name`, `old_path`, `new_path`, and `truth` entries.

## Metrics & Evaluation

- `metrics.score_mapping(predicted, truth)` counts how many truth-mapped lines were predicted correctly (missing lines count as incorrect).
- `metrics.accuracy_percent(correct, total)` converts counts into a percentage.
- `evaluate.py` orchestrates loader selection, pipeline execution, and metric reporting.

## Results Format

Prediction XML resembles the truth format:

```xml
<TEST NAME="Example01">
  <VERSION NUMBER="1" CHECKED="TRUE">
    <LOCATION ORIG="1" NEW="1"/>
    <LOCATION ORIG="2" NEW="2"/>
    <LOCATION ORIG="3" NEW="-1"/>
    ...
  </VERSION>
  <SPLITS>
    <SPLIT ORIG="15" NEW="20,21"/>
  </SPLITS>
</TEST>
```

`<SPLITS>` is optional and records Step 5 findings, but evaluation relies only on `<LOCATION>` entries.

## Testing & Verification

- Run `python my_dataset_loader.py` or `python provided_loader.py` to list detected pairs.
- Use `python main.py --dataset <name>` to regenerate prediction XML.
- Run `python evaluate.py --dataset <name>` to check accuracy.

## Contributing / Extending

- Additional datasets should follow a consistent naming convention and provide truth XML; implement a dedicated loader similar to the existing ones.
- Adjust Step 3/4 parameters (`k`, threshold) inside `candidate_match.py` if needed for other languages/sizes.
- Extend `split_detect.py` if you need more elaborate split detection.

## License 

MIT License

Copyright (c) 2025 University of Windsor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
