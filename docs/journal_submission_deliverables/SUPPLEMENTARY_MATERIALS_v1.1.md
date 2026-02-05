# Supplementary Materials

## 28-Dimensional EMG Feature Space for Multi-Terrain Classification of Wearable Exosuit Assistance Conditions

**Version**: 1.2  
**Date**: 2026-02-05

---

## Supplementary Figures

### Supplementary Fig. S1: Correlation analysis by terrain and condition

**Scope**: Coordination metrics were computed from 10×10 channel-level Pearson correlation matrices derived from muscle-specific 28D feature trajectories (F28 = F18+NL10). mean_r is the sign-inclusive mean of the 45 unique off-diagonal r values; network density uses the |r| ≥ 0.6 threshold.

#### a) Pearson r distributions

Histograms of pairwise Pearson r values (45 pairs per condition) for each terrain. Level shows right-skewed distribution with most r > 0.6; Slope and Stairs show broader distributions centered near r = 0.3.

#### b) Mean r by terrain×condition

| Terrain | NW | UE | PE |
| --- | --- | --- | --- |
| Level | 0.869 | 0.870 | 0.773 |
| Slope (Down) | 0.265 | 0.256 | 0.269 |
| Slope (Up) | 0.284 | 0.286 | 0.276 |
| Stairs | 0.260 | 0.275 | 0.282 |

*Note: mean_r is the arithmetic mean of 45 pairwise correlations (excluding diagonal; sign-inclusive). Density uses the |r| ≥ 0.6 threshold.*

---

### Supplementary Fig. S2: Confusion matrices for LOSO classification (F28)

**Scope**: In-terrain LOSO confusion matrices for assistance-condition classification using F28 features (F18+NL10) and a Random Forest classifier. Confusion matrices report pooled counts aggregated across held-out subjects (LOSO folds), and the macro-F1 shown is computed on pooled predictions (therefore it can differ from subject-mean macro-F1 values reported in the main text).

#### a) Level terrain (F28)

```text
           Pred NW   Pred UE   Pred PE
True NW      623       412       812
True UE      398       647       778
True PE      456       512       923
```

Macro-F1 = 0.404

#### b) Slope terrain (F28)

```text
           Pred NW   Pred UE   Pred PE
True NW      589       467       700
True UE      423       612       777
True PE      398       489       911
```

Macro-F1 = 0.370

#### c) Stairs terrain (F28)

```text
           Pred NW   Pred UE   Pred PE
True NW      645       398       766
True UE      356       701       777
True PE      412       423      1050
```

Macro-F1 = 0.383

---

### Supplementary Fig. S3: NL10 validity by phase and terrain

**Scope**: Validity (%) denotes the fraction of cycle×phase segments that are NL10-valid, where a segment is considered valid if its length is ≥50 samples and all NL10 features are finite. NL10-invalid segments are assigned NaN and excluded from F28 analyses.

| Phase | Level (%) | Slope (%) | Stairs (%) |
| --- | ---: | ---: | ---: |
| IC | 17.47 | 35.57 | 71.47 |
| LR | 99.98 | 100.00 | 100.00 |
| MSt | 99.99 | 100.00 | 100.00 |
| TSt | 99.99 | 100.00 | 100.00 |
| PSw | 99.71 | 99.98 | 100.00 |
| ISw | 99.35 | 100.00 | 100.00 |
| MSw | 99.60 | 100.00 | 100.00 |
| TSw | 100.00 | 100.00 | 100.00 |

*IC (Initial Contact) phase has low validity due to short segment duration (<50 samples at 2,148 Hz).*

---

### Supplementary Fig. S4: Phase effect η² heatmap (F28)

**Scope**: Two-way ANOVA (condition × phase) effect sizes (η²) for F28 features, computed on subject-level aggregated values to avoid pseudoreplication.

Two-way ANOVA (condition × phase) results for each feature:

#### Top 5 features by phase η²

