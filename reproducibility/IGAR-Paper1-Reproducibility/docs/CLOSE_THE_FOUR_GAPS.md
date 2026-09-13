# Closing the four reproducibility gaps

The package deliberately uses a **release barrier**: it is not marked `CLOSED` until exact evidence is captured from the author's final Colab/Drive environment.

Run:

```bash
python tools/colab_close_gaps.py \
  --package-root /content/drive/MyDrive/IGAR-Paper1-Reproducibility \
  --project-root /content/drive/MyDrive/IGAR_Paper1
```

The finalizer performs four actions.

## Gap 1 — exact final training source

It recursively scans the final Drive notebooks and requires verbatim code cells containing all markers:

```text
CELL 60A
CELL 60B
CELL 60C
CELL 60D
CELL 60E
```

They are concatenated with notebook/cell provenance into:

```text
src/08_train_paired_indobert_EXACT_EXTRACT.py
```

The script refuses to declare the package closed if any marker is missing.

## Gap 2 — exact row/group-ID source

It captures verbatim notebook code cells containing `row_id` or `duplicate_group_id` together with hashing/normalization/construction evidence and requires evidence for **both** identifiers.

Output:

```text
src/04_exact_row_duplicate_id_cells.py
```

This approach is intentional: no guessed join separator or guessed hash algorithm is substituted for the actual source.

## Gap 3 — exact environment

It records the complete runtime versions, including NumPy, pandas, scikit-learn, and statsmodels, and writes full `pip freeze` output:

```text
environment/runtime-info.json
environment/pip-freeze.txt
```

## Gap 4 — data and translation provenance

Public repository provenance is already locked to IGAR Mendeley Data Version 3:

```text
DOI: 10.17632/7zryc6k76z.3
Version publication date: 2025-11-07
License: CC BY 4.0
Documented files: Rating_labeled.csv, VADER_labeled.csv
```

The data article documents the VADER file as containing the translated review and VADER outputs, so reproduction should use the dataset-provided translation/VADER fields rather than silently invoking a new translation service.

The finalizer also searches local Drive for the documented source filenames, records local paths, mtimes and SHA256 values, and **does not fabricate a historical download date** when no contemporaneous log exists.

Output:

```text
config/local_data_provenance.json
```

## Closure rule

All four conditions must pass before:

```text
manifests/REPRODUCIBILITY_STATUS.json
```

is set to:

```json
{"status": "CLOSED"}
```

Afterward run:

```bash
python tools/verify_release.py \
  --package-root /content/drive/MyDrive/IGAR-Paper1-Reproducibility
```

Expected result:

```text
REPRODUCIBILITY RELEASE: CLOSED / PASS
```
