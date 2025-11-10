# EMG Gait Analysis (UMAP + DBSCAN)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

## 개요

본 저장소는 보행 보조 슈트 착용 전후의 근전도(EMG) 신호 분석을 위한 코드와 파이프라인을 제공합니다. 
8명의 피험자에 대해 3가지 조건(일반 보행, 슈트 착용 모터 오프, 슈트 착용 모터 온)에서 
수집된 EMG 데이터를 UMAP 임베딩과 DBSCAN 클러스터링으로 분석합니다.

## Quickstart

```bash
pip install -r requirements.txt

mkdir -p data

# 데이터 파일을 ./data/ 아래에 배치
python src/run_pipeline.py --config configs/default.yaml
```

## 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

## 사용 방법

### 1. 데이터 준비

원시 데이터를 `data/` 디렉토리에 배치합니다:

```
data/
├── subject_241211_1/
│   ├── 241211_1_walking_no_suit.csv
│   ├── 241211_1_walking_suit_motor_off.csv
│   └── 241211_1_walking_suit_motor_on.csv
└── ...
```

**원시 데이터는 Zenodo에서 다운로드하세요:**
- Zenodo DOI: [DOI 링크 추가 예정]
- 데이터셋 크기: 약 6.5GB (24개 CSV 파일, 8명 × 3조건)

### 2. 설정 파일 수정 (선택사항)

`configs/default.yaml`에서 다음 항목을 필요에 따라 수정할 수 있습니다:

- `file_extensions`: 지원할 파일 확장자 (기본: [".csv", ".tsv"])
- `target_columns`: 분석에 사용할 컬럼 (null이면 모든 수치형 컬럼 사용)
- `umap`: UMAP 파라미터 (n_neighbors, min_dist, n_components 등)
- `dbscan`: DBSCAN 파라미터 (eps, min_samples)

### 3. 파이프라인 실행

```bash
python src/run_pipeline.py --config configs/default.yaml
```

### 4. 결과 확인

결과는 `results/` 디렉토리에 저장됩니다:

- `embedding.npy`: UMAP 임베딩 결과 (NumPy 배열)
- `labels.csv`: DBSCAN 클러스터 레이블
- `metrics.json`: 분석 지표 (silhouette score, trustworthiness, noise fraction)
- `umap_dbscan_scatter.png`: UMAP 2D 산점도 시각화

## 데이터셋 정보

### 피험자 정보

| Subject ID | Collection Date | Conditions | Data Completeness |
|------------|----------------|------------|-------------------|
| 241211_1   | 2024-12-11     | 3/3        | Complete          |
| 241211_2   | 2024-12-11     | 3/3        | Complete          |
| 241212_1   | 2024-12-12     | 3/3        | Complete          |
| 241212_2   | 2024-12-12     | 3/3        | Complete          |
| 241212_3   | 2024-12-12     | 3/3        | Complete          |
| 241213_1   | 2024-12-13     | 3/3        | Complete          |
| 241213_2   | 2024-12-13     | 3/3        | Complete          |
| 241216_1   | 2024-12-16     | 3/3        | Complete          |

### 측정 조건

1. **no_suit**: 일반 보행 (보행 보조 슈트 미착용)
2. **suit_motor_off**: 보행 보조 슈트 착용, 모터 작동 안 함
3. **suit_motor_on**: 보행 보조 슈트 착용, 모터 작동 중

### 데이터 형식

- **샘플링 주파수**: 2148 Hz
- **EMG 채널 수**: 16채널
- **파일 형식**: CSV

## 분석 방법론

본 파이프라인은 다음 단계로 구성됩니다:

1. **데이터 로드**: CSV/TSV 파일에서 수치형 특징 추출
2. **표준화**: StandardScaler를 사용한 특징 정규화
3. **UMAP 임베딩**: 고차원 데이터를 2D/3D 공간으로 차원 축소
4. **DBSCAN 클러스터링**: 밀도 기반 클러스터링으로 패턴 식별
5. **평가 지표**: Silhouette score, Trustworthiness, Noise fraction 계산

## 인용 방법 (How to cite)

### Dataset
EMG gait analysis dataset. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

### Code
taniasongbi/taniasongbi (GitHub). https://github.com/taniasongbi/taniasongbi

### BibTeX (dataset)
```bibtex
@dataset{emg_gait_dataset,
  title   = {EMG Gait Analysis Dataset},
  doi     = {10.5281/zenodo.XXXXXXX},
  url     = {https://doi.org/10.5281/zenodo.XXXXXXX},
  publisher = {Zenodo},
  year    = {2025}
}
```

### BibTeX (software)
```bibtex
@software{emg_pipeline_software,
  title   = {EMG Gait Analysis Pipeline (UMAP–DBSCAN)},
  url     = {https://github.com/taniasongbi/taniasongbi},
  note    = {Version: v0.1.0 or later; see releases},
  year    = {2025}
}
```

## Data Availability

Data availability: The EMG gait analysis dataset is available at Zenodo: https://doi.org/10.5281/zenodo.XXXXXXX

Code repository: https://github.com/taniasongbi/taniasongbi

> **참고**: 배지 코드는 Zenodo 레코드 페이지의 **"Markdown"** 블록에서 그대로 복사하면 됩니다. 위 예시는 자리표시자입니다.

## 라이선스

이 코드는 [라이선스 정보 추가] 하에 배포됩니다.

## 문의

문의사항이 있으시면 GitHub Issues를 통해 문의해주세요.

## 참고 문헌

관련 논문이 출판되면 여기에 링크를 추가하겠습니다.
