#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_ed_fig7_personalization_window_v1_0.py
============================================
Create an optional Extended Data figure (ED Fig.7) demonstrating leakage-safe
subject adaptation ("personalization") using an unlabeled calibration window.

Inputs
------
1) Baseline + train-only-by-terrain 0-label results (Source Data ED Fig.2):
   - SourceData_ED_Fig2_delta_macro_f1_per_cell.csv
2) Personalization results produced by:
   - scripts/experiment_loso_cross_terrain_transfer_matrix_v1_0.py
     with --calibration test_window_by_terrain

Outputs
-------
- Figure_ED_Fig7_PersonalizationWindow_v1.0.png/.pdf
- SourceData_ED_Fig7_personalization_window.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]


METHODS = [
    ("Baseline", "baseline", "#9E9E9E"),
    ("0-label (train-only terrain)", "train_only_by_terrain", "#1976D2"),
    ("0-label (subject window)", "test_window_by_terrain", "#2E7D32"),
]


OFFDIAG_ORDER = [
    ("Level", "Slope"),
    ("Level", "Stairs"),
    ("Slope", "Level"),
    ("Slope", "Stairs"),
    ("Stairs", "Level"),
    ("Stairs", "Slope"),
]


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _asym_err(mean: float, lo: float, hi: float) -> tuple[float, float]:
    return max(0.0, mean - lo), max(0.0, hi - mean)


