# 데이터 저장소 업로드 가이드

본 문서는 연구 데이터를 공개 저장소에 업로드하는 방법을 안내합니다.

## 권장 저장소

### 1. Zenodo (추천)
- **URL**: https://zenodo.org
- **특징**: 
  - 무료, 오픈 액세스
  - DOI 자동 발급
  - 장기 보존 보장
  - GitHub 연동 가능
- **용량 제한**: 50GB (단일 파일 최대 50GB)

### 2. Figshare
- **URL**: https://figshare.com
- **특징**:
  - 무료, 오픈 액세스
  - DOI 발급
  - 다양한 파일 형식 지원
- **용량 제한**: 5GB (무료 계정)

### 3. OSF (Open Science Framework)
- **URL**: https://osf.io
- **특징**:
  - 무료, 오픈 액세스
  - 프로젝트 관리 기능
  - 버전 관리 지원
- **용량 제한**: 5GB (무료 계정)

## 업로드 전 체크리스트

- [ ] 모든 데이터 파일이 `data/raw/` 디렉토리에 있는지 확인
- [ ] README.md 파일이 완성되었는지 확인
- [ ] 메타데이터 파일들이 생성되었는지 확인
- [ ] 데이터 검증 스크립트 실행하여 오류 확인
- [ ] 파일 크기 확인 (저장소 용량 제한 확인)

## Zenodo 업로드 절차

### 1단계: 계정 생성
1. https://zenodo.org 접속
2. "Sign up" 클릭하여 계정 생성
3. 이메일 인증 완료

### 2단계: 새 업로드 시작
1. 로그인 후 우측 상단 "Upload" 클릭
2. "New Upload" 선택

### 3단계: 메타데이터 입력

#### 기본 정보
- **Upload type**: Dataset
- **Title**: EMG Walking Data Repository
- **Creators**: [저자명 입력]
- **Description**: 
  ```
  본 데이터셋은 보행 중 측정된 16채널 근전도(EMG) 신호를 포함합니다. 
  총 9개의 CSV 파일로 구성되어 있으며, 2024년 12월 11일부터 16일까지 
  수트 미착용 조건에서 측정된 보행 데이터입니다.
  ```

#### 추가 정보
- **Version**: 1.0
- **Publication date**: [발행일]
- **Keywords**: EMG, walking, gait analysis, electromyography, biomechanics
- **License**: CC BY 4.0 (또는 적절한 라이선스 선택)
- **Access right**: Open

### 4단계: 파일 업로드
1. "Files" 섹션에서 전체 `research_data_repository` 폴더를 압축
2. ZIP 파일 업로드 또는 개별 파일 업로드
3. 업로드 진행 상황 확인

### 5단계: 발행
1. 모든 정보 확인
2. "Publish" 클릭
3. DOI 발급 확인 및 저장

## Figshare 업로드 절차

### 1단계: 계정 생성
1. https://figshare.com 접속
2. "Sign up" 클릭하여 계정 생성

### 2단계: 새 데이터셋 생성
1. "Upload" 메뉴 선택
2. "Create a new item" 클릭
3. "Dataset" 선택

### 3단계: 메타데이터 입력
- Title, Description, Keywords 등 입력
- Category: Engineering > Biomedical Engineering

### 4단계: 파일 업로드
1. 파일 드래그 앤 드롭 또는 "Choose files" 클릭
2. 업로드 완료 대기

### 5단계: 발행
1. "Make public" 클릭
2. DOI 확인

## OSF 업로드 절차

### 1단계: 계정 생성
1. https://osf.io 접속
2. "Sign Up" 클릭하여 계정 생성

### 2단계: 프로젝트 생성
1. "Create" > "Project" 선택
2. 프로젝트 이름 및 설명 입력

### 3단계: 파일 업로드
1. "Files" 섹션에서 "Upload" 클릭
2. 전체 폴더 또는 개별 파일 업로드

### 4단계: 공개 설정
1. 프로젝트를 "Public"으로 설정
2. DOI 생성 확인

## 업로드 후 작업

### 1. DOI 저장
- 발급받은 DOI를 안전한 곳에 저장
- 논문에 인용 시 사용

### 2. README 업데이트
- 저장소 URL을 README.md에 추가
- DOI 정보 추가

### 3. 논문 인용 형식
```
[저자명]. (2024). EMG Walking Data Repository (Version 1.0) [Dataset]. 
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

## 주의사항

1. **파일 크기**: 일부 저장소는 무료 계정에 용량 제한이 있습니다. 
   - Zenodo: 50GB (권장)
   - Figshare: 5GB
   - OSF: 5GB

2. **데이터 압축**: ZIP 파일로 압축하여 업로드하면 용량을 절약할 수 있습니다.

3. **메타데이터**: 정확한 메타데이터 입력은 데이터 발견성과 재사용성을 높입니다.

4. **라이선스**: 적절한 라이선스를 선택하여 데이터 사용 조건을 명확히 합니다.

## 문의

업로드 과정에서 문제가 발생하면 각 저장소의 지원팀에 문의하거나 저장소 문서를 참고하세요.

