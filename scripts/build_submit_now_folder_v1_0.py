#!/usr/bin/env python3
"""
build_submit_now_folder_v1_0.py
================================
Create a clean, ready-to-upload submission folder that contains:
 - Manuscript(s) (EN v1.40; KR kept in translations/)
 - Cover letter (markdown)
 - Main figures (Lee_Fig1–5)
 - Extended Data figures (Lee_EDfig1–6)
 - Source Data CSVs
 - Supplementary Materials (markdown)
 - Data/Code availability statements
 - Optional extras (tables as PNG/PDF, reviewer code package zip)

This script copies existing repository artifacts; it does NOT re-run analysis.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


MAIN_FIGS = [f"Lee_Fig{i}.png" for i in range(1, 6)]
ED_FIGS = [f"Lee_EDfig{i}.png" for i in range(1, 7)]
ED_FIG7_PATTERN = "ED_FIG7_PERSONALIZATION_WINDOW_v1.0_*"
ED_FIG7_PNG = "Figure_ED_Fig7_PersonalizationWindow_v1.0.png"
ED_FIG7_PDF = "Figure_ED_Fig7_PersonalizationWindow_v1.0.pdf"
ED_FIG7_SD = "SourceData_ED_Fig7_personalization_window.csv"
ED_FIG7_SUBMISSION_NAME = "Lee_EDfig7.png"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def copy2(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def zip_dir(src_dir: Path, zip_basepath: Path) -> Path:
    """
    Create a zip archive from src_dir.

    Parameters
    ----------
    src_dir : Path
        Directory to archive.
    zip_basepath : Path
        Output path WITHOUT suffix (e.g., /path/to/archive_name).
    """
    if zip_basepath.with_suffix(".zip").exists():
        zip_basepath.with_suffix(".zip").unlink()
    archive = shutil.make_archive(str(zip_basepath), "zip", root_dir=str(src_dir.parent), base_dir=src_dir.name)
    return Path(archive)


def latest_dir(root: Path, glob_pat: str) -> Path | None:
    hits = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hits:
        return None
    p = hits[0]
    return p if p.is_dir() else p.parent


def render_manifest(out_dir: Path, *, has_ed_fig7: bool) -> str:
    ed_range = "1–7" if has_ed_fig7 else "1–6"
    return f"""# NBE Submit-Now Folder

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This folder is organized for immediate upload to the submission system.

## Upload checklist

- [ ] **Manuscript (English)**: `manuscript/` (v1.41)
- [ ] **Cover letter**: `cover_letter/`
- [ ] **Main figures (Fig.1–5)**: `figures_main/`
- [ ] **Extended Data figures (ED Fig.{ed_range})**: `extended_data/`
- [ ] **Source Data (CSV)**: `source_data/`
- [ ] **Supplementary information**: `supplementary/`
- [ ] **Data/Code availability statements** (if required separately): `statements/`

## Optional / internal
- `tables_optional/`: Table images (PNG/PDF) exported for convenience
- `reviewer_code_on_request/`: Reviewer code package zip (for peer-review requests)
- `zips/`: Pre-zipped bundles (some portals accept zip; keep originals too)

