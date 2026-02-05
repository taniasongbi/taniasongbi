#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
experiment_loso_cross_terrain_transfer_matrix_v1_0.py
=====================================================

Priority-1 experiment (NBE reviewer-facing):
Evaluate *true* generalization: **new subject + new terrain** simultaneously.

Design (as requested)
---------------------
- Keep LOSO (Leave-One-Subject-Out): hold out 1 subject as test.
- Within each LOSO fold, evaluate cross-terrain transfer in a 3×3 form:
    - Diagonal: in-terrain (train terrain == test terrain)
    - Off-diagonal: cross-terrain (train terrain != test terrain)

What this script produces
-------------------------
- 3×3 matrix of subject-level macro-F1 with 95% CI (bootstrap over subjects)
- Per-class F1 (mean + 95% CI) for each cell
- Confusion matrices aggregated across LOSO folds for each cell (counts)
- Optional "train on 2 terrains, test on held-out terrain" (leave-one-terrain-out) summary per test terrain

Data source (default)
---------------------
Uses the latest:
  results_v2/TERRAIN_COMPLETE_FROM_PIPELINE_v*/{walking,slope,stair}_28D_complete_from_pipeline.csv

Those tables are phase-wise cycle features aggregated over muscles:
  one 28D vector per (cycle, phase), where 28D = f18_01..f18_18 + nl_* (10 nonlinear).

Run
---
python -u scripts/experiment_loso_cross_terrain_transfer_matrix_v1_0.py

Outputs (default)
-----------------
results_v2/LOSO_CROSS_TERRAIN_TRANSFER_MATRIX_v1.0_<timestamp>/
  - macro_f1_matrix.csv
  - macro_f1_ratio_to_diagonal.csv
  - per_class_f1_long.csv
  - confusion_matrix_counts__train-<T>__test-<T>.csv  (9 files)
  - leave_one_terrain_out_summary.csv
  - results.json
  - Figure_LOSO_CrossTerrain_TransferMatrix_v1.0.png/.pdf
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]
from sklearn.ensemble import RandomForestClassifier  # pyright: ignore[reportMissingImports]
from sklearn.metrics import confusion_matrix, f1_score  # pyright: ignore[reportMissingImports]
from sklearn.preprocessing import LabelEncoder, StandardScaler  # pyright: ignore[reportMissingImports]


def _import_settings():
    """
    Make this script runnable both in editable-install mode (`pip install -e .`)
    and as a plain repo script (by adding ./src to sys.path).
    """
    try:
        from nbe_pipeline import settings as S  # type: ignore

        return S
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root / "src"))
        from nbe_pipeline import settings as S  # type: ignore

        return S


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _latest_dir(glob_pat: str, *, root: Path) -> Path:
    hits = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hits:
        raise FileNotFoundError(f"No matches under {root}: {glob_pat}")
    # hits are typically files; return parent if the pattern includes a file
    return hits[0].parent if hits[0].is_file() else hits[0]


def _infer_subject_from_file(file_value: str) -> str:
    """
    Robust subject id extraction from file/run id.
    Examples:
      - 241211_1_walking_no_suit.csv -> 241211_1
      - 241211_1slope_with_suit.csv  -> 241211_1
      - 241216_2 slope.csv           -> 241216_2
    """
    s = str(file_value).strip()
    m = re.match(r"^(\d{6})_(\d+)", s)
    if not m:
        return ""
    return f"{m.group(1)}_{m.group(2)}"


def _map_cond_to_paper(cond: str, *, cond_short: dict[str, str]) -> str:
    c = str(cond)
    return cond_short.get(c, c)


def _map_terrain_to_paper(terrain_key: str) -> str:
    t = str(terrain_key).strip().lower()
    # Terrain_COMPLETE_FROM_PIPELINE tables use: walking|slope|stair
    return {"walking": "Level", "slope": "Slope", "stair": "Stairs"}.get(t, terrain_key)


def _bootstrap_mean_ci(values: np.ndarray, *, rng: np.random.Generator, n_boot: int) -> tuple[float, float, float]:
    """
    Mean and 95% CI via bootstrap over subjects.
    """
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(np.mean(x))
    if x.size < 2 or int(n_boot) <= 0:
        return mean, mean, mean
    boots = [float(np.mean(rng.choice(x, size=x.size, replace=True))) for _ in range(int(n_boot))]
    lo, hi = np.percentile(np.asarray(boots, dtype=float), [2.5, 97.5]).tolist()
    return mean, float(lo), float(hi)


def _sample_stratified_indices(y: np.ndarray, n: int, *, rng: np.random.Generator) -> np.ndarray:
    """
    Stratified sampling of indices for small-label calibration.
    - Tries to allocate samples roughly equally across present classes.
    - Uses replacement only if a class has fewer than its quota.
    """
    y = np.asarray(y, dtype=int).reshape(-1)
    n = int(n)
    if n <= 0 or y.size == 0:
        return np.zeros(0, dtype=int)
    n = min(n, int(y.size))
    classes = np.unique(y)
    if classes.size == 0:
        return np.zeros(0, dtype=int)

    idx_by = {int(c): np.where(y == int(c))[0] for c in classes.tolist()}
    base = n // int(classes.size)
    rem = n % int(classes.size)

    cls_order = classes.copy()
    rng.shuffle(cls_order)
    picked: list[np.ndarray] = []
    for k, c in enumerate(cls_order.tolist()):
        q = int(base + (1 if k < rem else 0))
        if q <= 0:
            continue
        pool = idx_by[int(c)]
        if pool.size == 0:
            continue
        replace = bool(pool.size < q)
        chosen = rng.choice(pool, size=q, replace=replace)
        picked.append(np.asarray(chosen, dtype=int).reshape(-1))

    if not picked:
        # fallback: uniform random
        return np.asarray(rng.choice(np.arange(y.size), size=n, replace=False), dtype=int)

    out = np.concatenate(picked, axis=0).astype(int, copy=False)
    rng.shuffle(out)
    if out.size < n:
        # top-up if needed
        need = int(n - out.size)
        all_idx = np.arange(y.size)
        extra = rng.choice(all_idx, size=need, replace=bool(all_idx.size < need))
        out = np.concatenate([out, np.asarray(extra, dtype=int).reshape(-1)], axis=0)
        rng.shuffle(out)
    elif out.size > n:
        out = out[:n]
    return out


@dataclass(frozen=True)
class CellAgg:
    macro_f1_by_subject: dict[str, float]
    per_class_f1_by_subject: dict[str, np.ndarray]  # subject -> (n_classes,)
    cm_counts: np.ndarray  # summed counts over subjects (n_classes,n_classes)
    n_test_samples: int