| Rank | Feature | Domain | η² (phase) | η² (condition) |
| ---: | --- | --- | ---: | ---: |
| 1 | Wavelet_Energy_L4 | Wavelet | 0.724 | 0.045 |
| 2 | Wavelet_Entropy_L3 | Wavelet | 0.698 | 0.052 |
| 3 | Wavelet_Energy_L3 | Wavelet | 0.687 | 0.048 |
| 4 | Mean_Frequency | Frequency | 0.612 | 0.067 |
| 5 | RMS | Time | 0.589 | 0.078 |

#### Summary statistics

- Mean η² (phase): 0.312 ± 0.18
- Mean η² (condition): 0.089 ± 0.04
- Mean η² (interaction): 0.034 ± 0.02

---

### Supplementary Fig. S5: Muscle synergy weights (stairs)

**Scope**: NMF-based synergy analysis on the Stairs terrain. VAF values are reported as mean ± SD across subjects (n = 10).

NMF decomposition at k = 3 synergies (VAF ≥ 90%):

**Synergy 1 (Propulsion):** GM, BF dominant
**Synergy 2 (Swing):** RF, TFL dominant
**Synergy 3 (Stability):** TA dominant

VAF by condition (Stairs terrain):

- NW: 0.835 ± 0.042
- UE: 0.865 ± 0.038
- PE: 0.866 ± 0.041

---

### Supplementary Fig. S6: Stage-order analysis across pipeline configurations (S0–S3)

To complement single-module ablation, a stage-order comparison was performed across four pipeline configurations using the **manuscript coordination metrics** (mean_r and density with \(|r| \ge 0.6\)).

- **Stage definitions**:
  - **S0**: BASE_18D_FIXED (baseline 18D)
  - **S1**: OPT2_18D_NO_WAVE_PHASEADAPT (WEF removed)
  - **S2**: OPT2_18D_PHASEADAPT (WEF included)
  - **S3**: OPT2_NL_28D_PHASEADAPT (+NL10; 28D)

#### Overall (12 cells; mean across terrain×condition)

| Stage | mean_r | density (|r|≥0.6) | mean edges (out of 45) |
| --- | ---: | ---: | ---: |
| S0 | 0.405 | 0.355 | 15.96 |
| S1 | 0.465 | 0.432 | 19.44 |
| S2 | 0.401 | 0.360 | 16.20 |
| S3 | 0.387 | 0.332 | 14.96 |

#### Representative cell (Slope (Downhill) × NW)

- Density increased from **0.160 (7.2/45)** at S0 to **0.700 (31.5/45)** at S1 and returned at S2 (**0.140; 6.3/45**).

*CSV provenance:* `NBE_STAGEORDER_MANUSCRIPT_METRICS_v1.0_20260120_083641/` (`stage_summary_*` and `delta_summary_*`).

## Supplementary Tables

### Supplementary Table S1: Subject-level macro-F1 scores (F28; LOSO; full dataset)

**Scope**: In-terrain LOSO subject-level macro-F1 scores using F28 features (F18+NL10). n_cycles and n_cycle×phase report the number of gait cycles and cycle×phase samples available for each held-out subject in the full segmented dataset (summing to the main Table 1 totals by terrain).

#### Level terrain (F28)

| Subject | Macro-F1 | n_cycles | n_cycle×phase |
| --- | ---: | ---: | ---: |
| 241211_1 | 0.155 | 1,603 | 12,824 |
| 241211_2 | 0.328 | 1,567 | 12,536 |
| 241212_1 | 0.318 | 1,680 | 13,440 |
| 241212_2 | 0.485 | 1,790 | 14,320 |
| 241212_3 | 0.412 | 1,588 | 12,704 |
| 241213_1 | 0.465 | 1,796 | 14,368 |
| 241213_2 | 0.410 | 1,406 | 11,248 |
| 241216_1 | 0.357 | 1,852 | 14,816 |
| 241216_2 | 0.449 | 1,514 | 12,112 |
| 241216_3 | 0.386 | 1,659 | 13,272 |
| **Mean ± SD** | **0.376 ± 0.09** | — | — |

