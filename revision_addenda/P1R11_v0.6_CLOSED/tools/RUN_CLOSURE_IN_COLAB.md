# Run P1R-11 closure reproduction in Colab

This closure harness performs **no model training**. It reads preserved prediction matrices and metadata only.

```bash
pip install -q pyarrow==23.0.1 numpy==2.1.3 pandas==2.2.3 scikit-learn==1.6.1 statsmodels==0.15.0

python tools/reproduce_p1r11_from_preserved_predictions.py \
  --inputs-dir /content/drive/MyDrive/IGAR_Paper1/phase3/rq4_final/closure_inputs \
  --manifest manifests/P1R11_ADDENDUM_MANIFEST.json \
  --out-dir outputs/p1r11_closure
```

Expected closure condition:

- `P1R11_33_TARGET_VALIDATION.json` reports `all_33_pass: true` and `pass_count: 33`.
- No training/checkpoint creation is performed.
- The script is labeled **reconstructed closure/reproduction code**, not the original ephemeral P1R-11 execution script.
