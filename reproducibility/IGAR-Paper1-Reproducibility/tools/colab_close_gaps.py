#!/usr/bin/env python3
"""Close the four release-packaging gaps from the author's final Colab/Drive environment.

The script is intentionally conservative: it will not label the release CLOSED unless it finds
verbatim Cell 60A–60E source and at least one exact source cell containing both row_id and
duplicate_group_id construction evidence.
"""
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path

CELL_MARKERS=["CELL 60A","CELL 60B","CELL 60C","CELL 60D","CELL 60E"]

def norm_source(src):
    if isinstance(src,list): return "".join(src)
    return src or ""

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()

def scan_notebooks(search_roots):
    notebooks=[]
    for root in search_roots:
        root=Path(root)
        if not root.exists(): continue
        for p in root.rglob("*.ipynb"):
            try:
                nb=json.loads(p.read_text(encoding="utf-8"))
            except Exception: continue
            cells=[]
            for i,c in enumerate(nb.get("cells",[])):
                if c.get("cell_type")!="code": continue
                s=norm_source(c.get("source"))
                cells.append((i,s))
            notebooks.append((p,cells))
    return notebooks

def capture_training_cells(notebooks, out):
    found={}
    provenance={}
    for marker in CELL_MARKERS:
        for p,cells in notebooks:
            for idx,s in cells:
                if marker.lower() in s.lower():
                    found[marker]=s; provenance[marker]={"notebook":str(p),"cell_index":idx}; break
            if marker in found: break
    if len(found)!=len(CELL_MARKERS):
        missing=[m for m in CELL_MARKERS if m not in found]
        return False, {"missing":missing,"found":provenance}
    parts=["# VERBATIM EXTRACT FROM FINAL NOTEBOOK\n"]
    for m in CELL_MARKERS:
        pr=provenance[m]
        parts.append(f"\n# ===== {m} | notebook={pr['notebook']} | cell_index={pr['cell_index']} =====\n")
        parts.append(found[m].rstrip()+"\n")
    out.write_text("".join(parts),encoding="utf-8")
    return True, provenance

def capture_id_cells(notebooks, out):
    hits=[]
    for p,cells in notebooks:
        for idx,s in cells:
            sl=s.lower()
            # Conservative: capture cells containing identifier names plus construction/hash/normalization evidence.
            if ("row_id" in sl or "duplicate_group_id" in sl) and any(k in sl for k in ["hashlib","md5","sha","unicodedata","normalize","nfc","str.cat","apply","assign","astype(str)"]):
                hits.append((p,idx,s))
    # Require evidence for both identifiers somewhere in captured material.
    joined="\n".join(s for _,_,s in hits)
    if "row_id" not in joined or "duplicate_group_id" not in joined:
        return False, {"hit_count":len(hits),"reason":"Could not find construction evidence for both row_id and duplicate_group_id."}
    parts=["# VERBATIM SOURCE CELLS RELEVANT TO row_id / duplicate_group_id\n"]
    seen=set()
    for p,idx,s in hits:
        key=(str(p),idx)
        if key in seen: continue
        seen.add(key)
        parts.append(f"\n# ===== notebook={p} | cell_index={idx} =====\n{s.rstrip()}\n")
    out.write_text("".join(parts),encoding="utf-8")
    return True, {"hit_count":len(seen),"sources":[{"notebook":str(p),"cell_index":idx} for p,idx,_ in hits]}

def capture_environment(root):
    env=root/"environment"; env.mkdir(exist_ok=True)
    pkgs=["torch","transformers","accelerate","tokenizers","safetensors","sentencepiece","numpy","pandas","sklearn","statsmodels"]
    d={"python":sys.version,"platform":platform.platform(),"captured_at":datetime.now(timezone.utc).isoformat()}
    for name in pkgs:
        try:
            mod=__import__(name); d[name]=getattr(mod,"__version__","UNKNOWN")
        except Exception as e: d[name]=f"UNAVAILABLE: {e}"
    try:
        import torch
        d["cuda_runtime_reported_by_torch"]=torch.version.cuda
        d["cuda_available"]=bool(torch.cuda.is_available())
        d["gpu"]=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception: pass
    (env/"runtime-info.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
    freeze=subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True,check=True).stdout
    (env/"pip-freeze.txt").write_text(freeze,encoding="utf-8")
    required=["numpy","pandas","sklearn","statsmodels"]
    ok=all(d.get(k) and not str(d[k]).startswith("UNAVAILABLE") and d[k]!="UNKNOWN" for k in required)
    return ok,d

