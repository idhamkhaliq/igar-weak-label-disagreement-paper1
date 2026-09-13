# Notebook Provenance Reconciliation

**Status:** CLOSED / PASS — STRICT FORENSIC

The whole Colab notebook SHA changed during later
reproducibility-packaging execution.

This notebook-level drift does not define scientific
source-code identity.

A strict historical-source audit established that:

- Cell 60A–60E remained unchanged;
- row_id is constructed in historical cell 26;
- duplicate_group_id is constructed in historical cell 26;
- required historical source/dependency cells are 5, 25, 26;
- later packaging Cell 104 was a false-positive source hit;
- Cell 104 is excluded from scientific provenance.

Authoritative scientific source identity:

```text
COMPONENT_LEVEL_SHA256
bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530
```

No scientific result was changed or recomputed.
Training was not rerun.
No new statistical tests were performed.