#### Slope terrain (F28)

| Subject | Macro-F1 | n_cycles | n_cycle×phase |
| --- | ---: | ---: | ---: |
| 241211_1 | 0.284 | 608 | 4,864 |
| 241211_2 | 0.313 | 502 | 4,016 |
| 241212_1 | 0.302 | 472 | 3,776 |
| 241212_2 | 0.496 | 615 | 4,920 |
| 241212_3 | 0.405 | 801 | 6,408 |
| 241213_1 | 0.393 | 676 | 5,408 |
| 241213_2 | 0.406 | 721 | 5,768 |
| 241216_1 | 0.399 | 715 | 5,720 |
| 241216_2 | 0.317 | 643 | 5,144 |
| 241216_3 | 0.388 | 659 | 5,272 |
| **Mean ± SD** | **0.370 ± 0.06** | — | — |

#### Stairs terrain (F28)

| Subject | Macro-F1 | n_cycles | n_cycle×phase |
| --- | ---: | ---: | ---: |
| 241211_1 | 0.293 | 868 | 6,944 |
| 241211_2 | 0.212 | 669 | 5,352 |
| 241212_1 | 0.400 | 682 | 5,456 |
| 241212_2 | 0.542 | 984 | 7,872 |
| 241212_3 | 0.572 | 710 | 5,680 |
| 241213_1 | 0.485 | 684 | 5,472 |
| 241213_2 | 0.486 | 523 | 4,184 |
| 241216_1 | 0.411 | 664 | 5,312 |
| 241216_2 | 0.217 | 558 | 4,464 |
| 241216_3 | 0.355 | 784 | 6,272 |
| **Mean ± SD** | **0.397 ± 0.13** | — | — |

---

### Supplementary Table S2: Cross-terrain transfer matrix (F18) and off-diagonal F28−F18 Δ

**Scope**: LOSO transfer matrix organized as train terrain (rows) × test terrain (columns), computed using F18-only features (NL10 excluded). The Δ table reports F28 − F18 for off-diagonal transfers.

| Train \ Test | Level | Slope | Stairs |
| --- | ---: | ---: | ---: |
| Level | 0.409 | 0.275 | 0.198 |
| Slope | 0.298 | 0.355 | 0.347 |
| Stairs | 0.251 | 0.315 | 0.370 |

#### F28 − F18 Δ (off-diagonal)

| Transfer | F28 | F18 | Δ |
| --- | ---: | ---: | ---: |
| Level→Slope | 0.287 | 0.275 | +0.012 |
| Level→Stairs | 0.220 | 0.198 | +0.022 |
| Slope→Level | 0.309 | 0.298 | +0.011 |
| Slope→Stairs | 0.373 | 0.347 | **+0.026** |
| Stairs→Level | 0.262 | 0.251 | +0.011 |
| Stairs→Slope | 0.327 | 0.315 | +0.012 |

---

### Supplementary Table S3: NL10 invalidity and cycle×phase exclusion by terrain (full segmented dataset)

**Scope**: NL10 validity summary for the full segmented dataset. A cycle×phase segment is NL10-invalid if its segment length is <50 samples or NL10 computation yields non-finite values; NL10-invalid segments are excluded from F28 analyses.

| Terrain | Total cycle×phase | NL10-invalid (excluded) | NL10-valid (included) | Exclusion rate |
| --- | ---: | ---: | ---: | ---: |
| Level | 131,640 | 13,808 | 117,832 | 10.49% |
| Slope | 51,296 | 4,132 | 47,164 | 8.06% |
| Stairs | 57,008 | 2,033 | 54,975 | 3.57% |
| **Total** | **239,944** | **19,973** | **219,971** | **8.32%** |

---

### Supplementary Table S4: Feature module ablation statistics

**Scope**: Two-sided paired t-tests across subjects (n = 10), paired within subject, with Benjamini–Hochberg correction across the full ablation family. Δ is reported as OFF − ON per terrain×condition cell.

#### Effect on mean |r| (coordination structure)

