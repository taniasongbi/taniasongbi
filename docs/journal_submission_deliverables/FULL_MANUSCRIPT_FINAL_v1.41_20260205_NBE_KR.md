---
title: "케이블 구동 수트를 위한 생체역학적 스케일링 sEMG 기반 실시간 다지형 보조 상태 분류 및 캘리브레이션"
title_en: "Real-time multi-terrain assistance state classification and calibration for cable-driven suits using biomechanically scaled sEMG"
version: "v1.41 (NBE Final - 누수 없는 비지도 피험자-윈도우 적응(Extended Data Fig.7) 추가; 참고문헌 50개)"
last_updated: "2026-02-05"
format: "Nature Biomedical Engineering Article"
word_count_main: "~3,200 (목표 ≤3,500)"
display_items: "6 (그림 5 + 표 1)"
title_chars: "58 (≤130 ✓)"
abstract_words: "168 (≤175 ✓)"
changes_from_v1.34: |
  - (v1.41) 제목을 '보조 상태 분류 + 캘리브레이션'으로 명확화
  - 웨이블릿 특징을 조건-비의존 고정 앙상블로 통일하여 타깃 라벨 의존 가능성 제거
  - NL10 처리 규칙 고정: 세그먼트 <50 샘플 → NaN; NaN 포함 주기×위상 샘플은 F28 분류 분석에서 제외(보충표 S3)
  - 이벤트 검출/TO 선택/실패 처리/짧은 주기 제외 기준 명시(완화된 피크 탐색, 62% 규칙, HS<2 side 제외, HS→다음HS<50 제외)
  - 프로토콜 재현성 보강: 경사로 시행 평균 속도 및 지형별 평균 기록 시간 추가
  - macro-F1 집계/CI 단위 문장 고정: 피험자별 macro-F1 → 피험자 동일가중 평균; CI는 피험자 부트스트랩
  - 레이턴시 재현 조건 추가: OS/Python/패키지 버전, git commit, ~9 Hz=1/평균 레이턴시 근거
---

# 케이블 구동 수트를 위한 생체역학적 스케일링 sEMG 기반 실시간 다지형 보조 상태 분류 및 캘리브레이션

**Real-time multi-terrain assistance state classification and calibration for cable-driven suits using biomechanically scaled sEMG**

Song-Bi Lee, Yongjun Kim, Gisu Heo, Changmok Oh, Suyeong Eom¹, Dong-Woo Lee*

Electronics and Telecommunications Research Institute (ETRI), Daejeon, Republic of Korea  
¹ Formerly at ETRI  
*Corresponding author: Dong-Woo Lee (hermes@etri.re.kr)

## 초록 (Abstract)

