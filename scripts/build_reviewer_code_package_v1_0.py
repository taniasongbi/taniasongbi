#!/usr/bin/env python3
"""
build_reviewer_code_package_v1_0.py
==================================
Create a self-contained reviewer code package (NO raw EMG) that can:
 - regenerate Plotly HTML outputs from Source Data / bundle assets
 - verify Source Data integrity via SHA256 checksums

The package is intended for "code availability on request" during peer review.

Default inputs are wired to this repository layout under:
  docs/journal_submission_deliverables/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


REQUIRED_SOURCE_DATA = [
    # Main Fig.5
    "SourceData_Fig5a_curve.csv",
    "SourceData_Fig5b_critical_errors_keycells.csv",
    "SourceData_Fig5c_mismatch_delta_macro_ci.csv",
    "SourceData_Fig5d_abstain_calibration_metrics.csv",
    "SourceData_Fig5d_abstain_curve_summary.csv",
    "SourceData_Fig5d_abstain_reliability_bins.csv",
    # ED
    "SourceData_ED_Fig1_domain_importance.csv",
    "SourceData_ED_Fig2_delta_macro_f1_per_cell.csv",
    "SourceData_ED_Fig2_per_subject_macro_f1_long.csv",
    "SourceData_ED_Fig3_mismatch_6combo_delta_macro_and_risk.csv",
    "SourceData_ED_Fig4_speed_control_keycells_summary.csv",
    "SourceData_ED_Fig4_speed_control_overlap.csv",
    "SourceData_ED_Fig5_sampling_seed_cap_long.csv",
    "SourceData_ED_Fig5_sampling_seed_cap_summary.csv",
    "SourceData_ED_Fig6_nl10_invalid_rates.csv",
    "SourceData_ED_Fig6_nl10_missing_phase_long.csv",
    "SourceData_ED_Fig6_nl10_missing_summary.csv",
    "SourceData_ED_Fig6_wavelet_delta_macro_f1.csv",
    "SourceData_ED_Fig6_wavelet_sentinel_rate.csv",
    # ED Fig.7 (personalization / subject-window adaptation)
    "SourceData_ED_Fig7_personalization_window.csv",
]

ED_FIG7_PATTERN = "ED_FIG7_PERSONALIZATION_WINDOW_v1.0_*"
ED_FIG7_PNG = "Figure_ED_Fig7_PersonalizationWindow_v1.0.png"
ED_FIG7_SD = "SourceData_ED_Fig7_personalization_window.csv"
ED_FIG7_SUBMISSION_NAME = "Lee_EDfig7.png"


PINNED_PKGS = [
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "matplotlib",
    "umap-learn",
    "PyWavelets",
    "joblib",
    "plotly",
    "kaleido",
    "dash",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copytree_clean(src: Path, dst: Path) -> None:
    def _ignore(_dir: str, names: list[str]) -> set[str]:
        ignore = {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".DS_Store",
        }
        return {n for n in names if n in ignore or n.endswith(".pyc")}

    shutil.copytree(src, dst, dirs_exist_ok=False, ignore=_ignore)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_dir(root: Path, glob_pat: str) -> Path | None:
    hits = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hits:
        return None
    p = hits[0]
    return p if p.is_dir() else p.parent


def pkg_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for pkg in PINNED_PKGS:
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            # optional dependency
            continue
    return out


def render_requirements_review(versions: dict[str, str]) -> str:
    lines = [
        "# Reviewer reproduction environment (pinned to build machine)",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    for pkg in PINNED_PKGS:
        v = versions.get(pkg)
        if v:
            lines.append(f"{pkg}=={v}")
    lines.append("")
    return "\n".join(lines)


def render_readme(bundle_rel: str) -> str:
    return f"""# Reviewer Code Package (on request)

This package is prepared for **code availability on reviewer request**.

It is **self‑contained** for reproducing the **interactive Plotly HTML outputs** (and best‑effort PNG/PDF static exports) from the **final submission bundle assets + Source Data**, **without raw EMG**.