## Upload-this shortcut
- `UPLOAD_THIS/`: only the files/directories typically uploaded to the portal (clean subset)
"""


def build_upload_this(out_dir: Path) -> None:
    """
    Create UPLOAD_THIS/ containing only submission-upload materials.

    This is a convenience subset for portal upload: manuscript, cover letter,
    main/ED figures, Source Data, supplementary info, and statements.
    """
    upload_dir = out_dir / "UPLOAD_THIS"
    if upload_dir.exists():
        shutil.rmtree(upload_dir)

    # Keep the same category structure for clarity.
    for sub in [
        "manuscript",
        "cover_letter",
        "figures_main",
        "extended_data",
        "source_data",
        "supplementary",
        "statements",
    ]:
        src = out_dir / sub
        if src.exists():
            copytree(src, upload_dir / sub)

    # Optional tables (some portals request separate table files)
    if (out_dir / "tables_optional").exists():
        copytree(out_dir / "tables_optional", upload_dir / "tables_optional")

    # Copy manifest for convenience
    if (out_dir / "SUBMIT_MANIFEST.md").exists():
        copy2(out_dir / "SUBMIT_MANIFEST.md", upload_dir / "SUBMIT_MANIFEST.md")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    deliverables = repo_root / "docs" / "journal_submission_deliverables"
    results_v2 = repo_root / "results_v2"

    ed7_dir = latest_dir(results_v2, ED_FIG7_PATTERN)
    has_ed7 = bool(ed7_dir and (ed7_dir / ED_FIG7_PNG).exists() and (ed7_dir / ED_FIG7_SD).exists())

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out_dir",
        type=Path,
        default=deliverables / "NBE_SUBMIT_NOW_v1.41_20260205",
        help="Output folder to create.",
    )
    ap.add_argument(
        "--final_bundle",
        type=Path,
        default=deliverables / "NBE_FINAL_SUBMISSION_v1.0_20260204_125813",
        help="Source final bundle folder (figures/source_data/submission_names).",
    )
    ap.add_argument("--force", action="store_true", help="Overwrite out_dir if it exists.")
    args = ap.parse_args()

    out_dir: Path = args.out_dir
    if out_dir.exists():
        if not args.force:
            raise SystemExit(f"[ERROR] out_dir exists: {out_dir} (re-run with --force)")
        shutil.rmtree(out_dir)

    # Inputs
    final_bundle: Path = args.final_bundle
    submission_names = final_bundle / "submission_names"
    source_data = final_bundle / "source_data"
    tables_src = final_bundle / "plotly" / "tables"

    manuscript_en = deliverables / "FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE.md"
    manuscript_kr = deliverables / "FULL_MANUSCRIPT_FINAL_v1.41_20260205_NBE_KR.md"
    cover_letter = deliverables / "NBE_COVER_LETTER_DRAFT_v1.0.md"
    supplementary = deliverables / "SUPPLEMENTARY_MATERIALS_v1.1.md"
    statements_dir = deliverables / "statements"
    reviewer_zip = deliverables / "REVIEWER_CODE_PACKAGE_v1.41_20260205.zip"
    checklist = deliverables / "NBE_SCORE_BOOST_CHECKLIST_STATUS_20260204.md"

    # Validate existence (hard requirements)
    required_files = [
        manuscript_en,
        cover_letter,
        supplementary,
    ]
    required_dirs = [submission_names, source_data]
    missing = [str(p) for p in required_files if not p.exists()]
    missing += [str(p) for p in required_dirs if not p.exists()]
    if missing:
        raise SystemExit("[ERROR] Missing required inputs:\n" + "\n".join(f" - {m}" for m in missing))

    # Create structure
    ensure_dir(out_dir)
    write_manifest = out_dir / "SUBMIT_MANIFEST.md"
    write_manifest.write_text(render_manifest(out_dir, has_ed_fig7=has_ed7), encoding="utf-8")

    # Manuscripts
    ensure_dir(out_dir / "manuscript")
    copy2(manuscript_en, out_dir / "manuscript" / manuscript_en.name)
    if manuscript_kr.exists():
        ensure_dir(out_dir / "translations")
        copy2(manuscript_kr, out_dir / "translations" / manuscript_kr.name)

    # Cover letter
    ensure_dir(out_dir / "cover_letter")
    copy2(cover_letter, out_dir / "cover_letter" / cover_letter.name)

    # Supplementary
    ensure_dir(out_dir / "supplementary")
    copy2(supplementary, out_dir / "supplementary" / supplementary.name)

    # Statements
    if statements_dir.exists():
        copytree(statements_dir, out_dir / "statements")

    # Figures (submission names)
    ensure_dir(out_dir / "figures_main")
    for fname in MAIN_FIGS:
        src = submission_names / fname
        if not src.exists():
            raise SystemExit(f"[ERROR] Missing main figure: {src}")
        copy2(src, out_dir / "figures_main" / fname)

    ensure_dir(out_dir / "extended_data")
    for fname in ED_FIGS:
        src = submission_names / fname
        if not src.exists():
            raise SystemExit(f"[ERROR] Missing ED figure: {src}")
        copy2(src, out_dir / "extended_data" / fname)

    # Optional ED Fig.7 (personalization / subject-window adaptation)
    if has_ed7 and ed7_dir:
        copy2(ed7_dir / ED_FIG7_PNG, out_dir / "extended_data" / ED_FIG7_SUBMISSION_NAME)
        if (ed7_dir / ED_FIG7_PDF).exists():
            ensure_dir(out_dir / "internal_optional")
            copy2(ed7_dir / ED_FIG7_PDF, out_dir / "internal_optional" / "Lee_EDfig7.pdf")

    # Optional extras from submission_names
    for opt in [
        "Lee_Fig1.pdf",
        "Lee_Fig1to5_onepage.png",
        "Lee_Fig1to5_onepage.pdf",
        "Lee_Fig1to5_onepage.html",
    ]:
        src = submission_names / opt
        if src.exists():
            ensure_dir(out_dir / "internal_optional")
            copy2(src, out_dir / "internal_optional" / opt)

    # Source Data
    copytree(source_data, out_dir / "source_data")
    if has_ed7 and ed7_dir:
        copy2(ed7_dir / ED_FIG7_SD, out_dir / "source_data" / ED_FIG7_SD)

    # Optional table exports (PNG/PDF) for convenience
    if tables_src.exists():
        ensure_dir(out_dir / "tables_optional")
        for p in tables_src.glob("*.png"):
            # Table 4 was removed from the main manuscript to comply with the
            # 6-item (figures+tables) limit; keep its numerical values in
            # Source Data Fig.5 and Supplementary Table S8 instead.
            if p.name.startswith("Lee_Table4."):
                continue
            copy2(p, out_dir / "tables_optional" / p.name)
        for p in tables_src.glob("*.pdf"):
            if p.name.startswith("Lee_Table4."):
                continue
            copy2(p, out_dir / "tables_optional" / p.name)

    # Optional checklist
    if checklist.exists():
        ensure_dir(out_dir / "internal_optional")
        copy2(checklist, out_dir / "internal_optional" / checklist.name)

    # Optional reviewer code package
    if reviewer_zip.exists():
        ensure_dir(out_dir / "reviewer_code_on_request")
        copy2(reviewer_zip, out_dir / "reviewer_code_on_request" / reviewer_zip.name)

    # Zip bundles (optional)
    zips_dir = out_dir / "zips"
    ensure_dir(zips_dir)
    zip_dir(out_dir / "figures_main", zips_dir / "main_figures")
    zip_dir(out_dir / "extended_data", zips_dir / "extended_data_figures")
    zip_dir(out_dir / "source_data", zips_dir / "source_data")

    # Build upload-only subset
    build_upload_this(out_dir)

    print(f"[OK] Submit-now folder created: {out_dir}")


if __name__ == "__main__":
    main()

