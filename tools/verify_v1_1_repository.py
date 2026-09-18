#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

CANON_SHA="ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89"
ADD_SHA="ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b"

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

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

    p=r/'revision_addenda/P1R11_v0.6_CLOSED'
    ast=json.load(open(p/'manifests/P1R11_ADDENDUM_STATUS.json',encoding='utf-8'))
    checks['internal_addendum_closed']=ast.get('status')=='CLOSED'
    checks['internal_15_15']=ast.get('blocking_pass_count')==15 and ast.get('blocking_check_count')==15
    checks['internal_33_33']=ast.get('target_pass_count')==33 and ast.get('target_count')==33 and ast.get('all_33_targets_pass') is True

    val=json.load(open(p/'machine_outputs/P1R11_33_TARGET_VALIDATION.json',encoding='utf-8'))
    checks['validation_json_33_33']=val.get('all_33_pass') is True and val.get('pass_count')==33 and val.get('target_count')==33

    bad=[]
    for line in (p/'manifests/SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        h,rel=line.split(None,1)
        rel=rel.strip()
        fp=p/rel
        if not fp.exists() or sha256(fp)!=h:
            bad.append(rel)
    checks['internal_checksum_manifest']=len(bad)==0

    m1=(r/'MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256').read_bytes()
    ma=(r/'MANIFEST_PUBLIC_RELEASE.sha256').read_bytes()
    checks['tagged_release_manifest_alias_preserved']=m1==ma

    out={
        'all_pass':all(checks.values()),
        'checks':checks,
        'internal_bad_files':bad,
        'manifest_scope_note':'MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256 identifies the tagged v1.1.0 release snapshot. Current main contains narrative-only final-resubmission alignment updates and is not expected to match that historical full-repository manifest.'
    }
    print(json.dumps(out,indent=2))
    raise SystemExit(0 if out['all_pass'] else 2)

if __name__=='__main__':
    main()
