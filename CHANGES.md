# CHANGES — revised IJQI manuscript

Revision of *Angle-Encoded Quantum Kernels for Stroke Risk Stratification* in
response to the major-revision review. Section numbers in brackets refer to the
revision brief.

**Deliverables**

| File | What it is |
|---|---|
| `ijqi_stroke_qksp.tex` | Corrected LaTeX source |
| `ijqi_stroke_qksp.pdf` | Compiled manuscript, 14 pages |
| `ws-ijqi.cls` | **Local stand-in** for the official World Scientific class — see *Known limitations* |
| `figures/` | Figs. 1–7 (1–3 carried over, 4–7 regenerated) |
| `analysis.py` / `analysis.json` | Feature-importance and McNemar computations |
| `make_figures.py` | Regenerates Figs. 4–7 |
| `verify_numbers.py` | Cross-checks every printed value against `results.json` |

The paper was rewritten rather than patched: no `.tex` source existed in the
repository or the supplied zip (only the compiled `ijqi_2e (4).pdf`), so the
source was reconstructed from the PDF and then corrected.

---

## 1. Editorial fixes [Brief §2A]

- **Template placeholders removed.** Title, real author names, affiliations and
  emails set; running heads now `S. Shinde & N. Pikle` / `Angle-Encoded Quantum
  Kernels for Stroke Risk Stratification` (was *Instructions for Typing
  Manuscripts*).
- **Keywords** replaced (was `Keyword1; keyword2; keyword3`).
- **All cross-references resolve.** Every `\ref`/`\cite` is bound to a real
  label; the compile emits no `LaTeX Warning` at all. The bare `In,?`, `Table
  ??` and `Fig. 5 Enter Caption` failures are gone.
- **Typography.** No `¿`/`¡` artefacts remain (verified by scan of the compiled
  text).
- **Triplicated paragraph deleted.** The "Distribution of three critical
  clinical features…" paragraph appeared three times; one condensed copy
  remains, in §2.2. A duplicate-sentence scan of the compiled PDF now reports
  zero repeats.
- **Abstract rewritten**, 193 words (was ≈350).

## 2. Theory corrections [Brief §2B]

- **The "32 > 10 dimensions" claim is deleted everywhere** (abstract, §1,
  §2.5.1, §4). §2.5.3 now states plainly that the RBF kernel's RKHS is
  *infinite*-dimensional and that 32 dimensions is far smaller, so
  dimensionality cannot be the source of any advantage; differences must come
  from **inductive bias**.
- **"Implicit L2 regularization via amplitude normalization" deleted.** Replaced
  with the correct, weaker statement that every normalised kernel satisfies
  *K(x,x)=1*, so this is a property of normalisation, not of quantum mechanics.
- **Citations added and used correctly:** Huang *et al.* (2021) *Nat. Commun.*
  **12**, 2631 — cited for the *power of data* result (classical learners with
  data can match quantum models), not for "implicit regularization"; Thanasilp
  *et al.* (2024) *Nat. Commun.* **15**, 5200 — cited for exponential kernel
  concentration, which our n=5 measurement is shown to be safely outside.

## 3. Method/code contradictions resolved [Brief §2C]

- **Old Eq. 12 deleted.** `K = 2P(a=0)−1 = Re⟨ψ|φ⟩` was wrong twice (SWAP test
  gives the *squared magnitude*; `Re⟨ψ|φ⟩` is the Hadamard test). Only
  `K_Q = |⟨φ(x_i)|φ(x_j)⟩|²` survives, and §2.5.1 states it is computed by the
  adjoint/overlap method.
- **All SWAP-test language removed** from §2.4. §2.5.1 now explains that a SWAP
  test between two 5-qubit states would need 5+5+1 = **11 qubits** and would
  *weaken* the NISQ argument — the overlap method genuinely uses 5.
- **Old Eq. 6 (arcsin encoding) deleted**, along with the claim that it
  "amplifies angles near clinical thresholds" (arcsin amplifies near the scaler's
  ±1 extremes, not at age≥65 or glucose≥126). A single encoding is used
  throughout: `θ_i = π·x̃_i`, `x̃ ∈ [−1,1]`, matching `reproduce_qksp.py`.
