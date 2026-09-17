# GitHub + Zenodo publication guide — v1.1.0

This staging package is an **overlay**, not a replacement repository. Apply it to the current `main` branch only after verifying that the local clone still matches the audited v1.0.0 baseline.

## Safety rules

- Do not force-push.
- Do not delete or retag `v1.0.0`.
- Do not edit the historical GitHub Release `v1.0.0` to make it describe P1R-11.
- Do not change files inside `canonical_archive/`.
- Do not move P1R-11 into the original frozen `reproducibility/` tree.
- Do not upload raw IGAR data or the preserved probability Parquet inputs as new public data unless separately intended and licensed.

## Recommended local workflow

### 1. Clone the public repository

```bash
git clone https://github.com/idhamkhaliq/igar-weak-label-disagreement-paper1.git
cd igar-weak-label-disagreement-paper1
```

### 2. Confirm the audited baseline

```bash
git checkout main
git pull --ff-only
git rev-parse HEAD
```

Expected pre-update commit from the 2026-09-17 audit:

```text
795a5e187e5aef15f856d02ca01ce42e1e68e319
```

Also verify:

```bash
git rev-parse v1.0.0
```

Expected:

```text
795a5e187e5aef15f856d02ca01ce42e1e68e319
```

If `main` has moved, stop and inspect the intervening commits before applying this overlay.

### 3. Verify the original canonical archive before changes

```bash
sha256sum canonical_archive/IGAR-Paper1-Reproducibility_STRICT_FINAL.zip
```

Expected:

```text
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

### 4. Apply this staging overlay

From any directory, run:

```bash
python /path/to/IGAR_Paper1_GitHub_v1.1.0_READY/tools/apply_v1_1_overlay.py \
  --repo /path/to/igar-weak-label-disagreement-paper1 \
  --overlay /path/to/IGAR_Paper1_GitHub_v1.1.0_READY
```

The script does **not** commit, tag, push, or publish anything.

### 5. Inspect the Git diff

```bash
cd /path/to/igar-weak-label-disagreement-paper1
git status
git diff -- README.md PUBLIC_RELEASE_STATUS.json CITATION.cff .zenodo.json back_matter/CODE_AVAILABILITY_AFTER_ZENODO.txt
```

Confirm that:

- `canonical_archive/` is unchanged;
- the original `reproducibility/` tree is unchanged;
- `revision_addenda/` is new;
- root metadata changes from v1.0.0 to v1.1.0;
- `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` preserves the old manifest;
- the new current manifest is `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`.

### 6. Run verification

```bash
python tools/verify_v1_1_repository.py --repo .
```

Then, from the P1R-11 folder:

```bash
cd revision_addenda/P1R11_v0.6_CLOSED
sha256sum -c manifests/SHA256SUMS.txt
python tools/verify_addendum.py
cd ../..
```

Expected P1R-11 package ZIP SHA-256:

```text
ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b
```

### 7. Commit

Recommended commit message:

```text
Archive closed P1R-11 revision-stage reproducibility addendum
```

Commands:

```bash
git add README.md PUBLIC_RELEASE_STATUS.json CITATION.cff .zenodo.json \
  RELEASE_NOTES_v1.1.0.md GITHUB_ZENODO_RELEASE_GUIDE_v1.1.0.md \
  MANIFEST_STRATEGY.md REPO_BASELINE_AUDIT.json \
  MANIFEST_PUBLIC_RELEASE.sha256 MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256 \
  MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256 back_matter/CODE_AVAILABILITY_AFTER_ZENODO.txt \
  revision_addenda tools/verify_v1_1_repository.py

git commit -m "Archive closed P1R-11 revision-stage reproducibility addendum"
```

### 8. Push `main`

```bash
git push origin main
```

### 9. Tag the exact commit

```bash
git tag -a v1.1.0 -m "IGAR Paper 1 reproducibility v1.1.0 — P1R-11 revision addendum"
git push origin v1.1.0
```

Before publishing the GitHub release, verify:

```bash
git rev-parse HEAD
git rev-parse v1.1.0
```

They must be identical.

### 10. Create GitHub Release `v1.1.0`

Use:

- Tag: `v1.1.0`
- Title: `IGAR Paper 1 Reproducibility Package v1.1.0 — P1R-11 Revision Addendum`
- Body: paste `RELEASE_NOTES_v1.1.0.md`
- Prerelease: **off**

Optional but recommended release asset:

`revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip`

If attached, download the release asset again and verify its SHA-256 equals `ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`.

### 11. Zenodo

If GitHub–Zenodo integration is enabled, wait for Zenodo to ingest `v1.1.0`. Verify title, creators, version `1.1.0`, license, and description. Zenodo may mint a new version-specific DOI while preserving the concept DOI lineage.

Do not edit the manuscript to a newly minted version DOI unless you intentionally want the paper to cite that version-specific DOI. The already audited manuscript citation can remain unchanged if it uses the stable concept DOI.

### 12. Final public check

Open the public repository and confirm all of the following:

- v1.0.0 tag still resolves to the historical commit;
- v1.1.0 resolves to the new commit;
- README clearly describes the two provenance layers;
- `canonical_archive/` remains unchanged;
- `revision_addenda/P1R11_v0.6_CLOSED/` is browseable;
- the exact P1R-11 ZIP is present;
- `PUBLIC_RELEASE_STATUS.json` says repository version 1.1.0;
- `CITATION.cff` and `.zenodo.json` say 1.1.0;
- repository manifests verify;
- no raw IGAR dataset has been added.