---

## What you can reproduce with this package (scope)

✅ Reproducible from included files:
- Plotly HTML outputs under `.../plotly/` for:
  - Main Fig.1–5 (Fig.1 is embedded from the submission PNG; Fig.2–4 are copied from the legacy HTML artifact shipped here; Fig.5 is generated from Source Data)
  - Extended Data Fig.1–6 (generated from Source Data)
  - Extended Data Fig.7 is included as a submission-ready PNG and Source Data CSV (not regenerated via Plotly in this package)
- Tables (Table 1, ED Table 1–2) as Plotly HTML
- Source Data integrity check via SHA256 checksums

⚠️ Not reproducible (intentionally excluded):
- **Raw EMG → full re‑analysis pipeline** (raw EMG recordings are restricted by IRB consent and are not included in this package).
- Raw EMG can be provided **under controlled access / Data Use Agreement** upon reasonable request.

---

## Package layout

- `code/`
  - `src/nbe_pipeline/`: core pipeline modules (feature extraction, gait events, biomechanical scaling, etc.)
  - `scripts/export_plotly_submission_package_v1_0.py`: one‑shot exporter that generates Plotly outputs inside the final bundle folder
- `submission_bundle/`
  - Final submission bundle: `{bundle_rel}`
  - Legacy Plotly HTML artifact (for Fig.2–4 HTML copy step): `submission_bundle/SUBMISSION_PACKAGE_v1.0_20260119/`
- `supplementary/`: Supplementary Materials markdown
- `checksums_source_data.json`: SHA256 checksums for all required Source Data CSVs
- `reproduce_all.sh`: creates a Python venv, installs dependencies, generates Plotly outputs, then verifies results
- `verify_outputs.py`: verifies Source Data checksums and that expected Plotly outputs exist
- `requirements-review.txt`: pinned dependency versions used to build this package
- `CODE_OVERVIEW.md`: quick map of the core pipeline code for reviewers

---

## System requirements

- Python **3.10+** recommended (tested with Python 3.11)
- Internet access for `pip install` (or use your preferred offline/conda workflow)
- macOS/Linux recommended; Windows users can run via WSL

---

## Quickstart (recommended)

From this folder:

```bash
./reproduce_all.sh
```

### Expected outputs

After completion, open:
- `{bundle_rel}/plotly/index.html`

Generated outputs are under:
- `{bundle_rel}/plotly/main/`
- `{bundle_rel}/plotly/extended_data/`
- `{bundle_rel}/plotly/tables/`

---

## Verification (integrity + expected files)

```bash
python3 verify_outputs.py \\
  --bundle "{bundle_rel}" \\
  --check-plotly
```

This checks:
- Required Source Data CSV files exist
- SHA256 checksums match `checksums_source_data.json`
- Expected Plotly HTML outputs exist

---

## Common issues / troubleshooting

- **Permission denied running script**:

```bash
chmod +x reproduce_all.sh
```

- **Static export (PNG/PDF) fails**:
  - Static export uses `kaleido`. If it fails on your machine, HTML generation should still work.
  - You can edit `reproduce_all.sh` to remove `--export_static` (line containing the exporter call).

- **SciPy install errors** (needed for the dendrogram in ED Fig.2 clustergram):
  - Use a prebuilt wheel (recommended) or a conda environment.

---

## Contact / restricted data

