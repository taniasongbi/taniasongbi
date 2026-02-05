#!/usr/bin/env python3
"""
Export Plotly (interactive HTML + optional static images) for submission figures/tables.

This script is designed to work with the final submission folder created in:
  docs/journal_submission_deliverables/NBE_FINAL_SUBMISSION_*/

It will:
- Copy existing Plotly HTML for Fig.2–4 from the legacy submission package (if present)
- Generate Plotly HTML for Fig.1 (image-embedded), Fig.5 (composite + panels),
  ED Fig.1–6, and markdown tables (Table 1/4, ED Table 1/2)

Outputs are written under:
  <final_bundle>/plotly/{main,extended_data,tables}/
"""

from __future__ import annotations

import argparse
import base64
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Palette guidance in .cursorrules
PALETTE = {
    "cond": {"NW": "#5C6BC0", "UE": "#FFA726", "PE": "#66BB6A"},
    "terrain": {"Level": "#2196F3", "Slope": "#4CAF50", "Stairs": "#FF5722"},
}


def _std_layout(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        font=dict(family="Arial", size=11),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=dict(text=title or "", x=0.5, font=dict(size=16)),
        margin=dict(l=55, r=25, t=60, b=55),
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
        ),
    )
    return fig


def _write_plotly(
    fig: go.Figure,
    out_html: Path,
    *,
    export_static: bool,
    out_png: Path | None = None,
    out_pdf: Path | None = None,
) -> None:
    out_html.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out_html), include_plotlyjs="cdn", full_html=True)

    if not export_static:
        return

    # Static export via kaleido; keep this best-effort.
    try:
        if out_png is not None:
            fig.write_image(str(out_png), scale=2)
        if out_pdf is not None:
            fig.write_image(str(out_pdf))
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] Static export failed for {out_html.name}: {e}")


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _b64_png(png_path: Path) -> str:
    b = png_path.read_bytes()
    return base64.b64encode(b).decode("ascii")


def _fig_embed_png(png_path: Path, *, title: str | None = None) -> go.Figure:
    b64 = _b64_png(png_path)
    fig = go.Figure()
    fig.update_layout(
        images=[
            dict(
                source=f"data:image/png;base64,{b64}",
                xref="paper",
                yref="paper",
                x=0,
                y=1,
                sizex=1,
                sizey=1,
                sizing="contain",
                layer="below",
            )
        ],
        xaxis=dict(visible=False, range=[0, 1], fixedrange=True),
        yaxis=dict(visible=False, range=[0, 1], fixedrange=True),
        margin=dict(l=0, r=0, t=40 if title else 0, b=0),
        width=1100,
        height=760,
    )
    _std_layout(fig, title=title)
    return fig


