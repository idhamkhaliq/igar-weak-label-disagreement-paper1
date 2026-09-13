import json, platform, subprocess, sys
from pathlib import Path

PKGS = ["torch","transformers","accelerate","tokenizers","safetensors","sentencepiece","numpy","pandas","sklearn","statsmodels"]

def main(outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    versions = {"python": sys.version, "platform": platform.platform()}
    for name in PKGS:
        try:
            mod = __import__(name)
            versions[name] = getattr(mod, "__version__", "UNKNOWN")
        except Exception as e:
            versions[name] = f"UNAVAILABLE: {e}"
    try:
        import torch
        versions["cuda_runtime_reported_by_torch"] = torch.version.cuda
        versions["cuda_available"] = bool(torch.cuda.is_available())
        versions["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:
        pass
    (outdir/"runtime-info.json").write_text(json.dumps(versions, indent=2), encoding="utf-8")
    freeze = subprocess.run([sys.executable,"-m","pip","freeze"], capture_output=True, text=True, check=True).stdout
    (outdir/"pip-freeze.txt").write_text(freeze, encoding="utf-8")
    print(json.dumps(versions, indent=2))

if __name__ == "__main__":
    main(Path(__file__).resolve().parent)