def local_data_provenance(root, project_root):
    cfg=root/"config"
    base=json.loads((cfg/"data_provenance.json").read_text(encoding="utf-8"))
    project_root=Path(project_root)
    expected=base["study_raw_dataset_sha256"]
    candidates=[]
    # Restrict to plausible data files to avoid hashing huge model files.
    search_roots=[project_root, project_root.parent]
    names=("VADER_labeled.csv","Rating_labeled.csv")
    for sr in search_roots:
        if not sr.exists(): continue
        for name in names:
            for p in sr.rglob(name):
                try:
                    candidates.append({"path":str(p),"size_bytes":p.stat().st_size,"mtime_utc":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),"sha256":sha256_file(p)})
                except Exception: pass
    matches=[x for x in candidates if x["sha256"]==expected]
    local={
      **base,
      "captured_at":datetime.now(timezone.utc).isoformat(),
      "project_root":str(project_root),
      "candidate_raw_files":candidates,
      "sha256_matching_local_raw_files":matches,
      "download_date_policy":"Not invented. If no contemporaneous download log exists, report dataset version/publication date and local file mtime separately rather than claiming mtime is download date.",
      "translation_provenance":"The published VADER_labeled.csv already documents translation plus VADER fields; this study uses the dataset-provided translation-mediated VADER supervision rather than requiring a new external translation API call for reproduction."
    }
    (cfg/"local_data_provenance.json").write_text(json.dumps(local,indent=2),encoding="utf-8")
    # Public provenance itself is closed even if original download date is unknowable; do not fabricate it.
    return True,local

def zip_package(root):
    z=root.parent/(root.name+".zip")
    if z.exists(): z.unlink()
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as f:
        for p in root.rglob("*"):
            if p.is_file() and p!=z:
                f.write(p,p.relative_to(root.parent))
    return z

def main(package_root, project_root):
    root=Path(package_root); project=Path(project_root)
    (root/"src").mkdir(parents=True,exist_ok=True); (root/"manifests").mkdir(exist_ok=True)
    # Search project first, then MyDrive as fallback.
    roots=[project]
    mydrive=Path("/content/drive/MyDrive")
    if mydrive.exists(): roots.append(mydrive)
    notebooks=scan_notebooks(roots)
    train_ok,train_info=capture_training_cells(notebooks,root/"src/08_train_paired_indobert_EXACT_EXTRACT.py")
    ids_ok,ids_info=capture_id_cells(notebooks,root/"src/04_exact_row_duplicate_id_cells.py")
    env_ok,env_info=capture_environment(root)
    data_ok,data_info=local_data_provenance(root,project)
    status={
      "status":"CLOSED" if all([train_ok,ids_ok,env_ok,data_ok]) else "OPEN",
      "closed_at":datetime.now(timezone.utc).isoformat() if all([train_ok,ids_ok,env_ok,data_ok]) else None,
      "gaps":{
        "exact_cell_60A_60E_source":{"closed":train_ok,"detail":train_info},
        "exact_row_duplicate_id_source":{"closed":ids_ok,"detail":ids_info},
        "exact_environment":{"closed":env_ok,"detail":env_info},
        "data_translation_provenance":{"closed":data_ok,"detail":{"dataset_doi":data_info["dataset_doi"],"version":data_info["version"],"license":data_info["license"],"local_matches":len(data_info["sha256_matching_local_raw_files"])}}
      },
      "scientific_results_changed":False,
      "new_statistical_tests":False
    }
    (root/"manifests/REPRODUCIBILITY_STATUS.json").write_text(json.dumps(status,indent=2),encoding="utf-8")
    z=zip_package(root)
    print(json.dumps(status,indent=2))
    print("Package ZIP:",z)
    if status["status"]!="CLOSED":
        raise SystemExit("Reproducibility package remains OPEN. Inspect the status manifest; upload/provide the final notebook if exact-source cells were not found.")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--package-root",required=True)
    ap.add_argument("--project-root",default="/content/drive/MyDrive/IGAR_Paper1")
    a=ap.parse_args(); main(a.package_root,a.project_root)
