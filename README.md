# EMG Walking Data Repository

## 데이터 개요

본 저장소는 보행 중 근전도(EMG) 신호 데이터를 포함합니다. 총 9개의 CSV 파일로 구성되어 있으며, 각 파일은 보행 중 측정된 16채널 EMG 신호를 포함합니다.

## 데이터 구조

### 파일 목록

1. `241211_2_walking_no suit.csv` - 2024년 12월 11일, 세션 2
2. `241212_1_walking_no suit.csv` - 2024년 12월 12일, 세션 1
3. `241212_2_walking_no suit.csv` - 2024년 12월 12일, 세션 2
4. `241212_3_walking_no suit.csv` - 2024년 12월 12일, 세션 3
5. `241213_1_walking_no suit.csv` - 2024년 12월 13일, 세션 1
6. `241213_2_walking_no suit.csv` - 2024년 12월 13일, 세션 2
7. `241216_1_walking_no suit.csv` - 2024년 12월 16일, 세션 1
8. `241216_2_walking_no suit.csv` - 2024년 12월 16일, 세션 2
9. `241216_3_walking_no suit.csv` - 2024년 12월 16일, 세션 3

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

- **샘플링 레이트**: 약 2,147 Hz (평균 샘플 간격: 0.000466초)
- **평균 데이터 길이**: 약 670,000 - 680,000 행
- **평균 파일 크기**: 약 230-235 MB

## 디렉토리 구조

```
research_data_repository/
├── README.md                    # 본 파일
├── data/
│   └── raw/                     # 원시 데이터 파일
│       ├── 241211_2_walking_no suit.csv
│       ├── 241212_1_walking_no suit.csv
│       └── ... (총 9개 파일)
├── metadata/
│   ├── data_description.md      # 상세 데이터 설명
│   └── file_manifest.csv        # 파일 목록 및 메타데이터
└── scripts/
    └── validate_data.py         # 데이터 검증 스크립트
```

## 사용 방법

### 데이터 로드 예시 (Python)

```python
import pandas as pd

# 데이터 로드
file_path = 'data/raw/241211_2_walking_no suit.csv'
data = pd.read_csv(file_path)

# 시간과 EMG 신호 분리
time = data['Time (s)']
emg_signals = data.iloc[:, 1:]  # EMG 1-16
```

### 데이터 검증

```bash
python scripts/validate_data.py
```

## 라이선스

본 데이터는 연구 목적으로 제공됩니다. 사용 시 적절한 인용을 부탁드립니다.

## 인용 방법

이 데이터를 사용하실 경우, 다음 형식으로 인용해주세요:

```
[저자명]. (2024). EMG Walking Data Repository. [저장소 URL]
```

## 문의

데이터에 대한 문의사항이 있으시면 저장소 이슈를 통해 연락주시기 바랍니다.

