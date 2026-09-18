> **Historical release manifests remain immutable.** `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` and `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256` identify their tagged release snapshots. Narrative alignment on current `main` does not rewrite those historical identities.

# Manifest strategy after final-resubmission narrative alignment

The repository now has two distinct checksum purposes.

## 1. Historical tagged-release manifests

- `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` preserves the original v1.0.0 release manifest.
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256` preserves the tagged v1.1.0 release snapshot.
- `MANIFEST_PUBLIC_RELEASE.sha256` remains the historical convenience alias for the tagged v1.1.0 manifest.

These files are intentionally **not regenerated** after the final-resubmission narrative-alignment commit.

## 2. Current-main final-resubmission manifest

`MANIFEST_MAIN_FINAL_RESUBMISSION.sha256` verifies the current `main` tree after public-facing terminology and metadata were aligned to the final manuscript resubmission.

Its coverage is the repository file set on current `main`, excluding only:

- `.git/`;
- `MANIFEST_MAIN_FINAL_RESUBMISSION.sha256` itself;
- `MANIFEST_PUBLIC_RELEASE.sha256`;
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`.

The two historical v1.1.0 manifest files are excluded because they intentionally describe the tagged release snapshot rather than current `main`. The preserved `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` remains within current-main coverage.

## Verification

For current `main`:

```bash
sha256sum -c MANIFEST_MAIN_FINAL_RESUBMISSION.sha256
python tools/verify_v1_1_repository.py --repo .
```

The verifier checks exact current-main manifest coverage, all listed file hashes, the immutable scientific archive hashes, internal addendum closure, and preservation of the historical v1.1.0 manifest alias.

## Scientific immutability

The final-resubmission narrative alignment does not alter:

- `canonical_archive/`;
- the original frozen `reproducibility/` layer;
- the closed post hoc addendum package;
- machine-readable scientific outputs;
- source tables; or
- the cryptographic identities of the immutable scientific archives.
