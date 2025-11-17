import argparse, json, os, sys, glob
import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.manifold import trustworthiness
from scipy.io import loadmat
import umap.umap_ as umap
import matplotlib.pyplot as plt

def read_table(path: Path, cfg):
    ext = path.suffix.lower()
    if ext in [".csv", ".tsv"]:
        sep = "," if ext == ".csv" else "\t"
        df = pd.read_csv(path, sep=sep)
        return df
    if ext == ".mat":
        var = cfg.get("mat_variable")
        if not var:
            raise ValueError(f".mat 파일을 읽으려면 configs.default.yaml의 mat_variable을 지정하세요: {path}")
        mat = loadmat(path)
        if var not in mat:
            raise KeyError(f"'{var}' 변수가 {path.name}에 없습니다. keys={list(mat.keys())[:10]}")
        arr = np.asarray(mat[var])
        if arr.ndim != 2:
            raise ValueError(f"{path.name}:{var}는 2D 행렬이어야 합니다. shape={arr.shape}")
        # 행=샘플, 열=특징으로 가정
        cols = [f"f{i}" for i in range(arr.shape[1])]
        return pd.DataFrame(arr, columns=cols)
    raise ValueError(f"지원하지 않는 확장자: {ext}")

def load_all_frames(data_dir, exts, cfg):
    files = []
    for ext in exts:
        files += glob.glob(os.path.join(data_dir, f"**/*{ext}"), recursive=True)
    if not files:
        raise FileNotFoundError(f"{data_dir}에서 {exts} 확장자의 파일을 찾지 못했습니다.")
    frames, origins = [], []
    for fp in sorted(files):
        df = read_table(Path(fp), cfg)
        df["_source_file"] = os.path.relpath(fp, data_dir)
        frames.append(df)
        origins.append(fp)
    return pd.concat(frames, ignore_index=True), origins

def select_numeric(X, target_columns=None):
    if target_columns:
        return X[target_columns]
    return X.select_dtypes(include=[np.number])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", "-c", default=str(Path(__file__).parents[1] / "configs" / "default.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config, "r"))

    data_dir = cfg["data_dir"]
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)

    df_all, origins = load_all_frames(data_dir, cfg["file_extensions"], cfg)
    # 특징 행렬 추출
    X = select_numeric(df_all.drop(columns=[c for c in df_all.columns if c.startswith("_")], errors="ignore"),
                       cfg.get("target_columns"))
    if X.empty:
        raise ValueError("수치형 특징 열을 찾지 못했습니다. target_columns를 지정하거나 입력 표를 확인하세요.")

    # 표준화
    Xz = StandardScaler().fit_transform(X.values)

    # UMAP 임베딩
    umap_cfg = cfg["umap"]
    um = umap.UMAP(
        n_neighbors=umap_cfg["n_neighbors"],
        min_dist=umap_cfg["min_dist"],
        n_components=umap_cfg["n_components"],
        metric=umap_cfg["metric"],
        random_state=umap_cfg["random_state"]
    )
    Z = um.fit_transform(Xz)

    # DBSCAN 클러스터링 (임베딩 공간에서)
    dbc = cfg["dbscan"]
    min_samples = dbc["min_samples"] if dbc["min_samples"] else 2 * umap_cfg["n_components"]
    db = DBSCAN(eps=dbc["eps"], min_samples=min_samples, metric="euclidean").fit(Z)
    labels = db.labels_

    # 지표
    mask = labels != -1
    sil = float(silhouette_score(Z[mask], labels[mask])) if mask.any() and len(set(labels[mask])) > 1 else np.nan
    tw = float(trustworthiness(Xz, Z, n_neighbors=cfg["metrics"]["trustworthiness_k"]))
    noise_fraction = float(1.0 - mask.mean())

    # 저장
    np.save(out_dir / "embedding.npy", Z)
    pd.DataFrame({
        "source_file": df_all["_source_file"],
        "cluster": labels
    }).to_csv(out_dir / "labels.csv", index=False)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump({"silhouette": sil, "trustworthiness": tw, "noise_fraction": noise_fraction,
                   "n_samples": int(X.shape[0]), "n_features": int(X.shape[1])}, f, indent=2)

    # 간단한 산점도 (2D일 때)
    if Z.shape[1] == 2:
        plt.figure()
        plt.scatter(Z[:,0], Z[:,1], s=5, c=labels)
        plt.title("UMAP + DBSCAN")
        plt.xlabel("UMAP1"); plt.ylabel("UMAP2")
        plt.tight_layout()
        plt.savefig(out_dir / "umap_dbscan_scatter.png", dpi=200)

    print("Done. Results under 'results/'.")
    print({"silhouette": sil, "trustworthiness": tw, "noise_fraction": noise_fraction})

if __name__ == "__main__":
    sys.exit(main())