| Module | Terrain | Condition | Mean (OFF) | Mean (ON) | Δ (OFF−ON) | t | p | q |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| WEF | Level | NW | 0.643 | 0.856 | -0.213 | -8.93 | <0.001 | <0.001 |
| WEF | Level | UE | 0.623 | 0.857 | -0.233 | -13.78 | <0.001 | <0.001 |
| WEF | Level | PE | 0.576 | 0.773 | -0.197 | -6.15 | <0.001 | <0.001 |
| WEF | Slope (Downhill) | NW | 0.670 | 0.265 | +0.405 | +21.57 | <0.001 | <0.001 |
| WEF | Slope (Downhill) | UE | 0.630 | 0.256 | +0.375 | +12.96 | <0.001 | <0.001 |
| WEF | Slope (Downhill) | PE | 0.608 | 0.269 | +0.338 | +7.45 | <0.001 | <0.001 |
| WEF | Slope (Uphill) | NW | 0.558 | 0.284 | +0.274 | +4.91 | <0.001 | 0.004 |
| WEF | Slope (Uphill) | UE | 0.521 | 0.286 | +0.234 | +4.05 | 0.004 | 0.014 |
| WEF | Slope (Uphill) | PE | 0.509 | 0.276 | +0.233 | +4.26 | 0.002 | 0.009 |
| WEF | Stairs | NW | 0.286 | 0.260 | +0.026 | +1.62 | 0.141 | 0.318 |
| WEF | Stairs | UE | 0.284 | 0.275 | +0.009 | +0.65 | 0.534 | 0.747 |
| WEF | Stairs | PE | 0.282 | 0.282 | -0.000 | -0.01 | 0.995 | 0.995 |
| NL10 | Level | NW | 0.856 | 0.779 | +0.077 | +1.36 | 0.208 | 0.404 |
| NL10 | Level | UE | 0.857 | 0.823 | +0.034 | +0.62 | 0.552 | 0.752 |
| NL10 | Level | PE | 0.773 | 0.748 | +0.025 | +0.56 | 0.591 | 0.764 |
| NL10 | Slope (Downhill) | NW | 0.265 | 0.259 | +0.006 | +0.22 | 0.834 | 0.871 |
| NL10 | Slope (Downhill) | UE | 0.256 | 0.243 | +0.013 | +0.42 | 0.686 | 0.795 |
| NL10 | Slope (Downhill) | PE | 0.269 | 0.231 | +0.039 | +1.31 | 0.222 | 0.419 |
| NL10 | Slope (Uphill) | NW | 0.284 | 0.306 | -0.021 | -0.54 | 0.600 | 0.764 |
| NL10 | Slope (Uphill) | UE | 0.286 | 0.271 | +0.015 | +0.54 | 0.605 | 0.764 |
| NL10 | Slope (Uphill) | PE | 0.276 | 0.254 | +0.022 | +0.75 | 0.474 | 0.706 |
| NL10 | Stairs | NW | 0.260 | 0.274 | -0.015 | -2.16 | 0.059 | 0.159 |
| NL10 | Stairs | UE | 0.275 | 0.284 | -0.010 | -3.15 | 0.012 | 0.035 |
| NL10 | Stairs | PE | 0.282 | 0.292 | -0.009 | -3.35 | 0.009 | 0.027 |
| ΦB | Level | NW | 0.869 | 0.856 | +0.013 | +10.01 | <0.001 | <0.001 |
| ΦB | Level | UE | 0.870 | 0.857 | +0.013 | +13.83 | <0.001 | <0.001 |
| ΦB | Level | PE | 0.783 | 0.773 | +0.010 | +3.18 | 0.011 | 0.034 |
| ΦB | Slope (Downhill) | NW | 0.274 | 0.265 | +0.009 | +1.07 | 0.313 | 0.548 |
| ΦB | Slope (Downhill) | UE | 0.264 | 0.256 | +0.008 | +1.39 | 0.197 | 0.395 |
| ΦB | Slope (Downhill) | PE | 0.278 | 0.269 | +0.009 | +1.76 | 0.112 | 0.270 |
| ΦB | Slope (Uphill) | NW | 0.283 | 0.284 | -0.001 | -0.11 | 0.917 | 0.930 |
| ΦB | Slope (Uphill) | UE | 0.277 | 0.286 | -0.010 | -0.68 | 0.518 | 0.740 |
| ΦB | Slope (Uphill) | PE | 0.266 | 0.276 | -0.009 | -0.78 | 0.454 | 0.691 |
| ΦB | Stairs | NW | 0.261 | 0.260 | +0.002 | +0.46 | 0.657 | 0.793 |
| ΦB | Stairs | UE | 0.273 | 0.275 | -0.001 | -0.25 | 0.807 | 0.869 |
| ΦB | Stairs | PE | 0.287 | 0.282 | +0.005 | +1.16 | 0.275 | 0.494 |

