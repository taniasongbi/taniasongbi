# EMG Gait Analysis (UMAP + DBSCAN)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

## 개요

본 저장소는 보행 보조 슈트 착용 전후의 근전도(EMG) 신호 분석을 위한 코드와 파이프라인을 제공합니다. 
8명의 피험자에 대해 3가지 조건(일반 보행, 슈트 착용 모터 오프, 슈트 착용 모터 온)에서 
수집된 EMG 데이터를 UMAP 임베딩과 DBSCAN 클러스터링으로 분석합니다.

## 데이터 가용성

**원시 데이터는 DOI가 발급된 저장소에서 제공됩니다:**

- **Zenodo**: [DOI 링크 추가 예정]
- **데이터셋 크기**: 약 6.5GB (24개 CSV 파일, 8명 × 3조건)
- **샘플링 주파수**: 2148 Hz
- **EMG 채널 수**: 16채널

원시 데이터를 다운로드한 후 `data/raw/` 디렉토리에 배치하세요.

### 현재 포함된 데이터 (9개 파일)

본 저장소에는 "no suit" 조건의 데이터 9개 파일이 Git LFS로 포함되어 있습니다:

1. `data/raw/241211_2_walking_no suit.csv` - 2024년 12월 11일, 세션 2
2. `data/raw/241212_1_walking_no suit.csv` - 2024년 12월 12일, 세션 1
3. `data/raw/241212_2_walking_no suit.csv` - 2024년 12월 12일, 세션 2
4. `data/raw/241212_3_walking_no suit.csv` - 2024년 12월 12일, 세션 3
5. `data/raw/241213_1_walking_no suit.csv` - 2024년 12월 13일, 세션 1
6. `data/raw/241213_2_walking_no suit.csv` - 2024년 12월 13일, 세션 2
7. `data/raw/241216_1_walking_no suit.csv` - 2024년 12월 16일, 세션 1
8. `data/raw/241216_2_walking_no suit.csv` - 2024년 12월 16일, 세션 2
9. `data/raw/241216_3_walking_no suit.csv` - 2024년 12월 16일, 세션 3

**총 데이터 크기**: 약 2.0GB, 6,079,344 행

## Quickstart

```bash
pip install -r requirements.txt

mkdir -p data/raw

# 데이터 파일을 ./data/raw/ 아래에 배치 (또는 Git LFS로 다운로드)
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

원시 데이터를 `data/raw/` 디렉토리에 배치합니다:

```
data/
└── raw/
    ├── 241211_2_walking_no suit.csv
    ├── 241212_1_walking_no suit.csv
    └── ...
```

**Git LFS로 데이터 다운로드:**
```bash
git lfs pull
```

**원시 데이터는 Zenodo에서도 다운로드 가능:**
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

### 5. 데이터 검증

```bash
python scripts/validate_data.py
```

## 데이터 구조

### 데이터 형식

각 CSV 파일은 다음 구조를 가집니다:

- **컬럼 1**: `Time (s)` - 시간 (초)
- **컬럼 2-16**: `EMG 1` ~ `EMG 16` - 16채널 EMG 신호
  - EMG 1: Tibialis Anterior (L) - 왼쪽 전경골근
  - EMG 4: Upper Tibialis Anterior (L) - 왼쪽 상부 전경골근
  - EMG 5: Gastrocnemius (L) - 왼쪽 비복근
  - EMG 6: Rectus Femoris (L) - 왼쪽 대퇴직근
  - EMG 7: Tensor Fascia Lata (L) - 왼쪽 장경인대
  - EMG 8: Biceps Femoris (L) - 왼쪽 대퇴이두근
  - EMG 9: Tibialis Anterior (R) - 오른쪽 전경골근
  - EMG 10: Upper Tibialis Anterior (R) - 오른쪽 상부 전경골근
  - EMG 11: Gastrocnemius (R) - 오른쪽 비복근
  - EMG 12: Rectus Femoris (R) - 오른쪽 대퇴직근
  - EMG 13: Tensor Fascia Lata (R) - 오른쪽 장경인대
  - EMG 14: Biceps Femoris (R) - 오른쪽 대퇴이두근
  - EMG 2, 3, 15, 16: Unused - 미사용 채널

### 샘플링 정보

- **샘플링 레이트**: 약 2,148 Hz (평균 샘플 간격: 0.000466초)
- **평균 데이터 길이**: 약 670,000 - 680,000 행
- **평균 파일 크기**: 약 230-235 MB

## 디렉토리 구조

```
.
├── README.md                    # 본 파일
├── requirements.txt             # Python 패키지 의존성
├── configs/
│   └── default.yaml            # 파이프라인 설정 파일
├── src/
│   └── run_pipeline.py         # 메인 파이프라인 스크립트
├── data/
│   └── raw/                    # 원시 데이터 파일 (Git LFS)
│       ├── 241211_2_walking_no suit.csv
│       └── ... (총 9개 파일)
├── metadata/
│   ├── data_description.md     # 상세 데이터 설명
│   └── file_manifest.csv       # 파일 목록 및 메타데이터
├── scripts/
│   └── validate_data.py        # 데이터 검증 스크립트
└── results/                    # 분석 결과 (생성됨)
```

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
  title = {EMG Gait Analysis Pipeline (UMAP–DBSCAN)},
  url   = {https://github.com/taniasongbi/taniasongbi},
  note  = {Version: v0.1.0 or later; see releases},
  year  = {2025}
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