케이블 구동 웨어러블 보조 수트의 폐루프 제어를 위해서는 다양한 지형에 일반화 가능한 sEMG 기반 보조 상태(NW: 미착용, UE: 착용-비활성, PE: 착용-활성)의 실시간 3-class 판별이 필요하다. 본 연구는 10명의 건강한 성인으로부터 10채널 sEMG(2148 Hz)를 수집해 평지·경사로·계단에서의 29,993개 보행 주기(NW 9,907; UE 10,098; PE 9,988)를 분석했고, 보행 이벤트(HS/TO) 기반 8위상 분절을 통해 239,944개의 주기×위상 샘플(주기당 8위상)을 구성했다. 파이프라인은 28차원 특징(F28 = F18[시간–주파수–웨이블릿 18개] + NL10[비선형 동역학 10개])과 생체역학적 근육 스케일링(Φ\_B; PCSA·근섬유 분율·우각 기반의 근육별 고정 스케일 팩터를 채널별 특징 벡터에 적용해 보정)을 Random Forest(RF; n_estimators=200)와 결합했다. 기록 파일당 최대 50개 주기를 무작위로 추출(seed=42)한 LOSO 평가에서 동일 지형(훈련·평가 동일 지형) macro-F1은 0.375–0.399, 교차 지형(훈련 지형→다른 지형 전이) macro-F1은 0.171–0.394(최소: 평지→계단, 최대: 경사로→계단)였다. 훈련 피험자 통계만을 사용한 0-label 지형별 z-score 정규화(x'=(x−μ\_train,terrain)/σ\_train,terrain)는 전이 성능을 동일 지형 성능으로 정규화한 비율을 0.43–0.52에서 0.67–0.81로 개선했다. 또한 라벨 없는 피험자‑윈도우(기록 파일당 최초 4개 주기) 정규화는 최약 전이 성능을 0-label 대비 추가로 개선했다(평지→경사로 0.273→0.301, 평지→계단 0.269→0.290). Apple M1(Python 구현)에서 경량 배포 경로(F18+RF)는 주기당 end-to-end(이벤트 검출→분류) 115 ms(p99 182 ms), 28D 특징 벡터당 추론 전용 1.36 ms를 보였으며, 본 연구에서 실시간은 추론 단계 레이턴시를 의미한다. 이러한 결과는 다중 지형 배포를 위한 캘리브레이션 요구와 계산 가능성을 정량화한다.

## 본문 (Main text)

### 서론 (Introduction)

케이블 구동 수트와 같은 웨어러블 보행 보조 시스템은 적응형 폐루프 제어를 위해 사용자 보조 상태의 실시간 판별을 필요로 할 수 있다¹,²,¹⁶⁻²⁰. 표면 근전도(sEMG)는 비침습적으로 근활동을 측정할 수 있으며, 보행 모드 식별, 보철 제어, 분류에 사용되어 왔다³,⁴,²¹⁻²⁵. 다양한 시간, 주파수, 웨이블릿 특징이 EMG 분류에 제안되었으며⁴,²⁶⁻³⁴,⁴²⁻⁴⁴, 샘플 엔트로피, 근사 엔트로피, 순열 엔트로피, 프랙탈 차원과 같은 비선형 동역학 측정치는 보행 변동성과 관련된 신호 복잡성을 포착할 수 있다⁵,⁹,¹²,¹³,¹⁴,³⁶⁻⁴¹. 본 연구는 10개 근육 채널을 하나의 특징 벡터로 융합(평균)하므로, 근육 구조(PCSA, 근섬유 분율, 우각)에 기반한 고정 스케일링(Φ\_B)을 적용해 채널 특징을 ‘절대 크기’가 아니라 힘 생성 능력에 대응하도록 가중했다⁶,¹⁰.

본 연구에서는 계층적 다중 도메인 웨이블릿 앙상블 융합(H‑MD‑WEF) 파이프라인을 구현하여, 위상 정렬 다중 도메인 특징 융합을 해석 가능한 협응 지표와 다지형 추론 모듈에 공통으로 연결했다(그림 1). 공유 백본은 전처리, HS/TO 기반 8위상 분절, 다중 도메인 특징(F18: 시간·주파수·웨이블릿) 추출 및 Φ\_B 적용을 수행하며, 정보이론(엔트로피 기반) 가중치로 도메인 내/도메인 간 융합을 통해 s10(10D)을 생성한다. 비선형 특징(NL10; 10D)은 세그먼트 길이 ≥50 샘플에서만 별도로 계산하고, F18과 결합해 F28 = F18 + NL10을 구성해 분류에 사용한다. 타깃 라벨 의존을 피하기 위해, 본문에 보고하는 추론 결과는 조건 비의존 고정 웨이블릿 앙상블을 사용하며 라벨 조건부 가중치를 사용하지 않는다. 이를 바탕으로 우리는 다섯 가지 평가 축을 평가했다: (1) 교차 지형 전이를 포함한 피험자 독립 다중 지형 LOSO 분류, (2) 배포 현실형 캘리브레이션(0-label, 라벨 없는 피험자‑윈도우, 및 소량 라벨), (3) 레이턴시(추론 단계 및 end-to-end 별도 보고), (4) 임계값 견고성을 포함한 근육 간 상관 네트워크 기반 협응 지표, (5) 특징 모듈 ablation 효과.

---

## 결과 (Results)

아래의 모든 결과는 H‑MD‑WEF 파이프라인(그림 1)이 생성한 이벤트·위상 정렬 특징 테이블(F18/F28)과 융합 잠재 상태(s10)에서 계산하였다. 우리는 피험자 독립 교차 지형 분류(그림 2a; Source Data Fig.2), 캘리브레이션 전략(그림 5a; Source Data Fig.5), 레이턴시(그림 4), 그리고 해석 가능한 협응 지표 및 ablation(그림 3)을 보고한다.

### 연구 설계 및 데이터

건강한 성인 남성 10명(연령 25.3 ± 3.2세)으로부터 세 가지 지형(평지, 18° 경사로, 계단)과 세 가지 보조 조건(NW: 미착용, UE: 착용-비활성, PE: 착용-활성)에서 총 29,993개의 보행 주기를 수집했다. 보행 주기는 동일 발의 발뒤꿈치 착지(HS)부터 다음 HS까지(HS→다음 HS)로 정의했으며, HS/TO 이벤트를 기준으로 한 주기를 Perry 8위상으로 분절해 총 239,944개의 주기×위상 샘플(주기당 8위상)을 구성했다. NL10은 위상 세그먼트 ≥50 샘플에서만 계산되므로, 전체 239,944개 주기×위상 샘플 중 19,973개(8.32%)는 NL10-invalid로 분류되어 F28 분석에서 제외되었다(보충표 S3). 지형별 분포는 평지 16,455주기, 경사로 6,412주기, 계단 7,126주기였다(표 1). 경사로(18°) 시행은 상향과 하향을 모두 포함했으며, 경사로 6,412주기 중 상향 3,022주기, 하향 3,390주기였다. 분류 입력(F28, 28D)은 주기×위상 단위에서 10채널(양측 GM/TA/RF/TFL/BF)별 특징을 산술 평균으로 집계해 샘플당 1개 벡터로 만들었고, 협응 분석에서는 채널별 특징을 유지해 10×10 근육(채널) 간 상관 행렬을 계산했다.

### 피험자 독립 교차 지형 분류

Random Forest (RF)를 사용한 피험자 독립 평가는 leave-one-subject-out(LOSO)로 수행했다: 각 폴드에서 한 피험자를 테스트용으로 완전히 홀드아웃하고, 나머지 9명의 피험자 데이터로 학습했다. 교차 지형 전이(3×3 전이 행렬; 훈련 지형 1개→테스트 지형 1개)에서 동일 지형 대각선 성능은 macro-F1 0.375–0.399였고, 교차 지형 비대각선 성능은 0.171–0.394 범위였다(그림 2a; Source Data Fig.2). 훈련 지형별로, 평지 모델은 평지/경사로/계단에서 0.398/0.179/0.171, 경사로 모델은 0.206/0.375/0.394, 계단 모델은 0.200/0.350/0.399였다. macro-F1은 홀드아웃 피험자별 점수를 산출한 뒤 피험자에 동일 가중치를 주는 산술 평균으로 집계했으며, 95% CI는 피험자 단위 부트스트랩(2,000회)로 산출했다. 이 LOSO 실험에서는 기록 파일당 최대 50개 주기를 무작위로 추출(seed=42)해 구성한 균형 주기×위상 데이터셋에서 평가했다.

비대각선/대각선 비율은 각 비대각선 셀을 ‘동일 테스트 지형(열)’의 대각선 성능으로 정규화한 값으로 정의했으며 0.43–0.99였다. 가장 약한 전이는 평지→경사로/계단(0.48, 0.43)였고, 가장 강한 전이는 경사로↔계단(0.99, 0.93)이었다. 클래스별로는 교차 지형 저하가 비균일하게 나타났다: 평지→경사로에서 UE는 F1 0.503을 유지한 반면 NW 0.033, PE 0.001이었고, 평지→계단에서도 UE 0.467 대비 NW 0.040, PE 0.005로 유사한 패턴을 보였다.

### 배포 현실형 캘리브레이션

교차 지형 저하를 해결하기 위해 배포 시나리오에서 구현 가능한 두 가지 캘리브레이션 전략을 평가했다.

0-label 캘리브레이션에서는 테스트 시 지형 라벨이 알려져 있다는 가정 하에, 훈련 피험자에서만 계산한 지형별 통계(μ\_train,terrain, σ\_train,terrain)로 지형별 z-score 정규화를 적용했다(train_only_by_terrain). 각 샘플은 자신의 지형 라벨에 대응하는 통계로 변환했으며, 홀드아웃 피험자 데이터로는 μ/σ를 계산하지 않았다(누수 방지). 이 캘리브레이션은 가장 약한 교차 지형 셀을 개선했다(평지→경사로 0.179→0.273, 평지→계단 0.171→0.269). 또한 6개 비대각선 셀의 평균 macro-F1은 0.250→0.309로 증가했고, 대각선 정규화 비율 범위는 0.43–0.99에서 0.67–0.91로 개선되었다. 단, 강한 경사로↔계단 전이는 0.394→0.334 및 0.350→0.340으로 일부 감소했다(그림 2c; Source Data Fig.2).

누수 없는 비지도 피험자 적응(“개인화”)을 탐색하기 위해, 홀드아웃 피험자에서 기록 파일당 최초 4개 보행 주기를 라벨 없이 캘리브레이션 윈도우로 분리하고(평가에서 제외), 해당 윈도우로 피험자×지형별 z-score 통계를 추정해 나머지 주기에 적용했다. 이 방법은 가장 약한 전이를 train-only 0-label보다 추가로 개선했다(평지→경사로 0.273→0.301, 평지→계단 0.269→0.290). 다른 전이에서는 혼합된 영향을 보였고, 6개 비대각선 평균 macro-F1은 0.309→0.315로 증가했다(Extended Data 그림 7; Source Data Extended Data Fig.7).

소량 라벨 캘리브레이션에서는 leave-one-terrain-out(2지형 훈련→1지형 테스트) LOSO에서, 입력 특징에 0-label 피험자×지형별 z-score(subject\_by\_terrain)를 적용한 뒤, 홀드아웃 피험자×테스트 지형의 RF log-확률 출력을 입력으로 다항 로지스틱 회귀(solver=lbfgs, L2, C=1.0, max_iter=1000)를 사후 학습했다. 라벨 예산은 홀드아웃 피험자×테스트 지형에서 총 10/30/90개의 라벨된 주기×위상 샘플로, 클래스 간 균등 할당을 우선하는 계층화 샘플링(부족 클래스는 중복 허용)으로 선택했고, 선택된 라벨 샘플은 평가에서 제외했다. 30회 반복 무작위 샘플링(고정 시드 42) 결과, 0 라벨 기준선 macro-F1 0.312–0.387이 30 라벨에서 0.400–0.532로 향상되었고, 반복 간 표준편차는 10 라벨 0.019–0.021에서 90 라벨 0.006–0.010으로 감소했다(그림 5a; Source Data Fig.5). 주기당 8위상이므로 10/30/90 라벨은 최소 2/4/12 보행 주기 분량(최대 10/30/90주기 범위)으로 환산된다.

### End-to-end 레이턴시

Apple M1 하드웨어에서 지형당 5개 보행 주기(3개 지형 합계 N = 15개 주기)에 대해 전체 처리 파이프라인의 레이턴시를 측정했다. p95/p99는 N = 15 주기 측정치에 대한 경험적 분위수로 계산했다.

Full F28 경로 (NL10 비선형 특징 포함): 평균 end-to-end 레이턴시는 2,697 ms(p95 5,815 ms, p99 5,845 ms)였으며, NL10 계산이 지배적이었다(2,591 ms 특징 추출 시간 중 2,559 ms). 이 경로는 실시간 제어에 적합하지 않다.

F18 배포 경로 (NL10 제외, RF 추론 포함): 평균 end-to-end 레이턴시는 115 ms(p95 147 ms, p99 182 ms)였다. 주기 단위 레이턴시는 1개 보행 주기(HS→HS) 내 8위상 모두에 대해 근육 평균 28D 특징을 계산하고, 위상 벡터(최대 8개)마다 RF 추론을 수행한 전체 시간을 의미한다. 단계별 평균은 이벤트 검출 8 ms(파일당 1회 측정 후 주기 수로 분할), 전처리 28 ms, F18 특징 추출 26 ms, RF 추론 52 ms였고, 지형별 평균은 평지 125 ms, 경사로 105 ms, 계단 116 ms였다.

추론 전용 레이턴시 (사전 계산된 특징 1개 벡터 기준): 평균 1.36 ms(p99 2.36 ms)로 100 Hz 제어 예산(10 ms)의 13.6%를 사용했다.

본 연구에서 실시간은 추론 단계 레이턴시를 의미한다. F18+RF 경로의 평균 end-to-end 115 ms는 처리량 약 8.7 Hz(≈9 Hz)에 해당하며(≈1/0.115 s), 100 Hz(10 ms 예산) 수준의 end-to-end 폐루프 제어는 특징 계산/구현 최적화가 필요하다.

### 협응 네트워크 분석

근육 시너지 연구⁴⁵⁻⁵⁰에서 관찰된 모듈 구조와 유사하게, 근육(채널) 간 협응은 10채널(양측 GM/TA/RF/TFL/BF)에서 얻은 근육별 특징 궤적 간 Pearson r로 10×10 상관 행렬을 만들고, |r| ≥ 0.6인 45개(대각 제외) 근육쌍의 비율(네트워크 밀도)로 정량화했다(그림 3a). 값은 피험자(run_id) 단위로 계산한 뒤 평균 ± SD로 요약했으며, 평지에서는 NW/UE 1.000 ± 0.000, PE 0.904 ± 0.302로 상한에 근접한 반면, 경사로(상향/하향)와 계단에서는 0.129–0.198 범위로 낮아 더 희소한 연결성을 보였다.

지표 견고성을 평가하기 위해 네 가지 임계값 범위(0.30–0.90, 0.40–0.80, 0.50–0.90, 0.40–0.90)에서 정규화된 네트워크 밀도(edges_auc_norm)를 계산했다. 조건 순서는 모든 범위에서 완전히 일관되었다: 경사로에서 NW > UE > PE; 계단에서 PE > UE > NW(Extended Data 표 1). 평지는 높은 기준선 연결성으로 인해 좁은 범위에서 포화 효과를 보였다. 이러한 결과는 협응 결론이 합리적인 범위 내에서 임계값 선택에 견고함을 나타낸다.

### 특징 모듈 ablation

개별 특징 모듈 제거(ablation)는 각 지형×조건 셀에서 피험자 단위 mean |r|(=45개 근육쌍 Pearson |r|의 산술 평균)에 대해 양측 짝지은 t-검정으로 평가했다(그림 3b). ablation 분석에서는 경사로를 하향과 상향으로 세분화하여 4 지형 × 3 조건 = 12 셀(평지, 경사로 하향, 경사로 상향, 계단)을 사용했다. q값은 Benjamini–Hochberg 보정을 전체 비교(3 모듈 × 12 셀 × 2 지표[mean |r|, |r|>thr edge 수] = 72개)에 대해 적용했으며, q < 0.05를 셀별 비교에 적용해 유의성을 판단했다. 웨이블릿 특징(WEF) 제거는 12 셀 중 9개에서 유의한 변화(q < 0.05)를 생성했으며 평균 |Δ(mean |r|)| = 0.211이었다. NL10 제거는 2 셀에서만 유의했고(평균 |Δ(mean |r|)| = 0.024), 생체역학적 스케일링(Φ\_B) 제거는 3 셀에서 유의했다(평균 |Δ(mean |r|)| = 0.007). WEF ablation 결과는 협응 지표(mean |r|)에 대한 영향이며, 아래의 도메인 순열 중요도는 분류 성능(macro-F1)에 대한 영향을 평가한다.

도메인 수준 순열 중요도 분석(LOSO, 동일 지형)은 NL10 특징이 순열 시 가장 큰 macro-F1 하락을 기여함을 확인했다(지형별 0.065–0.072, 95% CI가 0을 제외; 피험자 부트스트랩). Time, Frequency, Wavelet 도메인은 더 작은 효과를 보였으며 종종 CI가 0을 포함했다(Extended Data 그림 1).

### 이벤트 검출 견고성

EMG 기반 HS/TO 검출은 band-pass+notch 후 정류한 신호를 가우시안(σ)으로 평활한 포락선을 만들고, TA 포락선 피크를 HS, GM 포락선 피크를 TO로 선택했다(포락선은 median/MAD로 정규화한 뒤 find_peaks로 최소 간격을 적용). TO는 HS 이후 주기 길이의 62% 지점에 가장 가까운 GM 피크로 정했고(없으면 62% 지점으로 대체), |Δt|는 기준선 파라미터(σ=100 ms, min_interval=0.5 s) 대비의 이벤트 시점 차이로 정의했다. 파라미터 민감도에서는 기준선과 변형 결과의 주기를 HS 근접 매칭으로 짝지은 뒤, 변형/기준선 주기 길이 비가 0.8–1.2인 ‘안정 주기’로 제한해 요약했으며, 안정 주기에서 HS는 모든 파라미터 조합에서 p95 |Δt| < 80 ms였다(Extended Data 표 2). 추가로 ±10/±20/±40 ms의 이벤트 오차를 모사하기 위해 기존 분절 인덱스(phase_start/end)를 일정 샘플만큼 일괄 시프트한 뒤(F18 재계산, NL10 제외) 분류 민감도를 평가했으며, ±20 ms에서 macro-F1 변화는 대각선 0.007–0.022, 비대각선 0.003–0.018 범위였다(보충 그림 6).

---

## 토론 (Discussion)

본 연구는 다중 지형에서 EMG 기반 보조 조건 분류의 피험자 독립 평가를 제시하며, 캘리브레이션 요구 사항과 계산 가능성을 본 연구 설정에서 정량화한 벤치마크를 제시한다.

피험자 독립 LOSO macro-F1(동일 지형 0.375–0.399; 그림 2a)과 피험자 내 5-fold stratified 교차검증 macro-F1(0.9997 ± 0.0003; Supplementary Table 6; 피험자 독립 아님) 간의 격차는, 동일 피험자/기록 맥락을 공유할 때는 높은 성능이 가능하지만 피험자 독립 일반화에서는 성능이 제한됨을 보여준다. Supplementary Table 6의 5-fold CV는 주기×위상 샘플이 아니라 보행 주기 단위(1 샘플=1 보행 주기)로 수행되었으나, 훈련·평가 폴드가 동일 피험자를 공유하므로 배포 성능의 상한(upper bound)으로 해석해야 한다. LOSO에서 피험자 수준 macro-F1이 0.155–0.572로 분포한 점(Supplementary Table 1)은 개인 간 EMG 특성 차이가 일반화 저하의 주요 요인일 가능성을 시사한다.

중요하게, 훈련 피험자 통계만을 사용한 0-label 캘리브레이션은(테스트 피험자 라벨 사용 없이) 가장 약한 교차 지형 전이 성능 비율을 0.43–0.52에서 0.67–0.81로 개선했다. 다만 0-label 캘리브레이션은 지형별 통계를 적용하므로, 배포 시 지형이 알려져 있거나 별도 모듈로 식별 가능하다는 전제 하에 지형별 정규화를 수행한다.

총 30개의 라벨 샘플(조건에 대해 계층화)을 사용한 소량 라벨 캘리브레이션은 낮은 샘플링 변동성(SD 0.008–0.010; 그림 5a)으로 안정적인 개선을 제공한 반면, 10 샘플은 더 높은 변동성(SD 0.019–0.021)을 보였다. 주기당 8위상 샘플을 생성하므로, 30개의 주기×위상 라벨 샘플은 대략 4개 보행 주기(30/8≈3.75) 분량의 라벨 데이터에 해당한다. 본 실험 설정에서 30개 라벨 예산은 성능 개선과 변동성 감소가 동시에 관측된 최소 단위로 나타났다.

End-to-end 레이턴시 분석은 "실시간" 주장의 범위를 명확히 한다. 추론 전용 레이턴시(평균 1.36 ms)는 100 Hz 제어 예산 내에 충분하지만, 특징 추출을 포함한 전체 파이프라인은 F18+RF 경로에 평균 115 ms가 필요해 현재 구현에서 약 9 Hz 피드백에 해당한다. 레이턴시 값은 지형당 5개 보행 주기(총 N = 15)에서 측정된 분포 기반 값이므로, 더 다양한 조건에서의 추가 측정이 필요하다. 더 높은 주파수의 폐루프 제어를 위해서는 NL10을 오프라인/저주파로 분리하거나 F18 계산 및 구현을 최적화하는 등의 설계 선택이 필요할 수 있다.

협응 지표는 지형에 따라 다른 결합 구조를 시사했다: 평지는 밀도가 상한에 근접해 포화가 발생할 수 있는 반면, 경사로/계단은 더 낮은 밀도로 희소하고 선택적인 결합을 보였다. 각 지형 내 조건 순서가 여러 임계값 범위에서 일관되게 유지된 점은 협응 지표 해석의 견고성을 뒷받침한다.

몇 가지 한계를 언급해야 한다. 첫째, 10명의 피험자 표본 크기는 일반화 가능성을 제한하며, 건강한 성인 집단은 임상 집단을 대표하지 않을 수 있다. 둘째, EMG 기반 이벤트 검출은 외부 센서(IMU, 힘판)로 검증되지 않았다; 그러나 민감도 분석은 ±20 ms 타이밍 이동이 결론을 실질적으로 변경하지 않음을 보여주었다. 셋째, LOSO macro-F1 0.375–0.399(동일 지형; 그림 2a)는 제한된 피험자 간 일반화를 나타낸다. 넷째, 0-label 캘리브레이션은 지형별 통계를 적용하므로 배포 시 지형 식별(또는 지형 라벨 가정)이 필요하다. 다섯째, 라벨 없는 피험자‑윈도우 적응은 초기 캘리브레이션 윈도우를 필요로 하며 전이별로 혼합된 영향을 보였다. 여섯째, 레이턴시 평가는 지형당 5주기(N = 15) 기반이므로, 더 다양한 조건에서의 추가 측정이 필요하다. 일곱째, 폐루프 제어는 구현되지 않았다; 레이턴시 결과는 계산 가능성을 확립하지만 제어 성능은 아니다.

결론적으로, 본 연구는 EMG 기반 보조 분류의 피험자 독립 성능, 캘리브레이션 효과, 레이턴시, 협응 지표를 정량적으로 제시한다. 본 데이터/설정/파이프라인 범위 내에서 이러한 결과는 배포를 위한 캘리브레이션 및 최적화 요구 사항을 명확히 한다.

---

## 온라인 방법 (Online Methods)

### 참가자

건강한 성인 남성 10명(연령 25.3 ± 3.2세; 신장 168.4 ± 8.7 cm; 체중 64.2 ± 11.3 kg)이 참여했다. 연구는 소속 기관의 기관생명윤리위원회(IRB) 승인을 받았으며, 모든 참가자로부터 서면 동의를 받았다.

### 프로토콜

세 가지 보조 조건(NW: 미착용, UE: 착용-비활성, PE: 착용-활성)과 세 가지 지형에서 데이터를 수집했다. 평지는 트레드밀에서 0.83 m/s로 수행했다. 계단은 이고진(Egojin) Highclimb 스텝밀 머신(스텝 높이 21 cm)에서 0.54 m/s로 수행했다. 경사로(18°)는 25 m 보도에서 자기 선택 속도로 수행했다(50 m 왕복; 시행 평균 속도 0.227 ± 0.016 m/s). 평균 기록 시간은 평지 299 ± 23 s, 경사로 221 ± 17 s, 계단 180 ± 6 s였다. 경사로 시행의 왕복은 동일 경사(18°)에서 진행 방향이 반대인 두 구간을 포함하며, 분석에서는 이 구간을 상향/하향으로 구분해 사용했다.

### EMG 수집

10채널 표면 EMG를 비복근 내측(GM), 전경골근(TA), 대퇴직근(RF), 대퇴근막장근(TFL), 대퇴이두근(BF)에서 양측으로 수집했으며, Delsys Trigno 표면 EMG 시스템(이하 Trigno)을 사용하여 2,148 Hz로 샘플링하고 SENIAM(Surface Electromyography for the Non-Invasive Assessment of Muscles) 전극 배치 지침⁷을 따랐다.

### 전처리

순차적 전처리: 각 기록에서 채널별 비영(0) 샘플을 기준으로 0.1–99.9 백분위수로 이상치를 클리핑(비영 샘플 ≥100일 때; 0 값은 통계 계산에서 제외하되 신호에는 유지), 4차 버터워스 band-pass(20–450 Hz), 60 Hz 노치 필터(Q = 30), 정류, 가우시안 포락선 평활(σ = 100 ms).

### 보행 분절

발뒤꿈치 착지(HS)는 TA 포락선 피크로 검출했고, 발가락 떼기(TO)는 GM 포락선 피크로 검출했으며, scipy.signal.find_peaks를 최소 거리 0.5 s로 사용했다. 피크 검출의 강건성을 위해 포락선을 median/MAD로 정규화한 뒤, (height, prominence) = (0.5, 0.3) → (0.3, 0.2) → (0.1, 0.1) → (0.05, 0.05) → (None, 0.02) 순으로 단계적으로 완화하며 피크를 찾았고(피크 ≥5개이면 종료), 마지막에는 최소 거리만으로 피크를 탐색했다(한쪽에서 HS 피크가 2개 미만이면 해당 쪽은 제외). 연속 HS 피크(HS→다음 HS)로 정의된 각 주기에서 TO는 HS 이후 주기 길이의 62% 지점에 가장 가까운 GM 피크로 선택했으며, HS와 다음 HS 사이에 GM 피크가 없으면 TO를 주기 길이의 62% 지점으로 추정했다. 보행 주기는 Perry 모델에 따라 8위상으로 나누었다⁸: IC(0–2%), LR(2–12%), MSt(12–31%), TSt(31–50%), PSw(50–62%), ISw(62–75%), MSw(75–87%), TSw(87–100%). 위상 경계(%)는 각 HS→다음 HS 구간 내에서 샘플 인덱스로 매핑했으며(시간 리샘플링 없음), 이 인덱스로 위상 구간을 절단했다. HS→다음 HS 길이가 50샘플 미만인 주기는 제외했다.

### 특징 추출

F18(18D)은 시간 도메인(6), 주파수 도메인(5), 웨이블릿 도메인(7)으로 구성되었다. 이벤트 검출은 포락선 신호에서 수행했고, F18 특징 계산은 band-pass 신호(bp)와 그 포락선(env)을 사용했다: RMS/MAV/분산은 env에서 계산했고, 파형 길이(WL), ZCR, SSC는 bp에서 계산했다(부가 임계값 ε 없이 부호 변화 기반). 주파수 특징은 bp에 대해 Welch PSD(scipy.signal.welch; nperseg=min(L,1024); 기타 파라미터는 SciPy 기본값)를 계산하고 20–450 Hz 대역으로 제한했으며, 상대 대역전력은 \(\int_{\mathrm{band}}P(f)\,df / \int_{20}^{450}P(f)\,df\)로 정의했다. 타깃 라벨 의존을 피하기 위해 웨이블릿 특징은 조건과 무관한 고정 3-웨이블릿 앙상블(레벨=5)을 사용했다: {db5, sym6, coif3}, 고정 가중치 {0.5, 0.3, 0.2}. 가중된 에너지/엔트로피를 연결했고, high/low 비율은 가장 큰 고정 가중치를 갖는 웨이블릿에서 계산했다. 이산 웨이블릿 분해가 불가능할 정도로 짧은 구간(pywt.dwt_max_level < 1)에서는 웨이블릿 요약을 0으로 반환했다(웨이블릿 분해 불가). NL10(10D)은 SampEn(m=2, r=0.2; z-score 신호), ApEn(m=2, r=0.2), 순열 엔트로피(order=3, delay=1, 정규화), Higuchi FD(kmax=min(10, N/4)), Katz FD, Hurst(max_lag=min(50, N/4)), RQA 지표(m=2, τ=1, threshold=0.1×최대 거리; DET lmin=2; LAM vmin=2), 최대 Lyapunov 지수(Rosenstein; m=2, τ=1)로 구성되었다. NL10은 세그먼트 ≥50 샘플(2,148 Hz에서 ≈23 ms)에서만 계산했고, 더 짧은 구간은 NaN으로 처리했으며 NaN이 포함된 주기×위상 샘플은 F28(F18+NL10) 분류 분석에서 제외했다(보충표 S3).

### 생체역학적 스케일링

스케일링 가중치는 \(w = w_\mathrm{PCSA}\,w_\mathrm{FT}\,w_\mathrm{pen}\)로 계산했으며, \(w_\mathrm{PCSA}=1/\mathrm{PCSA}\), \(w_\mathrm{FT}=1+0.6(\mathrm{FT}-0.5)\)(FT: fast-fiber 분율), \(w_\mathrm{pen}=1-\theta/90^\circ\)(θ: 우각)로 정의했다. 생성된 대각 행렬 Φ\_B는 근육 평균이 1.0이 되도록 정규화한 뒤, 근육별 스칼라로 모든 특징에 곱해 적용했다. 근육 파라미터(PCSA, FT, θ)는 해부학 문헌¹⁰,¹⁵에서 인용했고 피험자별 개인화 없이 근육별 고정 상수(좌/우 동일)로 사용했다: GM(PCSA 15.6 cm², FT 0.51, θ 17°, w 0.473), TA(6.5, 0.27, 9.6, 1.072), RF(12.9, 0.39, 13.5, 0.557), TFL(4.2, 0.45, 8.0, 1.904), BF(8.7, 0.67, 11.9, 0.994). **의도**: Φ\_B는 피험자별 정규화가 아닌 문헌 기반 근육별 prior이며(라벨로 학습되지 않음), 원 신호가 아니라 추출된 특징 벡터에 적용한다. 10채널 평균 융합 전 Φ\_B를 적용함으로써 근육 크기/구조로 인한 채널 간 규모 차이가 융합 표현을 지배하지 않도록 한다. 근육 파라미터 및 Φ\_B 가중치 요약은 보충표 S7에 제시했다.

### 분류

Random Forest (RF; scikit-learn¹¹ 1.7.1, n_estimators=200, random_state=42)³⁵를 LOSO 평가에 사용했다. 타깃은 보조 조건 3-class(NW, UE, PE)이며, 주기×위상(주기당 8위상) 단위에서 주기×위상 샘플당 하나의 28D 특징 벡터로 분류했다. 채널(근육)별 F18 특징에는 근육별 Φ\_B 스케일링을 먼저 적용했고, 분류 입력은 채널별 F28(=F18+NL10) 28D 벡터를 10채널 산술 평균으로 집계해 주기×위상 샘플당 1개의 28D 벡터로 만들었다. 각 폴드에서 한 피험자는 완전히 홀드아웃되었고 나머지 9명의 피험자가 모든 지형에 걸쳐 훈련 데이터를 제공했다. 교차 지형 전이는 별도의 훈련/테스트 지형 지정과 함께 동일한 LOSO 설계를 사용했다. LOSO 분류 및 캘리브레이션 실험을 위해, 기록 파일당 최대 50개 보행 주기를 무작위로 추출(seed=42)해 균형 평가 데이터셋을 구성했다(지형당 주기×위상 12,000개; 총 90 파일; NL10 필터링 이전).

### 캘리브레이션

0-label 캘리브레이션: 훈련 피험자로부터만 계산된 평균/표준편차를 사용한 지형별 z-score 정규화(train_only_by_terrain 모드). 각 특징 차원 x에 대해 x' = (x − μ\_train,terrain)/σ\_train,terrain 를 적용했으며, μ와 σ는 훈련 피험자로부터만 추정하고 지형별 통계는 해당 샘플의 지형 라벨로 선택했다. 이 절차는 홀드아웃 피험자 라벨이 필요 없고, 테스트 피험자 정보 누수가 없음을 보장한다. 지형 라벨은 실험 프로토콜로부터 제공되었으며, 지형별 통계를 선택하는 용도로만 사용했다.

비지도 피험자-윈도우 적응(test-window calibration): 홀드아웃 피험자에서 각 테스트 지형별로 기록 파일당 최초 4개 보행 주기를 라벨 없는 캘리브레이션 윈도우로 분리하고(평가에서 제외), 해당 윈도우로 피험자×지형별 z-score 통계(μ/σ)를 추정해 나머지 주기에 적용했다. 테스트 시 피험자-윈도우 정규화와 동일한 스케일을 유지하기 위해, 훈련 피험자 샘플은 (피험자, 지형) 단위로 z-score 정규화한 뒤 모델을 학습했다.

소량 라벨 캘리브레이션: 홀드아웃 피험자의 홀드아웃 지형 테스트 세트에서 총 10, 30, 또는 90개의 라벨된 주기×위상 샘플을 조건에 대해 계층화하여(log(RF 확률) 기반) 다항 로지스틱 회귀를 훈련했다. 수치 안정성을 위해 log 변환은 \(\log(\max(p,\varepsilon))\)로 계산했으며 \(\varepsilon=10^{-6}\)을 사용했다. 이 캘리브레이션은 교차 지형 leave-one-terrain-out 설정(두 지형으로 훈련, 홀드아웃 지형으로 테스트)에서 피험자 독립 LOSO로 평가했다. 평가는 나머지 샘플을 사용했다. 변동성을 추정하기 위해 다른 무작위 샘플로 30회 반복했다.

### 신뢰구간

부트스트랩 CI(95%)는 대체 추출로 피험자를 재샘플링(2,000회 반복)하고 2.5–97.5 백분위수 범위를 취하여 계산했다.
각 지형 셀에서 macro-F1은 홀드아웃 피험자별로 계산한 뒤 피험자에 동일 가중치를 주는 산술 평균(비가중 평균)으로 집계했으며, CI는 이 피험자 단위 점수에 대해 계산했다.

### 순열 중요도

도메인 수준 그룹 순열 중요도는 동일 지형(in-terrain) LOSO에서 계산했다. 각 지형과 홀드아웃 피험자에 대해, 나머지 피험자 샘플로 RF를 학습하고 홀드아웃 피험자에서 기준 macro-F1을 계산했다. 이후 각 도메인(Time: f18\_01–06; Freq: f18\_07–11; Wave: f18\_12–18; NL10: nl\_*)의 특징 열을 테스트 세트 행에 대해 독립적으로 순열(도메인당 20회 반복)하여 macro-F1 감소량을 측정했다. 95% CI는 피험자별 평균 감소량을 부트스트랩(2,000회)하여 추정했다.

### 협응 지표

각 피험자, 지형, 조건에 대해 근육별 28D 특징 벡터를 주기×위상 세그먼트 전반에 걸쳐 연결(특징 차원까지 펼침)하여 근육별 특징 궤적을 구성한 뒤, 지형×조건 셀 내에서 근육별 벡터를 z-score 변환했다. 이후 근육 벡터 간 Pearson r을 계산하여 10×10 근육 간 상관 행렬을 생성했다. 상관 구조 요약 지표로 mean |r|(mean_abs_r; 상삼각 대각 제외 45개 pair의 Pearson |r| 산술 평균)과 mean_r(부호 포함 r의 산술 평균)을 사용했다. 네트워크 밀도 = (|r| ≥ 임계값인 쌍) / 45. 정규화된 밀도 AUC(edges_auc_norm)는 임계값 범위에 걸쳐 밀도를 적분하고 범위 너비로 나누어 계산했다.

### 레이턴시 벤치마크

End-to-end 레이턴시는 Apple M1에서 Python 구현으로 지형당 5개 주기(3개 지형 합계 15개 주기)에 대해 측정했다. 이벤트 검출은 파일당 1회 측정한 뒤 주기 수로 나누어 주기당(분할) 시간으로 보정했으며, 주기 단위 처리에는 전처리, 위상 분절(인덱싱), 특징 추출(F18 또는 F28), 모델 추론을 포함했다. 준비/모델 학습 및 디스크 I/O는 제외했다. p95/p99는 주기 단위 측정치 분포에서 계산했다. 추론 전용 레이턴시는 사전 계산된 특징을 사용하여 워밍업 5회 후 1,000회 반복으로 측정했다. 벤치마크 환경/코드 식별자는 함께 기록했다(macOS 26.3 arm64; Python 3.11.5; numpy 1.26.4; scipy 1.15.2; scikit-learn 1.7.1; 저장소 커밋 4e38a5b409e338c1e890bb64f86461fa4cd46926). RF 추론은 scikit-learn 병렬화(n_jobs = −1)를 사용했다. 본문에 기재된 “~9 Hz 처리량”은 F18+RF 경로의 평균 end-to-end 레이턴시의 역수(≈1/0.115 s ≈ 8.7 Hz)에 해당한다.

### 이벤트 민감도

검출 파라미터를 변화시켰다: σ ∈ {50, 100, 150} ms, min_interval ∈ {0.4, 0.5, 0.6} s. HS/TO 타이밍 차이는 기준선(σ=100, interval=0.5) 대비로 계산했다. 분류 민감도는 F18 특징 재계산과 함께 ±10, ±20, ±40 ms의 인위적 위상 경계 이동을 사용했다.

### 통계 분석

Benjamini-Hochberg 보정(q < 0.05)을 적용한 짝지은 t-검정을 ablation 분석의 피험자 단위(n = 10) 지표(피험자 내 짝지음)에 사용했다. 2원 ANOVA(조건 × 위상)는 가성반복을 피하기 위해 피험자 수준 집계 값에 대해 수행했다.

---

## 데이터 가용성 (Data availability)

처리된 특징 텐서, 메타데이터, 벤치마크 결과는 출판 시 Zenodo에 업로드(아카이브)하여 DOI와 함께 공개할 예정이다(DOI: 추후 기입). 피어 리뷰 중에는 요청 시 편집자/리뷰어에게 비공개로 제공한다. 원시 EMG 신호는 IRB 승인 동의서가 공유 범위를 처리된 데이터로 제한하므로 데이터 사용 계약(Data Use Agreement) 체결 후 합리적인 요청에 따라 통제된 접근으로 이용 가능하다.

## 코드 가용성 (Code availability)

특징 추출, 분류, 분석을 위한 커스텀 Python 코드는 출판 시 Zenodo에 아카이브(업로드)하여 DOI와 함께 공개할 예정이다(DOI: 추후 기입). 피어 리뷰 중에는 요청 시 편집자/리뷰어에게 제공한다.

---

## 감사의 글 (Acknowledgements)

본 연구에 참여해 주신 모든 참가자께 감사드린다. 또한 본 원고의 영문 교정을 위해 Elsevier Language Editing Services의 전문 언어 교정 서비스를 이용했으며 이에 감사드린다.

본 연구는 과학기술정보통신부(MSIT) 재원으로 정보통신기획평가원(IITP) 지원을 받아 수행되었다(과제번호 RS-2022-II220025, “Development of soft-suit technology to support human motor ability”).

원고 준비 과정에서 저자들은 관련 참고문헌 탐색을 보조하기 위해 ChatGPT(OpenAI)를 사용했다. 해당 도구 사용 후 제안된 참고문헌을 확인했으며, 참고문헌의 정확성과 인용의 무결성에 대한 최종 책임은 저자들에게 있다.

## 저자 기여 (Author contributions)

저자 기여는 CRediT 분류 체계를 따른다:

- Song-Bi Lee: Conceptualization, Methodology, Formal analysis, Data curation, Visualization, Writing – original draft.
- Dong-Woo Lee: Funding acquisition, Project administration, Writing – review & editing.
- Yongjun Kim: Data curation, Software, Validation, Writing – review & editing.
- Gisu Heo: Writing – review & editing.
- Changmok Oh: Writing – review & editing.
- Suyeong Eom: IRB protocol development, Writing – review & editing.

## 이해 상충 (Competing interests)

저자들은 이해 상충이 없음을 선언한다.

---

## 참고문헌 (References)

1. Sawicki, G. S. et al. The exoskeleton expansion: improving walking and running economy. *J. NeuroEngineering Rehabil.* **17**, 25 (2020).
2. Young, A. J. & Ferris, D. P. State of the art and future directions for lower limb robotic exoskeletons. *IEEE Trans. Neural Syst. Rehabil. Eng.* **25**, 171–182 (2017).
3. Huang, H. et al. Continuous locomotion-mode identification for prosthetic legs based on neuromuscular-mechanical fusion. *IEEE Trans. Biomed. Eng.* **58**, 2867–2875 (2011).
4. Phinyomark, A. et al. Feature reduction and selection for EMG signal classification. *Expert Syst. Appl.* **39**, 7420–7431 (2012).
5. Richman, J. S. & Moorman, J. R. Physiological time-series analysis using approximate entropy and sample entropy. *Am. J. Physiol. Heart Circ. Physiol.* **278**, H2039–H2049 (2000).
6. Lieber, R. L. & Fridén, J. Functional and clinical significance of skeletal muscle architecture. *Muscle Nerve* **23**, 1647–1666 (2000).
7. Hermens, H. J. et al. Development of recommendations for SEMG sensors and sensor placement procedures. *J. Electromyogr. Kinesiol.* **10**, 361–374 (2000).
8. Perry, J. & Burnfield, J. M. *Gait Analysis: Normal and Pathological Function* 2nd edn (SLACK, 2010).
9. Higuchi, T. Approach to an irregular time series on the basis of the fractal theory. *Physica D* **31**, 277–283 (1988).
10. Ward, S. R. et al. Are current measurements of lower extremity muscle architecture accurate? *Clin. Orthop. Relat. Res.* **467**, 1074–1082 (2009).
11. Pedregosa, F. et al. Scikit-learn: machine learning in Python. *J. Mach. Learn. Res.* **12**, 2825–2830 (2011).
12. Hausdorff, J. M. Gait dynamics in Parkinson's disease: common and distinct behavior among stride length, gait variability, and fractal-like scaling. *Chaos* **19**, 026113 (2009).
13. Hausdorff, J. M. et al. Gait variability and fall risk in community-living older adults: a 1-year prospective study. *Arch. Phys. Med. Rehabil.* **82**, 1050–1056 (2001).
14. Rosenstein, M. T., Collins, J. J. & De Luca, C. J. A practical method for calculating largest Lyapunov exponents from small data sets. *Physica D* **65**, 117–134 (1993).
15. Johnson, M. A., Polgar, J., Weightman, D. & Appleton, D. Data on the distribution of fibre types in thirty-six human muscles: an autopsy study. *J. Neurol. Sci.* **18**, 111–129 (1973).
16. Panizzolo, F. A. et al. A biologically-inspired multi-joint soft exosuit that can reduce the energy cost of loaded walking. *J. NeuroEngineering Rehabil.* **13**, 43 (2016).
17. Ding, Y. et al. Human-in-the-loop optimization of hip assistance with a soft exosuit during walking. *Sci. Robot.* **3**, eaar5438 (2018).
18. Zhang, J. et al. Human-in-the-loop optimization of exoskeleton assistance during walking. *Science* **356**, 1280–1284 (2017).
19. Malcolm, P. et al. A simple exoskeleton that assists plantarflexion can reduce the metabolic cost of human walking. *PLoS ONE* **8**, e56137 (2013).
20. Quinlivan, B. T. et al. Assistance magnitude versus metabolic cost reductions for a tethered multiarticular soft exosuit. *Sci. Robot.* **2**, eaah4416 (2017).
21. Englehart, K. & Hudgins, B. A robust, real-time control scheme for multifunction myoelectric control. *IEEE Trans. Biomed. Eng.* **50**, 848–854 (2003).
22. Scheme, E. & Englehart, K. Electromyogram pattern recognition for control of powered upper-limb prostheses: state of the art and challenges for clinical use. *J. Rehabil. Res. Dev.* **48**, 643–659 (2011).
23. Farina, D. et al. The extraction of neural information from the surface EMG for the control of upper-limb prostheses: emerging avenues and challenges. *IEEE Trans. Neural Syst. Rehabil. Eng.* **22**, 797–809 (2014).
24. Hargrove, L. J. et al. Myoelectric pattern recognition outperforms direct control for transhumeral amputees with targeted muscle reinnervation: a randomized clinical trial. *Sci. Rep.* **7**, 13840 (2017).
25. Liu, J. et al. EMG-based real-time linear-nonlinear cascade regression decoding of shoulder, elbow and wrist movements in able-bodied persons and stroke survivors. *IEEE Trans. Biomed. Eng.* **67**, 1272–1281 (2020).
26. Nazarpour, K. et al. A note on the probability distribution function of the surface electromyogram signal. *Brain Res. Bull.* **90**, 73–79 (2013).
27. De Luca, C. J. The use of surface electromyography in biomechanics. *J. Appl. Biomech.* **13**, 135–163 (1997).
28. Merletti, R. & Farina, D. Analysis of intramuscular electromyogram signals. *Phil. Trans. R. Soc. A* **367**, 357–368 (2009).
29. Clancy, E. A. et al. Sampling, noise-reduction and amplitude estimation issues in surface electromyography. *J. Electromyogr. Kinesiol.* **12**, 1–16 (2002).
30. Phinyomark, A. et al. EMG feature evaluation for improving myoelectric pattern recognition robustness. *Expert Syst. Appl.* **40**, 4832–4840 (2013).
31. Tkach, D. et al. Study of stability of time-domain features for electromyographic pattern recognition. *J. NeuroEngineering Rehabil.* **7**, 21 (2010).
32. Hudgins, B. et al. A new strategy for multifunction myoelectric control. *IEEE Trans. Biomed. Eng.* **40**, 82–94 (1993).
33. Graupe, D. & Cline, W. K. Functional separation of EMG signals via ARMA identification methods for prosthesis control purposes. *IEEE Trans. Syst. Man Cybern.* **5**, 252–259 (1975).
34. Chan, A. D. C. & Englehart, K. B. Continuous myoelectric control for powered prostheses using hidden Markov models. *IEEE Trans. Biomed. Eng.* **52**, 121–124 (2005).
35. Breiman, L. Random forests. *Mach. Learn.* **45**, 5–32 (2001).
36. Katz, M. J. Fractals and the analysis of waveforms. *Comput. Biol. Med.* **18**, 145–156 (1988).
37. Pincus, S. M. Approximate entropy as a measure of system complexity. *Proc. Natl Acad. Sci. USA* **88**, 2297–2301 (1991).
38. Bandt, C. & Pompe, B. Permutation entropy: a natural complexity measure for time series. *Phys. Rev. Lett.* **88**, 174102 (2002).
39. Hurst, H. E. Long-term storage capacity of reservoirs. *Trans. Am. Soc. Civ. Eng.* **116**, 770–799 (1951).
40. Webber, C. L. Jr & Zbilut, J. P. Dynamical assessment of physiological systems and states using recurrence plot strategies. *J. Appl. Physiol.* **76**, 965–973 (1994).
41. Marwan, N. et al. Recurrence plots for the analysis of complex systems. *Phys. Rep.* **438**, 237–329 (2007).
42. Mallat, S. G. A theory for multiresolution signal decomposition: the wavelet representation. *IEEE Trans. Pattern Anal. Mach. Intell.* **11**, 674–693 (1989).
43. Daubechies, I. *Ten Lectures on Wavelets* (SIAM, 1992).
44. Englehart, K. et al. A wavelet-based continuous classification scheme for multifunction myoelectric control. *IEEE Trans. Biomed. Eng.* **48**, 302–311 (2001).
45. Ivanenko, Y. P. et al. Five basic muscle activation patterns account for muscle activity during human locomotion. *J. Physiol.* **556**, 267–282 (2004).
46. Clark, D. J. et al. Merging of healthy motor modules predicts reduced locomotor performance and muscle coordination complexity post-stroke. *J. Neurophysiol.* **103**, 844–857 (2010).
47. Tresch, M. C. et al. The construction of movement by the spinal cord. *Nat. Neurosci.* **2**, 162–167 (1999).
48. d'Avella, A. et al. Combinations of muscle synergies in the construction of a natural motor behavior. *Nat. Neurosci.* **6**, 300–308 (2003).
49. Ting, L. H. & Macpherson, J. M. A limited set of muscle synergies for force control during a postural task. *J. Neurophysiol.* **93**, 609–613 (2005).
50. Neptune, R. R. et al. Modular control of human walking: a simulation study. *J. Biomech.* **42**, 1282–1287 (2009).

---

## 표 (Tables)

### 표 1. 지형 및 조건별 보행 주기 분포(전체 수집 데이터)

| 지형 | NW | UE | PE | 합계 |
|------|---:|---:|---:|-----:|
| 평지 | 5,583 | 5,565 | 5,307 | 16,455 |
| 경사로 | 2,034 | 2,124 | 2,254 | 6,412 |
| 계단 | 2,290 | 2,409 | 2,427 | 7,126 |
| **합계** | 9,907 | 10,098 | 9,988 | **29,993** |

**범례**: NW(미착용), UE(착용-비활성), PE(착용-활성). 지형은 프로토콜의 수행 환경과 연결된다: 평지(트레드밀), 경사로(18° 보도/왕복 보행), 계단(스텝밀). 본 표는 전체 수집 분포(총 29,993주기)를 제시하며, LOSO 성능 평가에 사용한 균형 평가셋(기록 파일당 최대 50주기 샘플링)과는 별개이다.

---

> **Note**: 이전 버전의 표 2(LOSO 전이 행렬) 데이터는 그림 2a로 시각화했으며, 전체 수치 데이터(피험자별 값, 95% CI 산출용 원자료)는 Source Data Fig.2에 제공합니다.

---

> **Note**: 이전 버전의 표 3(0-label 캘리브레이션 효과) 데이터는 그림 2c로 시각화했으며, 전체 수치 데이터는 Source Data Fig.2에 제공합니다.

---
> **Note**: 소량 라벨 캘리브레이션 커브(그림 5a)의 수치 값은 Source Data Fig.5 및 보충표 S8에 제공합니다.

## 그림 범례 (Figure Legends)

### 그림 1. 연구 개요 및 파이프라인 구조

**(a)** 데이터 수집: 10명 피험자가 세 가지 보조 조건(NW: 미착용, UE: 착용-비활성, PE: 착용-활성)으로 세 가지 지형(평지, 18° 경사로, 계단)에서 보행 수행. **(b)** H‑MD‑WEF 파이프라인: 10채널 sEMG 전처리(이상치 클리핑, 20–450 Hz band-pass, 60 Hz 노치, 정류, 가우시안 포락선; 세부는 Online Methods 참조) → 보행 이벤트 검출(HS: TA, TO: GM) → HS→HS 주기를 Perry 고정 퍼센트 경계(0–2–12–31–50–62–75–87–100%)로 8위상 분절 → 특징 추출: F18(18D; 시간+주파수+웨이블릿)을 계층적으로 융합해 s10(10D)을 생성(임베딩/클러스터링에 사용)하고, NL10(10D; 비선형 동역학)은 세그먼트 ≥50 샘플에서 별도 계산하여 F28 = F18 + NL10을 구성(10채널 평균)해 RF 분류에 사용한다. Φ\_B(근육 구조 기반 고정 스케일링; 채널별 특징 벡터에 적용 후 융합)는 ablation에서 제외한 경우를 제외하고 적용했다. **(c)** 평가 항목(평가 축) 5가지: (1) 피험자 독립 교차 지형 분류, (2) 배포 현실형 캘리브레이션, (3) 레이턴시, (4) 협응 지표, (5) 특징 모듈 ablation. **(d)** Perry 위상 경계(0–2–12–31–50–62–75–87–100%)가 표시된 샘플 보행 주기(Initial Contact–Terminal Swing).

---

### 그림 2. 피험자 독립 교차 지형 분류 성능

**(a)** LOSO 3×3 전이 행렬(F28(+Φ\_B)+RF; 균형 평가셋)(훈련 지형(행) × 테스트 지형(열)). 대각선(동일 지형) macro-F1은 0.38–0.40, 비대각선(교차 지형) macro-F1은 0.17–0.39 범위로 관측되었다. 값은 피험자 평균이며 95% CI는 피험자 단위 부트스트랩으로 계산했다(피험자 n = 10). **(b)** 선택된 전이(평지→경사로, 평지→계단)의 대표 혼동 행렬: LOSO 폴드(피험자)별 혼동 행렬 count를 합산한 뒤(피험자 n = 10) 행 정규화하여 제시했으며, UE가 비교적 유지되는 반면 NW/PE는 더 큰 저하를 보인다. **(c)** 0-label 캘리브레이션(훈련 피험자 통계만으로 지형별 z-score; train_only_by_terrain)에서 비대각선/대각선 비율 범위가 0.43–0.99에서 0.67–0.91로 변화했다. 비율은 (캘리브레이션 후 비대각선 macro-F1) / (동일 테스트 지형 열의 대각선 macro-F1)로 정의한다. 색상 스케일: macro-F1 0(흰색)–0.5(진한 파란색; 0.5 초과 값이 있으면 상한으로 표시).

---

### 그림 3. 협응 네트워크 분석 및 특징 모듈 ablation

**(a)** 지형 및 조건별 네트워크 밀도(|r| ≥ 0.6인 근육 쌍 비율). 협응 분석은 균형 평가셋이 아닌 전체 분절 데이터에서, 채널(근육)별 28D(F28 = F18+NL10) 특징 궤적로부터 10×10 상관 행렬을 구성해 계산했다. 평지는 밀도가 상한에 근접(0.90–1.00)한 반면, 경사로(상향/하향)와 계단은 더 낮은 밀도(대략 0.13–0.20)를 보여 지형에 따라 더 희소한 연결 패턴이 나타났다. 오차 막대: 피험자 간 SEM(n = 10). **(b)** ablation(특징 모듈 제거) 효과 크기(|Δ(mean |r|)|): 12개 지형×조건 셀(4 지형 × 3 조건; ablation에서는 경사로를 하향/상향으로 세분화)에서 개별 모듈 제거의 영향을 비교했다. WEF(웨이블릿) 제거는 9/12 셀에서 유의(q < 0.05, BH 보정)(평균 |Δ| = 0.211); NL10은 2/12 셀; Φ\_B는 3/12 셀에서 유의. 별표는 q < 0.05를 나타냄.

---

### 그림 4. End-to-end 레이턴시 및 실시간 가능성

**(a)** Apple M1에서 측정한 end-to-end 레이턴시 분해: NL10 포함 경로(F28; F18+NL10 특징 추출 및 위상별 근육 평균 28D 벡터; 왼쪽)와 NL10 제외 배포 경로(F18+RF; 오른쪽). NL10이 F28 레이턴시를 지배(평균 2,559 ms); F18+RF는 평균 115 ms end-to-end. 구성 요소: 이벤트 검출(8 ms), 전처리(28 ms), 특징 추출, 추론. 주기 단위 레이턴시는 HS→HS 1주기에서 8위상(최대 8개 위상 벡터)에 대해 특징/추론을 수행한 시간을 의미한다. **(b)** F18+RF 경로의 지형별 end-to-end 레이턴시(지형당 5주기, 총 N = 15). 오차 막대: 주기 간 SD. **(c)** 추론 전용 레이턴시 분포(사전 계산된 특징 1개 벡터): 워밍업 5회 후 1,000회 반복. **(d)** 100 Hz 제어 예산(10 ms) 대비: 추론 전용은 13.6%인 반면, 115 ms end-to-end는 10 ms 예산의 약 11.5배(≈1150%)에 해당해 추가 최적화 없이는 ~9 Hz 처리량을 시사한다. RF 추론은 scikit-learn 병렬화(n\_jobs = −1) 조건에서 수행했다. 점선: 100% 예산(10 ms).

---

### 그림 5. 배포 리스크 분석

**(a)** 소량 라벨 캘리브레이션 커브(leave-one-terrain-out): 라벨 예산(0/10/30/90 주기×위상 샘플) 대비 macro-F1. 30회 반복 샘플링 평균 ± SD로 보고. 30 샘플(약 4주기)에서 안정적 개선(SD 0.008–0.010). **(b)** 위험 오분류율(critical error rates): 캘리브레이션 전후 P(pred=PE|true=NW) 및 P(pred=NW|true=PE) 변화. 0-label 및 소량 라벨 조건 비교. **(c)** 지형 라벨 mismatch 민감도: 0-label에서 테스트 시 지형 라벨을 일부러 틀리게 적용했을 때 ΔF1 히트맵. 정답 라벨 대비 성능 변화 범위 −0.18 ~ +0.06. **(d)** 확률 기반 유보(abstain) 정책: max prob ≥ τ인 경우만 출력하는 coverage–위험오류율 곡선. 높은 τ에서 coverage 감소하지만 위험 오분류율 감소.

---

## Extended Data

### Extended Data 그림 1. 도메인 순열 중요도 (LOSO, 동일 지형)

균형 평가셋(기록 파일당 최대 50주기)에서 F28(+Φ\_B)+RF를 사용한 동일 지형 LOSO 도메인 순열 중요도. 홀드아웃 피험자 테스트 세트에서 각 도메인(Time: 6D, Freq: 5D, Wave: 7D, NL10: 10D) 열을 순열해 macro-F1 하락을 계산했다. 오차 막대는 피험자 단위 부트스트랩(2,000회; 피험자 n = 10)로 산출한 95% CI이며, 도메인당 순열은 20회 반복했다.

---

### Extended Data 그림 2. 전체 전이 행렬 및 피험자별 분포(기준선 vs 0-label)

**(a)** baseline 및 0-label 캘리브레이션에 대한 3×3 LOSO 전이 행렬(훈련 지형(행) × 테스트 지형(열); macro-F1 평균 ± 95% 피험자 부트스트랩 CI, 피험자 n = 10). **(b)** 6개 비대각선(교차 지형) 전이에 대한 피험자별 macro-F1 분포(n = 10)를 baseline과 0-label로 비교한 박스플롯.

---

### Extended Data 표 1. 임계값 범위별 edges_auc_norm

| 지형 | 조건 | 0.30–0.90 | 0.40–0.80 | 0.50–0.90 | 0.40–0.90 |
|------|------|:---------:|:---------:|:---------:|:---------:|
| 평지 | NW | 0.972 | 1.000 | 0.958 | 0.967 |
| 평지 | UE | 0.957 | 0.996 | 0.936 | 0.949 |
| 평지 | PE | 0.976 | 1.000 | 0.964 | 0.971 |
| 경사로 | NW | 0.121 | 0.096 | 0.044 | 0.077 |
| 경사로 | UE | 0.097 | 0.080 | 0.042 | 0.064 |
| 경사로 | PE | 0.082 | 0.057 | 0.028 | 0.046 |
| 계단 | NW | 0.147 | 0.108 | 0.053 | 0.089 |
| 계단 | UE | 0.163 | 0.131 | 0.072 | 0.109 |
| 계단 | PE | 0.178 | 0.144 | 0.074 | 0.121 |

**범례**: 임계값 범위에 걸쳐 밀도를 적분하고 범위 너비로 나누어 계산한 정규화된 네트워크 밀도 AUC. 조건 순서는 모든 범위에서 일관됨: 경사로(NW > UE > PE), 계단(PE > UE > NW). 평지에서는 edges_auc_norm이 조건/범위 전반에서 0.936–1.000으로 상한에 근접해(포화) 높은 기준선 연결성과 일관된다.

---

### Extended Data 표 2. HS/TO 검출 파라미터 민감도

| 지형 | 이벤트 | σ=50,int=0.5 | σ=150,int=0.5 | σ=100,int=0.4 | σ=100,int=0.6 | 최대 p95 |
|------|-------|:------------:|:-------------:|:-------------:|:-------------:|:-------:|
| 평지 | HS | 45 | 62 | 38 | 51 | 81 |
| 경사로 | HS | 48 | 58 | 42 | 55 | 78 |
| 계단 | HS | 41 | 52 | 35 | 48 | 75 |
| 평지 | TO | 89 | 124 | 78 | 105 | 156 |
| 경사로 | TO | 95 | 118 | 82 | 112 | 148 |
| 계단 | TO | 87 | 108 | 71 | 98 | 135 |

**범례**: 안정 주기(기준선 σ=100, int=0.5 대비 길이 비율 0.8–1.2)에 대한 p95 |Δt|(ms). HS 타이밍 차이는 모든 변형에서 <80 ms(최대 p95)로 유지된다. TO는 검출(GM 피크, 62% fallback)하되, 위상 경계는 Perry 고정 퍼센트(62% 경계 포함)로 설정되므로 검출된 TO 타이밍은 위상 경계 계산에 사용되지 않는다. Int = min_interval(s).

---

### Extended Data 그림 3. 0-label 캘리브레이션의 지형 라벨 mismatch 민감도

0-label 캘리브레이션은 테스트 시 지형별 정규화 통계(μ/σ)를 선택한다. 지형 라벨 오류에 대한 민감도를 정량화하기 위해, 실제 테스트 지형과 다른 ‘가정 지형’의 정규화 통계를 고의로 적용했다. 히트맵은 각 실제 테스트 지형에 대해 가정 정규화 지형(μ/σ)별 macro-F1(피험자 평균)을 보고한다. 정답 라벨 대비 mismatch는 셀/구성에 따라 Δmacro-F1 −0.180~+0.060의 변화를 유발했다.

---

### Extended Data 그림 4. Stride-time 매칭을 통한 속도 교란(speed confound) 통제(주요 전이)

새 데이터 수집 없이 지형 간 속도 차이를 통제하기 위해, 주기별 stride time(HS→다음 HS)을 속도 대리변수로 사용하고 셀별 stride time 겹침 구간(q10–q90 overlap)을 기준으로 매칭된 부분집합에서 LOSO 전이를 재평가했다. 막대그래프는 주요 교차 지형 전이(평지→경사로, 평지→계단, 계단→평지)의 매칭 전(full)과 매칭 후(speed-matched) macro-F1을 비교하며, 매칭 후 결과의 오차 막대는 95% 피험자 부트스트랩 CI(n = 10)이다.

---

### Extended Data 그림 5. 샘플링 견고성: 시드 × 파일당 주기 cap 민감도

균형 평가셋은 고정 시드(seed = 42)로 기록 파일당 최대 50주기를 샘플링한다. 샘플링 선택에 대한 견고성을 평가하기 위해, 여러 랜덤 시드와 파일당 주기 cap 조건에서 LOSO 전이 평가를 반복하여 셀별 macro-F1 분포를 보고한다.

---

### Extended Data 그림 6. 결측/실패 모드 처리(NL10 NaN; 웨이블릿 sentinel=0)

NL10 비선형 특징은 짧은 위상 세그먼트(≥50 샘플 요구)에서 정의되지 않아 결측이 Initial Contact에 집중될 수 있다. 새 실험 없이 세 가지 전략을 비교했다: invalid 샘플 제거(현행), 결측 NL10을 0으로 대치, 0 대치 + `nl10_valid` 표시 특징 추가. 대각선(동일 지형) 셀에서 위상별 macro-F1을 보고한다. 별도로, 매우 짧은 세그먼트에서는 웨이블릿 요약이 sentinel 0을 반환할 수 있어 위상×지형별 sentinel 비율을 정량화하고, 다른 처리(제외/대치 및 선택적 플래그)가 macro-F1을 얼마나 바꾸는지 평가했다(|Δ| ≤ 0.0064). 신뢰도 곡선 및 캘리브레이션 지표는 Source Data에 제공한다.

---

### Extended Data 그림 7. 누수 없는 비지도 피험자 적응(캘리브레이션 윈도우)

홀드아웃 피험자에 대해 각 테스트 지형에서 기록 파일당 최초 4개 보행 주기를 라벨 없는 캘리브레이션 윈도우로 분리하고, 그 윈도우로 피험자×지형별 z-score 통계(μ/σ)를 추정한 뒤 나머지 주기에서 macro-F1을 평가했다(캘리브레이션 주기 제외). 막대그래프는 6개 비대각선 교차 지형 전이(훈련 지형→테스트 지형)에 대해 baseline, 0-label train-only terrain 정규화(train_only_by_terrain), subject-window 적응(test_window_by_terrain)을 비교한다. 막대는 피험자 평균 macro-F1, 오차 막대는 95% 피험자 부트스트랩 CI(n = 10)이다.

---

## Supplementary Information 목록

| 항목 | 제목 |
|------|------|
| 보충그림 S1 | 지형×조건별 Pearson r 및 mean_r(부호 포함) 분포(전체 분절 데이터) |
| 보충그림 S2 | LOSO 혼동 행렬(9개 훈련 지형 × 테스트 지형 조합; 피험자별 count 합산/풀링) |
| 보충그림 S3 | 위상 및 지형별 NL10 유효성(세그먼트 길이 ≥50 샘플 기준) |
| 보충그림 S4 | 위상 효과 η² 히트맵(2원 ANOVA: 조건 × 위상) |
| 보충그림 S5 | 근육 시너지 가중치(NMF; 계단; k=3) |
| 보충그림 S6 | 파이프라인 구성(S0–S3)별 stage-order 비교(협응 지표 기반) |
| 보충표 S1 | 피험자 수준 macro-F1 점수(지형별; F28; LOSO) |
| 보충표 S2 | 교차 지형 전이 행렬(F18) 및 비대각선 F28−F18 Δ |
| 보충표 S3 | NL10 무효로 인한 주기×위상 제외 수(지형별; 전체 분절 데이터) |
| 보충표 S4 | 특징 모듈 ablation 통계(짝지은 t-검정; BH 보정) |
| 보충표 S5 | 지형 및 feature set별 클래스별 F1 (F28, F18) |
| 보충표 S6 | 피험자 내 5-fold stratified CV 성능(피험자 독립 아님) |
| 보충표 S7 | 근육 구조 파라미터 및 Φ\_B 스케일링 가중치 |
| 보충자료(Data) | 보충자료 파일 및 스키마 요약(JSON/CSV/NPZ) |
