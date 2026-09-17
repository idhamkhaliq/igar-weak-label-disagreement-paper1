# Manifest strategy for repository v1.1.0

The repository's current `MANIFEST_PUBLIC_RELEASE.sha256` belongs to the historical v1.0.0 state. Updating root metadata for v1.1.0 changes several hashes, so the old manifest must be preserved rather than silently overwritten.

## Required sequence

1. Before applying this overlay, copy the existing root manifest:

   ```bash
   cp MANIFEST_PUBLIC_RELEASE.sha256 MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256
   ```

2. Apply the v1.1.0 overlay.
3. Generate a new full-repository manifest after all files are in place.
4. Save it as `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`.
5. Copy the same content to the convenience alias `MANIFEST_PUBLIC_RELEASE.sha256`.

## Self-reference rule

The v1.1.0 full-repository manifest intentionally excludes:

- `.git/`
- `MANIFEST_PUBLIC_RELEASE.sha256`
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`

It **does include** the preserved `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256`.

This avoids a self-referential checksum cycle while retaining the historical v1.0.0 manifest as an auditable object in v1.1.0.

## Recommended automation

Use:

```bash
python tools/apply_v1_1_overlay.py --repo /path/to/local/repo --overlay /path/to/IGAR_Paper1_GitHub_v1.1.0_READY
```

The script preserves the v1.0.0 manifest, applies only the intended files, generates the v1.1.0 repository manifest, and runs the verification script. It does **not** commit, tag, push, or publish a GitHub release.