def _make_main_1to5_onepage(fig_dir: Path, *, surname: str) -> go.Figure:
    """
    One-page composite of Main Fig.1–5 (as embedded PNG panels).

    This is meant for a polished single-sheet overview (not for NBE item uploads).
    """
    paths = {
        "Fig.1": fig_dir / f"{surname}_Fig1.png",
        "Fig.2": fig_dir / f"{surname}_Fig2.png",
        "Fig.3": fig_dir / f"{surname}_Fig3.png",
        "Fig.4": fig_dir / f"{surname}_Fig4.png",
        "Fig.5": fig_dir / f"{surname}_Fig5.png",
    }
    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing panel PNG(s): {missing}")

    # Layout in paper coordinates (x0, y0, x1, y1)
    layout_boxes = {
        "Fig.1": (0.00, 0.52, 0.54, 1.00),
        "Fig.2": (0.56, 0.52, 1.00, 1.00),
        "Fig.3": (0.00, 0.00, 0.32, 0.48),
        "Fig.4": (0.34, 0.00, 0.66, 0.48),
        "Fig.5": (0.68, 0.00, 1.00, 0.48),
    }

    fig = go.Figure()
    images = []
    shapes = []
    annotations = []

    for label, (x0, y0, x1, y1) in layout_boxes.items():
        # Panel frame (subtle)
        shapes.append(
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                line=dict(color="rgba(0,0,0,0.20)", width=1),
                fillcolor="white",
                layer="below",
            )
        )

        # Image
        b64 = _b64_png(paths[label])
        images.append(
            dict(
                source=f"data:image/png;base64,{b64}",
                xref="paper",
                yref="paper",
                x=x0,
                y=y1,
                sizex=(x1 - x0),
                sizey=(y1 - y0),
                xanchor="left",
                yanchor="top",
                sizing="contain",
                layer="above",
            )
        )

        # Panel label badge
        annotations.append(
            dict(
                text=f"<b>{label}</b>",
                x=x0 + 0.012,
                y=y1 - 0.012,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="black"),
                align="left",
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(0,0,0,0.18)",
                borderwidth=1,
            )
        )

    fig.update_layout(
        images=images,
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(visible=False, range=[0, 1], fixedrange=True),
        yaxis=dict(visible=False, range=[0, 1], fixedrange=True),
        width=1800,
        height=1200,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    _std_layout(fig, title="Main Figures 1–5 (one-page composite)")
    return fig


def _ci_fill_traces(
    x: Iterable[float],
    y_mean: Iterable[float],
    y_low: Iterable[float],
    y_high: Iterable[float],
    *,
    name: str,
    color: str,
    legendgroup: str,
    showlegend: bool,
) -> list[go.Scatter]:
    x = list(x)
    y_mean = list(y_mean)
    y_low = list(y_low)
    y_high = list(y_high)

    # Upper then lower (reversed) to make a filled polygon.
    upper = go.Scatter(
        x=x,
        y=y_high,
        mode="lines",
        line=dict(width=0),
        name=name + " (95% CI)",
        legendgroup=legendgroup,
        showlegend=False,
        hoverinfo="skip",
    )
    lower = go.Scatter(
        x=x,
        y=y_low,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor=_rgba(color, 0.18),
        name=name + " (95% CI)",
        legendgroup=legendgroup,
        showlegend=False,
        hoverinfo="skip",
    )
    mean = go.Scatter(
        x=x,
        y=y_mean,
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(color=color, size=7),
        name=name,
        legendgroup=legendgroup,
        showlegend=showlegend,
        hovertemplate="%{x}: %{y:.3f}<extra></extra>",
    )
    return [upper, lower, mean]


def _rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _make_fig5_composite(src_dir: Path) -> go.Figure:
    df_a = pd.read_csv(src_dir / "SourceData_Fig5a_curve.csv")
    df_b = pd.read_csv(src_dir / "SourceData_Fig5b_critical_errors_keycells.csv")
    df_c = pd.read_csv(src_dir / "SourceData_Fig5c_mismatch_delta_macro_ci.csv")
    df_d = pd.read_csv(src_dir / "SourceData_Fig5d_abstain_curve_summary.csv")

    # 2 rows × 5 cols layout to match the paper composite.
    fig = make_subplots(
        rows=2,
        cols=5,
        specs=[
            [{"colspan": 3}, None, None, {}, {}],
            [{"colspan": 2}, None, {}, {}, {}],
        ],
        # Use annotations for panel letters separately (keeps titles clean)
        horizontal_spacing=0.06,
        vertical_spacing=0.18,
    )

    # (a) small-label calibration curve
    for terrain in ["Level", "Slope", "Stairs"]:
        d = df_a[df_a["test_terrain"] == terrain].sort_values("label_budget")
        color = PALETTE["terrain"].get(terrain, "#444444")
        traces = _ci_fill_traces(
            d["label_budget"],
            d["macro_f1_mean"],
            d["macro_f1_ci_low"],
            d["macro_f1_ci_high"],
            name=terrain,
            color=color,
            legendgroup=f"a-{terrain}",
            showlegend=True,
        )
        for t in traces:
            fig.add_trace(t, row=1, col=1)
    fig.update_xaxes(title_text="Label budget (cycle×phase samples)", row=1, col=1)
    fig.update_yaxes(title_text="Macro-F1 (mean ±95% CI)", row=1, col=1, range=[0, 0.72])

    # (b) critical error rates: two subplots (one per metric)
    metric_to_col = {
        "p_pred_PE_given_true_NW": 4,
        "p_pred_NW_given_true_PE": 5,
    }
    metric_title = {
        "p_pred_PE_given_true_NW": "P(pred=PE | true=NW)",
        "p_pred_NW_given_true_PE": "P(pred=NW | true=PE)",
    }
    method_style = {
        "baseline": dict(color="#5C6BC0"),
        "0label": dict(color="#FFA726"),
    }
    cells = ["Level->Slope", "Level->Stairs", "Stairs->Level"]
    for metric, col in metric_to_col.items():
        dd = df_b[df_b["metric"] == metric].copy()
        dd["cell"] = dd["train_terrain"] + "->" + dd["test_terrain"]
        dd = dd.set_index(["method", "cell"]).reindex(
            pd.MultiIndex.from_product([["baseline", "0label"], cells], names=["method", "cell"])
        )
        # Plot as points with CI error bars.
        for method in ["baseline", "0label"]:
            d = dd.loc[method].reset_index()
            fig.add_trace(
                go.Scatter(
                    x=d["cell"],
                    y=d["mean"],
                    mode="markers",
                    marker=dict(size=9, **method_style[method]),
                    error_y=dict(
                        type="data",
                        symmetric=False,
                        array=(d["ci_high"] - d["mean"]).to_numpy(),
                        arrayminus=(d["mean"] - d["ci_low"]).to_numpy(),
                        thickness=1.5,
                        width=4,
                        color=method_style[method]["color"],
                    ),
                    name=method,
                    legendgroup=f"b-{method}",
                    showlegend=(metric == "p_pred_PE_given_true_NW"),
                    hovertemplate="%{x}<br>%{y:.3f}<extra></extra>",
                ),
                row=1,
                col=col,
            )
        fig.update_yaxes(title_text=metric_title[metric], row=1, col=col, range=[0, 1.02])
        fig.update_xaxes(tickangle=-35, row=1, col=col)

    # (c) mismatch sensitivity heatmap: worst-case across assumed terrain
    # heatmap axes: y=train_terrain, x=true test_terrain
    heat_rows = ["Level", "Slope", "Stairs"]
    heat_cols = ["Level", "Slope", "Stairs"]
    records = []
    for (train, true), g in df_c.groupby(["train_terrain", "test_terrain_true"]):
        # choose worst-case (minimum delta macro-F1)
        idx = g["delta_macro_f1_mean"].idxmin()
        r = g.loc[idx].to_dict()
        records.append(r)
    df_wc = pd.DataFrame.from_records(records)

    z = np.full((len(heat_rows), len(heat_cols)), np.nan, dtype=float)
    text = [["" for _ in heat_cols] for _ in heat_rows]
    for _, r in df_wc.iterrows():
        i = heat_rows.index(r["train_terrain"])
        j = heat_cols.index(r["test_terrain_true"])
        z[i, j] = float(r["delta_macro_f1_mean"])
        text[i][j] = f"{z[i, j]:+.3f}<br>[{r['delta_macro_f1_ci_low']:+.3f}, {r['delta_macro_f1_ci_high']:+.3f}]"

    fig.add_trace(
        go.Heatmap(
            z=z,
            x=heat_cols,
            y=heat_rows,
            text=text,
            texttemplate="%{text}",
            textfont={"size": 10},
            colorscale="RdBu_r",
            zmin=-0.20,
            zmax=0.20,
            colorbar=dict(title="Δmacro-F1", len=0.36, y=0.14),
            hovertemplate="Train=%{y}<br>True test=%{x}<br>Δmacro-F1=%{z:.3f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.update_xaxes(title_text="True test terrain", row=2, col=1)
    fig.update_yaxes(title_text="Train terrain", row=2, col=1)

    # (d) abstain curves: 3 subplots for OFFDIAG_ALL
    dd = df_d[df_d["group"] == "OFFDIAG_ALL"].copy()
    metric_cols = {
        "macro_f1": (2, 3, "Macro-F1"),
        "p_pred_PE_given_true_NW": (2, 4, "P(pred=PE | true=NW)"),
        "p_pred_NW_given_true_PE": (2, 5, "P(pred=NW | true=PE)"),
    }
    for metric, (r, c, ylab) in metric_cols.items():
        for method in ["baseline", "0label"]:
            d = dd[(dd["metric"] == metric) & (dd["method"] == method)].sort_values("threshold")
            color = method_style[method]["color"]
            traces = _ci_fill_traces(
                d["coverage_mean"],
                d["value_mean"],
                d["value_ci_low"],
                d["value_ci_high"],
                name=method,
                color=color,
                legendgroup=f"d-{method}",
                showlegend=(metric == "macro_f1"),
            )
            for t in traces:
                fig.add_trace(t, row=r, col=c)
        fig.update_xaxes(title_text="Coverage (fraction not abstained)", row=r, col=c, range=[0, 1.0])
        fig.update_yaxes(title_text=ylab, row=r, col=c, range=[0, 1.02] if metric != "macro_f1" else [0, 1.0])

    # Panel labels
    fig.add_annotation(text="<b>(a)</b>", x=0.01, y=1.08, xref="paper", yref="paper", showarrow=False)
    fig.add_annotation(text="<b>(b)</b>", x=0.74, y=1.08, xref="paper", yref="paper", showarrow=False)
    fig.add_annotation(text="<b>(c)</b>", x=0.01, y=0.48, xref="paper", yref="paper", showarrow=False)
    fig.add_annotation(text="<b>(d)</b>", x=0.62, y=0.48, xref="paper", yref="paper", showarrow=False)

    _std_layout(fig, title="Deployment risk analyses (Fig. 5)")
    fig.update_layout(width=1350, height=850)
    return fig


def _make_edfig1(src_dir: Path) -> go.Figure:
    df = pd.read_csv(src_dir / "SourceData_ED_Fig1_domain_importance.csv")
    domains = ["Time", "Freq", "Wave", "NL10"]
    terrains = ["Level", "Slope", "Stairs"]
    fig = make_subplots(rows=1, cols=3, subplot_titles=terrains, shared_yaxes=True)
    for i, terrain in enumerate(terrains, start=1):
        d = df[df["terrain"] == terrain].set_index("domain").reindex(domains).reset_index()
        fig.add_trace(
            go.Bar(
                x=d["domain"],
                y=d["importance_mean"],
                error_y=dict(
                    type="data",
                    symmetric=False,
                    array=(d["importance_ci_high"] - d["importance_mean"]).to_numpy(),
                    arrayminus=(d["importance_mean"] - d["importance_ci_low"]).to_numpy(),
                ),
                marker=dict(color=PALETTE["terrain"][terrain]),
                showlegend=False,
                hovertemplate="%{x}<br>%{y:.3f}<extra></extra>",
            ),
            row=1,
            col=i,
        )
        fig.update_xaxes(title_text="Domain", row=1, col=i)
    fig.update_yaxes(title_text="Δmacro-F1 (permutation importance)", row=1, col=1)
    _std_layout(fig, title="ED Fig.1 — Domain permutation importance")
    fig.update_layout(width=1100, height=420)
    return fig


def _make_edfig2(src_dir: Path) -> go.Figure:
    df_cell = pd.read_csv(src_dir / "SourceData_ED_Fig2_delta_macro_f1_per_cell.csv")
    df_long = pd.read_csv(src_dir / "SourceData_ED_Fig2_per_subject_macro_f1_long.csv")

    terrains = ["Level", "Slope", "Stairs"]
    # Heatmap: delta (calibrated - baseline)
    z = np.zeros((3, 3), dtype=float)
    text = [["" for _ in terrains] for _ in terrains]
    for _, r in df_cell.iterrows():
        i = terrains.index(r["train_terrain"])
        j = terrains.index(r["test_terrain"])
        z[i, j] = float(r["delta_mean"])
        text[i][j] = f"{z[i, j]:+.3f}"

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.55, 0.45],
        subplot_titles=["Δmacro-F1 (0-label − baseline)", "Per-subject macro-F1 distribution"],
    )
    fig.add_trace(
        go.Heatmap(
            z=z,
            x=terrains,
            y=terrains,
            text=text,
            texttemplate="%{text}",
            textfont={"size": 11},
            colorscale="RdBu_r",
            zmin=-0.15,
            zmax=0.15,
            colorbar=dict(title="Δmacro-F1", len=0.8, y=0.5),
            hovertemplate="Train=%{y}<br>Test=%{x}<br>Δmacro-F1=%{z:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.update_xaxes(title_text="Test terrain", row=1, col=1)
    fig.update_yaxes(title_text="Train terrain", row=1, col=1)

    df_long["cell"] = df_long["train_terrain"] + "→" + df_long["test_terrain"]
    # Keep consistent ordering (train major, test minor)
    cell_order = [f"{tr}→{te}" for tr in terrains for te in terrains]
    df_long["cell"] = pd.Categorical(df_long["cell"], categories=cell_order, ordered=True)
    # Box + points
    for method, color in [("baseline", "#5C6BC0"), ("0label", "#FFA726")]:
        d = df_long[df_long["method"] == method]
        fig.add_trace(
            go.Box(
                x=d["cell"],
                y=d["macro_f1"],
                name=method,
                marker_color=color,
                boxmean=False,
                boxpoints="all",
                jitter=0.35,
                pointpos=0.0,
                legendgroup=f"ed2-{method}",
                showlegend=True,
            ),
            row=1,
            col=2,
        )
    fig.update_xaxes(title_text="Train→Test cell", tickangle=-45, row=1, col=2)
    fig.update_yaxes(title_text="Macro-F1", row=1, col=2, range=[0, 0.8])
    _std_layout(fig, title="ED Fig.2 — Transfer deltas and per-subject distributions")
    fig.update_layout(width=1350, height=520, boxmode="group")
    return fig


def _make_edfig2_clustergram_delta(src_dir: Path) -> go.Figure:
    """
    Clustergram (heatmap + row/col dendrograms) for per-subject Δmacro-F1 across 3×3 transfer cells.

    Uses SourceData_ED_Fig2_per_subject_macro_f1_long.csv:
      - baseline and 0label macro-F1 per subject × (train→test) cell
    We visualize Δ = 0label − baseline and cluster both subjects and cells.
    """
    df_long = pd.read_csv(src_dir / "SourceData_ED_Fig2_per_subject_macro_f1_long.csv")
    terrains = ["Level", "Slope", "Stairs"]
    cell_order = [f"{tr}→{te}" for tr in terrains for te in terrains]

    df_long["cell"] = df_long["train_terrain"] + "→" + df_long["test_terrain"]
    base = df_long[df_long["method"] == "baseline"].pivot_table(index="subject", columns="cell", values="macro_f1")
    olab = df_long[df_long["method"] == "0label"].pivot_table(index="subject", columns="cell", values="macro_f1")

    mat = (olab - base).reindex(columns=cell_order)
    # clustering input: impute missing as 0 after centering (should be rare)
    X = mat.to_numpy(dtype=float)
    Xc = np.where(np.isfinite(X), X, 0.0)

    row_labels = mat.index.tolist()
    col_labels = mat.columns.tolist()

    # dendrograms (Plotly factory)
    fig_row = ff.create_dendrogram(Xc, orientation="left", labels=row_labels)
    fig_col = ff.create_dendrogram(Xc.T, orientation="top", labels=col_labels)

    # leaf order extracted from tick labels (factory stores leaves there)
    row_order = list(fig_row.layout.yaxis.ticktext)
    col_order = list(fig_col.layout.xaxis.ticktext)
    y_ticks = list(fig_row.layout.yaxis.tickvals)
    x_ticks = list(fig_col.layout.xaxis.tickvals)

    row_idx = [row_labels.index(x) for x in row_order]
    col_idx = [col_labels.index(x) for x in col_order]
    X_ord = X[np.ix_(row_idx, col_idx)]

    # Build a combined figure: [top dendro] + [left dendro] + [heatmap]
    fig = make_subplots(
        rows=2,
        cols=2,
        column_widths=[0.20, 0.80],
        row_heights=[0.22, 0.78],
        specs=[[{"type": "scatter"}, {"type": "scatter"}], [{"type": "scatter"}, {"type": "heatmap"}]],
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
    )

    # (1,1) empty
    fig.update_xaxes(visible=False, row=1, col=1)
    fig.update_yaxes(visible=False, row=1, col=1)

    # Column dendrogram (1,2)
    for tr in fig_col.data:
        tr.showlegend = False
        fig.add_trace(tr, row=1, col=2)

    # Row dendrogram (2,1)
    for tr in fig_row.data:
        tr.showlegend = False
        fig.add_trace(tr, row=2, col=1)

    # Heatmap (2,2)
    max_abs = float(np.nanmax(np.abs(X_ord))) if np.isfinite(np.nanmax(np.abs(X_ord))) else 0.15
    zlim = max(0.05, min(0.25, max_abs * 1.25))

    # Customdata: subject + cell labels
    custom = np.empty((len(row_order), len(col_order), 2), dtype=object)
    for i, s in enumerate(row_order):
        for j, c in enumerate(col_order):
            custom[i, j, 0] = s
            custom[i, j, 1] = c

    fig.add_trace(
        go.Heatmap(
            z=X_ord,
            x=x_ticks,
            y=y_ticks,
            colorscale="RdBu_r",
            zmin=-zlim,
            zmax=zlim,
            colorbar=dict(title="Δmacro-F1", len=0.70, y=0.30),
            text=[[f"{v:+.3f}" if np.isfinite(v) else "" for v in row] for row in X_ord],
            texttemplate="%{text}",
            textfont={"size": 10},
            customdata=custom,
            hovertemplate="Subject=%{customdata[0]}<br>Cell=%{customdata[1]}<br>Δmacro-F1=%{z:.3f}<extra></extra>",
        ),
        row=2,
        col=2,
    )

    # Axis styling & alignment
    x_min, x_max = float(np.min(x_ticks)), float(np.max(x_ticks))
    y_min, y_max = float(np.min(y_ticks)), float(np.max(y_ticks))

    # Column dendrogram axes: match x with heatmap x
    fig.update_xaxes(range=[x_min - 5, x_max + 5], showticklabels=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, row=1, col=2)

    # Row dendrogram axes: match y with heatmap y
    fig.update_yaxes(range=[y_min - 5, y_max + 5], showticklabels=False, row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=2, col=1)

    # Heatmap axes with labels
    fig.update_xaxes(
        range=[x_min - 5, x_max + 5],
        tickmode="array",
        tickvals=x_ticks,
        ticktext=col_order,
        tickangle=-45,
        row=2,
        col=2,
        title_text="Train→Test cell",
    )
    fig.update_yaxes(
        range=[y_min - 5, y_max + 5],
        tickmode="array",
        tickvals=y_ticks,
        ticktext=row_order,
        row=2,
        col=2,
        title_text="Subject",
    )

    _std_layout(fig, title="ED Fig.2 (clustergram) — per-subject Δmacro-F1 (0-label − baseline)")
    fig.update_layout(width=1400, height=900)
    return fig


def _make_edfig3(src_dir: Path) -> go.Figure:
    df = pd.read_csv(src_dir / "SourceData_ED_Fig3_mismatch_6combo_delta_macro_and_risk.csv")
    terrains = ["Level", "Slope", "Stairs"]
    df = df.set_index(["test_terrain_true", "norm_terrain_assumed"]).reindex(
        pd.MultiIndex.from_product([terrains, terrains], names=["test_terrain_true", "norm_terrain_assumed"])
    ).reset_index()

    # Build matrices (diagonal is NaN)
    def mat(col: str) -> np.ndarray:
        m = np.full((3, 3), np.nan, dtype=float)
        for _, r in df.iterrows():
            i = terrains.index(r["test_terrain_true"])
            j = terrains.index(r["norm_terrain_assumed"])
            if r["test_terrain_true"] == r["norm_terrain_assumed"]:
                continue
            if pd.isna(r[col]):
                continue
            m[i, j] = float(r[col])
        return m

    z_f1 = mat("delta_macro_f1_mean")
    z_nw_pe = mat("p_pred_PE_given_true_NW__delta_mean")
    z_pe_nw = mat("p_pred_NW_given_true_PE__delta_mean")

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Δmacro-F1", "ΔP(pred=PE|true=NW)", "ΔP(pred=NW|true=PE)"],
        shared_yaxes=True,
    )
    for col_idx, (z, title, zmin, zmax) in enumerate(
        [
            (z_f1, "Δmacro-F1", -0.20, 0.10),
            (z_nw_pe, "ΔP", -0.50, 0.70),
            (z_pe_nw, "ΔP", -0.50, 0.70),
        ],
        start=1,
    ):
        fig.add_trace(
            go.Heatmap(
                z=z,
                x=terrains,
                y=terrains,
                colorscale="RdBu_r",
                zmin=zmin,
                zmax=zmax,
                text=[[("" if np.isnan(v) else f"{v:+.3f}") for v in row] for row in z],
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar=dict(title=title, len=0.85, y=0.5) if col_idx == 3 else None,
                hovertemplate="True=%{y}<br>Assumed=%{x}<br>Δ=%{z:.3f}<extra></extra>",
            ),
            row=1,
            col=col_idx,
        )
        fig.update_xaxes(title_text="Assumed norm terrain", row=1, col=col_idx)
    fig.update_yaxes(title_text="True test terrain", row=1, col=1)
    _std_layout(fig, title="ED Fig.3 — Terrain-label mismatch sensitivity (full)")
    fig.update_layout(width=1350, height=450)
    return fig


def _make_edfig4(src_dir: Path) -> go.Figure:
    df = pd.read_csv(src_dir / "SourceData_ED_Fig4_speed_control_keycells_summary.csv")
    # Keep key off-diagonal cells for readability
    df["cell"] = df["train_terrain"] + "→" + df["test_terrain"]
    key_cells = ["Level→Slope", "Level→Stairs", "Stairs→Level"]
    df = df[df["cell"].isin(key_cells)]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Macro-F1", "P(pred=PE|true=NW)", "P(pred=NW|true=PE)"],
        shared_xaxes=True,
    )
    metric_map = {
        "macro_f1": (1, 1),
        "p_pred_PE_given_true_NW": (1, 2),
        "p_pred_NW_given_true_PE": (1, 3),
    }
    style = {"baseline": "#5C6BC0", "0label": "#FFA726"}
    for metric, (r, c) in metric_map.items():
        d = df[df["metric"] == metric]
        for scenario in ["full", "matched"]:
            for method in ["baseline", "0label"]:
                s = d[(d["scenario"] == scenario) & (d["method"] == method)].copy()
                s = s.set_index("cell").reindex(key_cells).reset_index()
                name = f"{method}-{scenario}"
                fig.add_trace(
                    go.Bar(
                        x=s["cell"],
                        y=s["mean"],
                        name=name,
                        marker=dict(color=style[method], opacity=0.55 if scenario == "matched" else 0.95),
                        error_y=dict(
                            type="data",
                            symmetric=False,
                            array=(s["ci_high"] - s["mean"]).to_numpy(),
                            arrayminus=(s["mean"] - s["ci_low"]).to_numpy(),
                        ),
                        legendgroup=name,
                        showlegend=(metric == "macro_f1"),
                    ),
                    row=r,
                    col=c,
                )
        fig.update_xaxes(tickangle=-35, row=r, col=c)
    fig.update_yaxes(title_text="Value", row=1, col=1)
    _std_layout(fig, title="ED Fig.4 — Speed (stride-time) control: full vs matched")
    fig.update_layout(width=1350, height=430, barmode="group")
    return fig


def _make_edfig5(src_dir: Path) -> go.Figure:
    df = pd.read_csv(src_dir / "SourceData_ED_Fig5_sampling_seed_cap_long.csv")
    df["cell"] = df["train_terrain"] + "→" + df["test_terrain"]
    # Focus on 3×3 cells; interactive can show all.
    terrains = ["Level", "Slope", "Stairs"]
    cell_order = [f"{tr}→{te}" for tr in terrains for te in terrains]
    df["cell"] = pd.Categorical(df["cell"], categories=cell_order, ordered=True)

    fig = go.Figure()
    for cap in sorted(df["cap_cycles_per_file"].unique()):
        d = df[df["cap_cycles_per_file"] == cap]
        fig.add_trace(
            go.Box(
                x=d["cell"],
                y=d["macro_f1_subject_mean"],
                name=f"cap={cap}",
                boxpoints="all",
                jitter=0.35,
                pointpos=0.0,
            )
        )
    fig.update_xaxes(title_text="Train→Test cell", tickangle=-45)
    fig.update_yaxes(title_text="Macro-F1 (subject-mean, per run)", range=[0, 0.7])
    _std_layout(fig, title="ED Fig.5 — Sampling sensitivity (seed × cap per file)")
    fig.update_layout(width=1350, height=520, boxmode="group")
    return fig


def _make_edfig6(src_dir: Path) -> go.Figure:
    df_invalid = pd.read_csv(src_dir / "SourceData_ED_Fig6_nl10_invalid_rates.csv")
    df_strategy = pd.read_csv(src_dir / "SourceData_ED_Fig6_nl10_missing_summary.csv")
    df_wave = pd.read_csv(src_dir / "SourceData_ED_Fig6_wavelet_delta_macro_f1.csv")
    df_sentinel = pd.read_csv(src_dir / "SourceData_ED_Fig6_wavelet_sentinel_rate.csv")

    terrains = ["Level", "Slope", "Stairs"]
    phases = ["IC", "LR", "MSt", "TSt", "PSw", "ISw", "MSw", "TSw"]

    def heat(df: pd.DataFrame, value_col: str) -> tuple[np.ndarray, list[list[str]]]:
        z = np.full((len(phases), len(terrains)), np.nan, dtype=float)
        text = [["" for _ in terrains] for _ in phases]
        for _, r in df.iterrows():
            i = phases.index(r["phase"])
            j = terrains.index(r["terrain"])
            v = float(r[value_col])
            z[i, j] = v
            text[i][j] = f"{v:.1f}"
        return z, text

    z_inv, t_inv = heat(df_invalid, "invalid_rate_pct")
    z_sent, t_sent = heat(df_sentinel, "sentinel_rate_pct")

    # Strategy performance (aggregate across cells)
    df_strategy["cell"] = df_strategy["train_terrain"] + "→" + df_strategy["test_terrain"]
    # Only show OFFDIAG + DIAG summary as mean over cells
    df_strategy["is_diag"] = df_strategy["train_terrain"] == df_strategy["test_terrain"]
    df_sum = (
        df_strategy.assign(group=lambda x: np.where(x["is_diag"], "DIAG", "OFFDIAG"))
        .groupby(["strategy", "group"], as_index=False)["macro_f1_mean"]
        .mean()
    )

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "NL10 invalid rate (%)",
            "NL10 handling strategies (mean macro-F1)",
            "Wavelet sentinel rate (%)",
            "Wavelet handling Δmacro-F1 vs keep0",
        ],
    )

    fig.add_trace(
        go.Heatmap(
            z=z_inv,
            x=terrains,
            y=phases,
            text=t_inv,
            texttemplate="%{text}",
            textfont={"size": 10},
            colorscale="Reds",
            zmin=0,
            zmax=max(1.0, float(np.nanmax(z_inv))),
            colorbar=dict(title="%", len=0.45, y=0.78),
        ),
        row=1,
        col=1,
    )
    fig.update_xaxes(title_text="Terrain", row=1, col=1)
    fig.update_yaxes(title_text="Phase", row=1, col=1)

    for grp, col in [("DIAG", "#2196F3"), ("OFFDIAG", "#FF5722")]:
        d = df_sum[df_sum["group"] == grp].set_index("strategy").reset_index()
        fig.add_trace(
            go.Bar(x=d["strategy"], y=d["macro_f1_mean"], name=grp, marker=dict(color=col)),
            row=1,
            col=2,
        )
    fig.update_xaxes(title_text="Strategy", row=1, col=2, tickangle=-25)
    fig.update_yaxes(title_text="Mean macro-F1", row=1, col=2, range=[0, 0.55])

    fig.add_trace(
        go.Heatmap(
            z=z_sent,
            x=terrains,
            y=phases,
            text=t_sent,
            texttemplate="%{text}",
            textfont={"size": 10},
            colorscale="Blues",
            zmin=0,
            zmax=max(1.0, float(np.nanmax(z_sent))) if np.isfinite(np.nanmax(z_sent)) else 1.0,
            colorbar=dict(title="%", len=0.45, y=0.22),
        ),
        row=2,
        col=1,
    )
    fig.update_xaxes(title_text="Terrain", row=2, col=1)
    fig.update_yaxes(title_text="Phase", row=2, col=1)

    fig.add_trace(
        go.Bar(
            x=df_wave["train_terrain"] + "→" + df_wave["test_terrain"],
            y=df_wave["delta_macro_f1_vs_keep0"],
            marker=dict(color="#78909C"),
            showlegend=False,
        ),
        row=2,
        col=2,
    )
    fig.update_xaxes(title_text="Train→Test", row=2, col=2, tickangle=-45)
    fig.update_yaxes(title_text="Δmacro-F1", row=2, col=2)

    _std_layout(fig, title="ED Fig.6 — Missing/failure modes (NL10 + wavelet)")
    fig.update_layout(width=1350, height=720)
    return fig