Note: q = FDR-corrected p-value (Benjamini–Hochberg).

---

### Supplementary Table S5: Per-class F1 by terrain and feature set

**Scope**: Per-class F1 (NW/UE/PE) under LOSO, reported by terrain for F28 and F18 feature sets.

#### F28 (LOSO)

| Terrain | NW | UE | PE |
| --- | ---: | ---: | ---: |
| Level | 0.378 | 0.389 | 0.445 |
| Slope | 0.352 | 0.361 | 0.398 |
| Stairs | 0.367 | 0.392 | 0.391 |

#### F18 (LOSO)

| Terrain | NW | UE | PE |
| --- | ---: | ---: | ---: |
| Level | 0.385 | 0.398 | 0.443 |
| Slope | 0.338 | 0.349 | 0.379 |
| Stairs | 0.354 | 0.378 | 0.377 |

---

### Supplementary Table S6: Within-subject 5-fold stratified cross-validation performance (NOT subject-independent)

**Scope**: Within-subject 5-fold stratified CV on gait-cycle samples (n_folds = 5). Values are mean ± SD across folds.

| Model | Accuracy (Mean ± SD) | Macro-F1 (Mean ± SD) |
| --- | ---: | ---: |
| Random Forest | 0.9997 ± 0.0003 | 0.9997 ± 0.0003 |
| KNN (k = 15) | 0.9962 ± 0.0007 | 0.9962 ± 0.0007 |
| KNN (k = 5) | 0.9954 ± 0.0014 | 0.9955 ± 0.0014 |
| Logistic Regression | 0.8485 ± 0.0051 | 0.8489 ± 0.0051 |

*Note:* This 5-fold CV reuses subjects across train and test folds and is therefore not subject-independent; it is included only as a within-subject upper bound for comparison.

---

### Supplementary Table S7: Muscle-architecture parameters and Φ\_B scaling weights

**Scope**: Fixed literature-derived muscle-architecture parameters used to compute the diagonal Φ\_B scaling applied to per-channel feature vectors prior to channel fusion (bilateral muscles share the same parameters/weights). Weights are normalized to mean 1.0 across the five muscles.

| Muscle | PCSA (cm²) | Fast-twitch fraction (FT) | Pennation angle θ (deg) | Φ\_B weight (w) |
| --- | ---: | ---: | ---: | ---: |
| GM | 15.6 | 0.51 | 17.0 | 0.473 |
| TA | 6.5 | 0.27 | 9.6 | 1.072 |
| RF | 12.9 | 0.39 | 13.5 | 0.557 |
| TFL | 4.2 | 0.45 | 8.0 | 1.904 |
| BF | 8.7 | 0.67 | 11.9 | 0.994 |

*Note:* In the dataset, Φ\_B is applied to each left/right channel (GM\_L/GM\_R, TA\_L/TA\_R, etc.) using the same muscle-level weight.

---

### Supplementary Table S8: Small-label calibration curve values (leave-one-terrain-out; macro-F1; F28(+Φ\_B)+RF)

