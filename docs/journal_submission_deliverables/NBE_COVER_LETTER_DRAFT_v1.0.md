# Cover Letter Draft for Nature Biomedical Engineering

**Version**: 1.5  
**Date**: 2026-02-05  
**Manuscript**: Real-time multi-terrain assistance state classification and calibration for cable-driven suits using biomechanically scaled sEMG

---

Dear Editors,

We submit the enclosed manuscript entitled "Real-time multi-terrain assistance state classification and calibration for cable-driven suits using biomechanically scaled sEMG" for consideration as an Article in *Nature Biomedical Engineering*.

**What is needed:** Closed-loop control of wearable gait assistance systems requires biosignal features that generalize across terrains and operate in real time. However, existing EMG classification studies are typically validated on single terrains, and the contribution of nonlinear dynamics features remains unquantified.

**What we show:** We designed a multistage sEMG-only pipeline that couples event-anchored 8-phase gait segmentation with a 28-dimensional feature space (F28: 18 time–frequency–wavelet features plus 10 nonlinear-dynamics features) and biomechanical muscle scaling. In a subject-independent leave-one-subject-out design across three terrains (level, slope, stairs) in 10 healthy adults, diagonal (in-terrain) macro-F1 ranged from 0.38 to 0.40, while off-diagonal (cross-terrain) macro-F1 ranged from 0.17 to 0.39. We further evaluated deployment-realistic calibration: leakage-free 0-label z-score normalization using only training-subject statistics improved the weakest cross-terrain ratios from 0.43–0.52 to 0.67–0.81 of diagonal performance. We additionally demonstrate leakage-safe unlabeled subject-window adaptation using only the first 4 gait cycles per recording file, which further improves the weakest transfers (level→slope 0.273→0.301; level→stairs 0.269→0.290). Inference-only latency was 1.36 ms (99th percentile 2.36 ms), while end-to-end latency for the deployment pathway (F18 + Random Forest inference) was 115 ms (99th percentile 182 ms) on Apple M1, clarifying the scope of real-time feasibility.

**Why this matters for NBE readers:** This work provides quantitative benchmarks—feature space design, terrain-dependent classification boundaries, calibration effects, and latency—that are directly relevant to researchers developing wearable exoskeletons, neural interfaces, and rehabilitation robotics. We transparently report limitations including limited cross-terrain generalization without calibration, the need for validation in clinical populations, and the absence of closed-loop control experiments.

We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree to its submission.

Sincerely,

Dong-Woo Lee  
Electronics and Telecommunications Research Institute (ETRI), Daejeon, Republic of Korea  
hermes@etri.re.kr