def _latest_file(root: Path, glob_pat: str) -> Path | None:
    hits = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    return hits[0] if hits else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--baseline-source",
        type=Path,
        default=None,
        help=(
            "CSV with baseline + train_only_by_terrain results (SourceData ED Fig.2). "
            "If omitted, the script will auto-locate the most recent "
            "`SourceData_ED_Fig2_delta_macro_f1_per_cell.csv` under "
            "`docs/journal_submission_deliverables/`."
        ),
    )
    ap.add_argument(
        "--personalization-matrix",
        type=Path,
        required=True,
        help="macro_f1_matrix.csv from test_window_by_terrain run.",
    )
    ap.add_argument(
        "--test-calib-cycles-per-file",
        type=int,
        default=4,
        help="Calibration window size used in personalization run (for caption).",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: results_v2/ED_FIG7_PERSONALIZATION_WINDOW_v1.0_<ts>/).",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    deliverables = repo_root / "docs" / "journal_submission_deliverables"

    baseline_path: Path | None = args.baseline_source.expanduser().resolve() if args.baseline_source else None
    if baseline_path is None:
        baseline_path = _latest_file(deliverables, "**/SourceData_ED_Fig2_delta_macro_f1_per_cell.csv")
        if baseline_path is None:
            raise FileNotFoundError(
                "Could not auto-locate SourceData ED Fig.2. "
                "Pass `--baseline-source path/to/SourceData_ED_Fig2_delta_macro_f1_per_cell.csv`."
            )

    pers_path: Path = args.personalization_matrix.expanduser().resolve()

    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline source not found: {baseline_path}")
    if not pers_path.exists():
        raise FileNotFoundError(f"Personalization matrix not found: {pers_path}")

    results_v2 = repo_root / "results_v2"
    out_dir = (
        args.out_dir.expanduser().resolve()
        if args.out_dir
        else (results_v2 / f"ED_FIG7_PERSONALIZATION_WINDOW_v1.0_{_now_tag()}").resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load baseline + train-only
    df_base = pd.read_csv(baseline_path)
    need_base = {
        "train_terrain",
        "test_terrain",
        "baseline_mean",
        "baseline_ci_low",
        "baseline_ci_high",
        "calibrated_mean",
        "calibrated_ci_low",
        "calibrated_ci_high",
    }
    if not need_base.issubset(df_base.columns):
        raise ValueError(f"Baseline source missing columns: {sorted(need_base - set(df_base.columns))}")

    # Load personalization matrix
    df_p = pd.read_csv(pers_path)
    need_p = {"train_terrain", "test_terrain", "macro_f1_mean", "macro_f1_ci_low", "macro_f1_ci_high"}
    if not need_p.issubset(df_p.columns):
        raise ValueError(f"Personalization matrix missing columns: {sorted(need_p - set(df_p.columns))}")

    df_p = df_p.rename(
        columns={
            "macro_f1_mean": "personalized_mean",
            "macro_f1_ci_low": "personalized_ci_low",
            "macro_f1_ci_high": "personalized_ci_high",
        }
    )

    # Merge
    df = df_base.merge(df_p, on=["train_terrain", "test_terrain"], how="inner")
    if df.shape[0] < 9:
        raise ValueError(f"Unexpected merge size: {df.shape[0]} rows (expected >=9)")

    # Build long source data for ED Fig.7
    rows = []
    for _, r in df.iterrows():
        train_t = str(r["train_terrain"])
        test_t = str(r["test_terrain"])
        rows.append(
            {
                "train_terrain": train_t,
                "test_terrain": test_t,
                "method": "baseline",
                "macro_f1_mean": float(r["baseline_mean"]),
                "macro_f1_ci_low": float(r["baseline_ci_low"]),
                "macro_f1_ci_high": float(r["baseline_ci_high"]),
            }
        )
        rows.append(
            {
                "train_terrain": train_t,
                "test_terrain": test_t,
                "method": "train_only_by_terrain",
                "macro_f1_mean": float(r["calibrated_mean"]),
                "macro_f1_ci_low": float(r["calibrated_ci_low"]),
                "macro_f1_ci_high": float(r["calibrated_ci_high"]),
            }
        )
        rows.append(
            {
                "train_terrain": train_t,
                "test_terrain": test_t,
                "method": "test_window_by_terrain",
                "macro_f1_mean": float(r["personalized_mean"]),
                "macro_f1_ci_low": float(r["personalized_ci_low"]),
                "macro_f1_ci_high": float(r["personalized_ci_high"]),
                "test_calib_cycles_per_file": int(args.test_calib_cycles_per_file),
            }
        )

    df_sd = pd.DataFrame(rows)
    df_sd.to_csv(out_dir / "SourceData_ED_Fig7_personalization_window.csv", index=False)

    # Plot: 2x3 bar plots for off-diagonal transfers
    fig, axes = plt.subplots(2, 3, figsize=(11.8, 6.2), sharey=True)
    axes = axes.reshape(-1)

    y_max = 0.6
    for ax, (train_t, test_t) in zip(axes, OFFDIAG_ORDER, strict=True):
        dcell = df_sd[(df_sd["train_terrain"] == train_t) & (df_sd["test_terrain"] == test_t)].copy()
        xs = np.arange(len(METHODS), dtype=float)
        means = []
        yerr_lo = []
        yerr_hi = []
        colors = []
        labels = []
        for k, (label, method_key, color) in enumerate(METHODS):
            rr = dcell[dcell["method"] == method_key]
            if rr.empty:
                means.append(np.nan)
                yerr_lo.append(0.0)
                yerr_hi.append(0.0)
            else:
                m = float(rr["macro_f1_mean"].iloc[0])
                lo = float(rr["macro_f1_ci_low"].iloc[0])
                hi = float(rr["macro_f1_ci_high"].iloc[0])
                e_lo, e_hi = _asym_err(m, lo, hi)
                means.append(m)
                yerr_lo.append(e_lo)
                yerr_hi.append(e_hi)
            colors.append(color)
            labels.append(label)

        bars = ax.bar(xs, means, color=colors, edgecolor="black", linewidth=0.6, alpha=0.9)
        ax.errorbar(
            xs,
            means,
            yerr=np.vstack([yerr_lo, yerr_hi]),
            fmt="none",
            ecolor="black",
            elinewidth=0.9,
            capsize=3,
            capthick=0.9,
            zorder=5,
        )
        ax.set_title(f"{train_t} → {test_t}", fontsize=11, fontweight="bold")
        ax.set_xticks(xs)
        ax.set_xticklabels(["Base", "0‑label", "Subj‑win"], rotation=0, fontsize=9)
        ax.set_ylim(0, y_max)
        ax.grid(axis="y", color="#E0E0E0", linewidth=0.8, alpha=0.9)
        for b in bars:
            b.set_zorder(3)

    # Remove any unused axes (safety)
    for k in range(len(OFFDIAG_ORDER), axes.size):
        axes[k].axis("off")

    fig.suptitle(
        "Extended Data Fig. 7 | Leakage-safe unlabeled subject adaptation (calibration window)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        f"Subject-window method uses the first {int(args.test_calib_cycles_per_file)} cycles per recording file "
        f"(unlabeled) for per-(subject, terrain) z-score; evaluation excludes calibration cycles. "
        "Bars show subject mean macro-F1 with 95% subject-bootstrap CI (n=10).",
        ha="center",
        va="bottom",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])

    out_png = out_dir / "Figure_ED_Fig7_PersonalizationWindow_v1.0.png"
    out_pdf = out_dir / "Figure_ED_Fig7_PersonalizationWindow_v1.0.pdf"
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"[OK] Wrote: {out_png}")
    print(f"[OK] Wrote: {out_pdf}")
    print(f"[OK] Wrote: {out_dir / 'SourceData_ED_Fig7_personalization_window.csv'}")
    print(f"[OK] Output dir: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