If reviewers require **raw EMG** or an **end‑to‑end rerun from raw signals**, raw recordings can be shared under controlled access (Data Use Agreement) consistent with the IRB‑approved consent.
"""


def render_reproduce_sh(bundle_rel: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$ROOT_DIR"

FINAL_BUNDLE="$ROOT_DIR/{bundle_rel}"

if [[ ! -d "$FINAL_BUNDLE" ]]; then
  echo "[ERROR] Final bundle not found: $FINAL_BUNDLE" >&2
  exit 2
fi

echo "[INFO] Creating/reusing venv: $ROOT_DIR/.venv"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

if [[ -f requirements-review.txt ]]; then
  echo "[INFO] Installing pinned requirements: requirements-review.txt"
  python -m pip install -r requirements-review.txt
else
  echo "[INFO] Installing project requirements: code/requirements.txt"
  python -m pip install -r code/requirements.txt
fi

# Generate Plotly HTML (and best-effort static if kaleido works)
echo "[INFO] Exporting Plotly outputs into: $FINAL_BUNDLE/plotly/"
python code/scripts/export_plotly_submission_package_v1_0.py \\
  --final_bundle "$FINAL_BUNDLE" \\
  --surname Lee \\
  --export_static

echo "[INFO] Verifying Source Data checksums + expected outputs"
python verify_outputs.py --bundle "$FINAL_BUNDLE" --check-plotly

echo "[OK] Reproduction finished."
echo "[OK] Open: $FINAL_BUNDLE/plotly/index.html"
"""


def render_code_overview() -> str:
    return """# Code overview (H‑MD‑WEF pipeline)

This note is provided to help reviewers navigate the code quickly.

## Reproduction entrypoint in this package

- Plotly outputs are reproduced by:
  - `code/scripts/export_plotly_submission_package_v1_0.py`
  - It reads **Source Data CSVs** under `submission_bundle/.../source_data/` and writes outputs to `submission_bundle/.../plotly/`

## Core pipeline modules (raw EMG → features → outputs)

> Raw EMG is not included in the reviewer package (IRB‑restricted). The pipeline code is included for transparency and for controlled‑access reproduction if required.

- **End‑to‑end runner**: `code/src/nbe_pipeline/pipeline.py`
  - `run_pipeline(...)` orchestrates: channel mapping → gait event detection/segmentation → feature extraction → optional clustering/metrics export.

- **Gait events + phase segmentation**: `code/src/nbe_pipeline/gait_events.py`
  - Heel‑strike/toe‑off detection and HS→HS cycle segmentation.

- **Feature extraction (F18 + fusion + wavelet)**: `code/src/nbe_pipeline/features.py`
  - Time/Frequency/Wavelet domains (F18) and fusion logic.
  - Note: the manuscript uses a **condition‑agnostic fixed wavelet ensemble** for leakage‑safe reporting.

- **Nonlinear features (NL10)**: `code/src/nbe_pipeline/nonlinear_features.py`
  - SampEn/ApEn/Permutation entropy/fractal dimensions/RQA/Lyapunov features.
  - NL10 is computed only for segments ≥50 samples (short segments become NaN and are excluded from F28 analyses, per manuscript).

- **Biomechanical scaling (Φ_B)**: `code/src/nbe_pipeline/biomechanics.py`
  - Muscle‑specific scaling computed from anatomical parameters (PCSA, fiber fraction, pennation angle).

- **Settings/constants**: `code/src/nbe_pipeline/settings.py`

## Scripts directory

`code/scripts/` contains figure generation scripts and reproducibility utilities used during manuscript preparation. The reviewer package focuses on `export_plotly_submission_package_v1_0.py` for **plot reproduction from Source Data**.
"""

def render_verify_py() -> str:
    return r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REQUIRED_SOURCE_DATA = """ + json.dumps(REQUIRED_SOURCE_DATA, indent=2) + r"""


