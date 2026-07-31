# Angle-Encoded Quantum Kernels for Stroke Risk Stratification

Code, data and manuscript for *Angle-Encoded Quantum Kernels for Stroke Risk
Stratification: An Empirical Comparison with Classical Kernel Methods*
(S. Shinde, N. Pikle), submitted to the **International Journal of Quantum
Information**.

A 5-qubit angle-encoded fidelity kernel SVM is evaluated on the Kaggle stroke
cohort (N = 4,981) against four classical baselines, under a **leakage-free**
cross-validation protocol. Every number in the manuscript is reproducible from
this repository.

## Headline results

Stratified 5-fold CV × 3 seeds = 15 folds. SMOTE-ENN applied **inside training
folds only**; held-out folds keep the natural 4.98% stroke prevalence.

| Model | AUC | AUPRC | Recall | Bal. acc. |
|---|---|---|---|---|
| RBF-SVM | **0.826 ± 0.024** | 0.183 ± 0.027 | 0.754 ± 0.077 | 0.753 ± 0.034 |
| Random forest | 0.804 ± 0.025 | 0.148 ± 0.019 | 0.443 ± 0.077 | 0.658 ± 0.036 |
| KNN (k=5) | 0.751 ± 0.033 | 0.121 ± 0.016 | 0.621 ± 0.074 | 0.705 ± 0.034 |
| **QSVM** | 0.749 ± 0.033 | 0.151 ± 0.030 | 0.613 ± 0.062 | 0.693 ± 0.029 |
| Decision tree | 0.717 ± 0.031 | 0.114 ± 0.017 | 0.562 ± 0.071 | 0.686 ± 0.033 |

**The quantum kernel is competitive with, but does not exceed, classical kernel
methods.** This repository makes no quantum-advantage claim.

A paired McNemar test does show the quantum kernel makes significantly
*different* predictions from the RBF-SVM — correcting more of its errors than it
introduces at the default threshold, consistently across three seeds
(p = 6.6×10⁻³, 2.0×10⁻², 1.3×10⁻³) — while ranking patients less well overall.

### The leakage finding

Applying SMOTE-ENN to the full dataset *before* splitting — the protocol used in
most prior work on this dataset, including the authors' own — inflates AUC by
0.13–0.25 and AUPRC by 0.78–0.85 for **every** model:

| Model | AUC (leakage-free) | AUC (leaky) |
|---|---|---|
| RBF-SVM | 0.826 ± 0.024 | 0.954 ± 0.006 |
| Random forest | 0.804 ± 0.025 | 0.997 ± 0.000 |
| QSVM | 0.749 ± 0.033 | 0.925 ± 0.010 |

The random forest's 0.997 under the leaky protocol is consistent with the 99.52%
accuracy previously reported for this dataset. **Results above AUC 0.95 on this
cohort should be read as artefacts of resampling order.**

### Kernel concentration

At n = 5 qubits the kernel shows no exponential concentration: off-diagonal
entries have mean 0.248 and standard deviation 0.238, and a 1200×1200 block has
numerical rank 1,176–1,179. The circuit sits well outside the concentrated
regime described by Thanasilp *et al.* (2024), so its limited performance
reflects the feature map's inductive bias rather than a degenerate kernel.

## The circuit

5 qubits, **15 gates, depth 3**, no variational parameters:

1. **Encoding** (10 gates) — `RY(π·x̃ᵢ)` then `RZ(π·x̃ᵢ)` per qubit, with
   `x̃ ∈ [-1,1]` from a MinMaxScaler fitted on the training fold only.
2. **Entanglement** (5 gates) — CNOT ring `Q₀→Q₁→Q₂→Q₃→Q₄→Q₀`.

The kernel `K(xᵢ,xⱼ) = |⟨ψ(xᵢ)|ψ(xⱼ)⟩|²` is computed by the adjoint/overlap
method (both statevectors computed, inner product taken directly). This needs
one 5-qubit register and no ancilla — a SWAP-test estimator would need 11.

Encoded features: `age`, `avg_glucose_level`, `bmi`, `hypertension`,
`heart_disease` — a clinical selection accounting for 80.1% of Random Forest
importance on the original data.

## Contents

| File | Description |
|---|---|
| `ijqi_stroke_qksp.tex` / `.pdf` | Revised manuscript (14 pp) |
| `ws-ijqi.cls` | **Local stand-in** for the official World Scientific class — see below |
| `CHANGES.md` | Every substantive edit in the revision, and three documented deviations |
| `brain_stroke.csv` | Dataset, 4,981 patients (248 stroke / 4,733 control) |
| `reproduce_qksp.py` | Main pipeline → `results.json` |
| `results.json` | Fold-level metrics, both protocols, plus kernel statistics |
| `analysis.py` | Feature importances and McNemar test → `analysis.json` |
| `make_figures.py` | Regenerates Figs. 4–7 |
| `verify_numbers.py` | Checks every value printed in the PDF against `results.json` |
| `figures/` | Figs. 1–7 |
| `ijqi_2e (4).pdf` | Original pre-revision submission, kept for reference |

## Reproducing

Requires Python 3.10+ with `numpy`, `pandas`, `scikit-learn`,
`imbalanced-learn`, `matplotlib` and `scipy`.

```bash
pip install numpy pandas scikit-learn imbalanced-learn matplotlib scipy

python reproduce_qksp.py     # -> results.json  (15 folds x 2 protocols)
python analysis.py           # -> analysis.json (RF importances, McNemar)
python make_figures.py       # -> figures/fig4..fig7

pdflatex ijqi_stroke_qksp.tex && pdflatex ijqi_stroke_qksp.tex
python verify_numbers.py     # confirms every printed value traces to results.json
```

`verify_numbers.py` extracts all 77 mean ± SD pairs from the compiled PDF and
checks each against a value computed from `results.json`. It requires
`pdftotext` (poppler-utils).

## Note on `ws-ijqi.cls`

The official World Scientific class file is distributed only through the
[journal's submission-guidelines page](https://www.worldscientific.com/page/ijqi/submission-guidelines)
and is not redistributable. The `ws-ijqi.cls` here is a local reimplementation
of its macro interface so the manuscript compiles from a clean checkout.
**Before submitting, replace it with the official file** — `ijqi_stroke_qksp.tex`
needs no changes.

## Citation

```bibtex
@article{shinde_qksp_stroke,
  title  = {Angle-Encoded Quantum Kernels for Stroke Risk Stratification:
            An Empirical Comparison with Classical Kernel Methods},
  author = {Shinde, Snehal and Pikle, Nileshchandra},
  note   = {Submitted to the International Journal of Quantum Information},
  year   = {2026}
}
```

Dataset: [Kaggle Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)
(fedesoriano, 2021).
