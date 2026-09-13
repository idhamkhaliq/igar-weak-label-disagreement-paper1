import argparse, json
from pathlib import Path

REQUIRED = [
    "src/08_train_paired_indobert_EXACT_EXTRACT.py",
    "src/04_exact_row_duplicate_id_cells.py",
    "environment/runtime-info.json",
    "environment/pip-freeze.txt",
    "config/local_data_provenance.json",
    "manifests/REPRODUCIBILITY_STATUS.json",
]

def main(root):
    root=Path(root)
    missing=[p for p in REQUIRED if not (root/p).exists()]
    if missing:
        raise SystemExit("RELEASE NOT CLOSED. Missing:\n- " + "\n- ".join(missing))
    status=json.loads((root/"manifests/REPRODUCIBILITY_STATUS.json").read_text())
    if status.get("status") != "CLOSED":
        raise SystemExit(f"RELEASE NOT CLOSED: status={status.get('status')}")
    print("REPRODUCIBILITY RELEASE: CLOSED / PASS")
    print(json.dumps(status, indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--package-root", required=True); a=ap.parse_args(); main(a.package_root)