PLOTLY_EXPECTED = {
    "main": [
        "Lee_Fig1.html",
        "Lee_Fig2.html",
        "Lee_Fig3.html",
        "Lee_Fig4.html",
        "Lee_Fig5.html",
        "Lee_Fig1to5_onepage.html",
    ],
    "extended_data": [
        "Lee_EDfig1.html",
        "Lee_EDfig2.html",
        "Lee_EDfig2_clustergram_delta.html",
        "Lee_EDfig3.html",
        "Lee_EDfig4.html",
        "Lee_EDfig5.html",
        "Lee_EDfig6.html",
    ],
    "tables": [
        "Lee_Table1.html",
        "Lee_EDtable1.html",
        "Lee_EDtable2.html",
    ],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True, help="Path to final bundle folder.")
    ap.add_argument(
        "--checksums",
        type=Path,
        default=(Path(__file__).resolve().parent / "checksums_source_data.json"),
        help="Expected Source Data checksums JSON (default: <script_dir>/checksums_source_data.json).",
    )
    ap.add_argument("--check-plotly", action="store_true", help="Also validate Plotly outputs exist.")
    args = ap.parse_args()

    bundle = args.bundle
    src_data = bundle / "source_data"
    if not src_data.exists():
        print(f"[FAIL] Missing source_data/: {src_data}", file=sys.stderr)
        raise SystemExit(2)

    missing = [f for f in REQUIRED_SOURCE_DATA if not (src_data / f).exists()]
    if missing:
        print("[FAIL] Missing required Source Data files:", file=sys.stderr)
        for f in missing:
            print(f"  - {f}", file=sys.stderr)
        raise SystemExit(2)

    # checksum validation (best-effort)
    if args.checksums.exists():
        expected = json.loads(args.checksums.read_text(encoding="utf-8"))
        bad = []
        for f in REQUIRED_SOURCE_DATA:
            p = src_data / f
            got = sha256_file(p)
            exp = expected.get(f)
            if exp and got != exp:
                bad.append((f, exp, got))
        if bad:
            print("[FAIL] Source Data checksum mismatch:", file=sys.stderr)
            for f, exp, got in bad:
                print(f"  - {f}\n    expected: {exp}\n    got:      {got}", file=sys.stderr)
            raise SystemExit(2)
        print("[OK] Source Data checksums match.")
    else:
        print(f"[WARN] Checksums file not found: {args.checksums} (skipping checksum validation)")

    if args.check_plotly:
        plotly_root = bundle / "plotly"
        if not plotly_root.exists():
            print(f"[FAIL] plotly/ not found. Did you run reproduce_all.sh? ({plotly_root})", file=sys.stderr)
            raise SystemExit(2)

        missing_plotly = []
        for subdir, files in PLOTLY_EXPECTED.items():
            for fname in files:
                p = plotly_root / subdir / fname
                if not p.exists():
                    missing_plotly.append(str(p))
        if missing_plotly:
            print("[FAIL] Missing expected Plotly outputs:", file=sys.stderr)
            for p in missing_plotly:
                print(f"  - {p}", file=sys.stderr)
            raise SystemExit(2)
        print("[OK] Plotly outputs present.")

    print("[OK] Verification complete.")


if __name__ == "__main__":
    main()