@dataclass(frozen=True)
class MdTable:
    heading: str
    headers: list[str]
    rows: list[list[str]]


def _parse_md_tables(md_text: str) -> list[MdTable]:
    tables: list[MdTable] = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            heading = line[4:].strip()
            # normalize common markdown escapes used in headings
            heading_norm = heading.replace("\\_", "_")
            # Scan forward for a markdown table.
            j = i + 1
            found = False
            while j < len(lines):
                nxt = lines[j]
                # If another heading starts before a table, this heading has no table.
                if nxt.startswith("### ") or nxt.startswith("## "):
                    break
                if nxt.lstrip().startswith("|"):
                    found = True
                    break
                j += 1
            if not found:
                i += 1
                continue
            # Collect contiguous table lines.
            k = j
            tbl_lines = []
            while k < len(lines) and lines[k].lstrip().startswith("|"):
                tbl_lines.append(lines[k].strip())
                k += 1
            # Parse
            def split_row(s: str) -> list[str]:
                parts = [p.strip() for p in s.strip().strip("|").split("|")]
                return parts

            if len(tbl_lines) >= 2:
                headers = split_row(tbl_lines[0])
                body = [split_row(x) for x in tbl_lines[2:]]  # skip separator row
                tables.append(MdTable(heading=heading_norm, headers=headers, rows=body))
            i = k
            continue
        i += 1
    return tables


