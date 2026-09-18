> **Historical/completed manifest-generation record for tagged release v1.1.0.** The v1.1.0 manifests identify the immutable tagged release snapshot. Narrative-only alignment commits on `main` after publication do not rewrite those historical manifests and must not be interpreted as changes to the frozen computational record.

# Manifest strategy for repository v1.1.0

The original v1.0.0 root manifest was preserved before the v1.1.0 overlay was applied. A new v1.1.0 manifest was then generated for the tagged release snapshot.

## Completed sequence

1. The historical v1.0.0 root manifest was copied to `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256`.
2. The v1.1.0 overlay was applied.
3. A full-repository manifest was generated for the v1.1.0 tagged release snapshot.
4. It was saved as `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`.
5. At release time, the same content was also used as the convenience alias `MANIFEST_PUBLIC_RELEASE.sha256`.

## Self-reference rule

The v1.1.0 full-repository manifest intentionally excludes:

- `.git/`
- `MANIFEST_PUBLIC_RELEASE.sha256`
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`

It includes the preserved `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256`.

## Scope after narrative alignment

The versioned v1.1.0 manifest remains the cryptographic identity record for the **tagged v1.1.0 release snapshot**. It is not a checksum manifest for current `main` after the final-resubmission narrative alignment.

The narrative alignment changes only public-facing documentation and metadata. It does not alter:

- `canonical_archive/`;
- the original frozen `reproducibility/` layer;
- the closed post hoc addendum package;
- machine-readable scientific outputs;
- source tables; or
- the cryptographic identities of the immutable scientific archives.
