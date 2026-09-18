#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

CANON_SHA="ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89"
ADD_SHA="ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b"
MAIN_MANIFEST="MANIFEST_MAIN_FINAL_RESUBMISSION.sha256"
MAIN_EXCLUSIONS={
    MAIN_MANIFEST,
    "MANIFEST_PUBLIC_RELEASE.sha256",
    "MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256",
}

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def parse_manifest(path):
    entries={}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        h,rel=line.split(None,1)
        entries[rel.strip()]=h
    return entries

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',default='.')
    a=ap.parse_args()
    r=Path(a.repo).resolve()
    checks={}

    checks['canonical_archive_sha256']=sha256(r/'canonical_archive/IGAR-Paper1-Reproducibility_STRICT_FINAL.zip')==CANON_SHA
    checks['post_hoc_addendum_zip_sha256']=sha256(r/'revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip')==ADD_SHA

    st=json.load(open(r/'PUBLIC_RELEASE_STATUS.json',encoding='utf-8'))
    checks['root_status_version_1_1_0']=st.get('repository_version')=='1.1.0'
    checks['root_status_addendum_closed']=st.get('revision_stage_addendum',{}).get('status')=='CLOSED'
    checks['final_resubmission_narrative_aligned']=st.get('narrative_alignment',{}).get('status')=='ALIGNED_TO_FINAL_RESUBMISSION'
    checks['current_main_manifest_declared']=st.get('current_main_manifest',{}).get('path')==MAIN_MANIFEST

    p=r/'revision_addenda/P1R11_v0.6_CLOSED'
    ast=json.load(open(p/'manifests/P1R11_ADDENDUM_STATUS.json',encoding='utf-8'))
    checks['internal_addendum_closed']=ast.get('status')=='CLOSED'
    checks['internal_15_15']=ast.get('blocking_pass_count')==15 and ast.get('blocking_check_count')==15
    checks['internal_33_33']=ast.get('target_pass_count')==33 and ast.get('target_count')==33 and ast.get('all_33_targets_pass') is True

    val=json.load(open(p/'machine_outputs/P1R11_33_TARGET_VALIDATION.json',encoding='utf-8'))
    checks['validation_json_33_33']=val.get('all_33_pass') is True and val.get('pass_count')==33 and val.get('target_count')==33

    internal_bad=[]
    for line in (p/'manifests/SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        h,rel=line.split(None,1)
        rel=rel.strip()
        fp=p/rel
        if not fp.exists() or sha256(fp)!=h:
            internal_bad.append(rel)
    checks['internal_checksum_manifest']=len(internal_bad)==0

    historical=(r/'MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256').read_bytes()
    alias=(r/'MANIFEST_PUBLIC_RELEASE.sha256').read_bytes()
    checks['historical_v1_1_manifest_alias_preserved']=historical==alias

    main_entries=parse_manifest(r/MAIN_MANIFEST)
    current_bad=[]
    for rel,h in main_entries.items():
        fp=r/rel
        if not fp.is_file() or sha256(fp)!=h:
            current_bad.append(rel)
    checks['current_main_manifest_entries_verify']=len(current_bad)==0

    expected=set()
    for fp in r.rglob('*'):
        if not fp.is_file():
            continue
        rel=fp.relative_to(r).as_posix()
        if rel.startswith('.git/'):
            continue
        if rel in MAIN_EXCLUSIONS:
            continue
        expected.add(rel)
    manifest_paths=set(main_entries)
    missing=sorted(expected-manifest_paths)
    unexpected=sorted(manifest_paths-expected)
    checks['current_main_manifest_exact_coverage']=not missing and not unexpected

    out={
        'all_pass':all(checks.values()),
        'checks':checks,
        'internal_bad_files':internal_bad,
        'current_main_bad_files':current_bad,
        'current_main_missing_paths':missing,
        'current_main_unexpected_paths':unexpected,
        'historical_manifest_scope_note':'MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256 identifies the tagged v1.1.0 release snapshot.',
        'current_main_manifest_scope_note':'MANIFEST_MAIN_FINAL_RESUBMISSION.sha256 verifies current main after final-resubmission narrative alignment.'
    }
    print(json.dumps(out,indent=2))
    raise SystemExit(0 if out['all_pass'] else 2)

if __name__=='__main__':
    main()