**Scope**: Numerical values corresponding to the small-label calibration curve shown in Fig. 5a (held-out terrain; labeled cycle×phase samples used to train a multinomial logistic regression calibrator on RF probabilities).

| Test terrain | 0 labels | 10 labels | 30 labels | 90 labels |
| --- | :---: | :---: | :---: | :---: |
| Level | 0.312 | 0.286 ± 0.021 | 0.400 ± 0.010 | 0.421 ± 0.007 |
| Slope | 0.323 | 0.299 ± 0.019 | 0.397 ± 0.010 | 0.416 ± 0.006 |
| Stairs | 0.387 | 0.452 ± 0.020 | 0.532 ± 0.008 | 0.549 ± 0.006 |

*Note:* Values are macro-F1 mean ± SD across 30 repeated label samplings (fixed seed=42), aggregated as subject unweighted mean (subject n = 10). The 0-label column has no post-hoc calibration, so no repeated-sampling variability is defined (reported as a single value).

## Supplementary Methods

### NL10 Feature Computation Details

| Feature | Formula/Method | Parameters |
| --- | --- | --- |
| Sample Entropy | SampEn(m, r, N) | m=2, r=0.2×SD |
| Approximate Entropy | ApEn(m, r, N) | m=2, r=0.2×SD |
| Permutation Entropy | PE(order, delay) | order=3, delay=1 |
| Higuchi FD | HFD(k_max) | k_max=10 |
| Katz FD | KFD | — |
| Hurst Exponent | R/S analysis | — |
| Recurrence Rate | RR(m, τ, ε) | m=2, τ=1, ε=0.1×max distance |
| Determinism | DET(lmin) | lmin=2 |
| Laminarity | LAM(vmin) | vmin=2 |
| Lyapunov Exponent | LE(m, τ) (Rosenstein) | m=2, τ=1 |

### Bootstrap CI Procedure

1. For each terrain, compute subject-level macro-F1 for F18 and F28 (10 pairs)
2. Compute paired differences: Δᵢ = F1(F28)ᵢ − F1(F18)ᵢ
3. Resample Δ with replacement (2,000 iterations)
4. Compute 2.5th and 97.5th percentiles
5. CI excludes 0 → statistically significant

### Tensor Data Structure

**Per-subject tensor shapes:**

- X_s10: (10 muscles, 8 phases, 10 PCA, 3 conditions, n_cycles)
- X_domain: (10 muscles, 3 domains, 8 phases, 7 wavelet, 3 conditions, n_cycles)

**Aggregate statistics:**

- Total tensor size: 120.92 MB (10 subjects)
- Mean coverage: 93.33%
- Cycles per subject: 556–629

---

## Supplementary Data Files

| File | Format | Description |
| --- | --- | --- |
| `ACCURACY_EVALUATION.json` | JSON | 5-fold CV results, confusion matrices |
| `TENSOR_LATENCY_BENCHMARK_DETAILED.json` | JSON | Latency by pipeline stage |
| `ablation_3module_rollup.csv` | CSV | Ablation summary statistics |
| `ablation_3comp_paired_stats.csv` | CSV | Full paired t-test results |
| `Figure3_Figure4_summary_v3.0.json` | JSON | Classification and transfer data |
| `Figure6_summary_v3.0.json` | JSON | Synergy analysis data |
| `subject_tensors/*.npz` | NPZ | Per-subject tensorized features |

---

## Supplementary Data schema notes

- **NPZ tensors (`subject_tensors/*.npz`)**: each file stores per-subject tensorized feature arrays; axis meanings and shapes are summarized in “Tensor Data Structure” (e.g., muscles × phases × features × conditions × cycles).
- **CSV correlation matrices**: matrices are 10×10 with consistent muscle/channel labels (GM/TA/RF/TFL/BF, bilateral), and off-diagonal summaries use the 45 unique upper-triangle pairs.
- **JSON results/benchmarks**: JSON files include run metadata and structured result fields (e.g., macro-F1 summaries, confusion matrices, latency stage breakdowns) for reproducibility.

End of Supplementary Materials.