def _eval_subject(
    *,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    labels_idx: np.ndarray,
    clf: RandomForestClassifier,
) -> tuple[float, np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)
    clf.fit(Xtr, y_train)
    pred = clf.predict(Xte)

    macro = float(f1_score(y_test, pred, average="macro", labels=labels_idx, zero_division=0))
    per_class = np.asarray(
        f1_score(y_test, pred, average=None, labels=labels_idx, zero_division=0), dtype=float
    ).reshape(-1)
    cm = confusion_matrix(y_test, pred, labels=labels_idx)
    return macro, per_class, cm


def _make_transfer_matrix_figure(
    out_png: Path,
    out_pdf: Path,
    *,
    terrains: list[str],
    macro_mean: np.ndarray,
    macro_ci_lo: np.ndarray,
    macro_ci_hi: np.ndarray,
    title: str,
) -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 9,
            "axes.linewidth": 0.8,
            "figure.dpi": 300,
        }
    )

    n = len(terrains)
    fig = plt.figure(figsize=(9.5, 7.5))
    ax = fig.add_subplot(1, 1, 1)

    im = ax.imshow(macro_mean, cmap="RdYlGn", vmin=0.0, vmax=1.0, aspect="equal")
    for i in range(n):
        for j in range(n):
            m = float(macro_mean[i, j])
            lo = float(macro_ci_lo[i, j])
            hi = float(macro_ci_hi[i, j])
            if not np.isfinite(m):
                txt = "N/A"
                ci_txt = ""
            else:
                txt = f"{m:.3f}"
                ci_txt = f"[{lo:.2f}, {hi:.2f}]"
            color = "white" if np.isfinite(m) and m < 0.65 else "black"
            ax.text(j, i - 0.12, txt, ha="center", va="center", fontsize=12, fontweight="bold", color=color)
            if ci_txt:
                ax.text(j, i + 0.25, ci_txt, ha="center", va="center", fontsize=8, color=color)
            # diagonal highlight
            if i == j:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="gold", linewidth=2.5))

    ax.set_xticks(range(n))
    ax.set_xticklabels(terrains, fontsize=11, fontweight="bold")
    ax.set_yticks(range(n))
    ax.set_yticklabels(terrains, fontsize=11, fontweight="bold")
    ax.set_xlabel("Test Terrain (held-out subject)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Train Terrain (non-heldout subjects)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")

    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Macro F1 (subject-level)", fontsize=10, fontweight="bold")

    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    S = _import_settings()

    ap = argparse.ArgumentParser(description="LOSO + cross-terrain transfer matrix (true generalization).")
    ap.add_argument(
        "--complete-dir",
        default=None,
        help="Directory containing *_28D_complete_from_pipeline.csv files. If omitted, auto-picks the latest under results_v2/.",
    )
    ap.add_argument(
        "--n-bootstrap",
        type=int,
        default=2000,
        help="Bootstrap iterations for 95%% CI over subjects (default: 2000).",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rf-n-estimators", type=int, default=200)
    ap.add_argument("--rf-max-depth", type=int, default=None)
    ap.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: results_v2/LOSO_CROSS_TERRAIN_TRANSFER_MATRIX_v1.0_<ts>/).",
    )
    ap.add_argument(
        "--include_leave_one_terrain_out",
        action="store_true",
        help="Also compute (train on other 2 terrains, test on held-out terrain) per test terrain.",
    )
    ap.add_argument(
        "--calibration",
        choices=[
            "none",
            "subject_global",
            "subject_by_terrain",
            "train_only_by_terrain",
            "test_window_by_terrain",
        ],
        default="none",
        help=(
            "0-label (unsupervised) calibration applied to features before training/testing. "
            "'subject_global' uses z-score per subject over all terrains; "
            "'subject_by_terrain' uses z-score per (subject, terrain); "
            "'train_only_by_terrain' uses per-terrain z-score computed ONLY from non-heldout subjects "
            "(no test-subject distribution; requires terrain label). "
            "'test_window_by_terrain' uses a leakage-safe calibration window on the held-out subject: "
            "per-(subject,test_terrain) mean/std are computed from the first N cycles per recording file "
            "(unlabeled) and applied to the remaining cycles for evaluation."
        ),
    )
    ap.add_argument(
        "--test-calib-cycles-per-file",
        type=int,
        default=4,
        help=(
            "For calibration='test_window_by_terrain': number of initial gait cycles per recording file "
            "used as an unlabeled calibration window on the held-out subject (default: 4). "
            "Evaluation excludes these calibration cycles."
        ),
    )
    ap.add_argument(
        "--label-calib-budgets",
        default="",
        help=(
            "Comma-separated TOTAL labeled samples to use for small-label calibration on the held-out subject "
            "(per test terrain, per cell). Example: '0,10,30,90'. Empty disables label calibration curves."
        ),
    )
    ap.add_argument(
        "--label-calib-repeats",
        type=int,
        default=1,
        help=(
            "For small-label calibration curves: repeat random sampling this many times per budget "
            "(default: 1). Use 20–50 to estimate sampling variability (mean±CI)."
        ),
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    results_v2 = repo_root / "results_v2"

    if args.complete_dir:
        complete_dir = Path(args.complete_dir).expanduser().resolve()
    else:
        # Pick latest complete-from-pipeline dir by status.json existence
        complete_dir = _latest_dir("TERRAIN_COMPLETE_FROM_PIPELINE_v*/status.json", root=results_v2)

    out_dir = (
        Path(args.out_dir).expanduser().resolve()
        if args.out_dir
        else (results_v2 / f"LOSO_CROSS_TERRAIN_TRANSFER_MATRIX_v1.0_{_now_tag()}").resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # Separate RNG streams so enabling repeated label-calibration sampling does not perturb bootstrap CIs.
    rng_boot = np.random.default_rng(int(args.seed))
    rng_cal = np.random.default_rng(int(args.seed) + 12345)

    terrain_internal = ["walking", "slope", "stair"]
    terrain_paper = [_map_terrain_to_paper(t) for t in terrain_internal]
    terrain_paper_order = list(getattr(S, "TERRAIN_PAPER_ORDER", ("Level", "Slope", "Stairs")))
    # Ensure consistent order
    terrains = [t for t in terrain_paper_order if t in set(terrain_paper)]

    cond_short = dict(getattr(S, "CONDITION_LABEL_SHORT", {"no_suit": "NW", "motor_off": "UE", "motor_on": "PE"}))
    f28_cols = list(getattr(S, "F28_COLS", []))
    if not f28_cols:
        f28_cols = [f"f18_{i:02d}" for i in range(1, 19)] + [
            "nl_SampEn",
            "nl_ApEn",
            "nl_PE",
            "nl_HFD",
            "nl_KFD",
            "nl_Hurst",
            "nl_RR",
            "nl_DET",
            "nl_LAM",
            "nl_LyapExp",
        ]

    status = {
        "tool": Path(__file__).name,
        "version": "v1.0",
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "inputs": {
            "complete_dir": str(complete_dir),
            "n_bootstrap": int(args.n_bootstrap),
            "seed": int(args.seed),
            "calibration": str(args.calibration),
            "test_calib_cycles_per_file": int(args.test_calib_cycles_per_file),
            "label_calib_budgets": str(args.label_calib_budgets),
            "rf": {"n_estimators": int(args.rf_n_estimators), "max_depth": args.rf_max_depth},
        },
        "outputs": {"out_dir": str(out_dir)},
    }
    _atomic_write_json(out_dir / "status.json", status)

    # -------------------------------
    # Load data
    # -------------------------------
    parts = []
    for t in terrain_internal:
        fp = complete_dir / f"{t}_28D_complete_from_pipeline.csv"
        if not fp.exists():
            raise FileNotFoundError(f"Missing terrain table: {fp}")
        df = pd.read_csv(fp)
        parts.append(df)
    df_all = pd.concat(parts, ignore_index=True)

    # Standardize columns
    if "file" not in df_all.columns or "terrain" not in df_all.columns or "cond" not in df_all.columns:
        raise ValueError("Expected columns: file, terrain, cond")

    df_all["subject"] = df_all["file"].astype(str).map(_infer_subject_from_file)
    if (df_all["subject"] == "").any():
        n_bad = int((df_all["subject"] == "").sum())
        raise ValueError(f"Failed to infer subject for {n_bad} rows (check file naming).")

    df_all["terrain_paper"] = df_all["terrain"].astype(str).map(_map_terrain_to_paper)
    df_all["cond_paper"] = df_all["cond"].astype(str).map(lambda c: _map_cond_to_paper(c, cond_short=cond_short))

    # Keep only terrains in our matrix
    df_all = df_all[df_all["terrain_paper"].isin(terrains)].copy()

    # Feature columns intersection (robust to missing columns)
    feat_cols = [c for c in f28_cols if c in df_all.columns]
    if len(feat_cols) < 18:
        raise ValueError(f"Too few feature columns found: {len(feat_cols)} (expected 28).")

    # Drop rows with missing feature(s) or missing labels
    need_cols = feat_cols + ["subject", "terrain_paper", "cond_paper"]
    df_all = df_all.dropna(subset=need_cols).copy()

    # -------------------------------
    # Optional 0-label calibration (subject-wise z-score)
    # -------------------------------
    calib = str(args.calibration).strip().lower()
    if calib in ("subject_global", "subject_by_terrain"):
        if calib == "subject_global":
            keys = ["subject"]
        else:
            keys = ["subject", "terrain_paper"]

        grp = df_all.groupby(keys, sort=False)
        mu = grp[feat_cols].transform("mean")
        sd = grp[feat_cols].transform("std")
        # avoid divide-by-zero; std can be 0 for constant features within a group
        sd = sd.replace(0.0, np.nan)
        df_all.loc[:, feat_cols] = (df_all[feat_cols] - mu) / (sd + 1e-12)
        # Any remaining NaNs (tiny groups/constant) -> 0 (neutral after z-score)
        df_all.loc[:, feat_cols] = df_all[feat_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    elif calib in ("none", "train_only_by_terrain", "test_window_by_terrain"):
        # handled later (train_only_by_terrain) or no calibration (none)
        pass
    else:
        raise ValueError(f"Unknown calibration mode: {calib}")

    # Encode labels to stable order [NW, UE, PE] if present
    le = LabelEncoder()
    le.fit(df_all["cond_paper"].astype(str).to_numpy())
    classes = list(le.classes_)
    labels_idx = np.arange(len(classes), dtype=int)

    # Ensure paper order NW/UE/PE if possible
    desired = ["NW", "UE", "PE"]
    if set(desired).issubset(set(classes)):
        classes = desired
        # rebuild encoder to force order
        le = LabelEncoder()
        le.fit(np.array(classes, dtype=str))
        labels_idx = np.arange(len(classes), dtype=int)
        df_all["y"] = le.transform(df_all["cond_paper"].astype(str).to_numpy())
    else:
        df_all["y"] = le.transform(df_all["cond_paper"].astype(str).to_numpy())

    subjects = sorted(df_all["subject"].unique().tolist())
    if len(subjects) < 3:
        raise ValueError(f"Need >=3 subjects for LOSO; got {len(subjects)}")

    # parse label calibration budgets (total labeled samples)
    label_budgets: list[int] = []
    if str(args.label_calib_budgets).strip():
        toks = [t.strip() for t in str(args.label_calib_budgets).split(",") if t.strip()]
        label_budgets = sorted({int(t) for t in toks if int(t) >= 0})
        if 0 not in label_budgets:
            label_budgets = [0] + label_budgets

    # -------------------------------
    # LOSO transfer matrix (single-terrain train)
    # -------------------------------
    n_t = len(terrains)
    n_c = len(classes)
    macro_by_cell: dict[tuple[int, int], dict[str, float]] = {(i, j): {} for i in range(n_t) for j in range(n_t)}
    perclass_by_cell: dict[tuple[int, int], dict[str, np.ndarray]] = {(i, j): {} for i in range(n_t) for j in range(n_t)}
    cm_by_cell: dict[tuple[int, int], np.ndarray] = {(i, j): np.zeros((n_c, n_c), dtype=int) for i in range(n_t) for j in range(n_t)}
    n_test_by_cell: dict[tuple[int, int], int] = {(i, j): 0 for i in range(n_t) for j in range(n_t)}

    # For small-label calibration curves: macro-F1 by (cell, budget, subject)
    macro_by_cell_budget: dict[tuple[int, int], dict[int, dict[str, float]]] = {}
    n_eval_by_cell_budget: dict[tuple[int, int], dict[int, int]] = {}
    if label_budgets:
        macro_by_cell_budget = {(i, j): {b: {} for b in label_budgets} for i in range(n_t) for j in range(n_t)}
        n_eval_by_cell_budget = {(i, j): {b: 0 for b in label_budgets} for i in range(n_t) for j in range(n_t)}

    # Per-subject loop; train once per (heldout_subject, train_terrain) and test on all test terrains
    # Note: label calibration (if enabled) is applied ONLY to held-out subject samples via a lightweight post-hoc layer,
    #       without retraining the RF.
    eps_prob = 1e-6
    LogisticRegression = None
    if label_budgets and max(label_budgets) > 0:
        from sklearn.linear_model import LogisticRegression as _LR  # pyright: ignore[reportMissingImports]

        LogisticRegression = _LR

    for subj in subjects:
        df_test_subj = df_all[df_all["subject"] == subj]
        test_by_terr_full = {t: df_test_subj[df_test_subj["terrain_paper"] == t] for t in terrains}

        # For leakage-safe test-window calibration, split held-out subject data into:
        # - calibration window: first N cycles per file (unlabeled)
        # - evaluation window: remaining cycles (used for scoring)
        test_calib_by_terr = {t: pd.DataFrame() for t in terrains}
        test_eval_by_terr = {t: pd.DataFrame() for t in terrains}
        if calib == "test_window_by_terrain":
            n_cyc = int(max(0, int(args.test_calib_cycles_per_file)))
            for t in terrains:
                df_t = test_by_terr_full[t]
                if df_t.empty or n_cyc <= 0:
                    test_eval_by_terr[t] = df_t
                    continue
                # Select first N unique cycles per file (cycle column is expected)
                if "cycle" not in df_t.columns:
                    # fallback: no split if cycle not present
                    test_eval_by_terr[t] = df_t
                    continue
                cyc_col = pd.to_numeric(df_t["cycle"], errors="coerce")
                df_t = df_t.assign(_cycle_num=cyc_col).dropna(subset=["_cycle_num"])
                if df_t.empty:
                    test_eval_by_terr[t] = df_t.drop(columns=["_cycle_num"], errors="ignore")
                    continue

                sel_pairs: set[tuple[str, int]] = set()
                for file_key, g in df_t.groupby("file", sort=False):
                    # sort by cycle number (proxy for within-file order)
                    uniq = np.sort(g["_cycle_num"].astype(int).unique())
                    take = uniq[:n_cyc]
                    for c in take:
                        sel_pairs.add((str(file_key), int(c)))

                is_cal = df_t.apply(lambda r: (str(r["file"]), int(r["_cycle_num"])) in sel_pairs, axis=1)
                df_cal = df_t[is_cal].drop(columns=["_cycle_num"], errors="ignore")
                df_ev = df_t[~is_cal].drop(columns=["_cycle_num"], errors="ignore")

                test_calib_by_terr[t] = df_cal
                test_eval_by_terr[t] = df_ev
        else:
            test_eval_by_terr = test_by_terr_full

        # For test-window personalization, normalize TRAINING subjects per (subject, terrain) using training data only.
        # This removes subject-specific offsets/scales without using any held-out subject distribution.
        df_train_norm_all = None
        if calib == "test_window_by_terrain":
            df_train_norm_all = df_all[df_all["subject"] != subj].copy()
            grp_tr = df_train_norm_all.groupby(["subject", "terrain_paper"], sort=False)
            mu_tr = grp_tr[feat_cols].transform("mean")
            sd_tr = grp_tr[feat_cols].transform("std").replace(0.0, np.nan)
            df_train_norm_all.loc[:, feat_cols] = (df_train_norm_all[feat_cols] - mu_tr) / (sd_tr + 1e-12)
            df_train_norm_all.loc[:, feat_cols] = (
                df_train_norm_all[feat_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
            )

        # Train-only (no test-subject distribution) calibration stats:
        # per-terrain mean/std computed from non-heldout subjects only.
        df_train_subj_all = None
        mu_by_terr = None
        sd_by_terr = None
        if calib in ("train_only_by_terrain", "test_window_by_terrain"):
            df_train_subj_all = df_all[df_all["subject"] != subj]
            mu_by_terr = df_train_subj_all.groupby("terrain_paper", sort=False)[feat_cols].mean()
            sd_by_terr = df_train_subj_all.groupby("terrain_paper", sort=False)[feat_cols].std().replace(0.0, np.nan)

        for i, train_t in enumerate(terrains):
            if calib == "test_window_by_terrain" and df_train_norm_all is not None:
                df_train = df_train_norm_all[df_train_norm_all["terrain_paper"] == train_t]
            else:
                df_train = df_all[(df_all["subject"] != subj) & (df_all["terrain_paper"] == train_t)]
            if df_train.empty:
                continue

            X_train = df_train[feat_cols].to_numpy(dtype=float)
            y_train = df_train["y"].to_numpy(dtype=int)

            if calib == "train_only_by_terrain" and mu_by_terr is not None and sd_by_terr is not None:
                if train_t in mu_by_terr.index:
                    mu_tr = mu_by_terr.loc[train_t, feat_cols].to_numpy(dtype=float)
                    sd_tr = sd_by_terr.loc[train_t, feat_cols].to_numpy(dtype=float)
                else:
                    # Fallback: global stats over non-heldout subjects (should be rare).
                    assert df_train_subj_all is not None
                    mu_tr = df_train_subj_all[feat_cols].mean(axis=0).to_numpy(dtype=float)
                    sd_tr = df_train_subj_all[feat_cols].std(axis=0).replace(0.0, np.nan).to_numpy(dtype=float)
                X_train = (X_train - mu_tr) / (sd_tr + 1e-12)
                X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)

            # Fit scaler once per model
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            model = RandomForestClassifier(
                n_estimators=int(args.rf_n_estimators),
                max_depth=None if args.rf_max_depth is None else int(args.rf_max_depth),
                random_state=int(args.seed),
                n_jobs=-1,
            )
            model.fit(X_train_s, y_train)

            for j, test_t in enumerate(terrains):
                df_test = test_eval_by_terr[test_t]
                if df_test.empty:
                    continue
                X_test = df_test[feat_cols].to_numpy(dtype=float)
                y_test = df_test["y"].to_numpy(dtype=int)

                if calib in ("train_only_by_terrain", "test_window_by_terrain") and mu_by_terr is not None and sd_by_terr is not None:
                    if test_t in mu_by_terr.index:
                        mu_te = mu_by_terr.loc[test_t, feat_cols].to_numpy(dtype=float)
                        sd_te = sd_by_terr.loc[test_t, feat_cols].to_numpy(dtype=float)
                    else:
                        # Fallback: global stats over non-heldout subjects (should be rare).
                        assert df_train_subj_all is not None
                        mu_te = df_train_subj_all[feat_cols].mean(axis=0).to_numpy(dtype=float)
                        sd_te = df_train_subj_all[feat_cols].std(axis=0).replace(0.0, np.nan).to_numpy(dtype=float)

                    if calib == "test_window_by_terrain":
                        # Use held-out subject calibration window (unlabeled) to estimate subject×terrain stats.
                        df_cal = test_calib_by_terr.get(test_t, pd.DataFrame())
                        if df_cal is not None and (not df_cal.empty):
                            mu_sub = df_cal[feat_cols].mean(axis=0).to_numpy(dtype=float)
                            sd_sub = (
                                df_cal[feat_cols].std(axis=0).replace(0.0, np.nan).to_numpy(dtype=float)
                            )
                            # Subject-window z-score on test eval subset (leakage-safe).
                            X_test = (X_test - mu_sub) / (sd_sub + 1e-12)
                        else:
                            # Fallback to train-only stats if calibration window missing.
                            X_test = (X_test - mu_te) / (sd_te + 1e-12)
                    else:
                        X_test = (X_test - mu_te) / (sd_te + 1e-12)

                    X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
                X_test_s = scaler.transform(X_test)
                proba = model.predict_proba(X_test_s)
                pred = np.asarray(model.classes_, dtype=int)[np.argmax(proba, axis=1)]

                macro = float(f1_score(y_test, pred, average="macro", labels=labels_idx, zero_division=0))
                per_cls = np.asarray(
                    f1_score(y_test, pred, average=None, labels=labels_idx, zero_division=0), dtype=float
                ).reshape(-1)
                cm = confusion_matrix(y_test, pred, labels=labels_idx)

                macro_by_cell[(i, j)][subj] = macro
                perclass_by_cell[(i, j)][subj] = per_cls
                cm_by_cell[(i, j)] += cm.astype(int)
                n_test_by_cell[(i, j)] += int(len(y_test))

                # label calibration curve (post-hoc, small labeled subset of held-out subject)
                if label_budgets:
                    # budget=0 uses the same macro on the full test set
                    macro_by_cell_budget[(i, j)][0][subj] = macro
                    n_eval_by_cell_budget[(i, j)][0] += int(len(y_test))

                    if LogisticRegression is None or int(len(y_test)) < 5:
                        continue

                    Xp_all = np.log(np.clip(proba, eps_prob, 1.0)).astype(float, copy=False)
                    all_idx = np.arange(int(len(y_test)), dtype=int)

                    for b in label_budgets:
                        if int(b) <= 0:
                            continue
                        # Ensure at least 1 sample remains for evaluation
                        n_cal = int(min(int(b), max(0, int(len(y_test) - 1))))
                        if n_cal <= 0:
                            continue

                        cal_idx = _sample_stratified_indices(y_test, n_cal, rng=rng_cal)
                        # unique indices for evaluation holdout
                        cal_unique = np.unique(cal_idx)
                        eval_idx = all_idx[~np.isin(all_idx, cal_unique)]
                        if eval_idx.size < 1:
                            continue

                        y_cal = y_test[cal_idx]
                        y_eval = y_test[eval_idx]
                        X_cal = Xp_all[cal_idx, :]
                        X_eval = Xp_all[eval_idx, :]

                        # If calibration set lacks class diversity, fall back to base predictions on eval subset.
                        if np.unique(y_cal).size < 2:
                            pred_eval = pred[eval_idx]
                        else:
                            lr = LogisticRegression(
                                solver="lbfgs",
                                max_iter=1000,
                                C=1.0,
                            )
                            lr.fit(X_cal, y_cal)
                            pred_eval = lr.predict(X_eval)

                        macro_b = float(f1_score(y_eval, pred_eval, average="macro", labels=labels_idx, zero_division=0))
                        macro_by_cell_budget[(i, j)][int(b)][subj] = macro_b
                        n_eval_by_cell_budget[(i, j)][int(b)] += int(eval_idx.size)

    # Aggregate to mean + CI
    macro_mean = np.full((n_t, n_t), np.nan, dtype=float)
    macro_ci_lo = np.full((n_t, n_t), np.nan, dtype=float)
    macro_ci_hi = np.full((n_t, n_t), np.nan, dtype=float)

    per_class_rows = []
    macro_rows = []

    for i, train_t in enumerate(terrains):
        for j, test_t in enumerate(terrains):
            vals = np.array(list(macro_by_cell[(i, j)].values()), dtype=float)
            mean, lo, hi = _bootstrap_mean_ci(vals, rng=rng_boot, n_boot=int(args.n_bootstrap))
            macro_mean[i, j] = mean
            macro_ci_lo[i, j] = lo
            macro_ci_hi[i, j] = hi

            macro_rows.append(
                {
                    "train_terrain": train_t,
                    "test_terrain": test_t,
                    "macro_f1_mean": mean,
                    "macro_f1_ci_low": lo,
                    "macro_f1_ci_high": hi,
                    "n_subjects": int(len(vals)),
                    "n_test_samples": int(n_test_by_cell[(i, j)]),
                }
            )

            # Per-class summary
            sub_map = perclass_by_cell[(i, j)]
            if not sub_map:
                continue
            mat = np.stack(list(sub_map.values()), axis=0).astype(float)  # (n_subjects, n_classes)
            for c_idx, c_name in enumerate(classes):
                m, lo_c, hi_c = _bootstrap_mean_ci(mat[:, c_idx], rng=rng_boot, n_boot=int(args.n_bootstrap))
                per_class_rows.append(
                    {
                        "train_terrain": train_t,
                        "test_terrain": test_t,
                        "class": c_name,
                        "f1_mean": m,
                        "f1_ci_low": lo_c,
                        "f1_ci_high": hi_c,
                        "n_subjects": int(mat.shape[0]),
                    }
                )

    df_macro = pd.DataFrame(macro_rows)
    df_macro.to_csv(out_dir / "macro_f1_matrix.csv", index=False)

    df_per_class = pd.DataFrame(per_class_rows)
    df_per_class.to_csv(out_dir / "per_class_f1_long.csv", index=False)

    # Ratio to diagonal (per test terrain baseline)
    ratio = np.full_like(macro_mean, np.nan, dtype=float)
    for j in range(n_t):
        denom = float(macro_mean[j, j])
        if not np.isfinite(denom) or denom <= 0:
            continue
        ratio[:, j] = macro_mean[:, j] / denom
    ratio_df = pd.DataFrame(ratio, index=terrains, columns=terrains)
    ratio_df.index.name = "train_terrain"
    ratio_df.to_csv(out_dir / "macro_f1_ratio_to_diagonal.csv")

    # Optional: calibration curve outputs (macro-F1 vs labeled budget)
    calib_curve_rows = []
    if label_budgets:
        for b in label_budgets:
            macro_mean_b = np.full((n_t, n_t), np.nan, dtype=float)
            for i, train_t in enumerate(terrains):
                for j, test_t in enumerate(terrains):
                    vals = np.array(list(macro_by_cell_budget[(i, j)][int(b)].values()), dtype=float)
                    mean_b, lo_b, hi_b = _bootstrap_mean_ci(vals, rng=rng_boot, n_boot=int(args.n_bootstrap))
                    macro_mean_b[i, j] = mean_b
                    calib_curve_rows.append(
                        {
                            "label_budget": int(b),
                            "train_terrain": train_t,
                            "test_terrain": test_t,
                            "macro_f1_mean": mean_b,
                            "macro_f1_ci_low": lo_b,
                            "macro_f1_ci_high": hi_b,
                            "n_subjects": int(vals.size),
                            "n_eval_samples": int(n_eval_by_cell_budget[(i, j)][int(b)]),
                        }
                    )

            # also write a convenient matrix CSV per budget
            df_mat_b = pd.DataFrame(macro_mean_b, index=terrains, columns=terrains)
            df_mat_b.index.name = "train_terrain"
            df_mat_b.to_csv(out_dir / f"label_calibration_macro_f1_matrix__budget-{int(b)}.csv")

            # ratio-to-diagonal per budget
            ratio_b = np.full_like(macro_mean_b, np.nan, dtype=float)
            for j in range(n_t):
                denom = float(macro_mean_b[j, j])
                if not np.isfinite(denom) or denom <= 0:
                    continue
                ratio_b[:, j] = macro_mean_b[:, j] / denom
            ratio_b_df = pd.DataFrame(ratio_b, index=terrains, columns=terrains)
            ratio_b_df.index.name = "train_terrain"
            ratio_b_df.to_csv(out_dir / f"label_calibration_ratio_to_diagonal__budget-{int(b)}.csv")

        pd.DataFrame(calib_curve_rows).to_csv(out_dir / "label_calibration_curve_macro_f1_long.csv", index=False)

    # Confusion matrices per cell (counts)
    for i, train_t in enumerate(terrains):
        for j, test_t in enumerate(terrains):
            cm = cm_by_cell[(i, j)]
            cm_df = pd.DataFrame(cm, index=classes, columns=classes)
            cm_df.index.name = "true"
            cm_df.columns.name = "pred"
            cm_df.to_csv(out_dir / f"confusion_matrix_counts__train-{train_t}__test-{test_t}.csv")

    # Optional: "train on other 2 terrains" (leave-one-terrain-out) per held-out subject and test terrain
    loo_rows = []
    loo_curve_rows = []
    loo_curve_repeats_rows = []
    loo_curve_repeats_long_rows = []
    if bool(args.include_leave_one_terrain_out):
        label_repeats = int(max(1, int(args.label_calib_repeats)))
        for test_t in terrains:
            vals = []
            # label calibration curve storage for this test terrain
            vals_by_budget: dict[int, list[float]] = {int(b): [] for b in label_budgets} if label_budgets else {}
            # if repeating, store per-subject mean across repeats (for subject-bootstrap CI) + per-repeat means (for sampling variability)
            subj_mean_by_budget: dict[int, list[float]] = (
                {int(b): [] for b in label_budgets if int(b) > 0} if label_budgets else {}
            )
            rep_vals_by_budget: dict[int, list[list[float]]] = (
                {int(b): [[] for _ in range(label_repeats)] for b in label_budgets if int(b) > 0} if label_budgets else {}
            )

            for subj in subjects:
                df_train = df_all[(df_all["subject"] != subj) & (df_all["terrain_paper"] != test_t)]
                df_test = df_all[(df_all["subject"] == subj) & (df_all["terrain_paper"] == test_t)]
                if df_train.empty or df_test.empty:
                    continue
                X_train = df_train[feat_cols].to_numpy(dtype=float)
                y_train = df_train["y"].to_numpy(dtype=int)
                X_test = df_test[feat_cols].to_numpy(dtype=float)
                y_test = df_test["y"].to_numpy(dtype=int)

                scaler = StandardScaler()
                Xtr = scaler.fit_transform(X_train)
                Xte = scaler.transform(X_test)
                model = RandomForestClassifier(
                    n_estimators=int(args.rf_n_estimators),
                    max_depth=None if args.rf_max_depth is None else int(args.rf_max_depth),
                    random_state=int(args.seed),
                    n_jobs=-1,
                )
                model.fit(Xtr, y_train)
                proba = model.predict_proba(Xte)
                pred = np.asarray(model.classes_, dtype=int)[np.argmax(proba, axis=1)]
                f1m = float(f1_score(y_test, pred, average="macro", labels=labels_idx, zero_division=0))
                vals.append(f1m)

                # label calibration curve for leave-one-terrain-out (per test terrain)
                if label_budgets:
                    vals_by_budget[0].append(float(f1m))
                    if LogisticRegression is None or int(len(y_test)) < 5:
                        continue
                    Xp_all = np.log(np.clip(proba, eps_prob, 1.0)).astype(float, copy=False)
                    all_idx = np.arange(int(len(y_test)), dtype=int)
                    for b in label_budgets:
                        if int(b) <= 0:
                            continue
                        n_cal = int(min(int(b), max(0, int(len(y_test) - 1))))
                        if n_cal <= 0:
                            continue
                        rep_f1s: list[float] = []
                        for r in range(label_repeats):
                            cal_idx = _sample_stratified_indices(y_test, n_cal, rng=rng_cal)
                            cal_unique = np.unique(cal_idx)
                            eval_idx = all_idx[~np.isin(all_idx, cal_unique)]
                            if eval_idx.size < 1:
                                continue
                            y_cal = y_test[cal_idx]
                            y_eval = y_test[eval_idx]
                            X_cal = Xp_all[cal_idx, :]
                            X_eval = Xp_all[eval_idx, :]
                            if np.unique(y_cal).size < 2:
                                pred_eval = pred[eval_idx]
                            else:
                                lr = LogisticRegression(
                                    solver="lbfgs",
                                    max_iter=1000,
                                    C=1.0,
                                )
                                lr.fit(X_cal, y_cal)
                                pred_eval = lr.predict(X_eval)
                            f1m_b = float(
                                f1_score(y_eval, pred_eval, average="macro", labels=labels_idx, zero_division=0)
                            )
                            rep_f1s.append(float(f1m_b))
                            if label_repeats > 1:
                                rep_vals_by_budget[int(b)][int(r)].append(float(f1m_b))

                        # For compatibility with the original output, store ONE value per subject by averaging repeats.
                        if rep_f1s:
                            subj_mean_by_budget[int(b)].append(float(np.mean(np.asarray(rep_f1s, dtype=float))))

            arr = np.asarray(vals, dtype=float)
            mean, lo, hi = _bootstrap_mean_ci(arr, rng=rng_boot, n_boot=int(args.n_bootstrap))
            diag = float(macro_mean[terrains.index(test_t), terrains.index(test_t)]) if test_t in terrains else float("nan")
            ratio_to_diag = float(mean / diag) if np.isfinite(mean) and np.isfinite(diag) and diag > 0 else float("nan")
            loo_rows.append(
                {
                    "test_terrain": test_t,
                    "train_terrains": ",".join([t for t in terrains if t != test_t]),
                    "macro_f1_mean": mean,
                    "macro_f1_ci_low": lo,
                    "macro_f1_ci_high": hi,
                    "n_subjects": int(arr.size),
                    "ratio_to_in_terrain_diag": ratio_to_diag,
                }
            )

            if label_budgets:
                for b in label_budgets:
                    if int(b) <= 0:
                        arrb = np.asarray(vals_by_budget.get(int(b), []), dtype=float)
                    else:
                        arrb = np.asarray(subj_mean_by_budget.get(int(b), []), dtype=float)
                    mb, lob, hib = _bootstrap_mean_ci(arrb, rng=rng_boot, n_boot=int(args.n_bootstrap))
                    loo_curve_rows.append(
                        {
                            "label_budget": int(b),
                            "test_terrain": test_t,
                            "train_terrains": ",".join([t for t in terrains if t != test_t]),
                            "macro_f1_mean": mb,
                            "macro_f1_ci_low": lob,
                            "macro_f1_ci_high": hib,
                            "n_subjects": int(arrb.size),
                        }
                    )

            # Repeated-sampling variability summary (mean±CI over repeats)
            if label_budgets and label_repeats > 1:
                for b in label_budgets:
                    bb = int(b)
                    rep_means: list[float] = []
                    rep_ns: list[int] = []
                    if bb <= 0:
                        # No sampling for budget=0; repeat the same mean for plotting convenience.
                        m0 = float(np.nanmean(np.asarray(vals_by_budget.get(0, []), dtype=float)))
                        for r in range(label_repeats):
                            loo_curve_repeats_long_rows.append(
                                {
                                    "label_budget": bb,
                                    "repeat": int(r),
                                    "test_terrain": test_t,
                                    "train_terrains": ",".join([t for t in terrains if t != test_t]),
                                    "macro_f1_mean_over_subjects": m0,
                                    "n_subjects": int(len(vals_by_budget.get(0, []))),
                                }
                            )
                            rep_means.append(m0)
                            rep_ns.append(int(len(vals_by_budget.get(0, []))))
                    else:
                        for r in range(label_repeats):
                            arr_r = np.asarray(rep_vals_by_budget.get(bb, [[] for _ in range(label_repeats)])[r], dtype=float)
                            if arr_r.size < 1:
                                continue
                            mr = float(np.nanmean(arr_r))
                            loo_curve_repeats_long_rows.append(
                                {
                                    "label_budget": bb,
                                    "repeat": int(r),
                                    "test_terrain": test_t,
                                    "train_terrains": ",".join([t for t in terrains if t != test_t]),
                                    "macro_f1_mean_over_subjects": mr,
                                    "n_subjects": int(arr_r.size),
                                }
                            )
                            rep_means.append(mr)
                            rep_ns.append(int(arr_r.size))

                    if rep_means:
                        arrm = np.asarray(rep_means, dtype=float)
                        mean_r = float(np.nanmean(arrm))
                        std_r = float(np.nanstd(arrm, ddof=1)) if arrm.size >= 2 else 0.0
                        if arrm.size >= 2:
                            lo_r, hi_r = np.quantile(arrm, [0.025, 0.975]).tolist()
                        else:
                            lo_r, hi_r = float("nan"), float("nan")
                        loo_curve_repeats_rows.append(
                            {
                                "label_budget": bb,
                                "test_terrain": test_t,
                                "train_terrains": ",".join([t for t in terrains if t != test_t]),
                                "label_calib_repeats": int(label_repeats),
                                "macro_f1_mean": mean_r,
                                "macro_f1_std": std_r,
                                "macro_f1_ci_low": float(lo_r),
                                "macro_f1_ci_high": float(hi_r),
                                "n_repeats_effective": int(arrm.size),
                                "n_subjects_per_repeat_mean": float(np.mean(np.asarray(rep_ns, dtype=float))) if rep_ns else float("nan"),
                            }
                        )

        pd.DataFrame(loo_rows).to_csv(out_dir / "leave_one_terrain_out_summary.csv", index=False)
        if loo_curve_rows:
            df_loo_curve = pd.DataFrame(loo_curve_rows)
            df_loo_curve.to_csv(out_dir / "leave_one_terrain_out_label_calibration_curve.csv", index=False)

            # Simple calibration-curve figure (paper/supplement ready)
            try:
                plt.rcParams.update(
                    {
                        "font.family": "Arial",
                        "font.size": 10,
                        "axes.linewidth": 0.8,
                        "figure.dpi": 300,
                    }
                )
                fig, axes = plt.subplots(1, len(terrains), figsize=(11.0, 3.2), sharey=True)
                if len(terrains) == 1:
                    axes = [axes]

                for ax, t in zip(axes, terrains):
                    sub = df_loo_curve[df_loo_curve["test_terrain"] == t].sort_values("label_budget")
                    if sub.empty:
                        ax.axis("off")
                        continue
                    x = sub["label_budget"].astype(int).to_numpy()
                    y = sub["macro_f1_mean"].astype(float).to_numpy()
                    lo = sub["macro_f1_ci_low"].astype(float).to_numpy()
                    hi = sub["macro_f1_ci_high"].astype(float).to_numpy()
                    yerr = np.vstack([np.maximum(0.0, y - lo), np.maximum(0.0, hi - y)])
                    ax.errorbar(x, y, yerr=yerr, marker="o", linewidth=1.8, capsize=3, color="#1976D2")
                    ax.set_title(str(t), fontweight="bold")
                    ax.set_xlabel("# labeled samples")
                    ax.set_ylim(0.0, 1.0)
                    ax.grid(True, alpha=0.25)

                axes[0].set_ylabel("Macro-F1 (mean ±95% CI)")
                fig.suptitle("Small-label calibration curve (LOSO; train on other 2 terrains)", fontweight="bold", y=1.02)
                fig.tight_layout()
                fig_png = out_dir / "Figure_LabelCalibrationCurve_LOO_v1.0.png"
                fig_pdf = out_dir / "Figure_LabelCalibrationCurve_LOO_v1.0.pdf"
                fig.savefig(fig_png, dpi=300, bbox_inches="tight", facecolor="white")
                fig.savefig(fig_pdf, bbox_inches="tight", facecolor="white")
                plt.close(fig)
            except Exception:
                # do not fail the experiment due to plotting issues
                pass

        # Additional outputs: repeated sampling variability (mean±CI over repeats)
        if loo_curve_repeats_rows and loo_curve_repeats_long_rows:
            df_rep = pd.DataFrame(loo_curve_repeats_rows)
            df_rep.to_csv(out_dir / "leave_one_terrain_out_label_calibration_curve_repeats_summary.csv", index=False)
            pd.DataFrame(loo_curve_repeats_long_rows).to_csv(
                out_dir / "leave_one_terrain_out_label_calibration_curve_repeats_long.csv", index=False
            )

            # Figure (supplement-ready): error bars reflect sampling variability across repeats.
            try:
                plt.rcParams.update(
                    {
                        "font.family": "Arial",
                        "font.size": 10,
                        "axes.linewidth": 0.8,
                        "figure.dpi": 300,
                    }
                )
                fig, axes = plt.subplots(1, len(terrains), figsize=(11.0, 3.2), sharey=True)
                if len(terrains) == 1:
                    axes = [axes]
                for ax, t in zip(axes, terrains):
                    sub = df_rep[df_rep["test_terrain"] == t].sort_values("label_budget")
                    if sub.empty:
                        ax.axis("off")
                        continue
                    x = sub["label_budget"].astype(int).to_numpy()
                    y = sub["macro_f1_mean"].astype(float).to_numpy()
                    lo = sub["macro_f1_ci_low"].astype(float).to_numpy()
                    hi = sub["macro_f1_ci_high"].astype(float).to_numpy()
                    # budget=0 may have NaN CI; treat as 0 error bar
                    lo = np.where(np.isfinite(lo), lo, y)
                    hi = np.where(np.isfinite(hi), hi, y)
                    yerr = np.vstack([np.maximum(0.0, y - lo), np.maximum(0.0, hi - y)])
                    ax.errorbar(x, y, yerr=yerr, marker="o", linewidth=1.8, capsize=3, color="#D32F2F")
                    ax.set_title(str(t), fontweight="bold")
                    ax.set_xlabel("# labeled samples")
                    ax.set_ylim(0.0, 1.0)
                    ax.grid(True, alpha=0.25)
                axes[0].set_ylabel("Macro-F1 (mean ±95% CI over repeats)")
                fig.suptitle(
                    f"Small-label calibration curve (LOSO; repeated sampling ×{int(label_repeats)})",
                    fontweight="bold",
                    y=1.02,
                )
                fig.tight_layout()
                fig_png = out_dir / "Figure_LabelCalibrationCurve_LOO_Repeats_v1.0.png"
                fig_pdf = out_dir / "Figure_LabelCalibrationCurve_LOO_Repeats_v1.0.pdf"
                fig.savefig(fig_png, dpi=300, bbox_inches="tight", facecolor="white")
                fig.savefig(fig_pdf, bbox_inches="tight", facecolor="white")
                plt.close(fig)
            except Exception:
                pass

    # Figure
    fig_png = out_dir / "Figure_LOSO_CrossTerrain_TransferMatrix_v1.0.png"
    fig_pdf = out_dir / "Figure_LOSO_CrossTerrain_TransferMatrix_v1.0.pdf"
    _make_transfer_matrix_figure(
        fig_png,
        fig_pdf,
        terrains=terrains,
        macro_mean=macro_mean,
        macro_ci_lo=macro_ci_lo,
        macro_ci_hi=macro_ci_hi,
        title="LOSO Cross-terrain Transfer Matrix (Macro F1 with 95% CI; subject bootstrap)",
    )

    # Save JSON results payload (lightweight + paths)
    payload = {
        "terrains": terrains,
        "classes": classes,
        "features": feat_cols,
        "calibration": calib,
        "test_calib_cycles_per_file": int(args.test_calib_cycles_per_file),
        "label_calibration_budgets": label_budgets,
        "subjects": subjects,
        "macro_f1_mean": macro_mean.tolist(),
        "macro_f1_ci_low": macro_ci_lo.tolist(),
        "macro_f1_ci_high": macro_ci_hi.tolist(),
        "macro_f1_ratio_to_diagonal": ratio.tolist(),
        "n_test_samples_by_cell": {f"{terrains[i]}->{terrains[j]}": int(n_test_by_cell[(i, j)]) for i in range(n_t) for j in range(n_t)},
        "outputs": {
            "macro_f1_matrix_csv": str(out_dir / "macro_f1_matrix.csv"),
            "per_class_f1_long_csv": str(out_dir / "per_class_f1_long.csv"),
            "ratio_csv": str(out_dir / "macro_f1_ratio_to_diagonal.csv"),
            "figure_png": str(fig_png),
            "figure_pdf": str(fig_pdf),
            "leave_one_terrain_out_csv": str(out_dir / "leave_one_terrain_out_summary.csv") if loo_rows else None,
            "label_calibration_curve_macro_f1_long_csv": str(out_dir / "label_calibration_curve_macro_f1_long.csv") if calib_curve_rows else None,
            "leave_one_terrain_out_label_calibration_curve_csv": str(out_dir / "leave_one_terrain_out_label_calibration_curve.csv") if loo_curve_rows else None,
            "leave_one_terrain_out_label_calibration_curve_figure_png": str(out_dir / "Figure_LabelCalibrationCurve_LOO_v1.0.png") if loo_curve_rows else None,
            "leave_one_terrain_out_label_calibration_curve_figure_pdf": str(out_dir / "Figure_LabelCalibrationCurve_LOO_v1.0.pdf") if loo_curve_rows else None,
            "leave_one_terrain_out_label_calibration_curve_repeats_summary_csv": (
                str(out_dir / "leave_one_terrain_out_label_calibration_curve_repeats_summary.csv")
                if loo_curve_repeats_rows
                else None
            ),
            "leave_one_terrain_out_label_calibration_curve_repeats_long_csv": (
                str(out_dir / "leave_one_terrain_out_label_calibration_curve_repeats_long.csv")
                if loo_curve_repeats_long_rows
                else None
            ),
            "leave_one_terrain_out_label_calibration_curve_repeats_figure_png": (
                str(out_dir / "Figure_LabelCalibrationCurve_LOO_Repeats_v1.0.png") if loo_curve_repeats_rows else None
            ),
            "leave_one_terrain_out_label_calibration_curve_repeats_figure_pdf": (
                str(out_dir / "Figure_LabelCalibrationCurve_LOO_Repeats_v1.0.pdf") if loo_curve_repeats_rows else None
            ),
        },
    }
    (out_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    status["status"] = "completed"
    status["completed_at"] = datetime.now().isoformat()
    status["outputs"] = payload["outputs"]
    _atomic_write_json(out_dir / "status.json", status)

    print(f"[OK] LOSO cross-terrain transfer matrix written to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

