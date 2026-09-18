> **Historical/completed v1.0.0 workflow record.** The steps below document preparation of the original frozen release and are not current publication instructions for the final resubmission.

# GitHub + Zenodo publication checklist

## GitHub

1. Create a public repository named `igar-weak-label-disagreement-paper1`.
2. Replace `REPLACE_WITH_YOUR_GITHUB_USERNAME` in `CITATION.cff`.
3. Upload all contents of this release directory to the repository root.
4. Confirm that the raw IGAR dataset is not present.
5. Commit the release contents.
6. Do not change files inside `canonical_archive/`.
7. Tag the commit as `v1.0.0`.

## Zenodo

1. Sign in to Zenodo and link your GitHub account.
2. Open the Zenodo GitHub integration page and enable the repository.
3. In GitHub, create Release `v1.0.0`.
4. Wait for Zenodo to ingest the release.
5. Open the Zenodo record and copy its DOI.
6. Add the DOI to the manuscript Code availability statement and cover letter.
7. Optionally update the GitHub README with the DOI badge after Zenodo has minted it.

## Historical manuscript wording

Code availability:

> The code, frozen analysis artifacts, and reproducibility materials supporting this study are publicly available in the archived software release: **[ZENODO DOI]**. The archived release corresponds to the frozen analyses reported in the manuscript. The IGAR dataset is not redistributed in the code archive and remains available from Mendeley Data, Version 3, DOI: 10.17632/7zryc6k76z.3.

## Do not

- regenerate the frozen 150,000-review RQ4 cohort;
- rerun training merely for repository preparation;
- replace exact historical source extracts with reconstructed code;
- redistribute the raw IGAR dataset;
- describe weak-label disagreement as verified label error.