- **Layer 3 (variational rotations) deleted entirely** — the pipeline trains no
  parameters. This makes the barren-plateau argument correct rather than
  contradictory, and §2.5.4 now says so explicitly.
- **Gate count corrected** to **15 gates, depth 3** (10 encoding + 5 CNOT)
  everywhere; "50 gates, depth 8" and "200 gates, depth 16" are gone.

## 4. Protocol [Brief §2D]

- **New §2.6 "Evaluation Protocol and Leakage Prevention"** explains why
  balance-then-split leaks (SMOTE interpolates test patients' neighbours into
  training; ENN deletes the hardest minority points) and specifies the corrected
  protocol.
- §2.2 and §3.1 now state that SMOTE-ENN is applied **inside training folds
  only** and that held-out folds keep the natural 4.98% prevalence.
- **§3.5 is now the ablation study** (was "Generalization to Imbalanced Data"),
  with Table 4 comparing both protocols — framed as the paper's second
  contribution.

## 5. Numbers rebuilt from `results.json` [Brief §2E]

Every numerical contradiction listed in the brief is resolved. `verify_numbers.py`
extracts all **77** mean±SD pairs from the compiled PDF and confirms each one
matches a value computed from `results.json`.

- Dataset is **N = 4,981** throughout (248 stroke / 4.98%, 4,733 control). The
  5,110 / 9,002 / 9,724 / 4,501:4,501 figures are gone, as is the non-existent
  "alcohol intake" feature. Feature count is **10**, not 11.
- **Old Tables 3, 4, 5 and 7 replaced** by Table 2 (all five models, honest
  protocol) and Table 4 (protocol ablation). Table 5's duplicate `Accuracy` row
  and the `Sensitivity`/`Recall` duplication are gone.
- **Table 7 deleted** — its CV SD (1.12%) and generalisation gap (1.80%) were
  unverifiable against the cited prior work.
- The fabricated RBF-SVM confusion matrix (TP=180/FP=15/FN=15/TN=1590, which
  implies 98.33% not 92.65%) is gone.
- **McNemar test added** (Table 3), and the **kernel concentration statistics**
  (off-diagonal mean 0.248, SD 0.238, rank 1,176–1,179 / 1,200) added to §3.3.
- **The 587-strokes claim is deleted.** Corrected arithmetic in §4: 10,000
  screened contain ≈498 strokes; QSVM detects ≈305 against RBF-SVM's ≈376, i.e.
  ≈70 **fewer** — stated plainly as the quantum kernel being worse on recall.
- **§3.5's reversed conclusion removed** — the old text claimed quantum benefits
  more from balancing while its own table showed the opposite.

## 6. Unsupported claims removed [Brief §2F]

Deleted: the arcsin/clinical-threshold claim; amplitude normalisation as a
quantum regulariser; "interpretability through quantum state analysis" (no such
analysis is performed); and all "validates/establishes quantum advantage"
language. The paper now claims a leakage-free baseline and a protocol
correction, not an advantage.

---

## 7. Deviations from the brief — please read

Three numbers in the brief did **not** reproduce. The brief's own binding
constraint ("every number must be traceable to `results.json` or be computed
from it") was followed, so the computed values are used and the brief's are not.

### 7.1 Feature-importance retention is 80.1%, not 87.6%

The brief conflated two different quantities. Recomputed on the original data
(RF, 100 trees, mean of seeds 0–2, `analysis.py`):

- The **RF's own top five** are avg_glucose (0.2845), BMI (0.2425), age (0.2269),
  smoking_status (0.0689), work_type (0.0472) — cumulatively **87.0%**. This is
  where the brief's "87.6%" comes from.
- The **paper's five clinically selected features** (age, glucose, BMI,
  hypertension, heart disease) are a *different set* and account for
  **80.1%**. Hypertension (0.0249) and heart disease (0.0225) rank 8th and 9th.

§2.3 now reports 80.1% and states openly that the clinical selection is not the
RF's own ranking. Table 1 carries the real per-feature importances.

### 7.2 Feature importance is *not* stable across SMOTE-ENN