"""


@dataclass(frozen=True)
class Inputs:
    repo_root: Path
    final_bundle: Path
    legacy_pkg: Path
    manuscript_en_v141: Path
    manuscript_kr_v141: Path
    supplementary_v11: Path


def default_inputs(repo_root: Path) -> Inputs:
    deliverables = repo_root / "docs" / "journal_submission_deliverables"
    final_bundle = deliverables / "NBE_FINAL_SUBMISSION_v1.0_20260204_125813"
    legacy_pkg = deliverables / "SUBMISSION_PACKAGE_v1.0_20260119"
    manuscript_en = deliverables / "FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE.md"
    manuscript_kr = deliverables / "FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE_KR.md"
    supplementary = deliverables / "SUPPLEMENTARY_MATERIALS_v1.1.md"
    return Inputs(
        repo_root=repo_root,
        final_bundle=final_bundle,
        legacy_pkg=legacy_pkg,
        manuscript_en_v141=manuscript_en,
        manuscript_kr_v141=manuscript_kr,
        supplementary_v11=supplementary,
    )


def update_manifest_manuscripts(manifest_path: Path) -> None:
    if not manifest_path.exists():
        return
    txt = manifest_path.read_text(encoding="utf-8")
    # Manuscript table (keep best-effort string replacements)
    txt = txt.replace(
        "| `FULL_MANUSCRIPT_FINAL_v1.39_20260204_NBE_KR.md` | Korean | v1.39 (최종) |",
        "| `FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE_KR.md` | Korean | v1.41 (final) |",
    )
    txt = txt.replace(
        "| `FULL_MANUSCRIPT_FINAL_v1.40_20260204_NBE_KR.md` | Korean | v1.40 (최종) |",
        "| `FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE_KR.md` | Korean | v1.41 (final) |",
    )
    txt = txt.replace(
        "| `FULL_MANUSCRIPT_FINAL_v1.35_20260202_NBE.md` | English | v1.35 (업데이트 필요) |",
        "| `FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE.md` | English | v1.41 (final) |",
    )
    txt = txt.replace(
        "| `FULL_MANUSCRIPT_FINAL_v1.40_20260204_NBE.md` | English | v1.40 (최종) |",
        "| `FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE.md` | English | v1.41 (final) |",
    )
    # ED Fig count best-effort update (if present)
    txt = txt.replace("| **Extended Data Figures** | 6 | ED Fig 1–6 |", "| **Extended Data Figures** | 7 | ED Fig 1–7 |")
    txt = txt.replace("| **Total Extended** | 8 | ≤10 limit ✓ |", "| **Total Extended** | 9 | ≤10 limit ✓ |")
    # remove outdated TODO lines if present
    txt = txt.replace("- [ ] 영문 원고 v1.39 동기화 필요\n", "- [x] 영문 원고 v1.41 동기화 완료\n")
    manifest_path.write_text(txt, encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    defaults = default_inputs(repo_root)

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out_dir",
        type=Path,
        default=repo_root
        / "docs"
        / "journal_submission_deliverables"
        / "REVIEWER_CODE_PACKAGE_v1.41_20260205",
        help="Output folder for reviewer package.",
    )
    ap.add_argument("--final_bundle", type=Path, default=defaults.final_bundle)
    ap.add_argument("--legacy_pkg", type=Path, default=defaults.legacy_pkg)
    ap.add_argument("--supplementary", type=Path, default=defaults.supplementary_v11)
    ap.add_argument("--manuscript_en", type=Path, default=defaults.manuscript_en_v141)
    ap.add_argument("--manuscript_kr", type=Path, default=defaults.manuscript_kr_v141)
    ap.add_argument("--include_plotly_cache", action="store_true", help="Copy existing plotly/ outputs too.")
    ap.add_argument("--zip", action="store_true", help="Create a zip archive next to out_dir.")
    ap.add_argument("--force", action="store_true", help="Overwrite out_dir if it already exists.")
    args = ap.parse_args()

    out_dir: Path = args.out_dir
    if out_dir.exists():
        if not args.force:
            raise SystemExit(
                f"[ERROR] out_dir exists: {out_dir}\n"
                "Re-run with --force to overwrite."
            )
        shutil.rmtree(out_dir)

    # Layout
    code_dir = out_dir / "code"
    bundle_root = out_dir / "submission_bundle"
    supp_dir = out_dir / "supplementary"

    ensure_dir(code_dir)
    ensure_dir(bundle_root)
    ensure_dir(supp_dir)

    # Copy code snapshot
    for rel in ["src", "scripts"]:
        src = defaults.repo_root / rel
        if src.exists():
            copytree_clean(src, code_dir / rel)

    for fname in ["requirements.txt", "setup.py", "README.md", "run_all_with_logs.sh", "reprocess_all_with_mdwef.py"]:
        src = defaults.repo_root / fname
        if src.exists():
            ensure_dir(code_dir)
            shutil.copy2(src, code_dir / fname)

    # Copy submission bundle assets (no raw EMG)
    final_bundle_src: Path = args.final_bundle
    final_bundle_dst = bundle_root / final_bundle_src.name
    ensure_dir(final_bundle_dst)

    # minimal subdirs needed by export script
    for sub in ["figures", "extended_data", "source_data", "submission_names", "manuscript"]:
        s = final_bundle_src / sub
        if s.exists():
            copytree_clean(s, final_bundle_dst / sub)

    for fname in ["SUBMISSION_MANIFEST.md", "SUBMISSION_MANIFEST.json", "MANIFEST.md", "MANIFEST.json"]:
        s = final_bundle_src / fname
        if s.exists():
            shutil.copy2(s, final_bundle_dst / fname)

    # Optional ED Fig.7 (personalization / subject-window adaptation) — include in bundle copy
    results_v2 = defaults.repo_root / "results_v2"
    ed7_dir = latest_dir(results_v2, ED_FIG7_PATTERN) if results_v2.exists() else None
    if ed7_dir and (ed7_dir / ED_FIG7_PNG).exists() and (ed7_dir / ED_FIG7_SD).exists():
        shutil.copy2(ed7_dir / ED_FIG7_SD, final_bundle_dst / "source_data" / ED_FIG7_SD)
        shutil.copy2(ed7_dir / ED_FIG7_PNG, final_bundle_dst / "extended_data" / ED_FIG7_SUBMISSION_NAME)
    else:
        raise SystemExit(
            "[ERROR] ED Fig.7 artifacts not found for reviewer package build.\n"
            f"Expected under: {results_v2}/{ED_FIG7_PATTERN}/\n"
            f"Missing: {ED_FIG7_PNG} and/or {ED_FIG7_SD}"
        )

    if args.include_plotly_cache and (final_bundle_src / "plotly").exists():
        copytree_clean(final_bundle_src / "plotly", final_bundle_dst / "plotly")

    # Put current manuscripts into bundle/manuscript
    if args.manuscript_en.exists():
        shutil.copy2(args.manuscript_en, final_bundle_dst / "manuscript" / args.manuscript_en.name)
    if args.manuscript_kr.exists():
        shutil.copy2(args.manuscript_kr, final_bundle_dst / "manuscript" / args.manuscript_kr.name)

    # Copy legacy Plotly html package (for Fig2–4 html copy step)
    legacy_src: Path = args.legacy_pkg
    if legacy_src.exists():
        copytree_clean(legacy_src, bundle_root / legacy_src.name)

    # Supplementary materials
    if args.supplementary.exists():
        shutil.copy2(args.supplementary, supp_dir / args.supplementary.name)

    # Generate Source Data checksums
    src_data_dir = final_bundle_dst / "source_data"
    missing = [f for f in REQUIRED_SOURCE_DATA if not (src_data_dir / f).exists()]
    if missing:
        raise SystemExit(
            "[ERROR] Missing required Source Data in copied bundle:\n"
            + "\n".join(f" - {m}" for m in missing)
        )
    checksums = {f: sha256_file(src_data_dir / f) for f in REQUIRED_SOURCE_DATA}
    write_text(out_dir / "checksums_source_data.json", json.dumps(checksums, indent=2) + "\n")

    # requirements-review.txt pinned
    req_txt = render_requirements_review(pkg_versions())
    write_text(out_dir / "requirements-review.txt", req_txt)

    # Repro/verify helpers
    bundle_rel = f"submission_bundle/{final_bundle_src.name}"
    write_text(out_dir / "README_REPRODUCE.md", render_readme(bundle_rel))
    write_text(out_dir / "CODE_OVERVIEW.md", render_code_overview())
    repro_sh = out_dir / "reproduce_all.sh"
    write_text(repro_sh, render_reproduce_sh(bundle_rel))
    repro_sh.chmod(0o755)
    verify_py = out_dir / "verify_outputs.py"
    write_text(verify_py, render_verify_py())
    verify_py.chmod(0o755)

    # update copied manifest (non-critical)
    update_manifest_manuscripts(final_bundle_dst / "SUBMISSION_MANIFEST.md")

    # Optional zip
    if args.zip:
        zip_path = out_dir.parent / f"{out_dir.name}.zip"
        if zip_path.exists():
            zip_path.unlink()
        archive = shutil.make_archive(str(out_dir), "zip", root_dir=out_dir.parent, base_dir=out_dir.name)
        print(f"[OK] Wrote zip: {archive}")

    print(f"[OK] Reviewer package created: {out_dir}")


if __name__ == "__main__":
    main()

