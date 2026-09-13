# Environment Provenance

## Historical scientific Transformer environment

The final paired Transformer models were trained under the Gate 6A / Gate 6B locked model stack:

```text
Python       3.13.15
PyTorch      2.11.0+cu128
CUDA         12.8
GPU          Tesla T4
transformers 4.57.6
accelerate   1.14.0
tokenizers   0.22.2
safetensors  0.8.0
sentencepiece 0.2.2
```

These versions remain authoritative for model training.

## Current reference reproduction runtime

transformers: 5.16.1

tokenizers: 0.23.1

NumPy: 2.1.3

pandas: 2.2.3

scikit-learn: 1.6.1

statsmodels: 0.15.0

The current runtime is preserved for future reproduction but does not overwrite the historical scientific training environment.

## Historical statistical-stack audit

Historical versions explicitly found in notebook.