The brief asked for a Fig. 5 caption stating "±0.3% variation … confirms that
synthetic oversampling does not distort feature selection". **This is false**,
and the original Fig. 5 contradicted it in its own annotations (−37.3%, +19.0%).
Measured shifts are large:

| Feature | Original | Balanced | Shift |
|---|---|---|---|
| age | 0.227 | 0.396 | **+16.9 pp** |
| avg_glucose_level | 0.284 | 0.080 | **−20.4 pp** |
| bmi | 0.243 | 0.062 | **−18.0 pp** |
| hypertension | 0.025 | 0.082 | +5.7 pp |
| heart_disease | 0.023 | 0.051 | +2.9 pp |

The selected five drop from 80.1% to 67.2% of total importance after balancing.
Fig. 5 was **regenerated** to show the true shifts, and §2.3 now draws the
correct methodological conclusion: importances computed after resampling
describe the resampled distribution, so feature selection must be justified on
the original data. This strengthens the paper's leakage theme rather than
weakening it.

### 7.3 McNemar counts differ from the brief

The brief gives 294/391 and *p* = 2.4×10⁻⁴. `results.json` contains **no
per-patient predictions**, so those figures cannot be reproduced from it. They
were recomputed with the exact pipeline (`analysis.py`), using one seed at a
time so the five held-out folds partition the cohort and each patient is counted
once (*n* = 4,981):

| Seed | classical-only correct | quantum-only correct | *p* |
|---|---|---|---|
| 0 | 288 | 358 | 6.6×10⁻³ |
| 1 | 280 | 339 | 2.0×10⁻² |
| 2 | 269 | 350 | 1.3×10⁻³ |

The **finding is unchanged and now more robust**: the quantum kernel corrects
more RBF-SVM errors than it introduces, consistently and significantly across
all three seeds. Only the magnitude of *p* differs (10⁻²–10⁻³ rather than
10⁻⁴). Pooling seeds would triple-count patients and was avoided.

### 7.4 Figures 4–7 were regenerated, not kept

The brief said to keep Figs. 1–6. Figs. 1–3 are genuine and were carried over
from the original PDF. Figs. 4–7 could not be kept: all four rendered the
fabricated numbers (0.3847/0.2563/0.1924/0.0892/0.0774, the "95.6%" threshold
line, "All 11 Features", 96.12% vs 92.65%, the invented per-fold accuracies).
Fig. 5 additionally had its bar labels mis-paired with their values. All four
were regenerated from `results.json` and `analysis.json` by `make_figures.py`.

### 7.5 Reference 15 (now 16)

Located and completed: *Int. J. Comput. Digit. Syst.* **15**(1), 1807 (2024).
**Please confirm** the volume/page details before submission — they come from a
secondary source, not the publisher record.

---

## Known limitations

- **`ws-ijqi.cls` is a local reimplementation.** The official class is
  distributed only through the World Scientific submission-guidelines page,
  which blocks automated download, and it is not in TeX Live or on CTAN. The
  stand-in reproduces the official *macro interface* (`\markboth`, `\title`,
  `\author`, `\address`, `\maketitle`, `history`, `abstract`, `\keywords`,
  `\tbl`, `\colrule`/`\botrule`, `\refcite`, superscript numeric citations, 5in
  text block measured from the original PDF). **Before submitting, download the
  official `ws-ijqi.cls` and drop it in this directory** — `ijqi_stroke_qksp.tex`
  needs no changes.
- Figures 1–3 are the original raster images extracted from the submitted PDF at
  ~1000 ppi. If the source plotting scripts still exist, regenerating them as
  vector PDF would improve print quality.
- The `history` block still reads *Day Month Year*; the journal fills this in.

## Reproducing

```bash
python reproduce_qksp.py     # -> results.json  (15 folds x 2 protocols)
python analysis.py           # -> analysis.json (RF importances, McNemar)
python make_figures.py       # -> figures/fig4..fig7
pdflatex ijqi_stroke_qksp.tex && pdflatex ijqi_stroke_qksp.tex
python verify_numbers.py     # every printed value vs results.json
```