def _plotly_table(md: MdTable, *, title: str) -> go.Figure:
    cols = list(zip(*md.rows)) if md.rows else [[] for _ in md.headers]
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=md.headers,
                    fill_color="#F2F2F2",
                    align="center",
                    font=dict(size=12, color="black"),
                ),
                cells=dict(
                    values=cols,
                    align="center",
                    fill_color="white",
                    font=dict(size=11),
                    height=24,
                ),
            )
        ]
    )
    _std_layout(fig, title=title)
    fig.update_layout(width=1100, height=420)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--final_bundle",
        type=Path,
        default=Path(
            "/Volumes/Expansion/EMG_Project_Backup_20250821_062537/nbe1_local/"
            "docs/journal_submission_deliverables/NBE_FINAL_SUBMISSION_v1.0_20260204_125813"
        ),
        help="Final submission folder (contains figures/, source_data/, manuscript/).",
    )
    ap.add_argument("--surname", type=str, default="Lee", help="Surname prefix for submission naming.")
    ap.add_argument("--export_static", action="store_true", help="Also export PNG/PDF via kaleido.")
    args = ap.parse_args()

    bundle = args.final_bundle
    out_root = bundle / "plotly"
    out_main = out_root / "main"
    out_ed = out_root / "extended_data"
    out_tables = out_root / "tables"
    out_root.mkdir(parents=True, exist_ok=True)

    src_data = bundle / "source_data"
    legacy_pkg = (
        bundle.parent / "SUBMISSION_PACKAGE_v1.0_20260119"
    )  # existing repository artifact

    # 1) Copy legacy Plotly HTML for Fig2–4 if present
    legacy_map = {
        "Fig2": "Figure_2_Classification_Results.html",
        "Fig3": "Figure_3_Ablation_Phase_Effects.html",
        "Fig4": "Figure_4_Realtime_Performance.html",
    }
    for key, fname in legacy_map.items():
        src = legacy_pkg / fname
        dst = out_main / f"{args.surname}_{key}.html"
        ok = _copy_if_exists(src, dst)
        print(f"[{'OK' if ok else 'SKIP'}] copy legacy {key}: {src.name if src.exists() else src}")

    # 2) Fig1 as embedded PNG (updated pipeline clean)
    fig1_png = bundle / "figures" / f"{args.surname}_Fig1.png"
    if fig1_png.exists():
        fig1 = _fig_embed_png(fig1_png, title="Fig.1 (embedded): Pipeline diagram")
        _write_plotly(
            fig1,
            out_main / f"{args.surname}_Fig1.html",
            export_static=args.export_static,
            out_png=(out_main / f"{args.surname}_Fig1.png") if args.export_static else None,
            out_pdf=(out_main / f"{args.surname}_Fig1.pdf") if args.export_static else None,
        )
        print("[OK] Fig1 embedded HTML")
    else:
        print(f"[SKIP] Fig1 PNG not found: {fig1_png}")

    # 3) Fig5 composite (and can be used as main Plotly Fig5)
    fig5 = _make_fig5_composite(src_data)
    _write_plotly(
        fig5,
        out_main / f"{args.surname}_Fig5.html",
        export_static=args.export_static,
        out_png=(out_main / f"{args.surname}_Fig5.png") if args.export_static else None,
        out_pdf=(out_main / f"{args.surname}_Fig5.pdf") if args.export_static else None,
    )
    print("[OK] Fig5 Plotly composite")

    # 3b) One-page composite of Fig1–5 (embedded PNGs from submission bundle)
    try:
        onepage = _make_main_1to5_onepage(bundle / "figures", surname=args.surname)
        _write_plotly(
            onepage,
            out_main / f"{args.surname}_Fig1to5_onepage.html",
            export_static=args.export_static,
            out_png=(out_main / f"{args.surname}_Fig1to5_onepage.png") if args.export_static else None,
            out_pdf=(out_main / f"{args.surname}_Fig1to5_onepage.pdf") if args.export_static else None,
        )
        print("[OK] Main Fig1–5 one-page composite")
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] One-page composite skipped: {e}")

    # 4) ED figs 1–6
    ed_builders = [
        (1, _make_edfig1),
        (2, _make_edfig2),
        (3, _make_edfig3),
        (4, _make_edfig4),
        (5, _make_edfig5),
        (6, _make_edfig6),
    ]
    for idx, fn in ed_builders:
        fig = fn(src_data)
        _write_plotly(
            fig,
            out_ed / f"{args.surname}_EDfig{idx}.html",
            export_static=args.export_static,
            out_png=(out_ed / f"{args.surname}_EDfig{idx}.png") if args.export_static else None,
            out_pdf=(out_ed / f"{args.surname}_EDfig{idx}.pdf") if args.export_static else None,
        )
        print(f"[OK] ED Fig{idx} Plotly")

    # 4b) ED Fig.2 clustergram (supplementary interactive view)
    try:
        cg = _make_edfig2_clustergram_delta(src_data)
        _write_plotly(
            cg,
            out_ed / f"{args.surname}_EDfig2_clustergram_delta.html",
            export_static=args.export_static,
            out_png=(out_ed / f"{args.surname}_EDfig2_clustergram_delta.png") if args.export_static else None,
            out_pdf=(out_ed / f"{args.surname}_EDfig2_clustergram_delta.pdf") if args.export_static else None,
        )
        print("[OK] ED Fig2 clustergram (delta) Plotly")
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] ED Fig2 clustergram skipped: {e}")

    # 5) Tables from KR manuscript markdown (Table 1/4, ED Table 1/2)
    md_candidates = sorted((bundle / "manuscript").glob("*_KR.md"))
    md_path = md_candidates[0] if md_candidates else None
    if md_path and md_path.exists():
        md_text = md_path.read_text(encoding="utf-8")
        tables = _parse_md_tables(md_text)
        wanted = {
            "표 1. 지형 및 조건별 보행 주기 분포(전체 수집 데이터)": f"{args.surname}_Table1",
            "표 4. 소량 라벨 캘리브레이션 커브 (leave-one-terrain-out; macro-F1; F28(+Φ_B)+RF)": f"{args.surname}_Table4",
            "Extended Data 표 1. 임계값 범위별 edges_auc_norm": f"{args.surname}_EDtable1",
            "Extended Data 표 2. HS/TO 검출 파라미터 민감도": f"{args.surname}_EDtable2",
        }
        for t in tables:
            if t.heading not in wanted:
                continue
            stem = wanted[t.heading]
            fig = _plotly_table(t, title=t.heading)
            _write_plotly(
                fig,
                out_tables / f"{stem}.html",
                export_static=args.export_static,
                out_png=(out_tables / f"{stem}.png") if args.export_static else None,
                out_pdf=(out_tables / f"{stem}.pdf") if args.export_static else None,
            )
            print(f"[OK] Table export: {stem}")
    else:
        print("[SKIP] KR manuscript not found in bundle/manuscript/")

    # 6) Convenience index
    index_lines = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Plotly exports</title></head><body>",
        "<h2>Plotly exports (submission)</h2>",
        "<h3>Main</h3><ul>",
    ]
    for p in sorted(out_main.glob("*.html")):
        index_lines.append(f"<li><a href='main/{p.name}'>{p.name}</a></li>")
    index_lines.append("</ul><h3>Extended Data</h3><ul>")
    for p in sorted(out_ed.glob("*.html")):
        index_lines.append(f"<li><a href='extended_data/{p.name}'>{p.name}</a></li>")
    index_lines.append("</ul><h3>Tables</h3><ul>")
    for p in sorted(out_tables.glob("*.html")):
        index_lines.append(f"<li><a href='tables/{p.name}'>{p.name}</a></li>")
    index_lines.append("</ul></body></html>")
    (out_root / "index.html").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"[OK] Wrote index: {out_root / 'index.html'}")


if __name__ == "__main__":
    main()

