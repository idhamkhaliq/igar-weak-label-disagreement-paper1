#!/usr/bin/env python3
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'manifests'/'P1R11_ADDENDUM_MANIFEST.json'
S=ROOT/'manifests'/'P1R11_ADDENDUM_STATUS.json'
C=ROOT/'manifests'/'SHA256SUMS.txt'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
manifest=json.loads(M.read_text())
status=json.loads(S.read_text())
checks=manifest['closure_checks']
assert len(checks)==15, f'Expected 15 blocking checks, found {len(checks)}'
assert all(checks.values()), [k for k,v in checks.items() if not v]
assert manifest['addendum']['status']=='CLOSED'
assert status['status']=='CLOSED'
assert status['blocking_check_count']==15 and status['blocking_pass_count']==15
val=json.loads((ROOT/'machine_outputs'/'P1R11_33_TARGET_VALIDATION.json').read_text())
assert val['all_33_pass'] and val['pass_count']==33 and val['target_count']==33
res=json.loads((ROOT/'machine_outputs'/'P1R11_REPRODUCED_RESULTS.json').read_text())
assert res['primary']['paired_jsd_max_abs_diff']==0.0
assert all(v['finite'] and v['nan_count']==0 and v['inf_count']==0 for v in res['probability_integrity'].values())
# All manifest artifact paths and declared hashes.
for group,items in manifest['artifact_index'].items():
    for x in items:
        p=ROOT/x['path']; assert p.is_file(), f'Missing {x["path"]}'
        assert sha(p)==x['sha256'], f'Hash mismatch {x["path"]}'
# Portable checksum manifest.
lines=[ln.strip() for ln in C.read_text().splitlines() if ln.strip()]
for ln in lines:
    digest,path=ln.split('  ',1); p=ROOT/path
    assert p.is_file(), f'Checksum path missing: {path}'
    assert sha(p)==digest, f'Checksum mismatch: {path}'
print(json.dumps({'status':'CLOSED','blocking_checks_pass':'15/15','numerical_targets_pass':'33/33','checksum_entries':len(lines),'result':'PASS'},indent=2))
